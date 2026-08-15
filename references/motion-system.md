# The Motion System

The token layer. Load this whenever you assign a duration, an easing, or a stagger — in the SPEC phase, and again in BUILD when translating tokens into Plugin API values.

The system exists to remove decisions. A designer who picks `t.lg` has made one decision; a designer who types `320ms` has made an unreviewable one. **Pick a token. Do not invent a number.**

## 1. Duration scale

Eight steps. Every value is corroborated by at least two published design systems — the spine is IBM Carbon's six-token scale, cross-checked against Material 3, Fluent 2, Atlassian, WinUI, and Material 1.

| Token | ms | seconds (Figma) | Scope | Corroboration |
|---|---|---|---|---|
| `t.none` | 0 | 0 | Deliberate non-animation. A real choice, not an omission. Also the reduced-motion target for decorative motion. | Atlassian and Salesforce both ship an explicit zero-duration token |
| `t.tap` | 70 | 0.07 | Press, toggle, checkbox — acknowledgment of touch. | Carbon `fast-01` 70ms ("button and toggle"), WinUI `Faster` 83ms, Fluent `ultraFast` 50ms |
| `t.xs` | 110 | 0.11 | Opacity-only change on a small element. Hover, focus ring, tiny fade. | Carbon `fast-02` 110ms ("fade"), Fluent `faster` 100ms, Material 3 `short2` 100ms |
| `t.sm` | 150 | 0.15 | **Default.** Menu, tooltip, dropdown, small expansion, short-distance travel. | Carbon `moderate-01` 150ms, Atlassian dropdown entrance 150ms, Fluent `fast` 150ms, M3 `short3` 150ms |
| `t.md` | 240 | 0.24 | Toast, accordion, medium surface, system communication. | Carbon `moderate-02` 240ms (names "toast" explicitly), M3 `medium1` 250ms, Atlassian modal entrance 250ms |
| `t.lg` | 300 | 0.30 | Bottom sheet, page transition on mobile, large surface arriving. | Material 1 mobile transition 300ms, M3 `medium2` 300ms, Fluent `slow` 300ms |
| `t.xl` | 400 | 0.40 | Container transform, full-screen overlay, large expansion. **The everyday ceiling.** | Carbon `slow-01` 400ms ("large expansion"), M3 `medium4` 400ms, Fluent `slower` 400ms, top of Atlassian's stated 150–400ms transition range |
| `t.2xl` | 700 | 0.70 | First-run reveal, hero moment, background dim. **Requires a written justification in the spec.** | Carbon `slow-02` 700ms ("background dimming, large hero transitions"), M3 `extra-long1` 700ms |

**Anything above `t.xl` is an exception that must be argued for, not a token you reach for.** Material 1 states motion beyond 400ms "may feel too slow"; Nielsen Norman Group finds that at 500ms "animations start to feel like a real drag." `t.2xl` exists because first-run moments genuinely earn it — frequency is 1.

### The three laws that select a token

**Law 1 — Frequency sets the ceiling.** A duration is only correct relative to how often it fires. See §5.

**Law 2 — Distance and area set the step within the ceiling.** A small element travelling a short distance takes less time than a large surface crossing the screen. Material 3, Carbon, and Fluent all state this independently: *"Duration should increase as the area/traversal of an animation increases."* The purpose is to hold *perceived velocity* constant, not to make important things slower.

**Law 3 — Exit is one token down.** Not 0.75×, not "a bit faster" — **one step down the scale.**

| Enter | Exit |
|---|---|
| `t.xl` 400 | `t.lg` 300 |
| `t.lg` 300 | `t.md` 240 |
| `t.md` 240 | `t.sm` 150 |
| `t.sm` 150 | `t.xs` 110 |

An entering element is earning attention. A leaving element already lost it — making the user watch it go is a tax. Material 1 encodes the same asymmetry (225ms enter / 195ms exit); Atlassian ships it as separate tokens and states it outright: *"Make exit motion faster than entrances so dismissed elements don't block someone's workflow."*

**The one documented inversion: button press.** Press-down (`t.tap`) is *faster* than release (`t.xs`). Press-down is not an entrance — it is an acknowledgment, and it must land inside Nielsen's 100ms instantaneity threshold or it is not feedback, it is a delayed reaction.

### Platform modifiers

Material 1 is the only source publishing these; treat them as step adjustments, not multipliers, so the scale stays intact.

| Context | Adjustment | Source |
|---|---|---|
| Desktop | **two tokens down** (300 → 150, 400 → 240) | M1: *"desktop animations should last 150ms to 200ms"* against 300ms mobile — that is two steps on this scale, not one |
| Tablet | one token up | M1: ≈ +30% |
| Wearable | one token down | M1: ≈ −30% |

Where a two-step drop reads as abrupt for a large surface, one step is defensible — but say so in the spec, because the cited source supports two.

## 2. Easing tokens

Seven tokens. The character is what matters; the exact curve is how you get parity between Figma and code.

| Token | Character | When |
|---|---|---|
| `e.enter` | Decelerate — starts at full speed, settles | Anything arriving: from off-screen, from nothing, from a trigger |
| `e.exit` | Accelerate — starts calm, leaves at full speed | Anything departing the screen or being dismissed |
| `e.move` | Eased at both ends | Motion that begins *and* ends on screen: an indicator sliding, a card repositioning |
| `e.expressive` | Slow, flat lead-in then a forceful settle | Hero and first-run moments, **and large choreographed container transforms** (card → detail, FAB → surface). This is the "expensive" curve — it reads as deliberate, and it reads as pretentious on a dropdown. Never on a high-frequency surface |
| `e.linear` | No easing | Continuous motion only: spinner rotation, shimmer loop, determinate progress, color-only crossfade |
| `e.spring` | Physical settle, optional overshoot | **Only where real velocity exists** — drag, flick, swipe-to-dismiss, gesture-driven back |
| `e.hold` | Step — no interpolation | Discrete state change, step reveal, intentionally abrupt toggle |

### The parity table

This is the table that keeps Figma and production in sync. Every row is the same motion expressed three ways.

| Token | Figma Plugin API easing object | CSS | motion.dev |
|---|---|---|---|
| `e.enter` | `{ type: "CUSTOM_CUBIC_BEZIER", easingFunctionCubicBezier: { x1: 0, y1: 0, x2: 0, y2: 1 } }` | `cubic-bezier(0, 0, 0, 1)` | `ease: [0, 0, 0, 1]` |
| `e.exit` | `{ type: "CUSTOM_CUBIC_BEZIER", easingFunctionCubicBezier: { x1: 0.3, y1: 0, x2: 1, y2: 1 } }` | `cubic-bezier(0.3, 0, 1, 1)` | `ease: [0.3, 0, 1, 1]` |
| `e.move` | `{ type: "CUSTOM_CUBIC_BEZIER", easingFunctionCubicBezier: { x1: 0.2, y1: 0, x2: 0, y2: 1 } }` | `cubic-bezier(0.2, 0, 0, 1)` | `ease: [0.2, 0, 0, 1]` |
| `e.expressive` | `{ type: "CUSTOM_CUBIC_BEZIER", easingFunctionCubicBezier: { x1: 0.05, y1: 0.7, x2: 0.1, y2: 1 } }` | `cubic-bezier(0.05, 0.7, 0.1, 1)` | `ease: [0.05, 0.7, 0.1, 1]` |
| `e.linear` | `{ type: "LINEAR" }` | `linear` | `ease: "linear"` |
| `e.spring` | `{ type: "CUSTOM_SPRING", easingFunctionSpring: { bounce: 0 } }` — use `0.15` for gesture release specifically | generated `linear(…)`, shape only — see [ship-to-code.md §6](ship-to-code.md#6-platform-notes) | `{ type: "spring", visualDuration: <s>, bounce: 0 }` |
| `e.hold` | `{ type: "HOLD" }` | `steps(1, jump-end)` | — (use a keyframe with no interpolation) |

`e.enter`, `e.exit`, and `e.move` are Material 3's `standard-decelerate`, `standard-accelerate`, and `standard` verbatim. `e.expressive` is M3's `emphasized-decelerate`.

The *construction* is the cross-system consensus, even where the coefficients differ: an entering curve zeroes the in-handle (`x1=0, y1=0`, so it starts already at speed); an exiting curve pushes the out-handle toward unit (`x2=1, y2=1`, so it never slows before it leaves). WinUI builds its pair exactly this way. Carbon's expressive set does; its productive exit lands `y2` slightly short of 1. **There is no consensus curve — pick one set and be consistent. Do not average them.**

> **Write the bezier, not the enum name.** Figma's named enums (`EASE_OUT`, `EASE_IN_AND_OUT`) are *cubic* easings and do **not** match the design-system curves above. If you use `EASE_OUT` in Figma and `cubic-bezier(0,0,0,1)` in code, the two will not look the same and nobody will be able to say why. Use `CUSTOM_CUBIC_BEZIER` with the token's exact values whenever the Figma file is meant to specify production motion. Use the named enums only for throwaway explorations where parity does not matter.

### Enum hazards

The complete public enum list, the rejected internal names, and the rejected shortened aliases are documented in [figma-use-motion's motion-easing reference](../../figma-use-motion/references/motion-easing.md) — **read them there rather than from memory**, because that file tracks the API and this one does not.

Two consequences worth stating here, because they are about the token system rather than the API:

- A bad enum **fails the entire script.** `use_figma` scripts are atomic: nothing is written. So an enum guess does not cost you one wrong track, it costs you the whole build step.
- Writing tokens as `CUSTOM_CUBIC_BEZIER` sidesteps most of the hazard surface anyway — which is the second reason to prefer it over the named enums, after parity.

## 3. Springs, and the overshoot budget

**Use a spring only where real velocity exists.** Drag, flick, swipe-to-dismiss, gesture-driven back. In those cases a fixed-duration curve visibly discards the velocity the user's finger just supplied, and the interface reads as fighting them — a failure users notice immediately even when they cannot name it.

Everywhere else — hover, press, state toggle, a modal opening from a click — a bezier is correct, cheaper, and easier to keep in parity.

Figma stores springs as a single normalized `bounce` in `0…1` — `0` settles with no overshoot, higher values oscillate more. The API shape, the physical-to-normalized conversion helper, and the read-back behavior are documented in [figma-use-motion's motion-easing reference](../../figma-use-motion/references/motion-easing.md). What matters for the system is the budget below.

### Overshoot budget

| bounce | Read as | Use |
|---|---|---|
| `0` | Confident, precise | Default for any spring in product UI |
| `0.1 – 0.2` | Alive, slightly physical | Drag release, swipe-to-dismiss, pull-to-refresh snap |
| `0.2 – 0.3` | Playful | Consumer products, low-frequency moments, brand-tone dependent |
| `> 0.3` | Toy-like | Almost never. Requires an explicit brand-tone justification in the spec |

**Never bounce opacity, color, or a data value.** Material's spring token set makes this structural: its "spatial" specs carry bounce while its "effects" specs are critically damped in every scheme. A number that overshoots to 1,047 before settling at 1,031 has displayed a figure that is not true — that is a correctness bug wearing a motion costume.

## 4. Stagger

Stagger exists to show *relationship and order*, not to fill time.

**The formula:**

```
k        = min(n, 8)                          // items that stagger; the rest arrive together
stagger  = clamp((500 − t_item) / (k − 1), 20, 60) ms
total    = (k − 1) × stagger + t_item         // must be ≤ 500 ms
```

`t_item` is the per-item duration, normally `t.sm` 150. The subtraction matters: the last item *starts* at `(k − 1) × stagger` and then still needs its own duration to finish, so a formula that divides 500 by `n` alone blows the cap for exactly the list sizes most common in practice.

Worked: **n = 12** → `k = 8`, `stagger = clamp(350 / 7, 20, 60)` = **50ms**, total = `7 × 50 + 150` = **500ms**. **n = 4** → `k = 4`, `clamp(350 / 3, 20, 60)` clamps to **60ms**, total = `3 × 60 + 150` = **330ms**.

If the computed total still exceeds 500ms, reduce the interval until it does not. **The cap wins over the formula** — it is the rule with a source behind it.

- The **20ms floor** is IBM Carbon's published value: *"staggering the entrance of table content by 20 ms significantly reduces the cognitive load."* Below it, stagger stops reading as sequence and becomes noise.
- The **60ms ceiling** sits inside the 30–80ms band practitioners use for group entrances. Above it, a list reveal starts to feel like it is being dealt to you.
- The **500ms total cap** is Carbon's, and it is the load-bearing rule: *"the delay should be adjusted to ensure that total time is still within 500 ms."* It is also bounded by Nielsen's 1-second flow-of-thought limit — a reveal that outlasts the user's readiness to act has stopped being decoration and become an obstacle.
- The **8-item cap** follows: staggering 40 rows at 40ms is a 1.6-second wait to see the bottom of a list. The user has already tried to scroll.

Beyond the base interval, everything about stagger is a judgment call and should be labelled as one — no vendor publishes stagger values except Carbon's 20ms.

### Direction

Stagger direction is not decoration; it encodes causality.

| Situation | Direction |
|---|---|
| Content populating | Reading order — top to bottom, left to right within a row (mirror under RTL) |
| Response to a tap | Outward from the interaction point |
| Data | Data order — chronological for a time series, ranked for a ranking |
| Hierarchy reveal | Importance order — the thing that matters most arrives first, not last |

### Never stagger

Menu and dropdown items. The contents of a sheet or modal. Tab panel content on switch. Toolbar icons. Form fields.

These are single surfaces, and staggering them is the clearest tell that motion was applied by decoration rather than by intent. A staggered menu looks lovely once in a portfolio loop and is unbearable by the fourth open of the working day.

## 5. Frequency tiers

Frequency is the first gate in INTENT and the ceiling on every duration decision afterward. Atlassian states the operative rule: high-frequency interactions stay *"under 150ms."*

| Tier | Examples | Budget |
|---|---|---|
| **≥ 100×/day** | Keyboard shortcuts, command palette, list-row hover, typeahead results | **`t.none`.** Do not animate. Motion here is a tax levied hundreds of times daily on someone who is trying to work |
| **~10×/day** | Navigation, menus, tabs, toggles, press feedback | `t.tap` – `t.sm`. Near-imperceptible. If in doubt, go down a step |
| **Occasional** | Modal, sheet, toast, page transition, expand-to-detail | `t.sm` – `t.xl`. The normal working range |
| **Rare / first-run** | Onboarding, empty → first success, celebration, hero reveal | Up to `t.2xl`. The delight budget lives here and only here |

**Tone changes character, not the ceiling.** A playful brand still does not animate a hundred-times-a-day action; it spends its personality on the first-run moment instead.

## 6. Property discipline

**Animate `transform` and `opacity`. Everything else needs a reason.**

Properties that change geometry or position — `width`, `height`, `top`, `left`, `margin`, `padding` — force the browser to recompute layout on every frame. At 60fps the frame budget is 16.7ms and the browser needs roughly 6ms of that for its own rendering, leaving about 10ms. Layout work does not fit in it, and no easing curve rescues the resulting jank.

This matters more in Figma than it looks, because **Figma's Plugin API will happily animate the expensive ones.** `WIDTH`, `HEIGHT`, `STACK_SPACING`, `STACK_PADDING_*`, and `GRID_*_GAP` are all in the public allowlist, and nothing warns you that they will read worse and cost more when the design becomes code.

| Intent | Animate this | Not this |
|---|---|---|
| Move | `TRANSLATION_X` / `TRANSLATION_Y` | `x` / `y` position, layout padding |
| Resize | `SCALE_X` / `SCALE_Y` (counter-scale the content) | `WIDTH` / `HEIGHT` |
| Reveal | `OPACITY` | `WIDTH` from 0 |
| Reflow a list | Transform each item | `STACK_SPACING` |
| Expand a panel | Measured-height transform, `clip-path`, or `scaleY` | Animated `height`, `max-height: 9999px` |

The `max-height: 9999px` accordion deserves its own warning: it makes the visible animation speed depend on the actual content height, so short panels snap and long ones crawl, and the easing curve you specified is effectively destroyed. Measure the real height.

## 7. Units — the factor-of-1000 trap

Four surfaces, two units.

| Surface | Unit |
|---|---|
| Figma Plugin API — `timelinePosition`, `timelines[].duration`, `setTimelineDuration()`, animation style `duration` / `timelineOffset` | **seconds** |
| `get_motion_context` — `timelineDurationMs`, `timelineCohorts[].durationMs` | **milliseconds** |
| CSS `animation` / `transition`, motion.dev `duration` / `visualDuration` | CSS accepts both `s` and `ms`; motion.dev is seconds. **Write seconds** so both match the token file |
| Android Compose | **milliseconds** |

**The rule: the Motion Spec stores milliseconds as canonical, and the conversion to seconds happens exactly once, at the point of the Plugin API call.** Never carry both units through the spec, never convert twice, and never let a reviewer see a number without a unit. The token table above lists both columns precisely so nobody has to compute one.

A `timelinePosition` of `250` is not a quarter-second — it is four minutes ten seconds. The failure is silent: the script succeeds, the timeline stretches, and the animation appears not to run.

## 8. Applying the system — worked examples

**A dropdown menu opening.** High frequency (~10×/day) → ceiling is `t.sm`. Small surface, no travel → no reason to step up. Arriving → `e.enter`. Exit one down → `t.xs`.

```
enter: t.sm (150ms) · e.enter · transform-origin at the trigger edge
exit:  t.xs (110ms) · e.exit
stagger: none — a menu is one surface
```

**A bottom sheet on mobile.** Occasional → normal range. Large surface, long travel → step up to `t.lg`. Arriving → `e.enter`. Exit one down → `t.md`. Draggable → the release is `e.spring`, bounce `0.15`, because the finger supplied velocity.

```
enter: t.lg (300ms) · e.enter · TRANSLATION_Y, scrim OPACITY on the same clock
exit:  t.md (240ms) · e.exit
drag release: e.spring bounce 0.15
stagger: none — contents ride with the container
```

**The same sheet on desktop.** Platform modifier: one token down. `t.md` enter / `t.sm` exit.

**A list of 12 cards populating for the first time.** Occasional, decorative → `t.sm` 150 per item. `k = 8`; `stagger = clamp((500 − 150) / 7, 20, 60)` = **50ms**, applied to the first 8 items; items 9–12 arrive with item 8. Total = `7 × 50 + 150` = **500ms**, exactly at the cap.

```
per item: t.sm (150ms) · e.enter · OPACITY + TRANSLATION_Y 12px
stagger: 50ms, reading order, first 8 items only
runs: once, on first population — never on back-navigation, never on tab switch
```

## Related

- [../SKILL.md](../SKILL.md) — the pipeline this system serves
- [motion-spec.md](motion-spec.md) — the artifact these tokens are recorded in
- [archetypes.md](archetypes.md) — per-pattern token assignments with sources
- [ship-to-code.md](ship-to-code.md) — carrying these tokens into production without drift
