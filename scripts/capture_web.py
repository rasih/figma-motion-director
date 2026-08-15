#!/usr/bin/env python3
"""
capture_web.py — record HTML/CSS/JS motion to a jitter-free MP4.

Screen recording gives you whatever frames the machine happened to produce.
This does not record in real time: it **virtualises the clock**, advances it one
frame at a time, and screenshots each step. Every frame lands exactly where the
spec says it should, at any fps, on any machine, headless.

It drives three clocks at once so both CSS and JS motion step together:
  * `document.getAnimations()`  — CSS animations, transitions, Web Animations API
  * `requestAnimationFrame`     — JS-driven motion (Motion, GSAP, hand-rolled rAF)
  * `performance.now` / `Date.now` — anything reading the wall clock

    python3 capture_web.py sheet.html -o anim.mp4 --width 390 --height 844 \
        --duration 1.2 --fps 60 --settle 0.3

Then frame it for social:

    python3 make_reel.py anim.mp4 -o reel.mp4 --caption "Sheet · 300ms · ease-out"

Requires: playwright (with chromium), ffmpeg.
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sys.exit("playwright is required:\n"
             "  pip install playwright --break-system-packages\n"
             "  (chromium is already present if PLAYWRIGHT_BROWSERS_PATH is set)")


# Installed before any page script runs, so nothing can capture the real clock
# first. Motion libraries read performance.now() on their first frame, so this
# has to be an init script, not an evaluate() after load.
VIRTUAL_CLOCK = r"""
(() => {
  const origRAF = window.requestAnimationFrame;
  let now = 0;                 // virtual ms
  let nextId = 1;
  let queue = new Map();       // id -> callback

  window.__vclock = {
    get now() { return now; },
    set(t) { now = t; },
    // run every rAF callback queued so far, once, at the current virtual time
    flush(passes = 2) {
      for (let p = 0; p < passes; p++) {
        const due = queue;
        queue = new Map();
        for (const cb of due.values()) {
          try { cb(now); } catch (e) { /* keep stepping */ }
        }
      }
    },
    pending() { return queue.size; },
  };

  window.requestAnimationFrame = (cb) => { const id = nextId++; queue.set(id, cb); return id; };
  window.cancelAnimationFrame = (id) => { queue.delete(id); };

  const realNow = performance.now.bind(performance);
  performance.now = () => now;
  const RealDate = Date;
  const origin = RealDate.now();
  window.Date = new Proxy(RealDate, {
    construct(t, a) { return a.length ? new t(...a) : new t(origin + now); },
    get(t, p) { return p === 'now' ? () => origin + now : Reflect.get(t, p); },
  });

  // keep a handle on the real rAF for the harness itself
  window.__realRAF = origRAF;
})();
"""

FREEZE_DECLARATIVE = r"""
() => {
  // Pause everything the browser is animating declaratively so the harness,
  // not the compositor, decides where each one sits.
  for (const a of document.getAnimations()) {
    try { a.pause(); } catch (e) {}
  }
  return document.getAnimations().length;
}
"""

SEEK_DECLARATIVE = r"""
(t) => {
  for (const a of document.getAnimations()) {
    try {
      const d = (a.effect && a.effect.getTiming) ? a.effect.getTiming().duration : null;
      const delay = (a.effect && a.effect.getTiming) ? (a.effect.getTiming().delay || 0) : 0;
      const total = (typeof d === 'number' ? d : 0) + delay;
      a.currentTime = (total > 0) ? Math.min(t, total) : t;
    } catch (e) {}
  }
}
"""


def run(cmd):
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("source", help="path to an .html file, or a http(s) URL")
    p.add_argument("-o", "--output", default="anim.mp4")
    p.add_argument("--width", type=int, default=390, help="viewport width (CSS px)")
    p.add_argument("--height", type=int, default=844, help="viewport height (CSS px)")
    p.add_argument("--dpr", type=float, default=3.0,
                   help="device pixel ratio — 3 gives a crisp phone-sized capture")
    p.add_argument("--duration", type=float, default=2.0, help="seconds to capture")
    p.add_argument("--fps", type=int, default=60)
    p.add_argument("--settle", type=float, default=0.3,
                   help="seconds of real time to let fonts/images/layout settle before t=0")
    p.add_argument("--start-at", type=float, default=0.0,
                   help="virtual seconds to skip before the first captured frame")
    p.add_argument("--click", default="",
                   help="CSS selector to click at t=0 — for motion that needs a trigger")
    p.add_argument("--wait-for", default="",
                   help="CSS selector to wait for before starting")
    p.add_argument("--realtime", action="store_true",
                   help="do NOT virtualise the clock; screenshot in real time. "
                        "Fallback for pages that break under a fake clock")
    p.add_argument("--transparent", action="store_true",
                   help="capture with a transparent background (outputs PNG frames + WebM)")
    p.add_argument("--keep-frames", action="store_true")
    a = p.parse_args()

    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg not found on PATH")

    url = a.source
    if not url.startswith(("http://", "https://", "file://")):
        path = os.path.abspath(a.source)
        if not os.path.exists(path):
            sys.exit(f"not found: {a.source}")
        url = "file://" + path

    n_frames = max(1, int(round(a.duration * a.fps)))
    step_ms = 1000.0 / a.fps
    tmp = tempfile.mkdtemp(prefix="capweb_")

    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=[
            "--force-color-profile=srgb",
            "--disable-lcd-text",              # consistent text rendering headless
            "--font-render-hinting=none",
            "--hide-scrollbars",
        ])
        ctx = browser.new_context(
            viewport={"width": a.width, "height": a.height},
            device_scale_factor=a.dpr,
            reduced_motion="no-preference",     # never capture the reduced variant by accident
            color_scheme="light",
        )
        if not a.realtime:
            ctx.add_init_script(VIRTUAL_CLOCK)

        page = ctx.new_page()
        page.goto(url, wait_until="load")
        if a.wait_for:
            page.wait_for_selector(a.wait_for, timeout=10000)
        try:
            page.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass
        page.wait_for_timeout(int(a.settle * 1000))   # real time: fonts, images, layout

        if a.click:
            page.click(a.click)

        n_decl = 0
        if not a.realtime:
            n_decl = page.evaluate(FREEZE_DECLARATIVE)
            page.evaluate("() => window.__vclock.flush(3)")

        for i in range(n_frames):
            t_ms = (a.start_at * 1000.0) + i * step_ms
            if not a.realtime:
                page.evaluate("(t) => window.__vclock.set(t)", t_ms)
                page.evaluate("() => window.__vclock.flush(2)")
                page.evaluate(SEEK_DECLARATIVE, t_ms)
                # a paused animation only repaints once its time is committed
                page.evaluate("() => new Promise(r => window.__realRAF(r))")
            else:
                page.wait_for_timeout(int(step_ms))
            page.screenshot(path=os.path.join(tmp, f"f{i:05d}.png"),
                            omit_background=a.transparent)

        browser.close()

    if a.transparent:
        out = a.output if a.output.endswith(".webm") else a.output.rsplit(".", 1)[0] + ".webm"
        run(["ffmpeg", "-y", "-framerate", str(a.fps), "-i", os.path.join(tmp, "f%05d.png"),
             "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-crf", "24", "-b:v", "0", out])
    else:
        out = a.output
        run(["ffmpeg", "-y", "-framerate", str(a.fps), "-i", os.path.join(tmp, "f%05d.png"),
             "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p",
             "-movflags", "+faststart", out])

    mode = "realtime" if a.realtime else f"virtual clock, {n_decl} declarative animation(s)"
    print(f"{out}  {a.width * a.dpr:.0f}x{a.height * a.dpr:.0f}  "
          f"{a.duration}s  {a.fps}fps  {n_frames} frames  ({mode})")

    if a.keep_frames:
        print(f"  frames: {tmp}")
    else:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
