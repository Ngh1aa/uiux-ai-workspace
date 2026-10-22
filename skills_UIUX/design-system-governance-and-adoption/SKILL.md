---
name: design-system-governance-and-adoption
description: Govern component/token evolution, contribution, deprecation, documentation and adoption so the system stays coherent as teams and AI generate UI faster. Use for mature or multi-project design systems.
---

# Design System Governance & Adoption

## Goal

Keep one system trustworthy enough that teams choose it over building their own, while it changes fast enough to meet their needs. Governance is a service with a decision process, not a gatekeeping committee: every request gets a fast, predictable answer (use existing, extend, compose locally, or add to the system), and every change ships with a version, a changelog and a migration path. Health is measured by adoption, exception rate and accessibility, never by component count.

## When not to use

- Building or extending tokens and component contracts themselves: use `design-system-and-components`.
- Implementing components in code with stories and tests: use `component-driven-development`.
- Detecting visual drift with screenshot baselines: use `visual-regression-and-design-drift`.
- Mobile token and handoff specifics: use `mobile-design-system-and-handoff`.
- A single product with one team and no consumers yet: use `design-system-and-components`; governance overhead is premature.

## Prerequisites

- Inventory of consuming products, their framework and their current package version.
- Current owners (named people or a team) for design assets, code packages and docs.
- Release channel: package registry, Figma library publishing, docs site.

## Decisions

**New component vs variant vs local composition**

| Situation | Decision |
|---|---|
| Need is met by an existing component with props/tokens | Use existing; fix docs if the team missed it |
| Same purpose and anatomy, different visual or density | Variant or token change, not a new component |
| Same purpose, needs a new behavior or slot | Extend the component contract (minor version) |
| Unique to one product, composed from system parts | Local composition, documented as a product pattern |
| Different purpose, needed by 2 or more products, or one product plus a clear roadmap need | Candidate for a new system component |
| Needed once, novel interaction, unvalidated | Local experiment, with a review date to promote or delete |

Run a gap analysis before any new component: list the nearest existing components and why each fails the need.

**Contribution model**
- Name the model explicitly: centralized (core team builds), federated (product teams build to system standards), or hybrid. Hybrid is the common default for multi-product systems: core owns foundations and high-reuse components, products contribute through review.
- Contribution path with stated service levels the team can actually keep: request triage, design review, accessibility review, code review, docs, release. State a response time for triage so teams do not fork while waiting.

**Maturity and status**
- Every component carries a status (for example: experimental, beta, stable, deprecated, removed) shown in both the design library and the docs. Stable requires: documented usage, all states specified, keyboard and screen reader behavior tested, WCAG 2.2 AA checks passed, visual regression baseline, at least one production consumer.

**Versioning (Semantic Versioning 2.0.0)**
- MAJOR: removed or renamed component, prop, token or slot; changed default behavior; token value change that alters meaning (for example `color-danger` changing hue family). MINOR: new component, prop, variant or token, backwards compatible. PATCH: bug and accessibility fixes that do not change the API.
- Treat design library changes the same way: renaming a Figma component or variant property breaks consumer instances and is a major change in effect.
- Tokens follow the same rules; publish in a tool-neutral format (W3C Design Tokens Community Group format; verify current spec status).

**Deprecation window**
- Deprecate in a minor release, remove in a later major release. Choose a fixed minimum window (for example two minor releases or one quarter, whichever is longer) and publish it as policy; consistency matters more than the exact length.
- Deprecation is discoverable in three places: runtime or lint warning in code, a deprecated label in the design library, and the docs page with the replacement and a codemod or migration guide where feasible.
- Do not remove while any tracked consumer still uses the API, unless the owner signed off on breaking them.

**Escape hatches**
- Allowed escape hatches are named (for example `className` passthrough, slot props, token overrides at the theme layer). Each override is detectable so it can be counted. Undocumented overrides of internal styles are not escape hatches; they are drift.

**AI-generated UI**
- Code assistants and generators must be pointed at the system (component manifest, token file, usage docs). Generated UI that imports raw values or rebuilds existing components counts as an exception in adoption metrics.

## Workflow

1. Define criteria for new component vs variant vs local composition using the decision table; publish it.
2. Assign ownership and contribution review: named owners per package and component, contribution model, triage service level.
3. Track component maturity, accessibility and test status in one status table visible to consumers.
4. Version/deprecate with migration guidance: semver per package, changelog, deprecation warnings, migration guide or codemod.
5. Audit duplicate patterns and token drift: search consuming repos for re-implementations, hardcoded values and detached library instances.
6. Measure adoption and exceptions per product and per component.
7. Document intentional escape hatches and review exceptions on a cadence; promote recurring ones into the system.
8. Report system health to stakeholders with the metrics below and a decision list.

## Anti-patterns

- "Button2", "NewCard" and "CardV3" coexisting with no deprecation of the old ones.
- Breaking prop rename shipped in a minor version because "it is just a rename".
- Figma library component renamed, silently breaking hundreds of instances in product files.
- Deprecated components that look and import exactly like stable ones, with no warning.
- Contribution queue with no response for weeks, so teams fork the package.
- Health dashboard that celebrates component count and Figma inserts.
- Every product overriding internal CSS classes because the system lacks one prop.
- Docs that show the ideal state only, with no do/don't, no accessibility notes and no code.

## Resources

- Need the metric definitions, deprecation timeline template, RFC template or worked example? Read [governance operations reference](references/governance-operations.md).

## Output

Deliver a governance package:

1. Decision table for new vs variant vs local, plus the gap-analysis template.
2. Ownership and contribution model with service levels.
3. Component status table with this header:

| Component | Status | Owner | Current version | A11y review (date, result) | Test coverage (unit/visual/a11y) | Consumers | Open exceptions | Deprecation and replacement |
|---|---|---|---|---|---|---|---|---|

4. Versioning and deprecation policy (semver rules, window, removal criteria).
5. Adoption and health report with the metrics in the reference file.

## Quality gate

Pass only if every statement is true:

- [ ] No duplicate component without gap analysis: every new component request has a recorded comparison to existing ones.
- [ ] Breaking changes have migration paths: every major release lists each break with a migration step or codemod.
- [ ] Breaking changes ship only in major versions; changelog entries are tagged major, minor or patch.
- [ ] Deprecated APIs are discoverable in code (warning or lint), in the design library and in the docs, each naming a replacement.
- [ ] Every component has a named owner and a visible status.
- [ ] System health includes usage and accessibility, not component count: report shows adoption, exceptions and a11y status per component.
- [ ] Escape hatches are named, documented and countable.

## Baseline / sources

- Semantic Versioning 2.0.0 specification.
- W3C Design Tokens Community Group format (verify current specification status).
- W3C WCAG 2.2 as the accessibility bar for stable status.
- Nathan Curtis (EightShapes) writing on design system team models and contribution.
- Brad Frost, Atomic Design, for layering of components and patterns.
- Public governance documentation of mature systems such as Shopify Polaris, IBM Carbon and Google Material (verify current process before citing specifics).
