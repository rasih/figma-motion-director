# The Motion Spec

The artifact. Load this in Phase 3, before any keyframe is written.

A Motion Spec is one table plus four short blocks. It takes a few minutes to write and it is the only place in the process where motion decisions are visible, reviewable, and arguable. Everything downstream — the Plugin API calls, the video review, the code handoff — is a transcription of it.

**Nothing gets built before the spec exists, and the spec gets shown to the user before the build starts.** Moving a row in a table is free; re-rendering a video export is not.

## 1. Why it exists

Four things are invisible without it, and all four are where motion goes wrong:

**What is *not* moving.** The stillness is what makes motion legible — a page transition reads as navigation because the nav bar holds; a sheet reads as temporary because the page behind it does not move. A spec that lists every element as animated has diagnosed nothing.

**The clock.** A Figma timeline is one shared clock with absolute positions. Production motion is a set of independent lifecycles — mount, exit, hover, gesture, state change. That translation is where design and code silently diverge, and the spec is where it gets decided rather than assumed.

**The tokens.** `t.lg` invites an argument. `317ms` does not — a reviewer has no purchase on it, so it ships unexamined.

**The exceptions.** Any value that departs from the archetype default carries a one-line reason. A value with no reason was not a decision; it was a default that nobody noticed.

## 2. Format

### Header block

```
MOTION SPEC — <what this is>
Archetype:    <one of the 16, or "custom">
Frequency:    <≥100×/day | ~10×/day | occasional | rare/first-run>
Purpose:      "This motion tells the user ___."
Tone:         <precise | calm | energetic | technical>
Timeline:     <total seconds> on <top-level frame name / node id>
Reference:    <benchmark card ids, or "archetype default">
```

### The track table

One row per animated property per node. Not one row per node — a node that moves and fades gets two rows, because they can have different timings and often should.

| Node | Role | Property | From → To | Start | Duration | Easing | Why |
|---|---|---|---|---|---|---|---|
| `Sheet` | lead | `TRANSLATION_Y` | +560 → 0 | 0ms | `t.lg` 300 | `e.enter` | archetype default |
| `Scrim` | support | `OPACITY` | 0 → 0.4 | 0ms | `t.lg` 300 | `e.enter` | same clock as sheet — decoupling produces a dimming void |
| `Handle` | — | — | — | — | — | — | **static** — anchors the top edge during travel |

Column rules:

- **Node** — the layer name, plus the node id once known. Names alone drift.
- **Role** — `lead` (the one thing the eye follows), `support` (moves because the lead does), `static` (explicitly does not move). **Exactly one lead per moment.** If you cannot name the lead, the choreography has not been decided.
- **Property** — the Plugin API field name (`TRANSLATION_Y`, `OPACITY`, `SCALE_XY`, `CORNER_RADIUS`, indexed `fills[0]`). Using real field names here means BUILD is transcription, not translation.
- **From → To** — remember that transform fields are *additive* in Figma: `0` means "no change from the resting transform," and scale is *multiplicative* with a neutral of `1`. Opacity and radius are absolute. Write the intent in these terms or BUILD will compose them wrong.
- **Start** — milliseconds from the start of this moment, not from the start of the file's timeline. Offsets to the shared clock are resolved in BUILD.
- **Duration** — the token *and* its millisecond value: `t.lg 300`. Both, every time.
- **Easing** — the token. `e.enter`, `e.spring bounce 0.15`.
- **Why** — `archetype default` is a complete answer. Anything else needs a real sentence.

### The stillness block

**Required, and must be non-empty.**

```
STAYS STILL
- Underlying page content — establishes that the sheet is temporary
- Nav bar and tab bar — the fixed reference that makes travel readable
- Sheet contents — they ride with the container, they do not choreograph themselves in
```

If the honest answer is "everything moves," either the observation was wrong or the design is. Go back.

### The lifecycle block

Where the Figma timeline maps to production behavior. Fill it in even when the deliverable stays in Figma — it is what stops a design from specifying something that cannot be built.

```
LIFECYCLE
Timeline 0 – 300ms   → mount / open
Timeline 300 – 540ms → exit (reversed, one token down)
Loops?               → no. The file loops for preview only; production plays once
Gesture?             → yes. Drag tracks 1:1; release uses e.spring bounce 0.15, not the curve
Interrupt?           → re-open during exit retargets from current position; never queues
```

### The reduced-motion block

**Required for every spec.** A substitution, not a deletion.

```
REDUCED MOTION
- Sheet: cross-fade in place, t.sm 150, no travel
- Scrim: unchanged — it carries the modality information
- Drag: unchanged — direct manipulation is not animation
```

## 3. Worked example — bottom sheet

```
MOTION SPEC — Share sheet, mobile
Archetype:    1 — bottom sheet
Frequency:    occasional
Purpose:      "This motion tells the user they have not left the screen, and that
               this surface will return to the bottom edge it came from."
Tone:         precise
Timeline:     0.6s on `Screen / Share` (top-level frame)
Reference:    archetype default; one observed card (shipped, confidence medium)
              contributed the origin and the exit asymmetry, not the numbers
```

| Node | Role | Property | From → To | Start | Duration | Easing | Why |
|---|---|---|---|---|---|---|---|
| `Sheet` | lead | `TRANSLATION_Y` | +560 → 0 | 0ms | `t.lg` 300 | `e.enter` | archetype default |
| `Scrim` | support | `OPACITY` | 0 → 0.4 | 0ms | `t.lg` 300 | `e.enter` | coupled to the sheet; a slower scrim leaves a dimming void |
| `Sheet` | lead | `TRANSLATION_Y` | 0 → +560 | 300ms | `t.md` 240 | `e.exit` | exit is one token down |
| `Scrim` | support | `OPACITY` | 0.4 → 0 | 300ms | `t.md` 240 | `e.exit` | stays coupled |

```
STAYS STILL
- Page content behind the scrim — its stillness is the whole message
- Status bar, nav bar
- Sheet contents — they ride with the container

LIFECYCLE
0 – 300ms    → open
300 – 540ms  → dismiss
Loops?       → no
Gesture?     → yes. Drag tracks the finger 1:1; release springs (bounce 0.15) and
                carries fling velocity — a fixed curve here reads as fighting the user
Interrupt?   → re-open during dismiss retargets from current Y

REDUCED MOTION
- Sheet: cross-fade in place, t.sm 150, no vertical travel
- Scrim: unchanged
- Drag: unchanged — direct manipulation, not animation
```

## 4. Worked example — staggered list reveal

Shows the stagger math and the run-once condition, which is the part people forget.

```
MOTION SPEC — Search results, first population
Archetype:    6 — list / grid entrance reveal
Frequency:    occasional — but ONLY on first population
Purpose:      "This motion tells the user the shape and volume of what arrived."
              Honest note: partly fashion. Budgeted, and gated to run once.
Tone:         technical
Timeline:     0.7s on `Screen / Results`
Reference:    archetype default
```

Stagger: `k = min(12, 8) = 8`; `clamp((500 − 150) / 7, 20, 60)` = **50ms**, applied to the first **8** items; items 9–12 arrive with item 8. Total = `7 × 50 + 150` = **500ms**, exactly at the cap.

| Node | Role | Property | From → To | Start | Duration | Easing | Why |
|---|---|---|---|---|---|---|---|
| `Row 1` | lead | `OPACITY` | 0 → 1 | 0ms | `t.sm` 150 | `e.enter` | archetype default |
| `Row 1` | lead | `TRANSLATION_Y` | +12 → 0 | 0ms | `t.sm` 150 | `e.enter` | archetype default — small travel signals arrival without implying a journey |
| `Row n` (2–8) | support | both | same | (n−1) × 50ms | `t.sm` 150 | `e.enter` | reading order |
| `Row 9–12` | support | both | same | 350ms | `t.sm` 150 | `e.enter` | stagger capped at 8; the tail arrives together |

```
STAYS STILL
- Search field, filter bar, result count — the frame the content arrives into
- Scroll position

LIFECYCLE
Runs on      → first population of an empty list, once per session
Does NOT run → back-navigation, tab switch, cache hit, pagination, re-sort
Loops?       → no

REDUCED MOTION
- Single fade of the whole list, t.sm 150, no stagger, no travel.
  This pattern is decorative; switching it off entirely is also acceptable.
```

## 5. Handing the spec over

Show the table. Ask two questions and no more:

1. *"Is the lead element right — is that what the eye should follow?"*
2. *"Anything in the stillness list that should actually move, or vice versa?"*

Do not ask the user to review durations. They will say a number, the number will not be in the scale, and the system will have been undone by a conversation. If a duration feels wrong to them, that is a token-step conversation — up one, or down one.

## 6. Spec smells

| Smell | What it means |
|---|---|
| Every node has a row | Nothing was decided. Motion is being applied, not directed |
| No `lead` role, or several | The choreography was never chosen. The eye will not know where to go |
| Empty stillness block | Either misobservation or a design problem. Do not proceed |
| Raw millisecond values in the duration column | The token system was bypassed; nobody can review this |
| Every row says "archetype default" but the values differ from the archetype | The reasons were never written; the values are drift |
| No lifecycle block | The design specifies something nobody has confirmed is buildable |
| Reduced motion says "disabled" for an informational animation | Deletion where substitution was required |
| A `Why` column reading "looks better" | Fashion that has not been labelled as fashion, budgeted, or frequency-gated |

## Related

- [../SKILL.md](../SKILL.md) — the pipeline
- [motion-system.md](motion-system.md) — the tokens every row uses
- [archetypes.md](archetypes.md) — the defaults a spec departs from
- [review.md](review.md) — how the built result is scored against this spec
- [ship-to-code.md](ship-to-code.md) — carrying the lifecycle block into production
