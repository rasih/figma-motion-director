# Reviewing Motion

Load this in Phase 5, and any time the user asks for a critique of existing motion.

Motion is not done when it runs. "Renders without error" and "renders correctly" are unrelated claims, and only one of them is checkable by reading the script.

**You are the critic, not the fan.** Do not praise motion you just produced. Name what is weakest in it. Say when the honest answer is that the animation should not exist.

## 1. Look at it

`get_screenshot` shows the timeline's **resting state only** — it can never show motion. To see motion you must export video and sample frames.

Exports render server-side and are slow and expensive. Frame extraction is free. **Pay for one render, then mine it for every frame that tells you something.**

**The `export_video` protocol — parameters, the `nodeId` / `jobId` exclusivity, the async polling loop, and the cost characterization — is documented in [figma-use-motion](../../figma-use-motion/SKILL.md#verifying-the-animation). Follow it there.** Two things that trip reviews:

- The render is asynchronous. A response carrying `status: "processing"` and a `jobId` is **normal, not a failure** — re-invoke with `{ fileKey, jobId }` and wait. Treating it as an error and re-exporting pays twice for one render.
- Export the **top-level frame that owns the timeline**, not the descendant you keyframed.

**Plan before rendering.** Cost scales with pixels × frames:

1. **Pick the moments first.** One frame per *phase* — per stagger step, or start / mid / settle — not smooth playback. Usually 4–6. This count sets your fps.
2. **Size to what you must read.** Start small and low-quality; raise the width only when judging fine detail like text.
3. Extract locally: `ffmpeg -ss <t> -i anim.mp4 -frames:v 1 frame_<t>.png`

**Read all the frames before changing anything, and batch every fix into one pass.** Re-exporting after each small change is how a review turns into an afternoon.

Skip the export entirely when the change is trivial or self-evident. Without `ffmpeg`, skip it and reason from the keyframes instead — but say that you did.

### What to look for, frame by frame

| Frame | Question |
|---|---|
| t = 0 | Is anything visible that should not be yet? Is anything *invisible* that should be — an element stuck at `opacity: 0` because its track starts late? |
| t = 0 vs mid | **Overlay them. What did not change that should have?** This is how a forgotten layer surfaces — the highlight that stayed put while its material rotated, the badge that never moved with its card. Easier to see as a difference than in sequence |
| First quarter | Has the lead element started before its supporting elements? Is the eye being led? |
| Midpoint | How many things are in motion at once? Count them. More than three is a finding |
| Settle | Does everything arrive, or does one element still lag by a beat? |
| Post-settle | Does anything continue to move after the moment has resolved? |
| Exit start | Does the exit mirror the entrance direction? |

The single most useful frame is the midpoint, because it shows simultaneity — the thing a keyframe table hides.

## 2. The Motion Score

Six criteria, weighted. Score each 1–10, then take the weighted sum.

| # | Criterion | Weight | The question |
|---|---|---|---|
| 1 | **Purpose** | 0.25 | Does the motion carry information the static design cannot? Would deleting it lose something? |
| 2 | **Frequency fit** | 0.20 | Does the duration match how often this fires? |
| 3 | **Spatial truth** | 0.20 | Does it come from, and return to, where the object actually lives? |
| 4 | **Restraint** | 0.15 | How many things move, and could fewer say the same? |
| 5 | **Craft** | 0.10 | Easing direction, exit asymmetry, property discipline, per-element origin |
| 6 | **Accessibility & performance** | 0.10 | Reduced-motion substitution, interruptibility, compositor-only properties |

### Calibration

Scoring is worthless without anchors. These are the anchors.

**1 — Purpose**

| Score | Looks like |
|---|---|
| 1–3 | Pure decoration. Deleting it loses nothing. Applied because the element existed |
| 4–6 | Vaguely supportive — softens a change, but a hard cut would communicate the same thing |
| 7–8 | Carries real information: state, causality, or origin. A reasonable person would notice its absence |
| 9–10 | Carries information the static design **cannot** express — identity across a navigation, hierarchy in a reveal, direction in a spatial model. Removing it would require adding UI to compensate |

**2 — Frequency fit**

| Score | Looks like |
|---|---|
| 1–3 | Animates an action performed 100+ times a day, or exceeds `t.xl` on a routine interaction |
| 4–6 | One token too generous for its tier — the kind of thing that feels fine in review and grating in week two |
| 7–8 | Inside the tier's budget |
| 9–10 | Inside budget *and* the tier was consciously identified, with the duration sitting at the bottom of the range rather than the top |

**3 — Spatial truth**

| Score | Looks like |
|---|---|
| 1–3 | Origin is arbitrary — scales from center when it belongs to a trigger; back navigates in the same direction as forward |
| 4–6 | Roughly right but unresolved edge cases: origin not flipped when a menu flips, RTL not mirrored |
| 7–8 | Origin correct, exit mirrors entry, direction encodes the real relationship |
| 9–10 | The above, plus honest fallbacks — when true origin bounds are unavailable it degrades to a plain transition instead of asserting a false identity |

**4 — Restraint**

| Score | Looks like |
|---|---|
| 1–3 | Everything moves. No lead element. A staggered menu, or a sheet whose contents choreograph themselves in |
| 4–6 | Three or four movers where two would do; overshoot with no brand-tone justification |
| 7–8 | One lead, supporting motion that earns its place, a non-empty stillness list |
| 9–10 | Something was deliberately *removed* during the design, and the spec says what and why |

**5 — Craft**

| Score | Looks like |
|---|---|
| 1–3 | Linear easing on UI travel; layout properties animated; symmetric enter/exit; `max-height: 9999px` |
| 4–6 | Right direction, wrong specifics — named enums where code parity was required, origin missing on a nested scaler |
| 7–8 | Correct easing direction, exit one token down, transform and opacity only, per-element origins |
| 9–10 | The above, plus parity: the Figma curve and the shipped curve are the same numbers, not the same adjective |

**6 — Accessibility & performance**

| Score | Looks like |
|---|---|
| 1–3 | No reduced-motion path, or a blanket kill. Large-area travel with no alternative. Animation not interruptible |
| 4–6 | Reduced motion handled by deletion where substitution was required; information lost with it |
| 7–8 | Substitutions defined per animation, motion is interruptible, compositor-only properties |
| 9–10 | The above, plus non-motion equivalents for anything motion was communicating, and a stated concurrent-animation budget |

### The threshold

**Ship at ≥ 8.0 weighted, with no individual criterion below 6.**

A high average hiding a 3 is not shippable — a beautiful animation with no reduced-motion path is an accessibility defect wearing good taste.

## 3. Four lenses

Score once through each. They catch different failures, and a single-perspective review reliably misses at least one class.

| Lens | Asks |
|---|---|
| **Motion Director** | Where does the eye go? Is there one lead? Does the timing have a rhythm, or is everything on the same clock? Does this look like the brand, or like a default? |
| **Engineer** | Can this be built at 60fps? Does it animate layout? What happens on interruption, on a slow network, on a low-end device? Is the origin resolvable at runtime? |
| **First-time user** | What just happened? Where did that come from? Where did it go? If they cannot answer, the motion failed at its only job |
| **Accessibility reviewer** | What does the reduced-motion path do — and does it still convey the information? Is anything large-area, parallax, or spinning? Is there a non-motion equivalent? Does anything flash more than three times a second? |

When the lenses disagree, the disagreement is the finding. The Engineer saying "this will jank" and the Director saying "it needs the extra travel" is a real design conflict, and it gets resolved in the spec, not by averaging.

## 4. Gap analysis

Plot **Purpose** (criterion 1) against **Execution** (criteria 4 and 5 — Restraint and Craft — averaged). The quadrant names the fix.

| | Execution low | Execution high |
|---|---|---|
| **Purpose high** | *Means something, looks sloppy.* Fix the execution — easing, origin, asymmetry, mover count. The idea is sound | *Strong.* Check accessibility and performance, then ship |
| **Purpose low** | *Restart.* Go back to INTENT. This is not a tuning problem | *Beautiful and pointless.* The most seductive failure. Delete it, or reassign the effort to a moment that would carry meaning |

The bottom-right quadrant is where good designers lose the most time — polishing motion that should not exist. Naming it out loud is the fastest intervention available.

## 5. Refinement

**Fix in this order. It is not arbitrary — earlier fixes make later ones unnecessary.**

1. **Delete the animation.** Most weak motion is over-specified, not under-specified
2. **Reduce it** — fewer movers, shorter travel, one token down
3. **Fix the easing** — direction first, then curve
4. **Correct the origin**
5. **Make it interruptible**
6. **Move it to the compositor** — transform and opacity only
7. **Make the timing asymmetric** — exit one token down
8. **Polish** — stagger rhythm, overshoot, secondary detail

Deleting outranks tuning. If step 1 was not seriously considered, the review has not happened yet.

### Stopping criteria

- **Score ≥ 8.0 and no criterion below 6** → ship
- **Three refinement passes completed** → deliver the best version with an honest note on where it landed and why
- **A pass improves the score by less than 0.3** → plateau. Stop. Say so

Do not loop. A fourth pass on a plateaued animation is not craft; it is avoidance — and each pass may cost a video render.

## 6. Red flags

Any of these caps the relevant criterion at 5 until resolved. They are not style preferences; each has a named failure.

**Purpose and restraint**

- Animation on an action performed 100+ times a day
- A staggered menu, dropdown, toolbar, or set of form fields
- An entrance reveal that re-runs on back-navigation, tab switch, or cache hit
- More than three elements in motion at the midpoint frame
- No identifiable lead element
- An empty stillness list

**Spatial**

- Back navigating in the same direction as forward
- A popover origin that does not flip when the menu flips
- A container transform from bounds that were guessed
- RTL not mirrored
- A sheet that enters from one edge and exits to another

**Craft**

- Linear easing on UI travel
- Symmetric enter/exit timing — **unless the spec names it as a cross-fade between peers on one clock** (archetype 5, tab switch), which is the one legitimate case
- `width`, `height`, `top`, `left`, `margin`, or `padding` animated without a stated reason
- `max-height: 9999px`
- Overshoot on a destructive confirmation, or on any displayed data value
- A scrim and its surface on different clocks
- **Layers of one material on different clocks** — colour fringing or highlights left static while the surface they belong to moves. Measurable: sample the colourful pixels across the loop; if their centroid does not travel while the material does, they were forgotten, whatever rationale was offered
- **Layers of one material rotating in opposite directions.** The half-fix that looks worse than the omission: the forgotten layer finally animates, with the sign inverted, and the component reads as running backwards because the eye tracks the colour rather than the chrome. Measurable — track one feature per layer and compare the signs
- **A rotation direction nobody chose.** If the request did not specify a direction and the reply does not say which one was used, it was not a decision. State it; it is one word to flip
- **A mask reveal standing in for a physical emission.** Measurable: track a printed feature across the clip — if it never travels while the object grows, it is a curtain, not a machine. Its companion failure is an object that stops dead where its material would follow through
- **Dead time at the end of the timeline.** Motion that finishes well before the frame does reads as broken rather than as a pause. Fill it with the settle or shorten the timeline
- **An approach chosen because it was the easiest node operation.** Growing a clipped frame, fading instead of moving, animating the wrapper because the child was awkward — each is a tool-shaped decision wearing a craft rationale
- An ambient material loop running faster than ~3s per cycle, where it reads as loading rather than as material
- Figma using a named easing enum where the code uses an explicit bezier

**Accessibility and performance**

- No reduced-motion path
- Reduced motion implemented by deletion where information was being conveyed — press feedback, loading states, toasts, and scrims all carry information and stay
- The blanket `animation-duration: 0.01ms !important` reset. **Near-zero duration is acceptable only for purely decorative motion**; anywhere else, substitute rather than collapse
- Large-area travel, parallax, or spin with no alternative
- Anything flashing more than three times per second
- A running animation that queues or restarts instead of retargeting when re-triggered
- A spinner with no timeout or error path

## 7. Delivering a critique

When the user asks for a review rather than a build, keep it short and ordered by severity:

1. **The verdict in one line.** "This is a 7.2 — sound idea, three fixable craft problems, and no reduced-motion path."
2. **The one thing that matters most.** Not a list. The single change with the largest effect
3. **The rest, ordered by the fix sequence above.** Each with what fails and why — never "feels off"
4. **What is working.** Last, and briefly. It is context for the critique, not a consolation prize

Do not soften findings into questions. "Have you considered whether the exit might be a bit long?" wastes the reviewer's authority and the reader's time. The exit is a token too long; say so.

## Related

- [../SKILL.md](../SKILL.md) — the pipeline
- [motion-system.md](motion-system.md) — the tokens the craft criterion is judged against
- [archetypes.md](archetypes.md) — per-pattern failure modes
- [motion-spec.md](motion-spec.md) — the spec this review scores the build against
- [ship-to-code.md](ship-to-code.md) — the interruptibility and performance criteria in production
