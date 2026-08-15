---
name: figma-motion-director
description: "Motion design judgment — turns a Figma link into keyframes on its timeline, decides whether a UI element should animate at all, picks duration and easing tokens instead of arbitrary numbers, scores finished motion against a rubric, and renders it as a device-framed 9:16 reel. Trigger whenever a figma.com URL is shared alongside any request to animate, and whenever animation needs to be designed, improved, critiqued, justified, or presented: 'animate this frame', 'add motion to this Figma link', 'what duration should this be', 'this feels cheap / janky / slow', 'review this motion', 'make it feel premium', 'should this animate at all', 'motion spec', 'our animations feel inconsistent', 'is this transition too long', 'easing', 'microinteraction', 'motion guidelines', 'put this in a phone mockup', 'make a reel of this animation'. Skip it when the animation is already specified and only needs writing (figma-use-motion) or merging into code (figma-implement-motion) — load alongside those when the task needs both."
license: CC-BY-4.0
---

# Motion Director

## Overview

Two skills already cover the *mechanics* of Figma motion: [figma-use-motion](../figma-use-motion/SKILL.md) writes keyframes through the Plugin API, and [figma-implement-motion](../figma-implement-motion/SKILL.md) turns Figma animation into code. Both answer "how do I write this." Neither answers **"what should this motion be, and is it any good."**

That is this skill: intent, reference, specification, review. **It delegates every API call to the two skills above and does not restate their mechanics** — when this file and one of those disagree on a mechanic, they win.

A keyframe written before anyone has said what the motion communicates is decoration, and decoration is what makes motion feel cheap. The Motion Spec exists to force that question before anything is built.

## Skill Boundaries

| Task | Skill |
|---|---|
| Design, improve, critique, or justify motion | **This skill** |
| Plugin API syntax, enums, field names, timeline mechanics, `export_video` protocol | [figma-use-motion](../figma-use-motion/SKILL.md) — load alongside for BUILD |
| Merging motion into a codebase, `get_motion_context`, snippet handling, node matching | [figma-implement-motion](../figma-implement-motion/SKILL.md) — load alongside for SHIP |
| Layout, components, variables — anything static | [figma-use](../figma-use/SKILL.md) / [figma-generate-design](../figma-generate-design/SKILL.md) |
| Executing an already-specified animation ("opacity 0 → 1 over 0.3s on this node") | `figma-use-motion` alone. This skill adds nothing |

## Prerequisites

- **For the Figma build path:** Figma MCP connected. Motion APIs are gated behind the `metronome` feature flag; `figma-use-motion` documents the bail-fast behavior — follow it. **If the flag is missing, do not stop — switch to the web build path**, which needs none of it.
- **For the web build path:** `ffmpeg`, plus `playwright` with chromium for capture and `numpy` + `Pillow` for measurement.
- For REVIEW on the Figma path: `ffmpeg` for frame extraction. Without it, reason from the keyframes and say that you did.

## The vocabulary

Every duration and easing decision in this skill uses a token. Full definitions, sources, and the Figma ↔ CSS ↔ motion.dev parity table are in [references/motion-system.md](references/motion-system.md) — **load it before assigning any value.** This strip is here so the phases below are readable without it.

| Duration | ms | s | Scope |
|---|---|---|---|
| `t.none` | 0 | 0 | Deliberate non-animation |
| `t.tap` | 70 | 0.07 | Press, toggle |
| `t.xs` | 110 | 0.11 | Small opacity-only change |
| `t.sm` | 150 | 0.15 | **Default** — menu, tooltip, short travel |
| `t.md` | 240 | 0.24 | Toast, accordion, modal |
| `t.lg` | 300 | 0.30 | Sheet, page transition |
| `t.xl` | 400 | 0.40 | Container transform. **The everyday ceiling** |
| `t.2xl` | 700 | 0.70 | First-run only. Requires written justification |

| Easing | Character |
|---|---|
| `e.enter` | Decelerate — arriving |
| `e.exit` | Accelerate — departing |
| `e.move` | Both ends eased — moves on screen |
| `e.expressive` | Slow lead-in, forceful settle — hero moments and large container transforms |
| `e.linear` | Continuous only — spinners, progress, shimmer |
| `e.spring` | Only where real velocity exists — drag, flick, gesture |
| `e.hold` | Step — discrete state change |

**Exit is one token down from enter.** The documented exception is press feedback, where press-down (`t.tap`) is faster than release (`t.xs`).

## Entry points

Pick the entry, then run only what it names. **Running the full pipeline on a small request is the most expensive mistake available here** — it is how a five-minute job becomes an hour.

**A Figma link → animate that node. This is the fast path, and it is a routing rule, not a judgment call.**
Go to [references/build-figma.md](references/build-figma.md) and follow it. A `figma.com` URL means the design already exists: read it, map the tree to an archetype, write the keyframes. **Do not rebuild the interface anywhere else.** Compressed pipeline — probe → read → archetype → four-row spec in the reply → one write → done. INTENT collapses to "which moment, and should it move at all"; BENCHMARK collapses to an archetype lookup; REVIEW happens only if asked or if the result is visibly wrong. Target: minutes.

**Designing new motion with no existing design** → the full pipeline: **INTENT → BENCHMARK → SPEC → BUILD → REVIEW → SHIP → PRESENT**. SHIP is skipped when the deliverable stays in Figma; PRESENT runs only when the motion has to leave the file.

**Critiquing motion that already exists** ("this feels cheap", "review this animation") → the short path: **reconstruct INTENT → REVIEW → deliver**. Reconstruct means answering Phase 1's three questions *about the existing motion*, because a critique with no stated purpose or frequency tier is just taste. Then score it and deliver in [review.md](references/review.md#7-delivering-a-critique)'s format.

**Fixing one value** ("is this transition too long?") → INTENT question 1 and the archetype's entry in [archetypes.md](references/archetypes.md). Do not run the pipeline for a single token.

**Presenting motion** ("put this in a phone mockup", "make a reel of this") → [reel.md](references/reel.md) and [`scripts/make_reel.py`](scripts/make_reel.py) directly. But read that file's first rule before touching the timing: **pace the reel, never pace the product for the reel.**

---

### Phase 1 — INTENT

Answer three questions in writing. They take a minute and they determine everything downstream.

**1. Should this animate at all?**

| Frequency | Budget |
|---|---|
| ≥ 100×/day — keyboard shortcuts, command palette, row hover | **`t.none`. Do not animate** |
| ~10×/day — nav, menus, tabs, toggles | `t.tap` – `t.sm`. Near-imperceptible |
| Occasional — modal, sheet, toast, page change | `t.sm` – `t.xl`. The normal range |
| Rare / first-run — onboarding, first success, hero | Up to `t.2xl`. The delight budget lives here and only here |

**Exception — direct-manipulation feedback is exempt from the ceiling.** Press, tap, and drag acknowledgment is a *response*, not a transition: it must land inside 100ms precisely because it fires constantly. Budget `t.tap`, and never remove it.

A motion that would be charming once becomes a tax at the four-hundredth repetition. **Deleting an animation is a valid — often the best — outcome of this phase.** Say so plainly when it is.

**2. What does this motion tell the user that the static design does not?**

One sentence: *"This motion tells the user ___."* Valid answers explain state, causality, origin, hierarchy, or continuity of identity. If the honest answer is "it looks nice," the motion is fashion. Fashion is allowed — labelled as fashion, budgeted, and confined to low-frequency moments.

**Is this product motion or a shot?** A portfolio piece inverts the brief — seen once, judged by designers, and the motion *is* the content. Restraint stops being the discipline and becomes a liability; mechanism and craft are where the budget goes. See [archetypes.md](references/archetypes.md#shot-motion-is-a-different-brief). Two things do not relax: say which one you built, and get the physics right.

**3. What should it feel like?**

Brand tone selects motion *character*. It does not raise the frequency ceiling — a playful product still does not animate a hundred-times-a-day action; it spends its personality on the first-run moment instead.

| Tone | Bias |
|---|---|
| Precise / enterprise | One token down; `e.move`; bounce 0 |
| Calm / premium / editorial | `e.expressive` on hero moments only; bounce 0 |
| Energetic / consumer | `e.spring` bounce ≤ 0.3; stagger readable |
| Technical / data-heavy | `t.tap` – `t.sm`; `e.move` or `e.linear` |

**Output:** the frequency tier, the one-sentence purpose, and the tone — which are exactly the `Frequency:` / `Purpose:` / `Tone:` fields of the spec header in Phase 3 — plus an explicit go / don't-animate decision.

---

### Phase 2 — BENCHMARK

Find out how the problem is already solved before solving it again. Load [references/benchmark.md](references/benchmark.md) for the method, the sources, and the access rules.

> **Observation tells you which band. The spec tells you which number in that band.** A millisecond value eyeballed from a video is a guess wearing the costume of a measurement.

**Where to look, in order:**

1. **[60fps.design](references/benchmark.md#2a-60fpsdesign--the-sanctioned-live-source) via its official MCP** (`https://mcp.60fps.design/mcp`, PRO licence). The one shipped-motion library that invites agents rather than blocking them, organised by animation type. `get_motion_breakdown` returns trigger, start, movement, settle point and rationale — which is nearly the whole Benchmark Card, as *documented* rather than estimated. Query for the design in front of you; never bulk-pull, cache, or re-host, and never use it to train or evaluate a model — their terms name that explicitly.
2. **Open-source component source.** Vaul, Sonner, shadcn/ui, Base UI, the Motion package, and the Material and Carbon token repos publish real transition constants as text under MIT and Apache licences. Exact numbers, no access question.
3. **Human observation** for everything else — Android, web, anything uncatalogued. The user watches; you ask structured questions and record the answers.

**Two prohibitions that must fire before the reference loads:**

- **Never fetch Mobbin, and never drive a browser through it.** Its content surfaces refuse non-browser clients, and its Terms prohibit using AI/ML tools to create derivative works from its material. Mobbin is human-in-the-loop only.
- **Never scrape Dribbble.** Search for shot URLs and surface links; never read, store, or cache assets. And **never take timing or element count from portfolio work** — take spatial ideas only.

**Output:** one or more Benchmark Cards (schema in the reference), or the explicit note "archetype default, no live reference." The spec's `Reference:` field consumes this.

**When there is no reference — the common case — use [references/archetypes.md](references/archetypes.md).** Eighteen patterns with sourced durations, easing, stagger, failure modes, and reduced-motion substitutions. It is the baseline a live benchmark must beat before it may override anything.

---

### Phase 3 — SPEC

**Write the Motion Spec before writing a single keyframe.** Format, worked examples, and the spec-smell table are in [references/motion-spec.md](references/motion-spec.md).

One table — node, role, property, from → to, start, duration token, easing token, why — plus a stillness block, a lifecycle block, and a reduced-motion block. It exists so that four normally-invisible things become arguable: what is *not* moving, how the Figma timeline maps to production lifecycles, which tokens were chosen, and why any value departs from the archetype default.

**Show the spec to the user and get agreement before building.** Moving a row in a table is free; re-rendering a video export is not. Ask two questions and no more: is the lead element right, and is anything in the stillness list misplaced. Do not ask them to review durations — that invites a number outside the scale and undoes the system. A duration objection is a token-step conversation: up one, or down one.

---

### Phase 4 — BUILD

**Routing is decided by the input, not by preference:**

| Input | Path |
|---|---|
| **A `figma.com` URL** | [references/build-figma.md](references/build-figma.md). Read the node, map the tree to an archetype, write keyframes onto its timeline. **Never rebuild the design elsewhere** |
| A Figma URL, but the `metronome` motion flag is off | Still start from the design: `get_design_context` → the token CSS → [build-web.md](references/build-web.md). The markup comes from Figma, so nothing is redesigned |
| **No design yet** — a description, a component to build from scratch | [references/build-web.md](references/build-web.md) + [`scripts/capture_web.py`](scripts/capture_web.py) |
| The motion is going to be CSS or a web motion library anyway | [references/build-web.md](references/build-web.md). Removes a translation step, and the artefact you review is the artefact that ships |

**Probe before you build.** One tiny `use_figma` read that touches a motion property tells you whether the Figma path is even open. Discovering the `metronome` gate after writing a spec and half a timeline is pure waste — the probe costs one call.

The web path also unlocks **measurement** — [`scripts/verify_motion.py`](scripts/verify_motion.py) reads the rendered frames and reports whether the build actually follows the specified duration and easing. There is no equivalent check against a Figma timeline. Use it in REVIEW.

#### Building in Figma

Full procedure — parsing the link, probing the gate, reading the tree cheaply, assigning roles, and the one-call write — is in [references/build-figma.md](references/build-figma.md).

**Load [figma-use-motion](../figma-use-motion/SKILL.md) and follow it exactly for all mechanics** — enum names, field names, timeline handling, script constraints, its pre-flight checklist. This phase adds only what that skill does not cover:

- **Translate tokens using the parity table** in [references/motion-system.md](references/motion-system.md#the-parity-table). **Write `CUSTOM_CUBIC_BEZIER` with explicit values rather than a named enum whenever the file specifies production motion** — Figma's named easings are cubic curves that do not match the design-system tokens, so using them silently breaks parity with code, and nobody will be able to say why the two look different.
- **Convert milliseconds to seconds exactly once**, here, at the call site. The spec is in ms; the Plugin API is in seconds. A `timelinePosition` of `250` is four minutes ten seconds, and the failure is silent — the script succeeds and the animation appears not to run.
- **Figma's allowlist will happily animate the expensive properties.** `WIDTH`, `HEIGHT`, `STACK_SPACING`, `STACK_PADDING_*`, and `GRID_*_GAP` are all writable and nothing warns you they force layout every frame in production. Use transform and opacity unless the spec states a reason.
- **Build the spine first, then the detail.** Animate the lead element, verify it, then add supporting elements. A wrong easing on one node is obvious; the same error across twenty is hours of untangling.
- **If you applied an animation style rather than manual keyframes, validate by reading back `node.animationStyles`** — style-generated tracks are not materialized into `node.animations`, so checking there will wrongly suggest the write failed.

---

### Phase 5 — REVIEW

Motion is not done when it runs. Load [references/review.md](references/review.md) for the sampling recipe, the calibrated rubric, the four lenses, and the red-flag list.

**Look at it.** `get_screenshot` shows the resting state only. Export video and sample frames — the protocol, sizing, and cost discipline are in `figma-use-motion`; the *reading* method (which frames, and what each one reveals) is in [review.md §1](references/review.md#1-look-at-it). The midpoint frame is the most useful one, because it shows simultaneity, which a keyframe table hides.

**Then measure it, if it was built on the web.** [`scripts/verify_motion.py`](scripts/verify_motion.py) reports the measured settle time, the deviation from the specified curve, and which token the motion actually resembles. A build that comes back `best fit e.linear` when the spec says `e.enter` lost its easing somewhere — read the best-fit line before the verdict, since it names the mistake rather than just failing.

**Then score it** on six weighted criteria — Purpose (0.25), Frequency fit (0.20), Spatial truth (0.20), Restraint (0.15), Craft (0.10), Accessibility & performance (0.10). **The calibration anchors are in [review.md §2](references/review.md#2-the-motion-score); a score assigned without them is invented.**

**Ship at ≥ 8.0 with no criterion below 6.** A high average hiding a 3 is not shippable. Below threshold, fix the weakest criterion and re-score. **Stop after three passes, or when a pass improves the score by less than 0.3** — then say where it landed and why. Do not loop; each pass may cost a render.

**Fix in this order — deleting outranks tuning:** remove the animation → reduce it → fix the easing → correct the origin → make it interruptible → move it to the compositor → make the timing asymmetric → polish. Most weak motion is over-specified, not under-specified.

**Output:** the score with its weakest criterion named, any spec rows that changed during review (update the spec — a stale spec is the drift this skill exists to prevent), and, for a critique-only request, the four-part format in [review.md §7](references/review.md#7-delivering-a-critique).

---

### Phase 6 — SHIP

**Load [figma-implement-motion](../figma-implement-motion/SKILL.md) and follow it for the merge** — `get_motion_context`, snippets, node matching, wrapper splitting, framework choice. Load [references/ship-to-code.md](references/ship-to-code.md) for what this skill adds on top: token parity, timeline-to-lifecycle translation, a substitution-based reduced-motion policy, and interruptibility.

Two things worth knowing before you open either file:

- **A Figma timeline is one clock; production motion is a set of lifecycles.** Deciding which timeline segment is mount, which is exit, what is actually a *state* rather than an animation, and what should not loop in production merely because the file loops — that is the spec's lifecycle block, and it is where design and code silently diverge.
- **Where the merge skill says reduced motion may "cut the duration to near-zero," prefer the substitution table** in [ship-to-code.md §3](references/ship-to-code.md#3-reduced-motion). Near-zero is correct for purely decorative motion and wrong for anything carrying information — press feedback, loading states, and toasts all stay.

---

### Phase 7 — PRESENT (optional)

When the motion has to leave the file — a Reel, a portfolio post, a design-review clip, a changelog GIF — load [references/reel.md](references/reel.md). The bundled [`scripts/make_reel.py`](scripts/make_reel.py) composites an `export_video` MP4 into a procedurally-drawn device frame and renders 1080×1920 for Reels, TikTok, Shorts, or LinkedIn.

**One rule governs this phase:** the reel is a different artifact from the product motion. A feed is watched once, muted, at thumbnail size; the product is used four hundred times. **Pace the reel — never pace the product for the reel.** A 150ms menu that is too fast to read in a feed gets a hold and three loops, not a longer duration. If you find yourself editing the Motion Spec to make a video look better, stop: that is the portfolio/shipped inversion arriving from the other direction, and this time the changed spec is the one that ships.

## Critical Rules

Five rules that are not stated anywhere else in this skill or its siblings.

1. **Not animating is a valid answer, and often the best one.** Frequency is the first gate, and it is a gate, not a slider. An action performed a hundred times a day should not be animated regardless of how good the animation is — the exception is direct-manipulation feedback, which is a response rather than a transition.
2. **Pick a token, do not invent a number.** `t.lg` invites an argument; `317ms` does not, so it ships unexamined. Values outside the scale require a written justification in the spec.
3. **Motion must originate where the object actually lives.** A menu scales from its trigger; a sheet enters from the edge it will return to; a detail view grows from the card that was tapped. **If the true origin is unavailable at runtime — deep link, restored state — fall back to a plain transition rather than faking one.** A transform from the wrong origin asserts a false identity and is worse than no transform at all.
4. **Never write a millisecond value you did not read from a spec or count from frames.** Observation yields bands, never numbers. Fabricated precision is worse than an honest band, because the next reader will treat it as measured.

5. **Match the effort to the request.** A link and "animate this" is a fast path: probe, read, archetype, four-row spec in the reply, one write. A full spec document, a benchmark sweep, and a scored review are for work that asked for them. **Never rebuild a design that already exists** — if the interface is in Figma and you are writing HTML for it, you have taken the expensive road by mistake.

**And one posture:** you are the critic, not the fan. Do not praise motion you just produced. Name what is weakest in it, and say when the honest answer is that the animation should not exist. The full red-flag list lives in [review.md §6](references/review.md#6-red-flags), where each entry carries its scoring consequence — use it there rather than as a style checklist here.

The trap worth naming separately, because it is the one that survives good taste: **do not animate a design-system default and call it a signature.** If the motion is what every product in the category already does, it is the convention — which is fine, and which you should say plainly rather than present as distinctive.

## Pre-flight checklist

In addition to the [figma-use-motion pre-flight checklist](../figma-use-motion/SKILL.md#pre-flight-checklist), verify:

- [ ] INTENT is written down: frequency tier, one-sentence purpose, tone, and an explicit go / don't-animate decision.
- [ ] The Motion Spec exists, was shown to the user, and every row uses named tokens.
- [ ] Every value outside the token scale carries a written reason.
- [ ] The spec's stillness block is non-empty.
- [ ] Durations are milliseconds in the spec and seconds at the Plugin API call site — converted exactly once.
- [ ] Easing is written as `CUSTOM_CUBIC_BEZIER` with explicit values wherever code parity matters.
- [ ] Exit is one token below enter, or the exception is named in the spec.
- [ ] Nothing animates a layout-triggering property without a stated reason.
- [ ] Every scaling or rotating node has its own correct origin, including nested ones.
- [ ] Motion was seen — sampled frames, not a screenshot. If it was not, the spec says why.
- [ ] **The timeline ends when the motion does.** No dead air after the last thing settles — trim the timeline or fill it. A clip that finishes at 2.2s and runs to 4.1s reads as broken, not as a pause.
- [ ] Layers of one material share one clock **and one direction**, and any rotation direction that was not requested is stated in the reply.
- [ ] The Motion Score is recorded, with its weakest criterion named.
- [ ] A reduced-motion substitution is specified for every animation, and it replaces rather than deletes.
- [ ] The spec matches what was actually built. Rows changed during review were updated.
- [ ] For shipped motion: tokens exist as constants, the timeline-to-lifecycle mapping is explicit, and re-triggered animations retarget rather than restart.
- [ ] For a published reel: the Motion Spec was not edited to improve the video, any speed change is labelled, and captioned numbers match the spec.

## References

Six deep dives, loaded on demand. When this skill names one inline, load it before continuing with that part of the task. You should not need all six for one task — the pipeline names the one that matters at each phase.

| Doc | Load when | Covers |
|---|---|---|
| [references/motion-system.md](references/motion-system.md) | **Before assigning any duration, easing, or stagger** | The duration scale with sources, the easing tokens, the Figma ↔ CSS ↔ motion.dev parity table, springs and the overshoot budget, stagger math, frequency tiers, property discipline, the seconds/milliseconds trap |
| [references/motion-spec.md](references/motion-spec.md) | Phase 3 | The spec format, two worked examples, the lifecycle and stillness blocks, the spec-smell table |
| [references/benchmark.md](references/benchmark.md) | Phase 2, when a live reference is available | Which sources are readable, the Mobbin and Dribbble rules, the Benchmark Card, duration bands and evidence levels, portfolio vs shipped motion |
| [references/archetypes.md](references/archetypes.md) | Any recognizable UI pattern; always when no live reference exists | 18 archetypes with sourced durations, easing, stagger, failure modes, and reduced-motion substitutions. Its quick-reference table answers most questions on its own |
| [references/review.md](references/review.md) | Phase 5, and any critique request | Frame-reading method, the calibrated six-criterion rubric, the four lenses, gap analysis, stopping criteria, red flags, critique format |
| [references/ship-to-code.md](references/ship-to-code.md) | Phase 6 | Token parity, the transform-semantics trap, timeline-to-lifecycle mapping, reduced-motion substitutions, interruptibility, performance, platform notes |
| [references/build-figma.md](references/build-figma.md) | **A Figma URL is in the prompt** — load it first, before anything else | Parsing the link, probing the `metronome` gate, reading the tree with `get_metadata`, assigning lead/support/static from layer names, the one-call write, and the call budget |
| [references/build-web.md](references/build-web.md) | Phase 4, when the motion will live in a browser | The deterministic-capture pipeline, tokens as CSS variables, transitions vs keyframes, measuring the build against the spec, what breaks and why |
| [references/reel.md](references/reel.md) | Phase 7 — presenting motion as video | Reel pacing vs product pacing, what makes a motion clip readable, `make_reel.py` usage, platform safe areas, caption honesty |

**Bundled scripts.** All three are standalone and need only `ffmpeg` plus Python:

| Script | Does |
|---|---|
| [`scripts/capture_web.py`](scripts/capture_web.py) | Records HTML/CSS/JS motion to MP4 with a virtualised clock — frame-exact at any fps, headless, reproducible |
| [`scripts/verify_motion.py`](scripts/verify_motion.py) | Measures a rendered animation and compares it to the specified duration and easing token |
| [`scripts/make_reel.py`](scripts/make_reel.py) | Composites a clip into a procedurally-drawn device frame and renders 1080×1920 for social |

Attribution and sources: [ATTRIBUTION.md](ATTRIBUTION.md). Values marked `[CONV]` in the references are convention, not published specification — own them as judgment rather than cite them as authority.
