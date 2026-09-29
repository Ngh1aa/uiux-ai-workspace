# Visual Signature Regression Contract

This contract protects recognizable visual and interaction identity when a task changes content, evidence, metadata, career positioning, accessibility copy, or other non-redesign concerns.

It is deliberately product-agnostic. A project does not need a portrait, marquee, hero animation, or any particular style. It only needs to identify the visual/interaction cues that are already part of the approved experience and must survive unrelated migrations.

## 1. When this contract applies

Apply this contract when a task changes an existing rendered UI and the task is **not explicitly authorized to redesign the affected signature surface**.

Typical triggering work:

- content/copy migrations;
- portfolio/case-study evidence upgrades;
- metadata or information-architecture changes;
- accessibility or semantic repairs;
- component refactors;
- runtime consolidation;
- framework migrations;
- design-system/token migrations;
- automated mass edits that can touch Home, hero, navigation, media or motion.

If the task explicitly redesigns the signature surface, the old invariant may change, but the decision, new owner and new acceptance evidence must be recorded.

## 2. Required project truth before editing

Before implementation, identify the representative surface and record only what actually exists:

- **Representative page/route** — the surface a user/recruiter is expected to recognize first.
- **Signature media** — important imagery, illustration, product object, art asset, video or other primary media; `N/A` when none exists.
- **Signature motion** — one-time reveal, spatial interaction, marquee, transition, parallax or other purposeful motion; `N/A` when none exists.
- **Signature composition** — the recognizable hierarchy/arrangement that gives the surface its role.
- **Page-role hierarchy** — what must remain visually primary, secondary and supporting.
- **Reduced-motion behavior** — what identity must remain when motion is disabled.
- **Canonical owners** — current DOM/component, style and behavior files/modules that actually render the signature.
- **Baseline evidence** — rendered evidence at representative viewport(s), or `UNKNOWN` if unavailable.

Do not invent signature requirements just to fill the contract. `N/A` is valid.

## 3. Source-owner consistency scan

Before a migration is allowed to change a signature surface, inspect for split or stale ownership:

- CSS selectors that no longer have matching DOM/component targets;
- JavaScript/event handlers that target missing elements;
- visual assets referenced by code but no longer rendered;
- duplicate/parallel Home or hero implementations;
- legacy layers silently overriding the current owner;
- content migrations that replace or delete structural wrappers needed by motion/media;
- reduced-motion rules that accidentally remove identity/content instead of only reducing motion.

A stale owner is a defect, not permission to ignore the visual behavior.

## 4. Compatibility rule

Unless the user/task explicitly authorizes redesign, identified signature invariants are compatibility requirements.

A content/evidence/metadata migration must not silently:

- remove signature media;
- remove the project’s primary visual cue;
- delete purposeful signature motion;
- replace an art-directed composition with a generic layout;
- add overlays/filters that materially soften or obscure the intended rendering;
- change page-role hierarchy so the representative surface no longer communicates the same role;
- leave behavior code with no rendered target;
- pass only because text, accessibility or build checks remain green.

## 5. Verification requirements

Verification must be proportional to the signature and must include rendered evidence, not only source assertions.

Minimum when the signature surface is affected:

1. **Baseline or declared invariant** recorded before editing.
2. **Post-change render** at representative desktop and mobile widths when responsive behavior exists.
3. **Media presence/integrity** check for required signature media.
4. **Behavior check** for required signature motion/interaction.
5. **Reduced-motion check** when motion exists: identity/hierarchy remains, continuous motion is reduced/stopped.
6. **Source-owner consistency** check after the edit: no missing targets or parallel accidental owners.
7. Existing accessibility/runtime/console checks continue to pass.

If baseline evidence is unavailable, do not claim pixel parity. Verify the declared invariants directly and record the limitation.

## 6. Promotion states

Use the narrowest truthful state:

- `PROJECT_FIX_VERIFIED` — the affected target project passes its signature contract and normal QA.
- `CROSS_PROJECT_REGRESSION_VERIFIED` — the Factory change also preserves representative golden projects.
- `FACTORY_FIX_VERIFIED` — Factory regressions, golden snapshots and current-head canaries all pass after the generic guardrail change.

A project-specific pass is not evidence that the Factory rule is safe for unrelated projects.

## 7. Failure handling

When a signature regression is found:

1. capture the rendered failure;
2. find the earliest owner that lost or overrode the signature;
3. repair the owner rather than layering a cosmetic patch when possible;
4. add a regression assertion for the class of failure;
5. rerun normal product QA;
6. if the failure exposed a Factory assumption, add the generic rule/test and run cross-project verification before promoting the Factory fix.

Do not weaken an assertion merely because the updated layout is different. First decide whether the difference was authorized.

## 8. Examples of generic invariants

These are examples, not mandatory patterns:

- a portfolio may preserve an art-directed hero media object + one signature motion cue;
- an ecommerce product page may preserve product imagery, variant-selection hierarchy and sticky purchase context;
- a B2B dashboard may have no decorative signature at all, but must preserve the information-density hierarchy and critical status surface;
- a museum/visual experience may preserve spatial discovery and motion as core identity;
- a static enterprise page may mark motion `N/A` and preserve only typography/media/composition.

The contract protects project truth; it does not force every project to look or behave alike.
