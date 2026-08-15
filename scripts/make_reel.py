#!/usr/bin/env python3
"""
make_reel.py — composite a screen recording into a device frame and render a
9:16 social video (Reels / TikTok / Shorts).

The device frame is drawn procedurally with Pillow — no bundled device images,
no third-party artwork, nothing to license. Composition and encoding are done
by ffmpeg.

Typical use, straight from a Figma `export_video` MP4:

    python3 make_reel.py anim.mp4 -o reel.mp4 \
        --bg "#0B0B0F" --loops 3 --hold-start 0.4 --hold-end 0.8

Requires: ffmpeg, ffprobe, Pillow.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
except ImportError:
    sys.exit("Pillow is required:  pip install Pillow --break-system-packages")


# ---------------------------------------------------------------- devices ---
# width/height are the SCREEN aspect; bezel is drawn around it.
# island: (w, h) of the top cutout, or None for a plain bezel.
DEVICES = {
    "iphone":      {"aspect": 19.5 / 9, "radius": 0.058, "bezel": 0.030,
                    "island": (0.30, 0.038), "body": "#1C1C1E"},
    "iphone-flat": {"aspect": 19.5 / 9, "radius": 0.058, "bezel": 0.030,
                    "island": None, "body": "#1C1C1E"},
    "android":     {"aspect": 20 / 9,   "radius": 0.045, "bezel": 0.026,
                    "island": None, "body": "#141414"},
    "bare":        {"aspect": None,     "radius": 0.030, "bezel": 0.0,
                    "island": None, "body": "#000000"},
}

CANVAS = (1080, 1920)  # 9:16


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)


def probe(path):
    out = run(["ffprobe", "-v", "error", "-select_streams", "v:0",
               "-show_entries", "stream=width,height,r_frame_rate,duration",
               "-show_entries", "format=duration",
               "-of", "json", path]).stdout
    d = json.loads(out)
    s = d["streams"][0]
    num, den = (s.get("r_frame_rate") or "30/1").split("/")
    dur = s.get("duration") or d.get("format", {}).get("duration") or "0"
    return {"w": int(s["width"]), "h": int(s["height"]),
            "fps": float(num) / float(den or 1), "dur": float(dur)}


def hexrgb(s):
    s = s.lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def build_overlay(vid_w, vid_h, dev, bg, scale, y_shift, caption, font_px,
                  caption_color, safe_guides, out_png):
    """
    Returns (overlay_path, screen_x, screen_y, screen_w, screen_h).

    The overlay is a full-canvas RGBA image that is opaque everywhere except a
    rounded-rect hole where the screen goes. Painting it OVER the video both
    masks the video's square corners and draws the bezel and background in one
    pass.
    """
    CW, CH = CANVAS
    ss = 4  # supersample for clean rounded corners
    W, H = CW * ss, CH * ss

    # a caption needs clear space at the top — make room rather than collide
    if caption:
        scale = min(scale, 0.80)
        y_shift += 0.022

    src_aspect = vid_h / vid_w
    aspect = dev["aspect"] or src_aspect

    # Fit the device (screen + bezel) into the canvas at `scale` of its height.
    dev_h = H * scale
    dev_w = dev_h / (aspect + 2 * dev["bezel"] * aspect) * 1.0
    # solve so that screen_h/screen_w == aspect and bezel is a fraction of screen width
    screen_w = dev_h / (aspect + 2 * dev["bezel"])
    screen_h = screen_w * aspect
    bezel = screen_w * dev["bezel"]
    dev_w = screen_w + 2 * bezel
    dev_h = screen_h + 2 * bezel

    if dev_w > W * 0.94:                      # never let it touch the edges
        k = (W * 0.94) / dev_w
        screen_w *= k; screen_h *= k; bezel *= k
        dev_w = screen_w + 2 * bezel
        dev_h = screen_h + 2 * bezel

    dev_x = (W - dev_w) / 2
    dev_y = (H - dev_h) / 2 + y_shift * H

    img = Image.new("RGBA", (W, H), hexrgb(bg) + (255,))
    body_r = screen_w * dev["radius"] + bezel

    # soft drop shadow, so the device separates from the background
    if dev["bezel"] > 0:
        sh = Image.new("L", (W, H), 0)
        ImageDraw.Draw(sh).rounded_rectangle(
            [dev_x, dev_y + dev_h * 0.012, dev_x + dev_w, dev_y + dev_h * 1.012],
            radius=body_r, fill=150)
        sh = sh.filter(ImageFilter.GaussianBlur(radius=int(bezel * 2.2)))
        img.paste(Image.new("RGBA", (W, H), (0, 0, 0, 255)), (0, 0), sh)

    d = ImageDraw.Draw(img)

    # device body
    d.rounded_rectangle([dev_x, dev_y, dev_x + dev_w, dev_y + dev_h],
                        radius=body_r, fill=hexrgb(dev["body"]) + (255,))

    # screen hole -> fully transparent, so the video shows through
    sx, sy = dev_x + bezel, dev_y + bezel
    d.rounded_rectangle([sx, sy, sx + screen_w, sy + screen_h],
                        radius=screen_w * dev["radius"], fill=(0, 0, 0, 0))

    # dynamic-island style cutout, drawn on top of the video
    if dev["island"]:
        iw, ih = dev["island"][0] * screen_w, dev["island"][1] * screen_h
        ix = sx + (screen_w - iw) / 2
        iy = sy + screen_h * 0.014
        d.rounded_rectangle([ix, iy, ix + iw, iy + ih], radius=ih / 2,
                            fill=(0, 0, 0, 255))

    img = img.resize((CW, CH), Image.LANCZOS)
    d = ImageDraw.Draw(img)

    sx, sy = sx / ss, sy / ss
    screen_w, screen_h = screen_w / ss, screen_h / ss

    if safe_guides:
        # Instagram/TikTok chrome: ~14% top, ~20% bottom, ~12% right
        g = (255, 64, 64, 110)
        for box in [(0, 0, CW, CH * 0.14), (0, CH * 0.80, CW, CH),
                    (CW * 0.88, 0, CW, CH)]:
            d.rectangle(box, outline=g, width=3)

    if caption:
        try:
            font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_px)
        except OSError:
            font = ImageFont.load_default()
        tw = d.textbbox((0, 0), caption, font=font)[2]
        d.text(((CW - tw) / 2, CH * 0.052), caption,
               font=font, fill=hexrgb(caption_color) + (255,))

    img.save(out_png)
    # even dimensions keep libx264 happy
    return out_png, int(sx), int(sy), int(screen_w) // 2 * 2, int(screen_h) // 2 * 2


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="source video (e.g. Figma export_video output)")
    p.add_argument("-o", "--output", default="reel.mp4")
    p.add_argument("--device", default="iphone", choices=sorted(DEVICES))
    p.add_argument("--bg", default="#0B0B0F", help="background colour")
    p.add_argument("--scale", type=float, default=0.82,
                   help="device height as a fraction of the canvas (0.55–0.9)")
    p.add_argument("--y-shift", type=float, default=0.0,
                   help="move the device up/down, fraction of canvas height")
    p.add_argument("--caption", default="", help="text across the top")
    p.add_argument("--caption-size", type=int, default=46)
    p.add_argument("--caption-color", default="#FFFFFF")
    p.add_argument("--loops", type=int, default=1, help="repeat the motion N times")
    p.add_argument("--hold-start", type=float, default=0.0,
                   help="seconds to hold the first frame before motion starts")
    p.add_argument("--hold-end", type=float, default=0.0,
                   help="seconds to hold the last frame after motion ends")
    p.add_argument("--boomerang", action="store_true",
                   help="play forward then reversed — hides the loop seam")
    p.add_argument("--fps", type=int, default=30)
    p.add_argument("--safe-guides", action="store_true",
                   help="overlay red boxes showing where platform UI covers the frame")
    p.add_argument("--keep-temp", action="store_true")
    a = p.parse_args()

    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            sys.exit(f"{tool} not found on PATH")
    if not os.path.exists(a.input):
        sys.exit(f"input not found: {a.input}")

    info = probe(a.input)
    tmp = tempfile.mkdtemp(prefix="reel_")

    overlay, sx, sy, sw, sh = build_overlay(
        info["w"], info["h"], DEVICES[a.device], a.bg, a.scale, a.y_shift,
        a.caption, a.caption_size, a.caption_color, a.safe_guides,
        os.path.join(tmp, "overlay.png"))

    # --- 1. pace the source: holds, boomerang, loops -----------------------
    clip = os.path.join(tmp, "clip.mp4")
    vf = [f"fps={a.fps}", f"scale={sw}:{sh}:force_original_aspect_ratio=increase",
          f"crop={sw}:{sh}"]
    if a.hold_start > 0:
        vf.append(f"tpad=start_duration={a.hold_start}:start_mode=clone")
    if a.hold_end > 0:
        vf.append(f"tpad=stop_duration={a.hold_end}:stop_mode=clone")
    run(["ffmpeg", "-y", "-i", a.input, "-vf", ",".join(vf),
         "-an", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", clip])

    if a.boomerang:
        boom = os.path.join(tmp, "boom.mp4")
        run(["ffmpeg", "-y", "-i", clip, "-filter_complex",
             "[0:v]split[a][b];[b]reverse[r];[a][r]concat=n=2:v=1[v]",
             "-map", "[v]", "-an", "-c:v", "libx264", "-crf", "16",
             "-pix_fmt", "yuv420p", boom])
        clip = boom

    if a.loops > 1:
        looped = os.path.join(tmp, "looped.mp4")
        run(["ffmpeg", "-y", "-stream_loop", str(a.loops - 1), "-i", clip,
             "-an", "-c", "copy", looped])
        clip = looped

    # --- 2. composite: video underneath, overlay on top --------------------
    run(["ffmpeg", "-y", "-i", clip, "-i", overlay, "-filter_complex",
         f"[0:v]setpts=PTS-STARTPTS[v];"
         f"color=c=black:s={CANVAS[0]}x{CANVAS[1]}:r={a.fps}[bgc];"
         f"[bgc][v]overlay={sx}:{sy}:shortest=1[stage];"
         f"[stage][1:v]overlay=0:0:format=auto[out]",
         "-map", "[out]", "-an", "-c:v", "libx264", "-preset", "slow",
         "-crf", "18", "-pix_fmt", "yuv420p",
         "-movflags", "+faststart", a.output])

    out = probe(a.output)
    print(f"{a.output}  {out['w']}x{out['h']}  {out['dur']:.2f}s  "
          f"{a.fps}fps  device={a.device}")
    if out["dur"] < 3:
        print("  note: under 3s — most platforms bury very short clips. "
              "Add --loops or --hold-end.")

    if a.keep_temp:
        print(f"  temp: {tmp}")
    else:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
