# A13 Cross-Project Dogfood — Nova vs Lumen vs CENNEXT

Status: `DOGFOOD COMPLETE / SYSTEM PATTERN CONFIRMED`

Branch: `a13-cross-project-dogfood` (stacked on `a13-nova-real-project-dogfood`)

## Why this exists

A13 first exercised the Factory against Nova, a consumer FinTech project. That exposed routing and scope-boundary problems, but one project could not tell us whether the failures were FinTech-specific. This addendum repeats the contract-level dogfood against two deliberately different products:

- **Lumen** — visual/cultural experience where art direction, composition, discovery mode and atmosphere are first-class evidence.
- **CENNEXT** — B2B/enterprise service prototype where information architecture, compliance, sitemap, component states and service workflow are first-class evidence.

The goal is not to force both projects through Nova's financial runner. The goal is to verify which A13 failures survive when the product archetype and evidence model change radically.

## Grounded source-of-truth profiles

| Project | Archetype | Grounded evidence | Dogfood focus |
| --- | --- | --- | --- |
| Nova | FinTech trust/data | `PROJECT-CONTEXT.md`, `.uiux-profile.json`, product UI | trust, financial data, taxonomy |
| Lumen | Visual / cultural experience | `AGENTS.md`, `PROJECT-CONTEXT.md`, `docs/DESIGN-DIRECTION.md`, `docs/CULTURAL-EXPERIENCE.md`, `docs/DISCOVERY-MODES.md`, `docs/COMPOSITION-PROOFS.md` | art direction, composition, cultural-experience continuity |
| CENNEXT | B2B / enterprise service | `README.md`, `BRIEF_COMPLIANCE.md`, `sitemap.html`, `design-system.html`, `component-states.html` | IA, workflow clarity, brief/compliance continuity |

## Result matrix

| A13 finding | Nova | Lumen | CENNEXT | Classification |
| --- | --- | --- | --- | --- |
| Explicit `change_surface` must remain authoritative | Reproduced | Reproduced at contract boundary | Reproduced at contract boundary | **SYSTEMIC** |
| Generic improve/refine work must not automatically expand into a full discovery/restrategy lane | Reproduced | Strongly exposed: visual refinement can be narrow while strategy stays frozen | Strongly exposed: IA/workflow clarity can be narrow while brief/compliance stays frozen | **SYSTEMIC** |
| Source-of-truth resolver must follow the repository instead of one project template | Nova profile shape works | Different filename + specialist design docs | No Nova-style project profile; brief/README/sitemap are authoritative | **SYSTEMIC** |
| Evidence model should be domain-specific | trust/data/regulatory | composition/cultural experience | IA/workflow/compliance | Domain-specific manifestation |
| Financial specialist assumptions may leak into generic dogfood infrastructure | Native to Nova | Invalid | Invalid | **SYSTEMIC COUPLING** |

## The additional bug found by dogfooding

`uiux-factory/core/dogfood/real_project.py` is a truthful Nova integration lane, but it is not a generic real-project lane. It currently contains Nova-specific assumptions such as:

- `_normalize_nova_domain(...)` as a mandatory profile gate;
- hard requirement for `.uiux-profile.json` with a Nova-supported financial domain;
- hard-coded `financial-product-intelligence` routing assertions;
- Nova-specific goal text, route expectations, workflow path and report labels.

Trying to reuse that runner for Lumen or CENNEXT would fail before the A13 system contracts are meaningfully exercised. Treating that failure as a Lumen/CENNEXT product failure would be a false conclusion.

**Classification: Factory dogfood-harness coupling, not FinTech product behavior.**

## Patch added in this branch

### `uiux-factory/core/dogfood/cross_project.py`

Adds explicit, repository-grounded project profiles for Nova, Lumen and CENNEXT. The cross-project lane:

1. keeps each project's evidence model separate;
2. accepts source-of-truth filename/shape differences instead of requiring Nova's profile shape;
3. compiles the canonical `GoalInterpreter` Task Contract;
4. applies explicit `PRODUCT` / `FACTORY` override semantics as an invariant independent of domain;
5. detects accidental Nova/FinTech token leakage into non-Nova profiles;
6. fails closed when required project-specific evidence is missing;
7. states a strict truth boundary: no browser, provider-quality, aesthetic, deploy or release verdict is invented.

### `uiux-factory/tests/test_cross_project_dogfood_a13.py`

Regression coverage now checks:

- Lumen visual/art-direction task remains `PRODUCT` scoped without Nova leakage;
- CENNEXT enterprise IA/workflow task remains `PRODUCT` scoped without FinTech assumptions;
- explicit `change_surface` is invariant across all three project archetypes;
- source truth accepts `PROJECT-CONTEXT.md` and legacy `PROJECT_CONTEXT.md` variants rather than coupling to one filename;
- Nova/Lumen/CENNEXT retain distinct archetype, routing-intent and evidence models;
- missing project-specific evidence fails closed rather than being silently invented.

## System verdict

A13's root problems are **not specific to FinTech**.

The repeated pattern is:

> **Explicit task boundaries and repository evidence must outrank generic “improve/redesign” inference, regardless of product domain.**

Nova exposed the problem through financial trust/data routing. Lumen exposes the same class of problem through art-direction tasks that should not trigger product re-strategy. CENNEXT exposes it through enterprise IA/workflow work that should not discard brief/compliance constraints or invent a Nova-style profile.

The root cause is therefore a **system-level contract/routing/source-truth problem with domain-specific symptoms**.

## What is intentionally not claimed

This branch does **not** claim that Lumen or CENNEXT received a full browser/provider/aesthetic QA pass. The cross-project tests isolate the exact A13 contract failures first. Full rendered dogfood should be a separate lane once the generic real-project runner no longer embeds Nova-specific taxonomy and specialist assertions.

## Recommended follow-through

1. Keep `RealProjectDogfoodRunner` as the pinned Nova integration lane for backward compatibility.
2. Promote project-profile/source-truth resolution to a generic Factory primitive rather than extending `_normalize_nova_domain` with more domain aliases.
3. Make specialist routing depend on resolved project/domain evidence, not on the dogfood harness.
4. Keep `change_surface` authoritative end-to-end and add equivalent contract tests at every entrypoint.
5. Only after those invariants are stable, add rendered Lumen and CENNEXT lanes with their own routes and project-specific visual/enterprise evidence requirements.
