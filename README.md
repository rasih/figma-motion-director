# Motion Director

A Claude Skill for **directing UI motion** — deciding what should move and why, specifying it in tokens instead of arbitrary numbers, building it in Figma or on the web, measuring whether the build matches the spec, and rendering the result as a device-framed reel.

It is the judgment layer that motion tooling usually skips.

---

## The gap it fills

Figma's official motion skills answer *"how do I write this keyframe"* — enum names, field names, timeline mechanics, code merge. They are good at that, and this skill delegates all of it to them rather than restating it.

Neither answers the question that actually decides whether motion is any good:

> **What should this motion be, and is it working?**

That question has answers. They are just scattered across a dozen design systems, a handful of practitioners, and a lot of tacit craft. This skill collects them into something a model can execute and a designer can argue with.

---

## The short version

Paste a Figma link, say what should move. It reads the node, maps the layer tree onto one of 18 archetypes, writes keyframes onto the frame's timeline, and can render the result as a 9:16 reel.

```
[figma.com/design/…?node-id=95-2]  animate the sheet opening
    ↓
probe motion API → read tree → archetype → 4-row spec → one write → export
```

No interface gets rebuilt. Where Figma's motion API isn't available, it starts from the same design via `get_design_context` and builds the motion in CSS instead.

## Pipeline

```
INTENT  →  BENCHMARK  →  SPEC  →  BUILD  →  REVIEW  →  SHIP  →  PRESENT
```

| Phase | What happens |
|---|---|
| **INTENT** | Should this animate *at all*? Frequency tier, one-sentence purpose, brand tone. Deleting the animation is a valid outcome — often the best one |
| **BENCHMARK** | How is this pattern already solved? Eighteen archetypes with sourced defaults, plus a method for reading real references without fabricating numbers |
| **SPEC** | One table. Node, role, property, from → to, start, duration token, easing token, why. Plus what stays still, the lifecycle mapping, and the reduced-motion substitution |
| **BUILD** | Two targets: Figma (Plugin API) or the web (CSS + deterministic capture). The web path needs no Figma at all |
| **REVIEW** | Sampled frames, a six-criterion weighted rubric with calibration anchors, four review lenses, and — on the web path — an actual measurement of the built curve |
| **SHIP** | Token parity into code, timeline → lifecycle translation, reduced motion as substitution, interruptibility |
| **PRESENT** | Device-framed 1080×1920 for Reels, TikTok, Shorts, LinkedIn |

There are shorter entry points too: critiquing existing motion, fixing a single value, or going straight to a reel.

---

## The opinionated part

**A duration scale where every value is corroborated by at least two published design systems** — Carbon as the spine, cross-checked against Material 3, Fluent 2, Atlassian, WinUI, and Material 1.

| Token | ms | Scope |
|---|---|---|
| `t.none` | 0 | Deliberate non-animation |
| `t.tap` | 70 | Press, toggle |
| `t.xs` | 110 | Small opacity-only change |
| `t.sm` | 150 | **Default** — menu, tooltip, short travel |
| `t.md` | 240 | Toast, accordion, modal |
| `t.lg` | 300 | Sheet, page transition |
| `t.xl` | 400 | Container transform. The everyday ceiling |
| `t.2xl` | 700 | First-run only. Requires written justification |

Seven easing tokens, each with a **parity table** giving the same curve in Figma Plugin API, CSS, and motion.dev form — because Figma's named easings are *not* the design-system curves, and using them silently breaks parity with production.

And one rule that removes most timing arguments: **exit is one token down from enter.**

Plus the rules that are actually load-bearing:

- **Frequency sets the ceiling.** An action performed 100+ times a day should not be animated, however good the animation is.
- **Never write a millisecond value you did not read from a spec or count from frames.** Observation yields bands, never numbers.
- **Motion must originate where the object actually lives** — and when the true origin is unavailable at runtime, fall back rather than fake it.
- **One material, one clock, one direction.** Every layer of a surface treatment — banding, colour fringing, highlights — moves together, or the material tears in half.
- **Emission is not a reveal.** If a mechanism should read as pushing something out, the object has to travel through a fixed aperture. A growing mask cannot carry the follow-through that sells it.
- **Reduced motion replaces; it does not delete.** Press feedback, loading states and toasts all carry information and stay.

The last three came out of the tool getting them wrong on real work, being measured, and being corrected. The rules are the residue.

---

## Bundled tools

Three standalone scripts. `ffmpeg` plus Python; no build step.

### `capture_web.py` — deterministic motion capture

Screen recording gives you whatever frames the machine happened to produce. This **virtualises the clock** and advances it one frame at a time — driving `document.getAnimations()`, `requestAnimationFrame`, and `performance.now` together, so CSS and JS motion step in lockstep.

Frame-exact at any fps, headless, reproducible on any machine.

```bash
python3 scripts/capture_web.py sheet.html -o anim.mp4 \
    --width 390 --height 844 --dpr 3 --duration 1.4 --fps 60
```

### `verify_motion.py` — measure the build against the spec

Review is usually "does it feel right." This makes part of it measurable: it reads the frames, measures displacement by profile alignment, and reports whether the motion follows the specified duration and easing — plus which token it *actually* resembles.

```
metric        shift (y-axis travel)
measured      250 ms to 99% settled
expected      250 ms   (-0 ms, -0.0%)  OK
easing        e.enter  max deviation 0.002 — follows the specified curve
best fit      e.enter 0.002 · e.expressive 0.178 · e.move 0.289
```

A build that comes back `best fit e.linear` when the spec says `e.enter` lost its easing somewhere. That is a very common CSS bug, and it is invisible to the eye.

### `make_reel.py` — device-framed social render

Composites a clip into a procedurally-drawn device frame — no bundled artwork, nothing to license — and renders 1080×1920.

```bash
python3 scripts/make_reel.py anim.mp4 -o reel.mp4 \
    --caption "Sheet · 300ms · ease-out" --hold-start 0.5 --hold-end 0.9 --loops 3
```

Holds, loops, boomerang, platform safe-area guides, iPhone / Android / bare frames.

**The rule attached to it:** pace the reel, never pace the product for the reel. A 150ms menu that is too fast to read in a feed gets a hold and three loops — not a longer duration.

---

## Install

**As a Claude Skill.** Drop the folder into your skills directory, or use the packaged `.skill` file.

**Alongside the Figma plugin skills.** The Figma build path expects `figma-use-motion` and `figma-implement-motion` as siblings and delegates all API mechanics to them. The web build path needs neither.

**Script dependencies:**

```bash
pip install playwright numpy Pillow --break-system-packages
playwright install chromium
# ffmpeg from your package manager
```

---

## What it deliberately does not do

**It does not scrape Mobbin or Dribbble.** Mobbin's terms prohibit using AI/ML tools to create derivative works from its material; Dribbble's prohibit scraping. The skill knows this and works within it.

**It does not invent numbers from video.** A millisecond value eyeballed from a recording is a guess wearing the costume of a measurement. Observation yields bands; documented specs yield numbers. The skill enforces the distinction in its own schema — the Benchmark Card refuses to hold a millisecond value on an `estimated` card.

**It prefers sanctioned sources over clever ones.** For shipped-app motion it uses **[60fps.design](https://60fps.design)**'s official MCP, which the publisher built for exactly this and which returns structured motion breakdowns rather than video to squint at. For component motion it reads real transition constants out of MIT and Apache-licensed source. Both give exact numbers, and neither requires working around anybody's terms.

Where nothing covers the case — Android, web, anything uncatalogued — it falls back to a structured interview: the designer watches, the agent records. That leg never becomes obsolete. A tool can tell you a sheet settles in 300ms; it cannot tell you the thing you noticed while watching.

---

## Credits

The phase architecture — a router, a mandatory intent phase before generation, recursive scoring against weighted criteria with stopping criteria, and a multi-perspective panel — is adapted from the **creative-director** skill by **Serge Shima** (CC BY 4.0). *"Insight before ideas"* became *"intent before keyframes."*

Craft rules draw on **Emil Kowalski**'s writing and published animation standards, and on **Rauno Freiberg**'s interaction-design notes.

Duration and easing values come from **Material Design 3** and **Material 1**, **IBM Carbon**, **Atlassian**, **Microsoft Fluent 2** and **WinUI**. Perceptual thresholds from **Nielsen Norman Group**; accessibility requirements from **W3C WCAG** and **MDN**.

Full credits in [`ATTRIBUTION.md`](ATTRIBUTION.md). Values marked `[CONV]` are convention, not published specification — the tag exists so the line between *sourced* and *defensible default* stays visible.

## Licence

Documentation CC BY 4.0 · scripts MIT. See [`LICENSE`](LICENSE).
