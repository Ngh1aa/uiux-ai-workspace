---
name: figma-professional-artifact
description: Build or audit a recruiter- and developer-inspectable Figma artifact for UI/UX/Product Design work. Use when the user explicitly asks for a professional Figma file, Figma portfolio proof, design-library quality, or Figma prototype/handoff craft. Covers file architecture, variables/tokens, auto layout, components/variants/states, responsive frames, prototype flows, annotations and cleanup without treating Figma polish as product validation.
---

# Figma Professional Artifact

## Goal

Turn a Figma file into inspectable design evidence rather than a collection of polished screenshots.

`project truth → file map → foundations → components → product states → responsive compositions → prototype flows → annotations/handoff → cleanup → review`

This skill proves **design-file craft and system thinking**. It does not replace a case study, direct-user validation, business outcomes or working-code evidence.

## 1. File architecture

Use clear top-level pages or sections appropriate to project scope. For a portfolio flagship, the preferred evidence map is:

1. `00 — Cover / Read Me`
2. `01 — Project Overview`
3. `02 — Research & Evidence`
4. `03 — Product / UX Strategy`
5. `04 — Information Architecture`
6. `05 — User Flows`
7. `06 — Wireframes / Exploration`
8. `07 — Foundations / Tokens`
9. `08 — Components / Variants`
10. `09 — Core Product Screens`
11. `10 — Responsive / Adaptive`
12. `11 — States / Edge Cases`
13. `12 — Prototype Flows`
14. `13 — Validation / Iteration`
15. `14 — Decisions / Trade-offs`
16. `15 — Measurement / Handoff`

Do not create empty pages just to imitate this list. Merge sections when project evidence is small; add domain-specific pages only when they improve inspectability.

## 2. Foundations and variables

Where the project justifies a reusable system:

- define color roles semantically rather than decorative swatches;
- define typography roles and text styles;
- define spacing/layout primitives or variables where they improve consistency;
- define radius, border, elevation and motion conventions where material;
- use variable modes/themes only when the product actually needs them;
- keep names predictable enough that another designer can navigate without oral explanation.

Do not manufacture an oversized design system for a small project.

## 3. Auto layout and responsive behavior

Representative production-intent frames should use Auto Layout or an equally inspectable layout model where appropriate.

Review:

- nested layout logic;
- fill / hug / fixed choices;
- min/max or wrapping behavior when relevant;
- component resizing;
- content expansion and long strings;
- desktop/tablet/mobile transformations;
- image/media crop behavior;
- navigation and dense-data adaptation.

A responsive claim is not proven by placing desktop and mobile screenshots side by side if components do not expose the underlying behavior.

## 4. Components, variants and properties

Create components for meaningful reuse, not for every layer.

For P0 interactive components, expose applicable:

- default;
- hover;
- focus;
- pressed/active;
- selected;
- disabled;
- loading;
- error;
- success.

Use component properties/variants so the reviewer can understand the behavior contract. Avoid duplicate components that differ only because a page was copied.

## 5. Product state coverage

A senior-quality flagship should show the states that materially change decisions or recovery:

- first-use / onboarding;
- empty;
- populated;
- loading/skeleton;
- validation error;
- system/server error;
- success/confirmation;
- permission or role restriction when relevant;
- destructive action confirmation;
- offline/retry or stale-data handling when relevant;
- partial/edge content;
- irreversible/high-consequence states for regulated or risk-sensitive domains.

State coverage follows product risk, not a universal checkbox count.

## 6. Prototype flows

Prototype only the journeys that demonstrate product reasoning.

Each flagship prototype flow should have:

- named start frame;
- clear task goal;
- critical branch or recovery path when material;
- meaningful transitions/microinteractions;
- a visible completion state;
- no dead-end click targets in the declared demo path.

Separate simulated behavior from real integrated behavior. A Figma prototype is interaction evidence, not production-system evidence.

## 7. Research, decisions and iteration evidence

Where evidence exists, connect frames to:

- research finding / evidence class;
- hypothesis;
- decision;
- rejected alternative;
- trade-off;
- iteration;
- remaining unknown.

Prefer short annotations next to the relevant artifact over long detached essays.

If research is planned but not completed, label it planned. Do not fabricate quotes, participants, task success or metrics.

## 8. Handoff and inspectability

For representative final screens/components, provide enough context for another designer or developer to understand:

- grid/layout behavior;
- token/style/component ownership;
- responsive rules;
- interaction/state behavior;
- content constraints;
- accessibility considerations;
- assets and source references where useful.

Use Dev Mode/Code Connect or equivalent only when they are actually configured; do not imply integration from visual similarity alone.

## 9. Cleanup gate

Before sharing:

- remove or archive obsolete explorations;
- remove detached copies that look canonical but are not;
- resolve obvious inconsistent component instances;
- remove accidental local styles/variables when a canonical owner exists;
- name key frames/components/flows;
- confirm links/start frames work;
- confirm no confidential material is exposed;
- confirm the reviewer can identify the canonical final path quickly.

## 10. Portfolio relationship

Treat the three artifacts differently:

- **Case study** explains why and what changed.
- **Figma** proves design-file/system craft and detailed UI decisions.
- **Working prototype** proves interaction/runtime behavior at higher fidelity.

For senior hiring, do not ask one artifact to impersonate the other two.

## Quality gate

PASS only when a reviewer can inspect the file and answer:

- what the product problem and key journey are;
- which frames are canonical;
- how the layout/system is structured;
- how components and states behave;
- how responsive behavior works;
- which decisions changed through evidence;
- what the prototype demonstrates;
- what remains unvalidated or simulated.

A visually polished but flat, duplicated or unexplained screen dump does not pass.
