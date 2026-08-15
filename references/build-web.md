# Building motion on the web

The second BUILD path. Load this instead of the Figma path when the motion is going to live in a browser — which is most motion, and all of it when Figma's motion APIs are not enabled for the account.

Same INTENT, same BENCHMARK, same SPEC, same REVIEW. Only the build target changes.

```
SPEC  →  HTML/CSS from the tokens  →  capture_web.py  →  verify_motion.py  →  make_reel.py
                                       deterministic       measured against      device-framed
                                       frames              the spec              9:16
```

Nothing in this path needs Figma, a plugin, or a feature flag. It runs headless.

## 1. Why capture instead of screen-record

A screen recording gives you whatever frames the machine happened to produce: dropped frames under load, timing that drifts with CPU, a different result on every run. For a review that is noise, and for a published reel it is a quality ceiling.

[`scripts/capture_web.py`](../scripts/capture_web.py) does not record in real time. It **virtualises the clock** and advances it one frame at a time:

- `document.getAnimations()` — every CSS animation, CSS transition, and Web Animations API animation is paused, then seeked frame by frame
- `requestAnimationFrame` — queued, then flushed manually at each virtual timestamp, so JS-driven motion steps in lockstep
- `performance.now` and `Date.now` — replaced, because motion libraries read the wall clock on their first frame

The result is frame-exact at any fps, on any machine, headless, and reproducible. It also means you can capture at 120fps for a slow-motion breakdown without owning a 120Hz display.

```bash
python3 scripts/capture_web.py sheet.html -o anim.mp4 \
    --width 390 --height 844 --dpr 3 --duration 1.4 --fps 60
```

| Flag | Notes |
|---|---|
| `--width` / `--height` | CSS pixels. 390×844 is a common phone frame; 1440×900 for desktop |
| `--dpr` | Device pixel ratio. 3 gives a crisp capture worth publishing; 1 is fine for a review pass |
| `--duration` / `--fps` | Virtual seconds and frame rate. 60fps for review, 60 for reels, 120 when you intend to slow it down |
| `--settle` | Real seconds before t=0, for fonts, images, and layout. Raise it if the first frame shows unstyled text |
| `--click` | CSS selector to click at t=0, for motion that needs a trigger |
| `--wait-for` | Selector to wait for before starting |
| `--start-at` | Skip virtual seconds — useful for capturing the second half of a long sequence |
| `--transparent` | PNG-alpha frames out to WebM, for compositing over a background later |
| `--realtime` | Fallback: no virtual clock, screenshot in real time. Use only if a page misbehaves under the fake clock |

## 2. Tokens as CSS

Put the system in `:root` and never type a number in a rule. This is the same discipline as [ship-to-code.md §1](ship-to-code.md#1-token-parity), and it makes the HTML a readable expression of the spec.

```css
:root{
  --t-none: 0ms;   --t-tap: 70ms;   --t-xs: 110ms;  --t-sm: 150ms;
  --t-md: 240ms;   --t-lg: 300ms;   --t-xl: 400ms;  --t-2xl: 700ms;

  --e-enter:      cubic-bezier(0, 0, 0, 1);
  --e-exit:       cubic-bezier(0.3, 0, 1, 1);
  --e-move:       cubic-bezier(0.2, 0, 0, 1);
  --e-expressive: cubic-bezier(0.05, 0.7, 0.1, 1);
  --e-linear:     linear;
  --e-hold:       steps(1, jump-end);
}

.sheet{
  transform: translateY(340px);
  animation: sheet-in var(--t-lg) var(--e-enter) forwards;
}
@keyframes sheet-in{ to{ transform: translateY(0); } }
```

A reviewer reading `var(--t-lg) var(--e-enter)` can check it against the spec at a glance. A reviewer reading `300ms cubic-bezier(0,0,0,1)` has to go and look it up.

## 3. Transitions or keyframes

The choice matters more than it looks, and it is the one place this path differs materially from the Figma path.

| Use | When |
|---|---|
| **CSS transition** | Anything the user can re-trigger: hover, press, toggle, open/close. A transition **retargets from the current value**, so re-triggering mid-flight is smooth |
| **CSS animation / keyframes** | A one-shot entrance on mount, or a deliberate loop. A keyframe animation **restarts from frame zero** on re-trigger, which is the interruptibility failure in [ship-to-code.md §4](ship-to-code.md#4-interruptibility) |
| **Web Animations API** | When you need to read or seek the animation from JS — and it is what `capture_web.py` drives, so it captures cleanly |
| **A motion library** | Where real velocity exists: drag, flick, swipe-to-dismiss. Springs that absorb gesture velocity cannot be expressed in CSS |

Capture handles all four. The virtual clock covers the library case because it replaces `requestAnimationFrame` and the wall clock before any page script runs.

## 4. Verify against the spec

This is the part the Figma path cannot do as well, and it is worth using.

```bash
python3 scripts/verify_motion.py anim.mp4 --expect-duration 300 --expect-easing e.enter
```

It measures displacement frame by frame — by aligning intensity profiles, so the measure stays linear in travel rather than saturating — and prints the measured settle time, the deviation from the specified curve, and which of the tokens the motion actually resembles.

```
metric        shift (y-axis travel)
measured      250 ms to 99% settled
expected      250 ms   (-0 ms, -0.0%)  OK
easing        e.enter  max deviation 0.002 — follows the specified curve
best fit      e.enter 0.002 · e.expressive 0.178 · e.move 0.289
```

**Read the best-fit line before the verdict.** An absolute threshold is fragile across scenes; "which curve does this actually look like" is stable, and when the answer is not the token you specified, it names the mistake. A build that comes back `best fit e.linear` when the spec says `e.enter` had its easing dropped somewhere — a very common CSS bug, since a missing `transition-timing-function` silently falls back to `ease`.

Limits, stated plainly: it assumes **one motion resolving to a settled end state**. Loops, boomerangs, and several overlapping moves on different clocks will not produce a clean curve — capture a single moment, or use `--region x,y,w,h` to measure only the element in question. For opacity-only or colour-only motion there is no travel to align, so it falls back to a pixel-difference metric that is noisier; trust the best-fit ranking over the absolute number there.

## 5. Recipes

**Motion that needs a trigger.** Put the interaction behind a class the click adds, and let capture click it at t=0:

```bash
python3 scripts/capture_web.py demo.html -o anim.mp4 --click "#open" --duration 1.2
```

**A slow-motion breakdown for teaching.** Capture at high fps, then slow the file — and label it, per [reel.md §1](reel.md#1-the-rule-that-matters):

```bash
python3 scripts/capture_web.py demo.html -o fast.mp4 --fps 120 --duration 0.4
ffmpeg -i fast.mp4 -filter:v "setpts=4.0*PTS" -an slow.mp4
python3 scripts/make_reel.py slow.mp4 -o reel.mp4 --caption "0.25× · 300ms actual"
```

**Before and after.** Capture both, stack them, label both. This is the most persuasive motion post there is, and it takes two captures:

```bash
python3 scripts/capture_web.py before.html -o a.mp4 --duration 1.4
python3 scripts/capture_web.py after.html  -o b.mp4 --duration 1.4
ffmpeg -i a.mp4 -i b.mp4 -filter_complex hstack -an compare.mp4
```

**Transparent, for compositing.** `--transparent` writes WebM with alpha, so the motion can sit over any background later.

## 6. What breaks, and what to do

| Symptom | Cause | Fix |
|---|---|---|
| First frame shows unstyled text | Web fonts had not loaded at t=0 | Raise `--settle`, or `<link rel=preload>` the font |
| Nothing moves in the capture | The motion needs a trigger, or starts on scroll/intersection | `--click`, or set the start state in markup instead of on an event |
| JS motion frozen at frame 0 | The library caches a timestamp before the init script — rare, but possible with some bundlers | `--realtime`, and accept the frame jitter |
| Video or canvas content is black | Neither is driven by the virtual clock | `--realtime`, or capture those elements separately |
| Capture is much slower than the clip | Expected. Each frame is a real screenshot; 60fps for 2s is 120 of them | Lower `--dpr` for review passes, raise it only for the published render |
| Motion looks right, `verify_motion` disagrees | Usually several animations on one clock | `--region` to isolate, or capture the element alone |

**One thing to check every time:** the context is created with `reduced_motion: no-preference`, so you are capturing the full-motion variant. If the page implements a reduced-motion path, **capture that separately and look at it** — it ships to real users and is almost never reviewed.

## 7. When to use this path instead of Figma

- Figma's motion APIs are gated behind the `metronome` flag. If the account does not have it, this path is the only one that runs.
- The motion is going to be CSS or a web motion library anyway — building it here removes a translation step, and the artefact you review is the artefact that ships.
- You want measurement. `verify_motion.py` reads real frames; there is no equivalent check against a Figma timeline.
- You want the reel to show the real thing. A recording of shipped behaviour is stronger evidence than a recording of a design file.

Use the Figma path when the design system lives in Figma and the motion has to be reviewable there by people who do not read code, or when the deliverable is a Figma file rather than an interface.

## Related

- [../SKILL.md](../SKILL.md) — the pipeline
- [motion-system.md](motion-system.md) — the tokens the CSS block expresses
- [motion-spec.md](motion-spec.md) — the spec this path builds from
- [review.md](review.md) — the scored rubric; this path adds a measured input to it
- [reel.md](reel.md) — turning the capture into something publishable
- [ship-to-code.md](ship-to-code.md) — token parity and interruptibility, which apply here directly
