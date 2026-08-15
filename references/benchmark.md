# Benchmarking Motion

Load this in Phase 2, before designing a pattern that already exists in the world — which is most of them.

Benchmarking is not copying. It is finding out what users already expect from this pattern, so that a deviation is a decision rather than an accident. Conventions carry expectation; departing from one costs comprehension, and that cost should be paid deliberately.

## 1. The governing rule

> **Observation tells you which band. The spec tells you which number in that band.**

A person watching a video at unknown capture rate, unknown playback rate, unknown frame rate cannot recover timing to better than roughly ±100ms. Writing "240ms" from such an observation is fabrication dressed as precision — and it is worse than writing nothing, because the next reader will treat it as measured.

So the phase has **two legs that do different jobs**:

| Leg | Source | Yields |
|---|---|---|
| **Observation** | A shipped app, a Mobbin flow, a Dribbble shot, a competitor | Structure: what moves, what stays still, direction, origin, simultaneity, continuity |
| **Documented spec** | Design-system token files, platform docs, open-source component source, published motion breakdowns | Numbers: exact durations and easing curves, citable |

Observation supplies the taste. Specs supply the authority. Inverting them produces fabricated precision; using only one produces either a generic result or an unjustifiable one.

**The line is the evidence, not the medium.** A source that publishes its own motion breakdown sits on the *documented* leg even though the subject is a shipped app — [60fps.design](#2a-60fpsdesign--the-sanctioned-live-source) returns trigger, start, movement, settle point and real code through its MCP, and numbers from there may be written down as numbers. What you got by watching still may not.

## 2. What you may and may not read

Verified by direct testing in August 2026. **Site behavior and Terms change — re-check before relying on a row, and treat the two prohibitions below as the durable part.** This is an access-and-terms question, not a capability question: some of these are technically reachable and still off-limits.

| Source | Verdict | Why |
|---|---|---|
| **60fps.design** | **Use it — via its official MCP** | The one purpose-built source for shipped motion that *invites* agents. See §2a |
| **Mobbin** | **Human-in-the-loop only** | Every content surface returns 403 to non-browser clients — including `robots.txt`. Its Terms prohibit automated access, and separately prohibit using AI/ML tools to create derivative works from its material. That second clause covers an agent that ingests flows and emits motion specs. It is not a gray area |
| **Dribbble** | **Search only** | Content pages return an empty body to any fetch — no title, no metadata, no asset URLs. Terms prohibit scraping and non-browser access to user content. You may search for shot URLs and surface links; you may not read, store, or cache |
| **Page Flows, Screensdesign** | Unusable | Login-gated, 403 to fetch. Genuine shipped-product flow videos — excellent for a human, invisible to an agent |
| **Codrops** (`tympanus.net/codrops`) | **Readable — highest value** | Free, public, server-rendered, hundreds of demos **with source code**. The only inspiration site where real durations and easing values can be read as text rather than eyeballed |
| **Material 3 tokens** | **Readable via the repo** | `m3.material.io` requires JavaScript and returns nothing. The token values are plain text in `material-components/material-web` at `tokens/versions/*/_md-sys-motion.scss` |
| **Material 1 spec** | Readable | `m1.material.io/motion/duration-easing.html` renders fully and still holds the classic 300 / 225 / 195 numbers and the platform modifiers |
| **IBM Carbon** | Readable | Full duration table and all six easing curves, with stated usage per token |
| **Atlassian** | Readable | Duration ranges, four named curves, explicit enter-vs-exit guidance |
| **Fluent 2** | **Readable via the repo** | The docs site is qualitative prose with no numbers; the values are in `microsoft/fluentui` at `packages/tokens/src/global/durations.ts` |
| **WinUI (Microsoft Learn)** | Readable | Three durations and both easing curves |
| **Apple HIG / SwiftUI docs** | Not fetchable | Requires JavaScript. **Do not cite Apple numbers that have not been verified directly** |
| **NN/g** | Readable | Perceptual thresholds, loading-indicator policy |
| **W3C WCAG, MDN** | Readable | Reduced-motion semantics and requirements |

**The pattern worth remembering: fetch the repos, not the docs sites.** Most vendor documentation is client-rendered and returns nothing, while the same values sit in plain text in the vendor's own open-source token package.

### 2a. 60fps.design — the sanctioned live source

The one purpose-built library of shipped motion that an agent may read, because **the publisher built an MCP server for exactly this** rather than trying to keep agents out.

- `robots.txt` is `User-agent: * / Allow: /`, with no AI-bot rules. Content pages render fully to a fetch.
- The library is organised the way this skill is: **by animation type** — bottom sheet, pull-to-refresh, stagger, parallax, shimmer, spring physics, morph, swipe, zoom — across hundreds of apps, rather than by screen.
- **Official MCP endpoint:** `https://mcp.60fps.design/mcp`, Bearer-authenticated with a **60fps PRO licence key**. In Claude Desktop: Settings → Connectors → Add custom connector.

The tools it exposes map almost exactly onto the Benchmark Card:

| Tool | Returns | Fills |
|---|---|---|
| `search_shots` | Natural-language search across the library | Finding the archetype's real-world examples |
| `get_shot` | Keyframes, filters, mood for one shot | `moves`, `properties`, `easing_character` |
| `get_motion_breakdown` | **Trigger state, start, movement, settle point, and rationale** | Almost the whole card — including `communicates`, which is the field humans skip |
| `get_motion_code` | Compile-checked SwiftUI for the motion | Real values, not estimates — the `documented` evidence level |
| `get_related_shots` | Variations on the same pattern | The 3+ cards §6 asks for before synthesising |

**`get_motion_breakdown` is the important one.** Trigger → start → movement → settle → rationale is the structure this skill's Benchmark Card was designed around, and getting it from the source removes the whole estimation problem: these are `documented`, not `estimated`, so **a millisecond value from here may be written down.**

**The boundaries, from their terms — respect them precisely:**

- **Query for the design in front of you. Do not pull the library.** "Bulk download or systematically copy the library, whether by hand or with a script" is prohibited, as is "rebuild, mirror, cache or re-host."
- **Do not use it to train, fine-tune, test, benchmark, or evaluate a machine learning model.** Their terms name this explicitly. Informing a design decision is the permitted use — "use 60fps for your own work, for the internal work of the business you work for, and to build your own products with" — and it is what the MCP exists for. Building a dataset is not.
- **Do not let it become a competing library.** They prohibit using their content "to build a standalone reference library." This is why [archetypes.md](archetypes.md) is derived from published design-system specifications and not from shots — keep it that way.
- **Link, cite, do not re-host.** A Benchmark Card stores the shot URL, never the video.

**It requires a PRO licence, so treat it as an accelerator rather than a dependency.** With it, BENCHMARK becomes a few structured queries. Without it, the archetype library and the open-source sources below still carry the phase — and the human-observation path in §3 still works.

### 2b. The sources that actually pay — open-source components

The best substitute for watching a shipped app is **reading a shipped component**. Open-source libraries that people already admire publish their real transition constants under permissive licences, as text, with no ToS problem at all. This is a strictly better benchmark than eyeballing a video, because the numbers are exact rather than estimated.

| Source | Where the numbers live | Licence |
|---|---|---|
| **Vaul** (drawer / bottom sheet) | `emilkowalski/vaul` → `src/constants.ts`. One tiny file: transition duration and easing, plus the velocity and close thresholds that make a drag feel right | MIT |
| **Sonner** (toast) | `emilkowalski/sonner` → `src/styles.css`. Grep `transition:`, `animation:`, `@keyframes` | MIT |
| **shadcn/ui** | `ui.shadcn.com/r/styles/new-york/<component>.json`, or the repo's registry `.tsx` files. Resolve the Tailwind classes: `duration-200` is 200ms, and an `animate-in` with no `duration-*` inherits **150ms / `ease`** | MIT |
| **Base UI** | `base-ui.com/react/handbook/animation` — readable, with concrete values and unusually good guidance on transitions over keyframes | MIT |
| **Motion** (the library) | Not the docs table — the shipped package. `motion-dom` → `dist/es/animation/generators/spring.mjs` for spring defaults, `.../utils/default-transitions.mjs` for the per-property defaults | MIT |
| **Material 3 tokens** | `material-components/material-web` → `tokens/versions/*/_md-sys-motion.scss`, or `material-foundation/material-tokens` → `json/motion.json` for parseable JSON | Apache-2.0 |
| **IBM Carbon** | `carbon-design-system/carbon` → `packages/motion/src/dtcg/motion.json`. The docs page lists token *names* only | Apache-2.0 |
| **Atlassian** | The motion page itself — exact curves paired with when to use them and a duration budget by interaction type | — |

Two cautions. **Check the licence before deriving anything but numbers** — at least one popular component library is AGPL-3.0, which is a different proposition for a public repo than MIT. And **extracting a factual timing value is a much weaker copyright question than copying source**; take the number, cite where it came from, and write your own implementation.

### 2c. Everything else in the shipped-app niche

Outside 60fps, the niche is closed. Page Flows, UI Movement, and UX Archive refuse non-browser clients; Screensdesign returns metadata only; the sites that *are* readable — Refero, Land-book, Lapa Ninja, recent.design — carry **static screenshots or marketing websites, not app motion**.

So the honest picture has three legs, in this order:

1. **60fps via its MCP** — sanctioned, structured, shipped iOS motion. Use it when it is available.
2. **Open-source component source** — exact numbers, permissive licences, no access question at all.
3. **Human observation** — for anything neither covers, including Android, web apps, and anything very recent. The designer watches; the agent interviews and records a Benchmark Card.

Leg 3 never becomes obsolete. A tool can tell you a sheet settles in 300ms; it cannot tell you the thing you noticed while watching.

## 3. Working with sources an agent cannot read

This is the path for Mobbin, for Android and web apps that 60fps does not cover, and for anything the designer has in front of them that no library has catalogued.

Mobbin in particular is off-limits to the agent entirely — 403 on every surface, and terms that prohibit AI-derived works. The workflow that is both possible and clean:

**The user watches. You interview. The card is the record.**

Ask short, structural questions — the ones a person can answer reliably from watching:

1. What moved, and what stayed completely still?
2. Which direction did it come from, and where did it appear to come *out of* — an edge, the thing they tapped, the middle of nothing?
3. Did the element persist through the change (same object, resized) or was it replaced?
4. How many separate things moved at once — one, two or three, or more?
5. Did it settle cleanly, wobble, or snap?
6. Did anything arrive one after another, or all together?
7. Roughly how long — a blink, a beat, or long enough to notice you were waiting?
8. What did that motion tell you that a static screenshot would not?

Question 8 is the one that matters. If the user cannot answer it, the reference is showing fashion, and it should be recorded as fashion.

## 4. Duration bands — the only honest vocabulary for observation

| Band | Range | Anchored to |
|---|---|---|
| `instant` | < 100ms | Below Nielsen's 0.1s instantaneity threshold. Carbon `fast-01` 70ms; Fluent `ultraFast` 50ms; WinUI 83ms |
| `quick` | 100–200ms | Carbon 110/150; Atlassian interactions 50–150ms; Fluent 150/200; Material 1 desktop 150–200ms |
| `standard` | 200–350ms | Material 1 mobile 300ms (enter 225 / exit 195); Carbon 240ms; Atlassian modal 250ms; M3 `medium1–3` |
| `deliberate` | 350–500ms | M3 `medium4`–`long2`; Carbon `slow-01` 400ms. Material 1's ">400ms may feel too slow" sits on this boundary |
| `slow` | 500–800ms | M3 `long3`–`extra-long2`; Carbon `slow-02` 700ms (background dimming only). Rarely correct for interactive UI |
| `showreel` | > 800ms | Not a shippable UI band. A reference landing here is portfolio work or a deliberate first-run moment |

Every recorded band carries **how you know**:

- `documented` — read from a spec, token file, or source. Cite it. **Only here may an exact millisecond value be written.**
- `frame-counted` — you had the file locally and counted. State the fps.
- `estimated` — you watched it. **Band only. No number. Ever.**
- `inferred` — you did not observe it; you assigned a band from convention. Name the convention.

## 5. The Benchmark Card

**The minimum viable card is eight fields** — `archetype`, `source_kind`, `moves`, `stays_put`, `spatial_origin`, `duration_band`, `duration_evidence`, `uncertainty`. Those are what the Motion Spec and the review rubric actually consume. Fill the rest when the reference is load-bearing enough to be worth the time; for a quick lookup, eight is enough and thirty-eight is procrastination.

```yaml
# Provenance
archetype:        bottom-sheet          # one of the 16, or "custom"
source_kind:      shipped               # shipped | portfolio | spec | live-observed
source_name:      "<app or system, with version if known>"
source_url:       ""                    # a link only — never a stored asset
observed_by:      human                 # human | agent-read
confidence:       medium                # high | medium | low

# Trigger and intent
trigger:          "tap Share in the toolbar"
communicates:     "a temporary layer over a task you have not left"

# Structure — high confidence, record as fact
moves:            [sheet, scrim]
stays_put:        [page-content, nav-bar, status-bar]      # required, must be non-empty
properties:       [translateY, opacity]
direction:        up
spatial_origin:   bottom-edge
continuity:       replaced              # persists (shared element) | replaced
simultaneous:     2                     # 1 | 2-3 | 4+

# Ordinal — bucketed, never numeric unless documented
duration_band:    standard
duration_evidence: estimated            # documented | frame-counted | estimated | inferred
exit_vs_enter:    exit-faster
easing_character: decelerate
stagger:          none                  # none | subtle | pronounced
overshoot:        slight                # none | slight | pronounced
gesture_driven:   true

# Judgment — label it as judgment
function:         "upward travel establishes it came from below and returns below"
fashion:          "slight overshoot — pleasant, not load-bearing"
frequency:        high
shippability:     safe                  # safe | needs-trimming | showreel-only
borrow:           "bottom origin, decelerate settle, faster dismissal"
reject:           "nothing"
uncertainty:      "could not tell whether the scrim fade is coupled to sheet travel"
```

**Rules that keep the card honest:**

1. `duration_evidence: estimated` **forbids any millisecond value anywhere in the card.** Enforce it — this is the entire point.
2. `uncertainty` is required, not optional. An `estimated` card with an empty `uncertainty` field is itself a smell; eyeballing always misses something.
3. `stays_put` must be non-empty. "Everything moves" means the observation was wrong or the reference is bad.
4. `source_url` is a link. Never an asset, never a cache, never an embed.
5. A `confidence: low` card may inform direction and structure. It may not drive a duration decision.

## 6. From cards to a decision

Never copy one card. Synthesize.

1. **Collect three or more** for the archetype where possible.
2. **Keep what all of them share.** That is the convention, and the convention carries user expectation.
3. **Note what one does differently.** That is either the brand's opportunity or that designer's mistake. Decide which, in writing.
4. **Take the numbers from the spec leg.** Cards give structure, direction, and character. Design systems give milliseconds. Let the observed band *select which documented token to use* — never let it become the value.

## 7. Portfolio motion is not shipped motion

Blunt version: **Dribbble is a portfolio site optimized for engagement in a scrolling feed. It is not a record of what works.**

| | Portfolio | Shipped |
|---|---|---|
| Judged by | Likes from other designers, while scrolling, muted, without context | Task completion by users who have seen it four hundred times |
| Seen | Once | Daily, for years |
| Optimal duration | Long enough to read as a loop in a feed | Short enough to disappear |
| Element count | Many — busy reads as effortful | Few — few is legible |
| Constraints | None. No real data, no error states, no slow network, no accessibility audit, no engineer | All of them |
| Failure cost | None | Support tickets |

These are not the same craft, and the portfolio version is not "the aspirational version" of the shipped one. It is a different artifact optimized against a different loss function.

**Rules that follow:**

1. **Never take a duration from portfolio work.** `duration_evidence` on such a card is `inferred` at best.
2. **Divide the observed element count by the frequency.** If a shot animates six things and the real pattern fires twenty times a session, animate two.
3. **A portfolio reference must earn its way in by naming what it communicates.** "It looks cool" means fashion — allowed, but labelled, budgeted, and confined to low-frequency moments where repetition will not grind it into irritation.
4. **When shipped and portfolio conflict, shipped wins.** Real apps have already run the experiment. Portfolio sites have run a popularity contest among designers.
5. **One portfolio card per benchmark set, maximum.** More than that and you have benchmarked a trend, not a pattern.
6. **Portfolio work is genuinely valuable for exactly one thing:** surfacing a spatial idea you had not considered — an unexpected origin, an unusual continuity, a novel shared element. Take the idea. Leave the timing, the element count, and the flourish.

## 8. When there is no reference

The common case, and it is fine. Go to [archetypes.md](archetypes.md) and use the documented default. Eighteen patterns, each with sourced durations, easing character, stagger guidance, failure modes, and a reduced-motion substitution.

The archetype default is the baseline a live benchmark must **beat** before it is allowed to override anything. A reference that merely differs from the default is not evidence that the default is wrong.

## Related

- [../SKILL.md](../SKILL.md) — the pipeline
- [archetypes.md](archetypes.md) — the offline library and the baseline
- [motion-system.md](motion-system.md) — the tokens an observed band selects from
- [motion-spec.md](motion-spec.md) — where benchmark findings land
