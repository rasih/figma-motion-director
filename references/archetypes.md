# The Archetype Library

Eighteen patterns that cover most product motion — plus two that cover the shot work product-UI libraries leave out. Load this whenever the thing being animated is a recognizable UI pattern — and always when no live reference is available.

**This is the baseline, not a menu.** A live benchmark must *beat* the default here before it is allowed to override it. A reference that merely differs is not evidence that the default is wrong.

Tokens (`t.sm`, `e.enter`, …) are defined in [motion-system.md](motion-system.md).

## Source key

| Tag | Source |
|---|---|
| **[M3]** | Material Design 3 motion tokens, read from the `material-web` token package |
| **[M1]** | Material Design 1 spec — mobile 300ms, enter 225 / exit 195, ">400ms may feel too slow", desktop 150–200ms, tablet +30%, wearable −30% |
| **[CARB]** | IBM Carbon — `fast-01` 70 ("button and toggle"), `fast-02` 110 ("fade"), `moderate-01` 150 ("small expansion, short distance"), `moderate-02` 240 ("expansion, system communication, toast"), `slow-01` 400 ("large expansion"), `slow-02` 700 ("background dimming") |
| **[ATL]** | Atlassian — interactions 50–150ms, transitions 150–400ms, dropdown entrance 150ms, modal entrance 250ms, "make exit motion faster than entrances" |
| **[FLU]** | Microsoft Fluent 2 duration tokens — 50 / 100 / 150 / 200 / 250 / 300 / 400 / 500 |
| **[WIN]** | WinUI — 83 / 167 / 250ms; entrance `(0,0,0,1)`, exit `(1,0,1,1)` |
| **[NNG]** | Nielsen Norman Group — 0.1s instantaneous, 1s flow of thought, 10s attention; progress-indicator thresholds; skeleton guidance |
| **[WCAG]** | W3C WCAG 2.1 SC 2.3.3 — interaction-triggered motion must be disableable "unless essential to the functionality or the information being conveyed" |
| **[MDN]** | MDN — `prefers-reduced-motion` asks you to "remove, reduce, **or replace**" motion |
| **[CONV]** | **Convention, not spec.** Widely observed but not published by any vendor. **Do not cite it as a source** — own it as judgment |

No Apple values appear here. Apple's documentation is not directly verifiable from this environment, and unverified vendor numbers do not belong in a reference.

## The five laws

Applied to every archetype below.

1. **Exits are faster than entrances** — one token down. [ATL] states it; [M1] encodes it (225 / 195).
2. **Frequency sets the ceiling.** [ATL] caps high-frequency interactions under 150ms.
3. **Distance and area set the step within the ceiling.** [M1], [M3], [CARB] all state this independently.
4. **Decelerate on enter, accelerate on exit.** Universal across [M3], [M1], [CARB], [WIN].
5. **Never animate layout-triggering properties.** Transform and opacity. Where a size change is genuinely required, use a measured-height transform, `clip-path`, or a counter-scaled `scaleY`.

## Quick reference

Most questions are answered by this table alone. Read the full entry when you need the failure modes, the origin rule, or the reduced-motion substitution.

| # | Archetype | Enter | Exit | Easing | Stagger |
|---|---|---|---|---|---|
| 1 | Bottom sheet | `t.lg` 300 | `t.md` 240 | `e.enter` / spring if draggable | none |
| 2 | Modal | `t.md` 240 | `t.sm` 150 | `e.move`, no overshoot | none |
| 3 | Popover / menu | `t.sm` 150 | `t.xs` 110 | `e.enter`, origin at trigger | **never** |
| 4 | Toast | `t.md` 240 | `t.sm` 150 | `e.enter`, slight overshoot ok | 50–80ms, cap 3 |
| 5 | Tab switch | `t.sm` 150 | `t.sm` 150 — **matched; cross-fade, Law 3 n/a** | `e.move` | none |
| 6 | List reveal | `t.sm` 150/item | — | `e.enter` | formula, first 8 |
| 7 | Card → detail | `t.lg` 300 – `t.xl` 400 | one down | `e.expressive` | ~50ms content offset |
| 8 | Page transition | `t.lg` 300 mobile / `t.sm` 150 desktop | one down | `e.enter` / `e.exit` | none |
| 9 | FAB transform | `t.xl` 400 | `t.lg` 300 | `e.expressive` | icon out 30%, content in 50% |
| 10 | Skeleton swap | `t.sm` 150 | — | linear cross-fade | per section, as data lands |
| 11 | Accordion | `t.md` 240 | `t.sm` 150 | `e.move` | none |
| 12 | Button press | **`t.tap` 70 down** | `t.xs` 110 up — **inverted; see law 1** | near-linear down | — |
| 13 | Pull-to-refresh | gesture-driven | `t.md` 240 | spring on release, linear spin | — |
| 14 | Onboarding | `t.lg` – `t.xl` per element | — | `e.expressive` | 80–150ms, total ≤ 1200ms |
| 15 | Counter / chart | `t.xl` 400 – `t.2xl` 700 | — | `e.enter`, **never overshoot** | 30–60ms |
| 16 | Spinner | 300–500ms delay | `t.xs` 110 | **`e.linear` rotation** | — |
| 17 | Ambient / material loop | **4–8s per cycle** | — | `e.linear`, seamless | none — **one material, one clock** |
| 18 | Emission / dispensing | drive 400–700ms + settle 300–600ms | — | `e.linear` drive, `e.spring` settle | none — **travel, don't unmask** |

**Global modifiers.** Desktop two tokens down · tablet one up · wearable one down ([M1]). Exit one token down, except where a row above says otherwise. High-frequency patterns cap at `t.sm` ([ATL]).

---

## 1 — Bottom sheet / drawer

**Message.** *You have not left this screen; this is temporary; it will return where it came from.* The persistence of the parent is the entire point.

**Animate** `TRANSLATION_Y` on the sheet, `OPACITY` on the scrim.
**Never animate** the sheet's width, height, corner radius, or internal layout during travel. Never move the page beneath. Never choreograph the sheet's contents separately — they ride with the container.

**Origin.** From the edge it will return to. A bottom sheet enters up and exits down; a side drawer enters and exits on its own edge. A sheet that enters from the bottom and exits to the side destroys the spatial model.

**Timing.** Enter `t.lg` 300 · exit `t.md` 240. Desktop drawers step down to `t.md` / `t.sm` per [M1]'s desktop guidance. Sources: [CARB] 240–400 for expansion, [M1] 300ms mobile, [ATL] 150–400 transitions, [M3] `medium1–3`.

**Easing.** `e.enter` in, `e.exit` out. **If draggable, the release is `e.spring` (bounce 0.15)** — the finger supplied real velocity and a fixed curve visibly discards it.

**Stagger.** None. The sheet is one object.

**Fails when** height is animated instead of `TRANSLATION_Y` (content reflows every frame and the sheet appears to grow rather than arrive) · the scrim lingers after the sheet is gone, leaving a frozen-looking dimmed screen · dismissal ignores fling velocity.

**Reduced motion.** Cross-fade in place, `t.sm` 150. **Keep the scrim** — it carries the modality information [MDN].

---

## 2 — Modal dialog

**Message.** *Stop; this is above everything; resolve it.* Unlike a sheet, a modal has no spatial home — it belongs to the moment, not to an edge.

**Animate** `OPACITY` plus a small `SCALE_XY` on the dialog; `OPACITY` on the scrim.
**Never animate** travel across the screen — a modal that slides in from an edge implies it came from somewhere and can be sent back, which is false and undercuts the interruption. Never animate its size.

**Origin.** In place, at final position, scaling `0.92 → 1`. Not from 0 — a dialog growing from nothing reads as a zoom effect, and at large sizes it is disorienting. The start value is [CONV]; the principle (small delta, in place) follows from [ATL] recommending its ease-in-out curve specifically "for scaling Modals".

**Timing.** Enter `t.md` 240 · exit `t.sm` 150. [ATL] states modal entrance = 250ms directly — the strongest single citation in the library. [WIN] `ControlNormal` 250. [M3] `medium1` 250. Note this is *shorter* than a bottom sheet despite feeling more significant, because there is no distance to travel.

**Easing.** `e.move` in (both ends eased — it is a scale, not an arrival from off-screen), `e.exit` out. **No overshoot.** A bouncing confirmation trivializes the decision it is asking for, and on a destructive confirm it is tonally wrong.

**Stagger.** None.

**Fails when** the scrim and dialog run on different clocks — a dialog arriving in 240ms over a scrim fading for 700ms floats in a still-darkening void · a springy entrance on a destructive confirmation · sliding in from an edge.

**Reduced motion.** Drop the scale; fade only, `t.sm` 150. Keep the scrim fade — it is the modality signal, and removing it loses information rather than polish.

---

## 3 — Popover / dropdown / menu

**Message.** *This belongs to the thing you just tapped.* The binding is the whole job.

**Animate** `OPACITY` + `SCALE_XY` 0.95 → 1 with the origin at the trigger edge. Optionally 4–8px of `TRANSLATION_Y`.
**Never animate** width or height — text reflow inside a menu is extremely visible. Never animate individual menu items.

**Origin.** **Anchored to the trigger, and flipped when the menu flips.** A menu that opens upward because it is near the viewport bottom must scale from its *bottom* edge. Getting this wrong is the most common popover bug and it makes the menu feel detached from the control that opened it.

**Timing.** Enter `t.sm` 150 · exit `t.xs` 110. [ATL] states dropdown entrance = 150ms and caps high-frequency interactions under 150ms. [CARB] `moderate-01` 150 describes exactly this pattern. Menus are high-frequency: this must land near [NNG]'s 0.1s threshold.

**Easing.** `e.enter` in; at 110ms out the curve barely matters — speed does.

**Stagger.** **Never.** Staggered menu items are the canonical portfolio-motion tell: lovely once in a feed, unbearable by the fourth open of the day.

**Fails when** the origin is stale after a flip · items are staggered · the exit is slow enough that reopening catches the old menu still fading, producing a double image.

**Reduced motion.** Fade only, `t.xs` 110. Drop scale and translate.

---

## 4 — Toast / snackbar / notification

**Message.** *Something happened; you may ignore this.* It must be noticeable without stealing focus — a toast that demands attention has become a modal and failed.

**Animate** `TRANSLATION_Y` (or X) + `OPACITY`.
**Never animate** scale (implies importance), color, or the underlying content. Never move other UI to make room — reserve the space or overlay it.

**Origin.** The nearest screen edge, exiting to the same edge. Consistency of edge across the app matters more than which edge — users learn where notifications live.

**Timing.** Enter `t.md` 240 · exit `t.sm` 150. **[CARB] `moderate-02` 240 names "toast" explicitly** — the most direct citation in the library.

**Dwell time** — separate from the transition, and more often wrong: **4–6s informational, 8–10s or persistent for actionable.** Bounded above by [NNG]'s 10s attention limit; an actionable toast must survive long enough to be read and acted on. Must pause on hover or focus. Dwell values are [CONV].

**Easing.** `e.enter` in, `e.exit` out. Slight overshoot is acceptable here — one of the few places a small bounce earns its keep, because a toast genuinely needs to catch peripheral vision.

**Stagger.** Multiple toasts: 50–80ms apart, stack capped at 3 [CONV]. The better answer is not to stack — queue.

**Fails when** it covers the primary action or the tab bar · an actionable toast auto-dismisses before it can be read (an Undo that vanishes in two seconds is worse than no Undo) · arriving toasts shift page content.

**Reduced motion.** Fade in place, `t.sm` 150, no travel. **Keep the toast** — suppressing it removes information, which [WCAG] 2.3.3's "essential to the information being conveyed" exception explicitly protects.

---

## 5 — Tab / segmented control switch

**Message.** *These are siblings, side by side; you moved along a row, you did not go deeper.*

**Animate** the indicator (`TRANSLATION_X`, `SCALE_X`) and the content (`OPACITY` plus a **small** shared-axis `TRANSLATION_X`, roughly 20–30px).
**Never animate** the tab labels. Never slide content the full viewport width — that reads as navigation and destroys the "peers" reading. Never animate the indicator's position or width as layout.

**Origin.** **Direction must match the tabs' spatial relationship.** Moving to a right-hand tab: indicator right, incoming content from the right. The sign being backwards is subtly nauseating in a way users cannot articulate.

**Timing.** Indicator and content both `t.sm` 150 — **matched, and deliberately so.** This is the one archetype where law 1 does not apply: a tab switch is a *cross-fade between peers on one clock*, not an enter/exit pair, and stepping the outgoing panel down would split one event into two. Note this in the spec so a reviewer does not read it as the symmetric-timing red flag. A wide indicator travel may step to `t.md` 240, but tabs are very high frequency and [ATL] caps this class under 150ms.

**Easing.** `e.move` for the indicator — this is a move, not an entrance, so a symmetric curve is correct. Content: near-linear cross-fade.

**Stagger.** None. If the incoming panel is a list, archetype 6 applies **on first visit only**, never on every switch.

**Fails when** content slides the full width · the indicator and content run on different durations, producing two events · the list-entrance stagger re-runs on every switch — the most common way tabs become exhausting.

**Reduced motion.** The indicator may still move — it is small, localized, and informational. Content: cross-fade with no travel.

---

## 6 — List / grid entrance reveal

**Message.** *This is the shape and volume of what arrived.* Genuinely useful once; actively hostile when repeated.

**Animate** `OPACITY` + a small `TRANSLATION_Y` (8–16px).
**Never animate** scale (popcorn effect at volume), rotation, or blur. Never reveal on scroll for long or paginated lists.

**Origin.** Items rise slightly in reading order — top to bottom, left to right within a row, mirrored under RTL. Small travel only: it signals *arriving* without implying the items came from somewhere.

**Timing.** Per item `t.sm` 150. Stagger by the formula in [motion-system.md §4](motion-system.md#4-stagger) — `clamp((500 − t_item) / (k − 1), 20, 60)` where `k = min(n, 8)` — applied to the **first 8 items only**; the remainder arrives together. Total capped at 500ms. The 20ms floor is [CARB]'s published table-row value; the total cap is [CARB]'s and is bounded by [NNG]'s 1s flow-of-thought limit. Stagger values beyond the floor are [CONV].

**Easing.** `e.enter`.

**Fails when** the reveal re-runs on every navigation back to the list. **Run it once, on first population — never on cache hits, back-navigation, or tab switches.** Also: uncapped stagger on long lists (40 rows at 40ms is a 1.6s wait to see the bottom, well past [NNG]'s threshold, and the user has already tried to scroll) · staggering items that were already visible.

**Reduced motion.** Single fade of the whole list, `t.sm` 150, no stagger. Or nothing at all — this pattern is decorative and is the safest thing here to switch off.

---

## 7 — Card expand into detail (shared element / container transform)

**Message.** *This detail view **is** that card — the same object, larger.* It preserves identity across a navigation, which is why it is worth the cost.

**Animate** `TRANSLATION` + `SCALE` on one container, corner radius, and a cross-fade between card content and detail content.
**Never animate** the card and the detail as two objects. The entire point is that there is **one**. Surrounding cards fade or hold; they do not move independently.

**Origin.** **From the tapped card's exact bounds to the detail's exact bounds.** Not screen center, not the tap point — the element. **If the origin bounds are unknown (deep link, restored state), do not fake it — fall back to archetype 8.** A container transform from the wrong origin asserts a false identity and is worse than a plain transition.

**Timing.** Enter `t.lg` 300, stepping to `t.xl` 400 when travel and scale delta are large · exit one token down. The longest justified transition in the library, and it earns it: [CARB] `slow-01` 400 "large expansion" is the direct match; [M1] 300ms mobile with a >400ms ceiling; [ATL] transitions top out at 400.

**Easing.** `e.expressive` — this curve exists for large, choreographed transitions.

**Stagger.** The container does not stagger. Detail content may fade in ~50ms behind the container settling, no more [CONV].

**Fails when** content cross-fades on a different curve than the container moves, so text visibly detaches and slides across the surface · there is no fallback when origin bounds are unavailable · the destination layout differs so much that the "same object" claim is not credible, at which point you are paying 400ms for a lie.

**Reduced motion.** Cross-fade between the two screens, `t.md` 240. The identity claim is lost; accept it. **Do not attempt a reduced-scale version** — partial motion of a large surface is precisely the vestibular trigger [MDN] warns about.

---

## 8 — Page / route transition

**Message.** *Where you are relative to where you were.* Forward goes deeper; back returns.

**Animate** `TRANSLATION_X` + `OPACITY`.
**Never animate** persistent chrome — nav bars, tab bars, headers. **What stays still is what makes the transition readable.** Never scale whole pages. Never move both pages at full travel (parallax the outgoing at ~30%, or hold it).

**Origin.** **Forward: incoming from the right, outgoing exits left (LTR). Back: exactly reversed.** Non-negotiable, and mirrored under RTL. **Peer-level navigation — bottom tabs — cross-fades with no direction**, because sliding between tab roots implies a hierarchy that does not exist.

**Timing.** `t.lg` 300 mobile · `t.sm` 150 desktop · exit one token down. [M1] gives this directly: 300ms mobile, 225 entering, 195 leaving, and "desktop animations should last 150ms to 200ms" — which is two steps down this scale, not one. A very wide desktop panel may hold at `t.md` 240; say so in the spec. Tablet steps up, wearable steps down.

**Easing.** `e.enter` in, `e.exit` out. **If back is gesture-driven, `e.spring` with velocity continuity** — an interactive back-swipe that snaps to a fixed curve on release feels broken in a way users notice immediately.

**Stagger.** None. The page is one object.

**Fails when** back uses the same direction as forward — this destroys the spatial model and is surprisingly common · the nav bar animates with the content, leaving no fixed reference so the whole screen appears to slosh · the transition outlasts the data fetch, so the user arrives at a spinner · RTL is not mirrored.

**Reduced motion.** Cross-fade, `t.md` 240, no travel. Directionality is lost — compensate with breadcrumbs or a visible back affordance, since that spatial information was doing real work.

---

## 9 — FAB → surface transform

**Message.** *This surface came from this button.* A specialization of archetype 7 with a much larger scale delta and a much more asymmetric shape change.

**Animate** `TRANSLATION` + `SCALE`, corner radius (full-round → surface radius), background color, and a cross-fade from icon to content.
**Never animate** the icon and the surface as separate entities. The icon fades out *early* — within roughly the first third — while the container continues expanding.

**Origin.** The FAB's exact bounds. Its corner is the anchor; the surface grows away from it.

**Timing.** Enter `t.xl` 400 · exit `t.lg` 300. The scale delta here is larger than a card expand (a 56px circle to a full sheet), so sit at the top of the range per [M1]'s distance principle. [CARB] `slow-01` 400.

**Easing.** `e.expressive`. **Corner radius must animate on the same curve as scale**, or the shape visibly lags the size and the object appears to be made of two materials.

**Stagger.** Icon fades out over the first ~30%; surface content fades in over the last ~50%. The deliberate gap in the middle — where the container is neither one thing nor the other — is what sells the transform [CONV].

**Fails when** corner radius snaps instead of animating · the icon persists into the expanded surface · the reverse transition returns to the wrong position because the FAB moved or was hidden. Always re-resolve the target bounds on exit.

**Reduced motion.** Cross-fade to the surface, `t.md` 240. Same reasoning as archetype 7.

---

## 10 — Skeleton → content swap

**Message.** *This is loading, here is its shape, it is not broken.* [NNG] finds skeletons prevent abandonment and let users build a mental model of the page structure incrementally.

**Animate** an `OPACITY` cross-fade from skeleton to content. Optionally a slow shimmer *while waiting*.
**Never animate** layout. **The skeleton's dimensions must match the real content's dimensions.** If content reflows on arrival, the skeleton actively misled the user and is worse than a spinner. Never swap with translate or scale.

**When to use it.** [NNG] is specific: **2–10s full-page loads.** Under 1s they are "unnecessary and may annoy users" — show nothing. Over 10s, use a determinate progress bar. Single components generally want a spinner instead.

**Timing.** Swap `t.sm` 150, stepping to `t.md` 240 for a full page. Shimmer loop **1000–1500ms** — deliberately slow, because a fast shimmer reads as urgency and creates anxiety during a wait [CONV]. **Minimum display ~300–500ms**: if data returns in 80ms, do not flash a skeleton — one frame of skeleton is a flicker that reads as a rendering bug [CONV].

**Easing.** Linear cross-fade. Shimmer eased and looped.

**Stagger.** Swap each section as its data lands. Never stagger artificially — that fakes progress you do not have.

**Fails when** skeleton dimensions do not match content, causing a layout jump on swap — the defining failure of this pattern · it flashes on fast loads · the shimmer is over-animated ([NNG] explicitly warns that pulsating gradients can be "distracting, annoying, or even create accessibility problems") · the skeleton is frame-only (header and footer with an empty middle), which conveys no layout information.

**Reduced motion.** No shimmer — a looping animation is exactly what these users opted out of. Static blocks, instant or ~100ms swap. **Also expose a text status ("Loading…")** — the visual skeleton conveys nothing to assistive technology.

---

## 11 — Accordion / expand-collapse

**Message.** *More content is here now; everything else kept its place.*

**Animate** height (measured-height transform, `clip-path`, or counter-scaled `scaleY`), the chevron rotation, and content `OPACITY` fading in slightly behind.
**Never animate** the panel's width, `margin`, or `padding`. Do not fade content out on collapse — collapse is quicker and content can clip.

**Origin.** Expands downward from the header. **The header stays fixed** — it is the anchor. If the expanded panel would fall below the fold, scroll it into view *after* the expansion, not during.

**Timing.** Expand `t.md` 240 · collapse `t.sm` 150 — and **[CARB] literally provides this token pair for this pattern**: `moderate-01` 150 ("small expansion") and `moderate-02` 240 ("expansion"). Drop to `t.sm` for a two-line panel. **Cap at `t.xl` 400 regardless of height** — past that the user has read the first line and is waiting on an animation.

**Easing.** `e.move`, productive rather than expressive — accordions are utilitarian and high-frequency. **The chevron rotates on the same duration and curve as the panel**, or the two read as unrelated events.

**Stagger.** None within a panel. In a single-open accordion, overlap the close and the open — do not sequence, or the total becomes 400ms of shuffling.

**Fails when** `max-height` is set to an arbitrary large value, which makes the visible speed depend on actual content height — short panels snap, long ones crawl, and the easing curve is effectively destroyed. Measure the real height. Also: page scroll jumping because content above the viewport expanded · the chevron on a different clock.

**Reduced motion.** Instant expand/collapse, or a ~100ms content fade with no height animation. The height change is the vestibular-relevant part, since it moves everything below it.

---

## 12 — Button press feedback

**Message.** *Received.* The highest-frequency motion in any product, and therefore the one with the tightest budget.

**Animate** `SCALE_XY` 0.96–0.98 and/or background opacity or color.
**Never animate** position, width, corner radius, or the label independently. Never scale below ~0.95 — deep-squish buttons read as toys, and on small controls the touch target visibly shrinks under the finger.

**Origin.** In place, from center. **If there is a ripple, its origin is the touch point** — that is the entire informational content of a ripple.

**Timing.** **Press-down `t.tap` 70 · release `t.xs` 110.** [CARB] `fast-01` 70 names "button and toggle" explicitly — the most precise citation available. [NNG]'s 0.1s threshold is the hard ceiling: **press feedback must land inside 100ms or it is not feedback, it is a delayed reaction.**

**This is the documented inversion of law 1** — press-down is *faster* than release. Press-down is not an entrance; it is an acknowledgment, and it must feel connected to the finger. The release can relax.

**Easing.** Down: near-linear — at 70ms the curve is imperceptible and speed is all that matters. Up: `e.enter`. Slight overshoot on release only, never on press.

**Fails when** feedback waits for the network response — it must be immediate and optimistic, decoupled entirely from the action's result · press-down is slow enough that a fast tap never completes it, showing a strange partial state · `:hover` motion fires on touch devices, leaving buttons stuck in a hover state after the tap.

**Reduced motion.** **Keep it.** A 0.97 scale over 70ms is not a vestibular trigger, and removing it removes genuine interaction feedback. Substitute opacity or color if preferred. This is the clearest case in the library where [WCAG] 2.3.3's "essential to the functionality" exception applies.

---

## 13 — Pull-to-refresh

**Message.** *You are in control of this; here is the threshold; it is now working.* Uniquely, the first phase is not an animation at all.

**Animate** the indicator's `TRANSLATION_Y` and `OPACITY` **tracking the finger 1:1** during the pull; rotation during refresh; travel + opacity on release.
**Never animate** the indicator on a fixed timeline during the pull. **Phase 1 is a direct-manipulation mapping, not an animation** — position is a function of scroll offset, not of time. Never hide the list content.

**Origin.** Down from the top edge, returning up.

**Timing.** Three phases: **pull** — gesture-driven, no duration, with rubber-band resistance past the threshold (60–80px, [CONV]) · **release snap** `t.md` 240 · **dismiss** `t.md` 240, with a **minimum visible refresh of ~500ms** [CONV] so the spinner does not flash and leave the user unsure whether anything happened.

**Easing.** Release snap: `e.spring` — the gesture had velocity and discarding it feels wrong. Dismiss: `e.exit`. Spinner rotation: `e.linear`, always.

**Stagger.** Genuinely new items may use archetype 6. Never the whole list.

**Fails when** the indicator does not track the finger, making the pull feel laggy · there is no threshold feedback, so users cannot tell when release will trigger the refresh (use haptics or a visual state change) · the refresh completes so fast the indicator flashes · content jumps when new items are prepended — anchor the scroll position.

**Reduced motion.** **Keep the pull tracking** — it is direct manipulation, and removing it removes the interaction itself. Replace the spinner rotation with a static indicator plus text status. Swap new-item entrance for an instant swap.

---

## 14 — Onboarding / hero reveal

**Message.** *This is what matters here, in this order.* **The only archetype where a budget above `t.xl` is defensible** — because frequency is 1.

**Animate** `OPACITY`, `TRANSLATION_Y` (16–40px, larger than a list reveal), `SCALE` on hero imagery. Deliberate sequencing.
**Never animate** anything the user needs in order to skip. **The skip control must be present and interactive from the first frame**, never faded in last. Never block interaction during the reveal.

**Origin.** Upward and forward, in reading order: headline, supporting text, imagery, CTA. The CTA arrives last because it is the resting point of the sequence — but it must be *tappable* before it is fully opaque.

**Timing.** Per element `t.lg` 300 – `t.xl` 400 · stagger 80–150ms · **total sequence ≤ 1200ms** [CONV]. This is where [M3]'s `long` tokens and [CARB] `slow-01` belong. [M1]'s ">400ms may feel too slow" warning is about *transitions*, not first-run reveals — a different context, worth stating rather than appearing to contradict a cited spec.

**Easing.** `e.expressive`. This is the one moment where expressive is the point.

**Stagger.** 80–150ms — noticeably longer than a list reveal, because here the sequence *is* the content [CONV].

**Fails when** it runs on every launch instead of first launch only — the worst failure in the library, because it converts a delightful moment into a daily tax · the skip control is unavailable until the sequence completes · this generosity is applied to any non-first-run screen · input is blocked during the sequence.

**Reduced motion.** Cross-fade the whole composition in `t.md` 240, no stagger, no travel. The sequencing is lost, and that is acceptable — it was always fashion, honestly labelled.

---

## 15 — Number counter / data-viz update

**Message.** *This value changed, and here is the direction and magnitude of the change.* Unusual in this library: the motion carries **actual information**, not affordance.

**Animate** numeric interpolation, bar `SCALE_Y`, line-path trim, arc sweep.
**Never animate** axis labels, gridlines, or legends. **Never animate the axis scale and the data simultaneously** — if the y-axis rescales while bars grow, the visual change is uninterpretable and the animation has destroyed the information it existed to convey. Rescale first, then animate data.

**Origin.** Bars grow **from the axis baseline** — never from center, never from the top. Lines draw **left to right** (time direction). Counters count **from the previous value**, not from zero: counting from zero on an update falsely implies the value *was* zero.

**Timing.** Counter `t.xl` 400 – `t.2xl` 700 · chart entrance `t.xl` 400 · chart update `t.lg` 300. Longer than most UI transitions because the animation is conveying magnitude, and magnitude needs time to be read. **Bounded above by [NNG]'s 1s flow-of-thought limit — never exceed it**, or the user is waiting on a number they could have simply read.

**Easing.** `e.enter`. **Never spring, never overshoot.** A counter that overshoots to 1,047 before settling at 1,031 has displayed a number that is not true. This is a correctness issue, not a taste issue.

**Stagger.** Series: 30–60ms in data order, total capped at ~600ms [CONV].

**Fails when** overshoot displays false values · a counter counts from zero on an update · axis and data animate together · a live dashboard animates on every poll, so the chart never sits still long enough to read · there is no static fallback — **always expose the final value as text immediately**, regardless of the animation.

**Reduced motion.** **Snap to the final value.** No counting, no drawing. The value is the information; the animation was only ever emphasis. The cleanest substitution in the library, because nothing is lost.

---

## 16 — Loading spinner / progress

**Message.** *Not frozen; here is how long.* Determinate and indeterminate are different tools with different thresholds, and conflating them is the core mistake.

**Animate** rotation (indeterminate), `SCALE_X` or path trim (determinate), opacity on appear and disappear.
**Never animate** the surrounding layout — reserve the space. **Never use a determinate-looking bar for an indeterminate wait.** A progress bar sitting at 90% is a lie the user will remember.

**Which one, from [NNG]:**

| Wait | Indicator |
|---|---|
| < 1s | Nothing — "animated feedback becomes distracting" |
| 1–10s | Looped / indeterminate |
| ≥ 10s | Percent-done |
| 2–10s, full page | Prefer a skeleton (archetype 10) |

**Timing.** Rotation period **800–1200ms per revolution** [CONV] — below ~600ms it reads as frantic and raises anxiety; above ~1500ms it reads as stalled. **Appear delay 300–500ms**: never show a spinner instantly, because most requests resolve faster and a two-frame flash looks like a bug. **Disappear `t.xs` 110** ([CARB] `fast-02` names "fade"). **Minimum visible ~500ms** once shown, to prevent flicker if the response lands right after the delay elapsed [CONV].

**Easing.** Rotation: **`e.linear`, always.** An eased spinner appears to stutter each cycle, which reads as the system hitching. Determinate progress: linear or `e.enter` per increment; **never animate backwards.**

**Stagger.** One indicator per region, or one for the whole page — never both, which reads as multiple independent failures.

**Fails when** the spinner appears instantly on fast responses · a fake progress bar stalls near completion · rotation is eased · an indeterminate spinner covers a wait over 10s, where [NNG] is explicit that users need a percent-done indicator · there is no timeout or error path — a spinner that spins forever is the worst possible failure state, because it is indistinguishable from working.

**Reduced motion.** The hardest case here, and it deserves an honest answer. A rotating spinner is continuous motion, which these users opted out of — but "the system is working" is essential information, and [WCAG] 2.3.3 exempts animation essential to the information conveyed. **Replace, do not remove:** a pulsing opacity fade (no movement), a text status ("Uploading 3 of 12"), or a determinate bar advancing in discrete steps. Text is the most robust replacement because it also serves screen readers.

---

## 17 — Ambient / material loop

**Message.** *This surface is made of something.* Chrome bezels, liquid-glass edges, conic border sweeps, iridescent gradients, aurora backgrounds, slow highlight travel. Alone in this library it communicates neither state nor causality — it communicates **material**. It has no trigger, no beginning, and no end.

**Animate** whatever expresses the material: rotation of a gradient sweep, travel of a highlight, a slow hue or opacity drift.
**Never animate the object's silhouette.** A chrome key does not tumble — its *reflection* moves while the key holds still. Rotating the node itself throws the shadow, the glyph and the outline around with it, and the illusion dies instantly. Rotate the material inside a clipped mask shaped like the object.

**Material coherence — the rule this archetype exists for.** Every layer belonging to the same material moves **together, on one clock, in one direction**. Specular banding, colour fringing, chromatic accents, iridescent dots, rim highlights — if the designer drew it as part of the surface treatment, it travels with the surface treatment.

**Get coherence by construction, not by discipline.** Where the layers can be grouped, **wrap them in one parent and rotate the parent** — one track, one node, and the layers physically cannot drift apart. Writing a matching track onto each layer is the fallback, and it is fragile: two tracks are two chances to get the sign, the magnitude, or the duration wrong.

**When you must write per-layer tracks, they must be identical** — same field, same sign, same magnitude, same duration, same easing. There is a specific failure here that looks like success: animating the forgotten layer at last, but with the opposite sign, so the metal turns one way and the colour turns the other. The eye locks onto the colour, so the whole key reads as running backwards even though the chrome is correct. **Fixing a missing layer and getting its direction wrong is worse than leaving it out**, because now it looks deliberate.

**Sign convention.** In the Figma Plugin API, positive `ROTATION` is **counter-clockwise** and negative is **clockwise**, and motion rotation is not normalised — so a full clockwise turn is exactly `-360`, on top of the resting transform. **When the direction is not specified, use clockwise, and say which you used** — the request "rotate the border" carries no direction, and a stated default is one word to flip. Never let two layers of one material end up with different signs by accident.

Leaving the colour layer static while the metal spins is the signature failure here, and it is seductive because it has a plausible defence: *"those are fixed light sources; the metal passes underneath."* That model is real in physics and almost always wrong in a design file, because the accents were drawn as part of the bezel, not as a lamp in the room. **If you are going to hold a layer still while its neighbours move, say so explicitly and check that it reads as a light source rather than as a bug.** It usually reads as a bug — and it is trivially measurable: sample the colourful pixels across the loop and see whether their centroid travels.

**Timing.** **One cycle every 4–8 seconds.** [CONV] — no vendor publishes this. The derivation is the boundary against the loading vocabulary: [NNG] puts indeterminate indicators at 1–10s, archetype 16 puts spinner rotation near 1s, and archetype 10's shimmer sits at 1000–1500ms and is *already* described as deliberately slow so it does not read as urgency. **A material loop signals nothing at all, so it must sit further below the attention threshold than any of them.** Under roughly 3s per cycle it reads as *working*, and the user starts waiting for something to finish.

Sit at 5s unless the surface is unusually small or large, and **extend the frame's timeline to match the period** — a 5s rotation on a 2s timeline does not loop, it jumps.

**Easing.** `e.linear`, always, no exceptions. The loop must close: one full turn over exactly the timeline duration, so the end state equals the start state.

**Distribute the information evenly.** A conic gradient whose stops are crammed into the first 40% of the sweep will *look* like it surges and stalls even though the node rotates perfectly linearly — the eye reads change, not angle. Spread the stops, or accept the pulse as a deliberate choice and say which.

**Stagger.** None. One material, one clock.

**Fails when** the cycle is fast enough to read as loading · colour or highlight layers sit on a different clock from the material, or on no clock at all · **two layers of one material rotate in opposite directions** · the silhouette rotates instead of the surface · the seam shows because the period and the timeline disagree · it runs inside a high-frequency control.

**Check the direction before shipping, do not assume it.** It is measurable in seconds: track one distinctive feature — the darkest band, the most saturated pixel — around the ring across the loop and read the sign. Doing this on both the material and its colour layer catches every version of this failure at once.

**That last one deserves naming.** An ambient loop on a stepper, a submit button, or a nav item is decoration bolted to something used constantly — lovely in a shot, a permanent tax in the product. Keep material loops on surfaces the user looks *at* (hero cards, empty states, marketing) rather than controls they look *through*. **Shipping the shot and shipping the product are different decisions; make both, and say which one this is.**

**Reduced motion.** `t.none`. Remove it entirely — the static material still shows what the surface is made of, and nothing is lost. The cleanest deletion in the library.

---

## 18 — Emission / dispensing

**Message.** *A mechanism is putting this out.* A receipt printing, a ticket or boarding pass dispensing, a card ejecting, a drawer sliding open, a message leaving. The subject is not the object — it is **the machine that produced it**, and the object is the evidence.

**Animate** `TRANSLATION` on the emitted object, clipped by a fixed aperture. Plus a settle after the drive stops.
**Never animate** the aperture, the machine, or anything around the slot. The housing's stillness is what makes it read as a housing.

### Emission is not a reveal — this is the whole archetype

There are two ways to make something appear out of a slot, and they look completely different:

| | **Reveal** (a mask grows) | **Emission** (the object travels) |
|---|---|---|
| What moves | The clip. The object is static | The object, through a fixed clip |
| Reads as | A curtain opening | A machine pushing |
| Momentum | None. Nothing is moving, so nothing can settle | Real. The free end can overshoot, sway, and follow through |
| Cost in a design tool | Cheap — resize a clipped frame | One translate track inside a clipping parent |

**The test, and it is measurable in one line: does a printed feature travel?** Pick a word, a line, a barcode. If it sits at the same distance from the slot in every frame while the object gets longer, it is a mask, whatever it was called. In real emission the first thing out ends up furthest from the slot, and it keeps moving as more feeds through.

**A reveal cannot carry a settle**, which is usually the tell that sends you back here: there is no way to add the ending you want, because nothing was ever in motion.

**Beware the easiest node operation.** A mask reveal wins by default in Figma because growing a clipped frame is the simplest thing to build — not because it is the right motion. **Do not let the cheapest operation choose the choreography.** When you notice you picked an approach because it was easy to author, say so and check it against what the moment is supposed to communicate.

### Timing and the settle

Three phases, and the last two are what people remember:

| Phase | Timing | Easing |
|---|---|---|
| **Drive** — the mechanism feeds | 400–700ms, scaled by the length emitted | **`e.linear`.** One of the few places linear is correct for travel: motors run at constant speed, and easing the drive makes the machine look hesitant |
| **Overshoot** — the free end carries past | a few percent of the travel | continues the drive |
| **Settle** — momentum dissipates | 300–600ms | `e.spring`, bounce 0.15–0.3 |

**Follow-through is the point, not a garnish.** An object with mass does not stop the instant its motor does. Paper flexes and sways; a plastic card ticks once and stops; a heavy drawer thumps. **Match the settle to the material** — amplitude scaling with both the length emitted and how floppy the thing is. This is the one archetype where an overshoot needs no justification, because it *is* the physics.

Sway is usually cheapest as a small `ROTATION` on the emitted object after the drive ends — a degree or two, spring-settled. Note that Figma rotates around a node's visual centre by default, so for a long receipt either give it a wrapper pivoting at the slot or keep the angle small and let the free end's few pixels of lateral travel do the work.

**Do not leave dead time at the end.** A drive that finishes at 1.4s in a 2.4s timeline leaves a full second of nothing, which reads as the animation having broken. Either fill it with the settle or shorten the timeline.

**Stagger.** None on the object. If content prints progressively, that is a *second* motion layered on the emission and it must run on the paper's own coordinates so it travels with it.

**Fails when** it is a mask reveal wearing an emission's name · it stops dead with no follow-through · the emitted content is revealed in place rather than travelling · the machine or aperture moves · dead time after the drive · the settle bounces so hard the paper reads as rubber.

**Reduced motion.** Cut the settle, shorten the drive, or cross-fade the final state in. The mechanism story is lost; that is acceptable, because it was always flourish rather than information.

---

## Shot motion is a different brief

Fifteen of the archetypes above are written for product UI, where restraint is the whole discipline. **A portfolio shot inverts the brief**, and this skill will otherwise talk you into the safe answer:

| | Product UI | A shot |
|---|---|---|
| Seen | Hundreds of times | Once, while scrolling |
| Goal | Disappear | Be remembered |
| Motion's job | Explain state and causality | **Be the content** |
| Restraint | The point | A liability |

So when the brief is a shot — "make something creative for this frame", a Dribbble piece, a reel — **spend the budget on mechanism and craft**: the emission rather than the reveal, the settle rather than the stop, the material rather than the fade. Longer durations, more choreography, and delight are all in scope.

Two obligations that do not relax:

1. **Say which one you built.** Shot motion that ships into a product unlabelled becomes someone's daily tax. The `Purpose` line in the spec should name it: this is fashion, deliberately, and here is where it belongs.
2. **The physics still has to be right.** A shot is judged by designers, who will forgive a long duration and never forgive an object that stops dead or a material torn into two clocks.

---

## Related

- [../SKILL.md](../SKILL.md) — the pipeline
- [motion-system.md](motion-system.md) — the tokens used throughout
- [benchmark.md](benchmark.md) — when a live reference may override these defaults
- [review.md](review.md) — the failure modes above, as a scored rubric
