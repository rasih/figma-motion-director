# Shipping Motion to Code

Load this in Phase 6, alongside [figma-implement-motion](../../figma-implement-motion/SKILL.md).

That skill owns the merge mechanics: `get_motion_context`, snippet handling, `data-node-id` matching, wrapper splitting, `transformOrigin` placement, framework choice, and the mandatory rules that go with them. **Follow it; where it and this file disagree on a mechanic, it wins.**

This file *extends* it with four things the design side owns: **token parity**, **timeline-to-lifecycle translation**, a **substitution-based** reduced-motion policy (that skill requires reduced motion; this one specifies what to replace with what), and **interruptibility**.

## 1. Token parity

**Ship the tokens, not the numbers.**

Motion drifts the moment fifteen components each carry their own `0.3`. Six months later nobody can answer "what is our standard transition" because the answer is forty-one different values.

```ts
// motion.ts — the complete token set, in seconds
export const duration = {
  none: 0,      // t.none — deliberate non-animation; reduced-motion target
  tap:  0.07,   // t.tap
  xs:   0.11,   // t.xs
  sm:   0.15,   // t.sm — default
  md:   0.24,   // t.md
  lg:   0.30,   // t.lg
  xl:   0.40,   // t.xl — everyday ceiling
  xxl:  0.70,   // t.2xl — requires written justification
} as const

export const easing = {
  enter:      [0, 0, 0, 1],
  exit:       [0.3, 0, 1, 1],
  move:       [0.2, 0, 0, 1],
  expressive: [0.05, 0.7, 0.1, 1],
  linear:     'linear',
  hold:       'steps(1, jump-end)',   // e.hold
} as const

export const spring = {
  settle:  { type: 'spring', visualDuration: 0.3, bounce: 0 },      // e.spring default
  gesture: { type: 'spring', visualDuration: 0.3, bounce: 0.15 },   // drag / flick release only
} as const
```

`t.2xl` is exported as `xxl` because `2xl` is not a valid identifier; the comments carry the mapping so a reader can trace any constant back to the spec.

Then every component references `duration.lg` and `easing.enter`. A design change becomes a one-line edit instead of a search-and-replace across the codebase — and a reviewer can see at a glance that a component using `0.35` has stepped outside the system.

**Two rules that keep parity real:**

- **Use the numbers from the parity table, not the adjective.** "Ease out" in Figma and `ease-out` in CSS are different curves. If the Figma file used `CUSTOM_CUBIC_BEZIER` with explicit values — as it should have — the code uses the same four numbers.
- **Use `codeSnippets` values verbatim.** Factor the *code* for reuse; never rewrite the values. The merge skill's Rule 1 covers why, and it governs.

### The transform trap

The two directions disagree about what a transform value means:

| Direction | Semantics |
|---|---|
| **Figma Plugin API** (writing motion *into* Figma) | Transform keyframes are **additive / multiplicative**. `TRANSLATION_X: 0` means "no change from the resting transform"; `SCALE_X: 1` is neutral |
| **`get_motion_context`** (reading motion *out of* Figma) | The emitted `rotate` / `x` / `scale` are **absolute** — they already include any static base transform, so a snippet must be offset against that base. The merge skill's interleaved-transform section has the worked example |

Any statement of the form "Figma transform values are X" is wrong on one side. **State the direction, always** — including in the spec, where a `From → To` written in absolute terms will be composed wrongly at BUILD time.

## 2. Timeline → lifecycle

A Figma timeline is **one clock with absolute positions**. Production motion is **a set of independent lifecycles**. Nothing in the file expresses that difference, so it has to be decided — and the spec's lifecycle block is where it was decided.

| Timeline segment | Production lifecycle |
|---|---|
| 0 → enter duration | Mount, or the open transition |
| The segment after | Exit — usually reversed, one token down |
| A held state | Not motion at all. A CSS state, a variant, a class |
| A looping section | A `while` condition — loading, pending, live — with a defined stop |
| Gesture-driven travel | Not a timeline at all. A direct mapping from input to position |

**Three decisions to make explicitly:**

**What loops in production?** A Figma file loops for preview. That is a viewing convenience, not a specification. `timelineCohorts[].loopMode` reports `once`, `loop`, or `boomerang` — treat `loop` as a claim requiring confirmation, not an instruction. A looping animation with no stop condition is a battery cost and an accessibility problem.

**What is a lifecycle and what is a state?** If the design shows an element at rest, then moved, then at rest, ask whether the second rest is a *different state* rather than the end of an animation. States belong in the component's state model with a transition on the changing properties — not in a keyframe track.

**Where does exit live?** React removes DOM before an exit animation can run. Exit requires an explicit mechanism — `AnimatePresence` in motion.dev, or equivalent — and it is the single most commonly dropped half of a design. **Anything with an entrance needs an exit.**

## 3. Reduced motion

**The preference asks you to remove, reduce, *or replace*. Replacement is almost always the right answer.**

Ship the substitution the spec defined. As a general mapping:

| Original | Reduced |
|---|---|
| Travel (slide, sheet, page transition) | Cross-fade in place, one or two tokens down |
| Large scale or container transform | Cross-fade between the two states — **never a smaller version of the same transform**, since partial motion of a large surface is exactly the vestibular trigger |
| Parallax, scroll-linked motion | Nothing. Static |
| Staggered reveal | Single fade, or instant |
| Looping decorative motion | Static |
| Press feedback | **Keep it.** 0.97 over 70ms is not a trigger, and removing it removes function |
| Loading spinner | Pulsing opacity, a text status, or discrete-step progress. **Never remove the loading state** |
| Toast arrival | Fade in place. **Keep the toast** — it carries information |
| Data-viz animation | Snap to final value. Nothing is lost |

**Precedence, stated plainly:** the merge skill offers "skip the `animate` or cut the duration to near-zero" as its reduced-motion default. **That is correct for purely decorative motion and wrong for anything carrying information.** Where the table above names a substitution, the substitution wins; near-zero is the fallback for the decorative rows only.

**Never ship the blanket reset.** `* { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }` kills motion that was explaining relationships between elements, and on JavaScript-driven animation it can produce something faster and more dizzying than the original — the precise opposite of the intent.

Two structural notes: `@media (prefers-reduced-motion)` is equivalent to `: reduce`, and progressive enhancement — build without motion and add it inside `(prefers-reduced-motion: no-preference)` — makes the reduced path the default rather than the afterthought.

Beyond the preference, three hard requirements: nothing flashes more than three times in one second; auto-starting motion that runs longer than five seconds alongside other content needs a pause, stop, or hide control; and anything the motion was *communicating* needs a non-motion equivalent.

## 4. Interruptibility

**A re-triggered animation must retarget from where it is, not queue or restart.**

This is the property that separates interfaces that feel alive from ones that feel like they are playing a recording at you. It is invisible in a Figma file, because a timeline cannot express it — which is exactly why it belongs on this list.

- **Use transitions or springs for rapidly-triggered elements, not keyframes.** A keyframe animation restarts from frame zero; a transition retargets from the current computed value.
- **Springs absorb velocity; CSS spring approximations do not.** A generated `linear()` curve is a fixed shape — it can look like a spring but cannot respond to how fast the user was dragging. Where real velocity exists, use a real spring.
- **Gesture-driven motion tracks input 1:1 and inherits release velocity.** Snapping to a fixed curve on release feels broken in a way users notice instantly and cannot name.
- **Commit lightweight actions mid-gesture; commit destructive ones only on release.** The commitment threshold should scale with the consequence.
- **Never make the user wait for an animation to finish before they can act.**

## 5. Performance

At 60fps the frame budget is 16.7ms, and the browser needs roughly 6ms of it for its own work — leaving about **10ms**. Layout work does not fit.

- **Compositor-only properties: `transform` and `opacity`.** Everything else triggers paint, layout, or both.
- **Layout-triggering properties can sometimes be animated safely** on elements that do not affect surrounding layout — `position: absolute`, for instance. Test on a low-end device before relying on it.
- **`will-change` is a last resort, not a default.** Excessive use costs memory and creates its own rendering complexity. Toggle it from JavaScript around the animation rather than declaring it in a stylesheet, where the browser holds the optimization far longer than needed.
- **Motion library transform shorthands are not always accelerated.** In motion.dev, individual transforms like `x` and `scale` compile to CSS variables and are not hardware-accelerated even though they end up on `transform`. **Do not rewrite an emitted snippet to work around this** — the merge skill's verbatim-snippet rule governs, and the shorthands are also what its own layout-collision fix depends on. Raise it as a measured finding if profiling shows it matters.
- **Budget concurrent animations.** More than a handful of simultaneously animating elements is a design problem before it is a performance problem — and it is both.
- **Respond to input within 100ms** regardless of how long the resulting animation runs. Feedback and animation are separate obligations.

## 6. Platform notes

Framework choice and library selection belong to [figma-implement-motion](../../figma-implement-motion/SKILL.md#framework-recommendations) — **match the codebase's existing motion stack before introducing another one.** What matters here is how the token system survives the crossing:

| Target | Duration | Easing | Notes |
|---|---|---|---|
| **CSS** | seconds | `cubic-bezier(…)` verbatim from the parity table | Springs become a generated `linear()` — shape only, no velocity capture |
| **motion.dev / React** | seconds | `ease: [x1, y1, x2, y2]` | Springs as `{ visualDuration, bounce }` rather than stiffness/damping — easier to keep in parity with Figma's normalized `bounce` |
| **SwiftUI** | seconds | Map to a real SwiftUI API — see the merge skill's SwiftUI translation section | Springs are native here; a duration+bezier token often translates better as a spring than as a literal curve |
| **Android Compose** | milliseconds | `CubicBezierEasing(x1, y1, x2, y2)` | Watch the unit — Compose is ms while the token file above is seconds |

## 7. Drift

Motion drifts silently, because nothing fails when it does. Three cheap checks:

1. **The token file is the source of truth for values, and it lives in the codebase.** If the canonical numbers live only in a Figma file that one designer can open, they will diverge within a quarter.
2. **Know which conflict you are resolving.** When `get_design_context` and `get_motion_context` disagree about a value, `get_motion_context` wins — that is the merge skill's rule and it is about which *tool* to trust. When the Figma file and the codebase's token file disagree, that is a *drift* question, and the Motion Spec decides which side is stale. Never overwrite the token file from a Figma read without that decision.
3. **Re-run the review rubric against the shipped build, not the Figma file.** Production has real data, real network latency, and real interruptions. A transition that outlasts its data fetch tests fine in Figma and delivers the user to a spinner in production.

## Related

- [../SKILL.md](../SKILL.md) — the pipeline
- [../../figma-implement-motion/SKILL.md](../../figma-implement-motion/SKILL.md) — the merge mechanics this file assumes
- [motion-system.md](motion-system.md) — the parity table
- [motion-spec.md](motion-spec.md) — the lifecycle block this phase implements
- [review.md](review.md) — the rubric to re-run against the shipped build
