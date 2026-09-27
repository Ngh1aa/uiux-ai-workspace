# A1 — Migration Boundaries

Status: **ACTIVE MIGRATION CONTRACT**  
Audit date: **2026-09-28**

This document defines what A2+ may change without accidentally turning architecture cleanup into a rewrite.

## 1. Canonical direction

Target direction for later phases:

```text
uiux-factory/
├── canonical executable product/runtime
├── orchestration
├── providers
├── tools
├── browser/QA
├── memory
└── evaluation

skills_UIUX/
├── skills
├── flows
├── policies
├── schemas
└── portable integration/reference contracts
```

A1 records this direction only. A4 owns the actual consolidation.

## 2. Preserve until A4 proves replacement

Do not delete or bypass these surfaces before equivalent behavior is demonstrated by tests/evidence:

```text
uiux-factory/run.py
uiux-factory/core/manager/
uiux-factory/core/runtime/
uiux-factory/qa/
skills_UIUX/runtime/
skills_UIUX/flows/
skills_UIUX/scripts/uiux-agent.py
```

The fact that two surfaces overlap is not permission to remove either one prematurely.

## 3. Skill ownership boundary

UI/UX/domain knowledge belongs in `skills_UIUX`, not provider adapters or manager prompts.

Providers may consume routed skills, but must not become the source of design methodology.

A future canonical runtime should depend on skill contracts rather than copy their knowledge into Python orchestration code.

## 4. Flow ownership boundary

Declarative stage order, required/conditional skills, gates and replanning rules belong in flow documents where practical.

Managers own lifecycle enforcement, not specialist design knowledge.

Provider/model responses never own stage handoff authority.

## 5. Provider boundary

Provider adapters own transport/model-specific request-response conversion only.

They must not own:

- task classification;
- stage order;
- skill routing;
- approval policy;
- release authority;
- evidence truth semantics.

A4 must preserve the provider-neutral interface exposed by the managed runtime when consolidating execution surfaces.

## 6. QA/evidence boundary

Source inspection, generated code and model assertions are not rendered visual evidence.

Keep these claim types separate:

```text
code correctness → compile/test/runtime evidence
UI behavior → browser evidence
visual quality → screenshot/creative-review evidence
accessibility → automated + manual/browser evidence as applicable
release → deployment/workflow evidence
```

Later A4.4 will make evidence machine-verifiable; A1 only freezes the semantics.

## 7. External integration boundary

MCP, Figma, browser adapters and release/deploy adapters are external capability surfaces.

They must use narrow allowlisted operations and existing authority rules. Do not introduce arbitrary shell/filesystem access to make an integration easier.

A5 must not begin until A4.1–A4.4 security/integrity blockers pass.

## 8. Compatibility boundary

During migration:

- keep existing CLI commands valid where feasible;
- prefer adapters/deprecation notices over abrupt removal;
- preserve persisted run/checkpoint readability or provide an explicit migration path;
- preserve existing flow IDs unless a schema/versioned migration is intentional;
- keep `engine=external` truthful: handoff is not implementation PASS;
- keep regression fixtures separate from product acceptance evidence.

## 9. Documentation truth boundary

Documents are classified by authority, not age alone.

Runtime truth priority for architecture work:

1. current source and executable tests;
2. current root README / AGENTS contract;
3. current runtime/flow documentation that matches source;
4. active capability/QA docs;
5. historical implementation plans and sprint notes.

Historical plans must not override current code.

## 10. A1 → A4 handoff

A4 may start only from the following frozen facts:

- `uiux-factory` is the repository-declared canonical product source today;
- `skills_UIUX/runtime` is an active, validated managed Flow OS surface today;
- CI deliberately validates both surfaces today;
- consolidation is therefore a migration problem, not a simple directory deletion;
- the post-A4 target is one orchestration/runtime authority with reusable skills/flows remaining portable.

Any A4 proposal that cannot preserve the A1 baseline or provide equivalent evidence must be treated as a regression until proven otherwise.
