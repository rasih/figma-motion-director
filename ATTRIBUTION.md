# Attribution and sources

This skill stands on work worth naming.

## Architecture

The phase architecture — a router with distinct entry points, a mandatory intent phase before generation, recursive scoring against weighted criteria with explicit stopping criteria, a multi-perspective review panel, a gap-analysis quadrant, and a blunt anti-pitfall posture — is adapted from the **creative-director** skill by **Serge Shima**, licensed **CC BY 4.0**.

- Source: https://github.com/smixs/creative-director-skill

"Insight before ideas" became "intent before keyframes." The saturation rule — cap originality when a mechanic already appears across the canon — became "do not animate a design-system default and call it a signature."

## Craft

The frequency-tier gate, the delete-before-tuning fix order, and the interruptibility posture draw on **Emil Kowalski**'s writing and published animation standards.

- https://emilkowal.ski/ui/great-animations
- https://emilkowal.ski/ui/7-practical-animation-tips
- https://emilkowal.ski/ui/you-dont-need-animations
- https://animations.dev

Interaction-craft framing — spatial consistency, origin-aware motion, gesture continuity, commitment scaling with consequence — draws on **Rauno Freiberg**'s interaction-design notes and Apple's *Designing Fluid Interfaces* (WWDC 2018, session 803).

- https://rauno.me/craft/interaction-design

## Duration and easing values

Every value in the token scale is corroborated by at least two of:

- **Material Design 3** motion tokens — read from the `material-components/material-web` token package, since the documentation site is client-rendered
- **Material Design 1** — https://m1.material.io/motion/duration-easing.html
- **IBM Carbon** — https://carbondesignsystem.com/elements/motion/overview/
- **Atlassian Design System** — https://atlassian.design/foundations/motion
- **Microsoft Fluent 2** — duration tokens from the `microsoft/fluentui` token package
- **WinUI** — https://learn.microsoft.com/en-us/windows/apps/design/motion/timing-and-easing

## Perceptual thresholds and accessibility

- **Nielsen Norman Group** — response-time limits, animation duration guidance, progress-indicator and skeleton-screen thresholds
- **W3C WCAG 2.1** — SC 2.3.3 Animation from Interactions, 2.2.2 Pause Stop Hide, 2.3.1 Three Flashes
- **MDN** — `prefers-reduced-motion` semantics ("remove, reduce, **or replace**")
- **web.dev / Chrome** — the rendering pipeline and the per-frame budget

## Figma mechanics

Plugin API surface, easing enums, animatable fields, timeline behavior, `export_video` protocol, and `get_motion_context` response shape are Figma's, and are documented in the sibling skills this one delegates to:

- `figma-use-motion` — writing motion into Figma
- `figma-implement-motion` — taking Figma motion to code
- `figma-use` — Plugin API foundations

## A note on `[CONV]`

Values marked `[CONV]` in the references are **convention, not published specification**. They are widely observed across shipped products, but no vendor documents them. Own them as judgment; do not cite them as authority. The tag exists so the line between "sourced" and "defensible default" stays visible.

No Apple duration or spring values appear in this skill. Apple's motion documentation was not directly verifiable during authoring, and unverified vendor numbers do not belong in a reference.
