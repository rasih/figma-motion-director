#!/usr/bin/env python3
"""
verify_motion.py — measure what a rendered animation actually does, and compare
it to what the Motion Spec said it would.

Review is usually "does it feel right." This makes part of it measurable: it
reads the frames, derives a normalised visual-progress curve, and reports the
measured duration and how far the motion deviates from the specified easing.

    python3 verify_motion.py anim.mp4 --expect-duration 300 --expect-easing e.enter

Output is a small table plus a verdict. A deviation under ~0.05 means the built
motion follows the specified curve; a larger one means the file and the spec
disagree, and the spec is not the thing that shipped.

Progress metric: for every frame, how far the image has travelled from the first
frame toward the last, measured as normalised mean absolute difference. It is
property-agnostic — translation, opacity, scale and colour all register — which
is what makes it usable without instrumenting the page.

Limits worth knowing: it assumes one motion resolving to a settled end state. A
looping animation, a boomerang, or several overlapping moves with different
timings will not produce a clean monotonic curve — crop to a single moment
first. Use --region to exclude parts of the frame that move independently.

Requires: ffmpeg, numpy, Pillow.
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image

# The skill's easing tokens, as cubic-bezier control points.
EASINGS = {
    "e.enter":      (0.0,  0.0,  0.0,  1.0),
    "e.exit":       (0.3,  0.0,  1.0,  1.0),
    "e.move":       (0.2,  0.0,  0.0,  1.0),
    "e.expressive": (0.05, 0.7,  0.1,  1.0),
    "e.linear":     (0.0,  0.0,  1.0,  1.0),
    # common aliases, so a CSS keyword can be checked too
    "ease-out":     (0.0,  0.0,  0.58, 1.0),
    "ease-in":      (0.42, 0.0,  1.0,  1.0),
    "ease-in-out":  (0.42, 0.0,  0.58, 1.0),
    "ease":         (0.25, 0.1,  0.25, 1.0),
    "linear":       (0.0,  0.0,  1.0,  1.0),
}


def bezier_curve(x1, y1, x2, y2, samples=2000):
    u = np.linspace(0, 1, samples)
    xs = 3 * u * (1 - u) ** 2 * x1 + 3 * u ** 2 * (1 - u) * x2 + u ** 3
    ys = 3 * u * (1 - u) ** 2 * y1 + 3 * u ** 2 * (1 - u) * y2 + u ** 3
    return xs, ys


def bezier_at(t, pts):
    xs, ys = bezier_curve(*pts)
    return np.interp(np.clip(t, 0, 1), xs, ys)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("video")
    p.add_argument("--expect-duration", type=float, default=None,
                   help="specified duration in ms (e.g. 300 for t.lg)")
    p.add_argument("--expect-easing", default=None,
                   help=f"one of: {', '.join(sorted(EASINGS))}")
    p.add_argument("--region", default="",
                   help="x,y,w,h in source pixels — measure only this area")
    p.add_argument("--settle", type=float, default=0.99,
                   help="progress counted as settled (default 0.99)")
    p.add_argument("--width", type=int, default=240,
                   help="downscale width for analysis; smaller is faster and less noisy")
    p.add_argument("--metric", default="auto",
                   choices=["auto", "shift", "mad"],
                   help="shift = geometric, measures travel by profile alignment (accurate for "
                        "movement); mad = pixel difference (works for opacity and colour, "
                        "noisier for composite scenes); auto picks shift when there is "
                        "clear directional travel")
    a = p.parse_args()

    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg not found on PATH")
    if not os.path.exists(a.video):
        sys.exit(f"not found: {a.video}")

    fps = float(subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=r_frame_rate", "-of", "csv=p=0", a.video],
        capture_output=True, text=True).stdout.strip().split("/")[0]) / 1.0
    rate = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=r_frame_rate", "-of", "csv=p=0", a.video],
        capture_output=True, text=True).stdout.strip()
    num, den = rate.split("/")
    fps = float(num) / float(den or 1)

    tmp = tempfile.mkdtemp(prefix="verify_")
    vf = [f"scale={a.width}:-1"]
    if a.region:
        x, y, w, h = (int(v) for v in a.region.split(","))
        vf = [f"crop={w}:{h}:{x}:{y}"] + vf
    subprocess.run(["ffmpeg", "-y", "-i", a.video, "-vf", ",".join(vf),
                    os.path.join(tmp, "f%05d.png")], capture_output=True)

    files = sorted(f for f in os.listdir(tmp) if f.endswith(".png"))
    if len(files) < 4:
        sys.exit("not enough frames to measure")
    frames = [np.asarray(Image.open(os.path.join(tmp, f)).convert("RGB"),
                         dtype=np.float32) for f in files]
    shutil.rmtree(tmp, ignore_errors=True)

    first, last = frames[0], frames[-1]
    span = np.abs(first - last).mean()
    if span < 0.5:
        sys.exit("first and last frame are nearly identical — nothing measurable. "
                 "Is this a loop? Crop to a single moment.")

    def prog_mad():
        v = np.array([1.0 - np.abs(f - last).mean() / span for f in frames])
        return np.clip(v, 0.0, 1.0)

    def profiles(axis):
        """1-D intensity profile per frame: mean along the other axis."""
        ax = 1 if axis == "y" else 0
        return [f.mean(axis=2).mean(axis=ax) for f in frames]

    def shifts(axis):
        """Displacement of each frame relative to the FINAL frame, in pixels,
        by 1-D alignment of intensity profiles.

        This measures travel directly, so it stays linear in displacement —
        unlike a whole-frame pixel difference, which saturates the moment the
        element has moved its own size."""
        profs = profiles(axis)
        ref = profs[-1] - profs[-1].mean()
        n = len(ref)
        lim = max(2, n // 2)
        out = []
        for pr in profs:
            p = pr - pr.mean()
            best, best_s = None, 0
            for s in range(-lim, lim + 1):
                if s >= 0:
                    aa, bb = p[s:], ref[:n - s] if s else ref
                else:
                    aa, bb = p[:n + s], ref[-s:]
                if len(aa) < n // 3:
                    continue
                err = float(np.mean((aa - bb) ** 2))
                if best is None or err < best:
                    best, best_s = err, s
            out.append(float(best_s))
        return np.array(out)

    metric, axis = a.metric, "y"
    sy = sx = None
    if metric in ("auto", "shift"):
        sy, sx = shifts("y"), shifts("x")
        ty, tx = abs(sy[0] - sy[-1]), abs(sx[0] - sx[-1])
        axis = "y" if ty >= tx else "x"
        travel = max(ty, tx)
        # a shift worth trusting must exceed a few pixels at analysis scale
        if metric == "auto":
            metric = "shift" if travel >= 4 else "mad"

    if metric == "shift":
        s = sy if axis == "y" else sx
        s0 = s[0]
        if abs(s0) < 1e-6:
            prog, metric = prog_mad(), "mad"
        else:
            prog = np.clip(1.0 - s / s0, 0.0, 1.0)
    else:
        prog = prog_mad()

    prog[0] = 0.0
    # a settling curve should not go backwards; smooths alignment noise
    prog = np.maximum.accumulate(prog)

    settled = np.argmax(prog >= a.settle) if (prog >= a.settle).any() else len(prog) - 1
    measured_ms = settled / fps * 1000.0

    print(f"\nsource        {a.video}")
    print(f"frames        {len(frames)} @ {fps:.3f} fps")
    print(f"metric        {metric}" + (f" ({axis}-axis travel)" if metric == "shift" else
                                       " (whole-frame pixel difference)"))
    print(f"measured      {measured_ms:.0f} ms to {a.settle:.0%} settled")

    if a.expect_duration:
        # A front-loaded curve reaches 99% well before its nominal duration, so
        # compare like with like: when SHOULD the specified curve hit --settle?
        ref_ms = a.expect_duration
        if a.expect_easing in EASINGS:
            xs, ys = bezier_curve(*EASINGS[a.expect_easing])
            ref_ms = float(np.interp(a.settle, ys, xs)) * a.expect_duration
        d = measured_ms - ref_ms
        pct = d / ref_ms * 100 if ref_ms else 0.0
        flag = "OK" if abs(pct) <= 12 else "MISMATCH"
        note = (f"  (specified {a.expect_duration:.0f} ms nominal; "
                f"{a.expect_easing} reaches {a.settle:.0%} at {ref_ms:.0f} ms)"
                if ref_ms != a.expect_duration else "")
        print(f"expected      {ref_ms:.0f} ms   ({d:+.0f} ms, {pct:+.1f}%)  {flag}{note}")

    if a.expect_easing:
        key = a.expect_easing
        if key not in EASINGS:
            sys.exit(f"unknown easing '{key}'. known: {', '.join(sorted(EASINGS))}")
        pts = EASINGS[key]
        dur_ms = a.expect_duration or measured_ms
        n = max(2, int(round(dur_ms / 1000.0 * fps)))
        print(f"\n{'t (ms)':>8} {'measured':>10} {'expected':>10} {'err':>8}")
        errs = []
        for i in range(0, n + 1, max(1, n // 8)):
            i = min(i, len(prog) - 1)
            t_ms = i / fps * 1000.0
            exp = float(bezier_at(min(t_ms / dur_ms, 1.0), pts))
            e = abs(prog[i] - exp)
            errs.append(e)
            print(f"{t_ms:8.0f} {prog[i]:10.3f} {exp:10.3f} {e:8.3f}")
        worst = max(errs)
        verdict = ("follows the specified curve" if worst < 0.05 else
                   "close, but off the specified curve" if worst < 0.12 else
                   "does NOT follow the specified curve")
        print(f"\neasing        {key}  max deviation {worst:.3f} — {verdict}")

    # Best-fit ranking is the more honest reading: an absolute threshold is
    # fragile across scenes, but "which curve does this actually look like"
    # is stable, and it names the mistake when the answer is not the spec.
    dur_ms = a.expect_duration or measured_ms
    n = max(2, int(round(dur_ms / 1000.0 * fps)))
    idxs = [min(i, len(prog) - 1) for i in range(0, n + 1)]
    fits = []
    for name, pts in EASINGS.items():
        if name in ("ease-out", "ease-in", "ease-in-out", "ease", "linear"):
            continue  # rank against the skill's own tokens
        err = max(abs(prog[i] - float(bezier_at(min(i / fps * 1000.0 / dur_ms, 1.0), pts)))
                  for i in idxs)
        fits.append((err, name))
    fits.sort()
    print("\nbest fit      " + " · ".join(f"{n} {e:.3f}" for e, n in fits[:3]))
    if a.expect_easing and fits and fits[0][1] != a.expect_easing:
        print(f"              closest curve is {fits[0][1]}, not the specified "
              f"{a.expect_easing} — check the build against the spec")

    if not a.expect_duration and not a.expect_easing:
        print("\n(pass --expect-duration and --expect-easing to check against the spec)")

    print()


if __name__ == "__main__":
    main()
