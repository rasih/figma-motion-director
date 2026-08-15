# Reels — presenting motion

Load this when motion needs to leave the file: a Reel, a TikTok, a Short, a portfolio post, a design-review clip, a changelog GIF.

Bundled tool: [`scripts/make_reel.py`](../scripts/make_reel.py). It takes the MP4 that `export_video` produced (or any screen recording), composites it into a procedurally-drawn device frame, and renders a 1080×1920 video. The frame is drawn with Pillow — **no bundled device artwork, nothing to license.**

## 1. The rule that matters

> **The reel is a different artifact from the product motion. Pace the reel. Never pace the product for the reel.**

Product motion is optimized to be invisible on the four-hundredth viewing. A reel is watched **once, muted, at thumbnail size, while someone is scrolling**. Those are opposite targets, and the second one is seductive: a 150ms menu that is exactly right in the product is genuinely too fast to read in a feed.

The wrong fix is to slow the menu to 400ms. The right fix is to **hold, repeat, and label** — change the presentation, not the spec.

| Problem in the reel | Wrong fix | Right fix |
|---|---|---|
| Too fast to see | Lengthen the duration in Figma | `--hold-start` before it, `--loops 3` after it |
| The loop restart is jarring | Add an artificial settle | `--boomerang` |
| Nobody can tell what triggered it | Add a bigger, showier animation | Show the tap, or caption the trigger |
| It reads as slight | Add overshoot or extra movers | Say what it is: caption it `150ms · ease-out` |

**If you find yourself editing the Motion Spec to make a video look better, stop.** That is the portfolio/shipped inversion this skill warns about in [benchmark.md §7](benchmark.md#7-portfolio-motion-is-not-shipped-motion), arriving from the other direction — and it is more dangerous here, because the changed spec is the one that ships.

The one legitimate presentation-only transform is **slow motion for teaching** — and it must be labelled. A clip slowed to 0.25× with "0.25× speed" burned into the caption is honest; the same clip unlabelled is a false claim about the product's timing.

```bash
# label it, always
ffmpeg -i anim.mp4 -filter:v "setpts=4.0*PTS" -an slow.mp4
python3 scripts/make_reel.py slow.mp4 -o reel.mp4 --caption "0.25× speed · 150ms actual"
```

## 2. What makes a motion reel work

- **One idea per reel.** A sheet, or a list reveal, or a tab switch. Three patterns in one clip means none of them was seen.
- **Show the trigger.** Motion with no visible cause reads as a glitch. A tap indicator, a cursor, or a caption naming the trigger — something.
- **Hold before you move.** Roughly 0.4–0.6s of the resting state first. The viewer needs a beat to read the screen before anything changes, and in a feed that beat has to be inside the clip.
- **Repeat two or three times.** First pass is orientation, second is comprehension, third is appreciation. One pass is a blink.
- **Hold after.** Roughly 0.8s on the settled state, so the loop restart does not feel like a stutter.
- **Label the spec.** `300ms · ease-out · sheet from bottom edge` earns more from a design audience than any amount of gloss. It also makes the post *about* something.
- **Show the before, when you are showing a fix.** Side by side or cut together, with both labelled. A fix nobody can see is not a fix anybody will believe.
- **Total 4–8 seconds.** Under three and platforms bury it; over ten and a motion clip has become a video that needs editing.

## 3. Using the script

```bash
python3 scripts/make_reel.py anim.mp4 -o reel.mp4 \
    --device iphone \
    --bg "#0B0B0F" \
    --caption "Bottom sheet · 300ms · ease-out" \
    --hold-start 0.5 --hold-end 0.8 \
    --loops 3
```

| Flag | Does |
|---|---|
| `--device` | `iphone` (with island cutout), `iphone-flat`, `android`, `bare` (no bezel — for web or when the frame would distract) |
| `--bg` | Background colour. Pull it from the design's own palette; a neutral near-black or near-white reads best in a feed |
| `--scale` | Device height as a fraction of the canvas. Default 0.82, dropping to 0.74 automatically when a caption is set |
| `--y-shift` | Nudge the device up or down |
| `--caption`, `--caption-size`, `--caption-color` | Text across the top |
| `--hold-start`, `--hold-end` | Freeze the first / last frame for N seconds |
| `--loops` | Repeat the whole clip |
| `--boomerang` | Forward then reversed — removes the loop seam. Use for continuous motion, **not** for a transition with a real direction, since reversing it shows an exit that does not exist |
| `--safe-guides` | Overlay the regions platform UI covers. Render once with this, check nothing important is under it, then render for real without it |
| `--fps` | Default 30. Use 60 only when the motion has fast travel worth resolving |

Output is H.264 / yuv420p / `+faststart` at 1080×1920 — which is what Instagram Reels, TikTok, and YouTube Shorts all want, and what LinkedIn accepts.

## 4. Safe areas

Every platform covers part of a 9:16 frame with its own UI. Approximate, and they change:

| Region | Roughly | Covered by |
|---|---|---|
| Top | ~14% | Status bar, account name |
| Bottom | ~20% | Caption, audio strip, progress |
| Right | ~12% | Like / comment / share rail |

**Keep the device inside the middle band, and never put a caption in the bottom 20%.** `--safe-guides` draws these so you can check before publishing rather than after.

LinkedIn is the friendliest of the four — it crops least and its audience actually reads captions — which makes it the right target for a spec-labelled motion post.

## 5. From `export_video` to a reel

1. **Export from Figma at a usable size.** Reviews are exported small and cheap; a reel is not. Export at the frame's natural width or larger, `quality: "high"`, `fps: 30`. This is the one time the render cost is worth paying twice.
2. **Download the returned URL.** It is presigned and expires — fetch it before it does.
3. **Run the script.** Start with `--safe-guides` to check placement.
4. **Watch it muted at phone size** before publishing. That is the actual viewing condition, and things that read fine at desktop scale disappear at it.

If the motion lives in code rather than Figma, record the running interface instead and feed that MP4 in — the script does not care where the video came from. **A recording of the shipped thing is a stronger post than a recording of the file**, because it is evidence rather than intent.

## 6. Honesty in the caption

A motion post makes a claim. Keep it true:

- If the clip is slowed, say the speed and the real duration.
- If it is a prototype rather than shipped code, say so.
- If the spec numbers are in the caption, they must be the numbers in the spec — this is exactly the drift the token system exists to prevent, and a screenshot of the wrong number outlives the correction.
- Device frames here are generic shapes, not any manufacturer's industrial design. If a post needs a specific branded device, that is a licensing question and it belongs to the person publishing.

## Related

- [../SKILL.md](../SKILL.md) — the pipeline
- [review.md](review.md) — the export and frame-sampling method the reel reuses
- [benchmark.md](benchmark.md) — portfolio vs shipped motion, the same trap from the other direction
- [motion-spec.md](motion-spec.md) — the numbers a caption must match
