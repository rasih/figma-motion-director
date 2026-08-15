# Building motion in Figma from a link

**A `figma.com` URL in the prompt routes here. That is a rule, not a judgment call.** The design already exists; rebuilding it anywhere else is wasted work, and it is the single largest time sink this skill can fall into.

Target: **a link in, keyframes on the timeline out, in minutes.** If a run is taking tens of minutes, something in this file is being skipped.

Mechanics — enum names, field names, script constraints, `export_video` protocol — come from [figma-use-motion](../../figma-use-motion/SKILL.md). Load it. This file is the procedure that sits on top.

## 0. Parse and probe — before any other work

```
https://figma.com/design/:fileKey/:fileName?node-id=1-2
                         └ fileKey ┘                └ nodeId "1:2"
```

`node-id=1-2` becomes `1:2`.

**Then probe the motion API immediately**, in one tiny `use_figma` read:

```js
const node = await figma.getNodeByIdAsync("1:2");
return { id: node.id, name: node.name, type: node.type,
         timelines: node.timelines, tracks: node.manualKeyframeTracks };
```

- **It returns** → motion is enabled. Continue at §1.
- **It throws `"<name>" is not a supported API`** → the `metronome` flag is off for this account. **Do not retry, and do not silently switch strategies.** Say so in one line, then take §6.

Probing costs one call and saves the entire build. Discovering the gate after writing a spec and half a timeline is how a five-minute job becomes an hour.

## 1. Read the node cheaply

**`get_metadata` first — not `get_design_context`.** Metadata returns the tree: names, types, positions, sizes. That is everything needed to decide what moves. Design context returns full generated code, which is large, slow, and irrelevant when the destination is Figma rather than a codebase.

```
get_metadata(fileKey, nodeId)      → the tree
get_screenshot(fileKey, nodeId)    → one look at the resting state
```

Two things to establish from the tree, and nothing more:

1. **Is the linked node itself a top-level frame** (a direct child of the page)? If so, **animate its children** — a page-level frame cannot be animated, and it is also the frame you will later pass to `export_video`. Note its id now; you need it twice.
2. **What is in it?** Layer names do most of the work. `Sheet`, `Scrim`, `Overlay`, `Modal`, `Toast`, `Card`, `Row`, `Item`, `Tab`, `Indicator` — designers name things, and those names map straight onto [archetypes.md](archetypes.md).

## 2. Ask one question, at most

If the frame contains more than one animatable moment — a sheet *and* a list *and* a toast — ask which one. One question, offering the moments you actually found:

> "This frame has a sheet over a list. Animate the sheet opening, or the list arriving?"

Do not ask about durations, tone, or easing. Those come from the archetype and the tokens. **A link plus a pattern is enough to start; anything else is a question the archetype already answers.**

## 3. Assign roles from the tree

This is the whole "director" step on this path, and it takes one pass over the metadata.

| Signal in the tree | Role |
|---|---|
| The surface the archetype is named after — the sheet, the modal, the toast | **lead** |
| A full-bleed dark rectangle behind it, usually named `Scrim`, `Overlay`, `Backdrop` | **support** — opacity, on the lead's clock |
| Repeated siblings under one parent — `Row 1..n`, `Item`, `Card` | **support**, staggered, but only in a list-reveal moment |
| Status bar, nav bar, tab bar, header, background, page content | **static** — and say so explicitly |
| Children *inside* the lead surface | **static.** They ride with the container. Animating them separately is the most common way to make a 300ms transition feel like 600ms |
| Sibling layers that are parts of **one visual material** — a bezel's metal banding, its colour fringing, its rim highlight, its iridescent accents | **One role, one clock.** They move together or the material falls apart. See [archetypes.md](archetypes.md#17--ambient--material-loop) |

**Before writing, name every layer you are leaving still and ask whether it belongs to something that is moving.** A layer left out of a material's rotation does not look "held" — it looks broken, and it is the failure that survives review most often because each layer looked correct in isolation.

**For a shared material, prefer one track on a shared parent over matching tracks on each layer.** Group them if the file allows it and rotate the group: one node, one track, and they cannot drift apart. Per-layer tracks are the fallback, and they must be *identical* — same field, same sign, same magnitude, same duration. Two tracks are two chances to invert a sign, and an inverted sign on the most colourful layer makes the whole component read as running backwards.

Exactly one lead. If you cannot name it from the tree, look at the screenshot — it is the thing the eye should follow.

## 4. Spec inline, and keep it short

For a single moment from a link, the spec is four to six rows and lives in the reply, not in a file. Everything else in [motion-spec.md](motion-spec.md) still applies — tokens not numbers, a non-empty stillness list, a reduced-motion line — but a full document is for multi-moment work.

```
Sheet   lead     TRANSLATION_Y  +560 → 0    0ms  t.lg 300  e.enter   archetype default
Scrim   support  OPACITY        0 → 0.4     0ms  t.lg 300  e.enter   same clock as the sheet
Sheet   lead     TRANSLATION_Y  0 → +560  300ms  t.md 240  e.exit    exit one token down
Scrim   support  OPACITY        0.4 → 0   300ms  t.md 240  e.exit
STILL: page content, status bar, nav bar, sheet contents
```

**Get the travel distance from the metadata**, not from a guess: a sheet's `TRANSLATION_Y` start is its own height, so it begins exactly off the bottom edge. The tree already told you that number.

Show it, then build. Do not wait for approval on a four-row spec unless the user asked to review it.

## 5. Write it in one call

**One `use_figma` call for the whole moment.** Not one per node, not one per track. Every extra call is a round trip, and the atomicity works in your favour: if the script fails, nothing was written and you fix it once.

```js
const sheet = await figma.getNodeByIdAsync("12:34");
const scrim = await figma.getNodeByIdAsync("12:35");
const mutatedNodeIds = [sheet.id, scrim.id];

const ENTER = { type: "CUSTOM_CUBIC_BEZIER",
                easingFunctionCubicBezier: { x1: 0, y1: 0, x2: 0, y2: 1 } };
const EXIT  = { type: "CUSTOM_CUBIC_BEZIER",
                easingFunctionCubicBezier: { x1: 0.3, y1: 0, x2: 1, y2: 1 } };

sheet.applyManualKeyframeTrack({ type: "PROPERTY", name: "TRANSLATION_Y" }, {
  keyframes: [
    { timelinePosition: 0,    value: { type: "FLOAT", value: 560 } },
    { timelinePosition: 0.30, value: { type: "FLOAT", value: 0 },   easing: ENTER },
    { timelinePosition: 0.54, value: { type: "FLOAT", value: 560 }, easing: EXIT  },
  ],
});

scrim.applyManualKeyframeTrack({ type: "PROPERTY", name: "OPACITY" }, {
  keyframes: [
    { timelinePosition: 0,    value: { type: "FLOAT", value: 0 } },
    { timelinePosition: 0.30, value: { type: "FLOAT", value: 0.4 }, easing: ENTER },
    { timelinePosition: 0.54, value: { type: "FLOAT", value: 0 },   easing: EXIT  },
  ],
});

const [timeline] = sheet.timelines;
if (timeline && timeline.duration < 0.6) {
  sheet.setTimelineDuration(timeline.id, 0.6);
  mutatedNodeIds.push(timeline.id);
}

return { mutatedNodeIds, tracks: sheet.manualKeyframeTracks, timelines: sheet.timelines };
```

Five things this snippet is doing deliberately, each of which is a common failure:

- **Seconds, not milliseconds.** The spec is in ms; `timelinePosition` is in seconds. `0.30`, never `300`.
- **`CUSTOM_CUBIC_BEZIER` with explicit values**, not `EASE_OUT` — the named enums are not the token curves, and using them breaks parity with whatever ships.
- **`TRANSLATION_Y` is additive**: `0` means the node's resting position, and `560` means 560px below it. You are not writing coordinates.
- **No redundant `t=0` keyframe on the scrim's resting value** — the first keyframe already holds back to zero. The `t=0` rows above exist because the value differs from rest.
- **The timeline id goes into `mutatedNodeIds`** when it is extended.

## 6. When motion is not enabled

The `metronome` flag being off does not end the job — it changes where the motion is built. Say which branch you are taking, then take it.

```
get_design_context(fileKey, nodeId)   → the design as markup
  → apply the token CSS block and the same spec
  → scripts/capture_web.py            → deterministic MP4
  → scripts/verify_motion.py          → measured against the spec
  → scripts/make_reel.py              → the reel
```

Full procedure in [build-web.md](build-web.md). **The important difference from building on the web from scratch: the markup comes from Figma, so no interface is being redesigned** — which is exactly the waste this whole file exists to prevent. The result is a video and code rather than a Figma timeline, which is often what was actually wanted anyway.

## 7. Verify, then present

- `get_screenshot` shows the **resting state only** — it can never show motion. Do not use it as a check.
- `export_video` on the **top-level frame** noted in §1, not the node you keyframed. Small and low-fps for a review pass.
- For a reel, export once at full size and `quality: "high"`, then [`scripts/make_reel.py`](../scripts/make_reel.py). See [reel.md](reel.md) — and do not re-time the motion to make the video read better.

## 8. Time budget

A single moment from a link should cost roughly:

| Step | Calls |
|---|---|
| Probe | 1 read |
| Read the node | `get_metadata`, `get_screenshot` |
| Spec | 0 — it is written in the reply |
| Build | **1 write** |
| Verify | 1 export (skip when the change is self-evident) |
| Reel | 1 render, only if asked |

**If you are past a handful of calls, stop and look at what you are doing.** The usual culprits: building the interface instead of animating the existing one, one write per node, re-exporting after each small fix, or running the full REVIEW rubric on a four-row spec. Score the motion when the user asks for a review — not on every build.

## Related

- [../SKILL.md](../SKILL.md) — the pipeline
- [../../figma-use-motion/SKILL.md](../../figma-use-motion/SKILL.md) — the API mechanics this file assumes
- [archetypes.md](archetypes.md) — the pattern the tree maps onto
- [motion-system.md](motion-system.md) — tokens and the parity table
- [build-web.md](build-web.md) — the fallback branch, and the from-scratch path
- [reel.md](reel.md) — turning the export into something publishable
