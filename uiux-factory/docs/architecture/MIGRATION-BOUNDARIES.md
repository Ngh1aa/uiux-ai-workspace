# A40.1 — Post-A4 Architecture Boundaries

Status: **ACTIVE ARCHITECTURE CONTRACT**  
Audit date: **2026-10-02**  
Baseline: `main@304baefb6999e552708150a20e5c01491aa3663e`

This document replaces the A1-era migration contract that described A4 consolidation as future work. A4 consolidation is now implemented and validated: `uiux-factory/core/runtime/flow_os/` is the shared executable Flow OS owner and `skills_UIUX/runtime/*.py` is compatibility-only Python surface.

The purpose of this contract is now to protect the post-A4 architecture while Brain OS work begins.

## 1. Canonical direction now in force

```text
uiux-factory/
├── canonical executable product/runtime
├── product managers / specialist execution
├── shared Flow OS runtime
├── providers / tools / sandbox
├── browser/QA
├── evidence / provenance
├── memory
└── evaluation

skills_UIUX/
├── skills / methodology
├── flows
├── policies
├── schemas
├── runtime-policy.json
└── portable documentation / integration contracts
```

A future Brain OS may add an intelligence/control layer under Factory, but it must consume these canonical owners rather than duplicate them.

## 2. Preserve current canonical owners

Do not delete, bypass or silently fork these surfaces without equivalent evidence and migration tests:

```text
uiux-factory/run.py
uiux-factory/core/manager/
uiux-factory/core/runtime/flow_os/
uiux-factory/core/orchestration/intelligent_flow.py
uiux-factory/core/evaluation/
uiux-factory/core/memory/
uiux-factory/core/provenance/
uiux-factory/qa/
skills_UIUX/flows/
skills_UIUX/runtime/runtime-policy.json
skills_UIUX/scripts/uiux-agent.py
```

`skills_UIUX/runtime/*.py` compatibility wrappers may be deprecated later, but new executable decision logic must not be added there.

## 3. Brain OS boundary

Brain OS is allowed to own:

- product/task framing above the current Task Contract;
- bounded reasoning plans and next-best-action selection;
- hypothesis/decision contracts;
- uncertainty states;
- memory recall/write orchestration under existing trust rules;
- critique routing/synthesis;
- evaluation aggregation/scorecards;
- evidence graph adapters over existing evidence/provenance records.

Brain OS must **not** own a new execution runtime.

The required direction is:

```text
Brain OS
→ canonical GoalInterpreter / FlowPlanner
→ Factory manager or ManagedFlowController
→ specialist execution / tools
→ existing evidence + QA
→ existing evaluation / memory
```

Brain OS must not execute an independent stage lifecycle beside Factory/Flow OS.

## 4. Skill and knowledge ownership boundary

UI/UX/product/domain methodology belongs in `skills_UIUX` or a future declarative Knowledge OS, not provider adapters, manager prompts or Brain planner Python constants.

Providers and Brain modules may consume routed knowledge, but they must not become the source of design methodology.

A future Knowledge OS must have an explicit owner and retrieval contract; it must not silently turn memory into universal knowledge or duplicate `SKILL.md` content without a migration plan.

## 5. Flow ownership boundary

Declarative stage order, required/conditional skills, gates and bounded replanning rules belong in:

```text
skills_UIUX/flows/*.json
uiux-factory/core/runtime/flow_os/flow.py
```

Factory detailed-stage mapping may remain in `core/orchestration/intelligent_flow.py` as an adapter.

Brain OS may propose or request replanning only through the canonical planner/replanning interface. It must not invent a competing stage order.

Provider/model output never owns stage handoff authority.

## 6. Manager boundary

There is one product-level Development Manager lineage under `uiux-factory/core/manager/`.

`ManagedFlowController` is a lifecycle/checkpoint controller and must not evolve into a second product manager.

Future Brain modules must coordinate with these owners instead of introducing `BrainDevelopmentManager`, `BrainRuntime`, or equivalent parallel orchestration classes unless the architecture is intentionally migrated and parity is proven first.

## 7. Provider boundary

Provider adapters own transport/model-specific request-response conversion and usage/cost metadata only.

They must not own:

- task classification;
- change-surface selection;
- stage order;
- skill routing;
- approval policy;
- evidence truth semantics;
- merge/release authority.

Two provider entry paths currently remain active:

```text
uiux-factory/core/runtime/free_provider.py
uiux-factory/core/runtime/flow_os/provider*.py
```

Future work may converge them behind a common capability contract. It must not introduce a third provider policy surface.

## 8. Evidence and provenance boundary

Do not create a second evidence truth system.

Current evidence/provenance owners include:

```text
uiux-factory/core/runtime/flow_os/evidence.py
uiux-factory/core/runtime/flow_os/browser_evidence.py
uiux-factory/core/provenance/evidence_lineage.py
uiux-factory/core/provenance/release_evidence_registry.py
uiux-factory/qa/
```

Future Brain OS Evidence Graph work must normalize/reference/adapt these records and add missing relationship types. It must not downgrade provenance or replace trusted runtime evidence with model-authored graph nodes.

Keep claim types separate:

```text
model/provider statement → claim/advisory context
code correctness         → compile/test/runtime evidence
UI behavior              → browser evidence
visual quality           → screenshot + creative/human review evidence
accessibility            → automated + browser/manual evidence as applicable
user validation          → direct-user evidence
release                  → deployment/workflow evidence
```

## 9. Memory boundary

Current evaluation memory is bounded, project-scoped and advisory.

Future semantic/project/decision memory may expand stored types, but memory must never:

- select or rewrite the flow by itself;
- escalate authority;
- satisfy a current-run gate;
- become current-run evidence merely because it was stored previously;
- approve merge/deploy/release;
- override current project truth.

Persistent memory writes must preserve schema versioning, project scope, atomicity, path safety and provenance.

## 10. Critique boundary

The current `VisualCritic` is an existing specialist capability and should be adapted into future critique orchestration.

A future Critique Orchestrator may route multiple critics and synthesize root causes/repair directives, but:

- a critic cannot self-PASS a gate;
- a critic cannot rewrite another critic's evidence;
- critique prose is not trusted runtime evidence by default;
- changes to product/business direction require human authority;
- existing visual-critic contracts require migration/adapters rather than incompatible duplicate schemas.

## 11. Evaluation and benchmark boundary

Existing benchmark/eval sources are versioned evidence, not disposable fixtures:

```text
uiux-factory/core/benchmarks/
uiux-factory/benchmarks/corpus/
skills_UIUX/scripts/eval-harness.py
A13/A14/A20 workflows and tests
```

A future unified Brain scorecard may aggregate these surfaces, but must keep deterministic, model-assisted and human-review channels distinguishable.

Do not silently mutate historical corpus truth to make a new architecture pass.

## 12. External integration boundary

GitHub, MCP, Figma, browser, deploy/release and other external capability surfaces must use narrow allowlisted operations and existing authority rules.

The GitHub connector bridge is metadata-only ingress. It cannot introduce arbitrary install/build/serve commands or claim execution evidence by itself.

External integrations must not become alternate policy/runtime owners merely because they provide transport.

## 13. Compatibility boundary

During Brain OS evolution:

- keep existing CLI commands valid where feasible;
- preserve canonical class identity tests;
- prefer adapters/deprecation notices over abrupt removal;
- preserve persisted run/checkpoint readability or provide a versioned migration;
- preserve existing flow IDs unless migration is intentional;
- keep `engine=external` truthful: handoff is not implementation PASS;
- keep regression fixtures separate from target acceptance evidence;
- do not move executable logic back into `skills_UIUX/runtime/*.py` compatibility shims.

## 14. Documentation truth boundary

Architecture truth priority is:

1. current source and executable tests;
2. current root `AGENTS.md`, runtime policy and Contract Ownership map;
3. `CURRENT-RUNTIME-MAP.md` and this active architecture contract;
4. current Flow OS / QA / capability documentation that matches source;
5. historical A-series implementation notes.

Historical plans describe how the repository got here. They do not override current code.

## 15. A40.1 → A40.2 handoff

A40.2 should encode the following as executable architecture guardrails:

- Flow OS executable owner remains `uiux-factory/core/runtime/flow_os/`;
- legacy `skills_UIUX/runtime/*.py` stays compatibility-only;
- declarative flows/skills/policy remain outside provider code;
- Brain OS cannot mutate authority/gates/release directly;
- Brain OS cannot become a third execution runtime;
- current evidence/provenance primitives remain canonical inputs for any future Evidence Graph;
- memory remains advisory and cannot satisfy current-run evidence gates;
- provider/model claims cannot become trusted runtime evidence;
- existing benchmark corpus truth cannot be rewritten silently.

Any later A-step that violates these invariants must be treated as an architecture regression until an explicit migration with parity evidence is approved.
