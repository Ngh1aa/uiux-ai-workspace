# Declarative Website Flows

`flows/*.json` is the routing layer between a user task, agent roles and specialist `SKILL.md` packages.

```text
task context
→ FlowResolver
→ flow
→ stage agent
→ SkillResolver(role defaults + required + conditional + explicit additions)
→ active specialist run
→ gate evidence
→ PASS: advance | explicit failure/risk: bounded ReplanningEngine
```

## Why this layer exists

Agents should manage **which capability is active**, not duplicate the knowledge inside every skill. Adding a capability to a website type should normally be a flow edit, not an agent-code edit.

For example, ecommerce activates `ecommerce-website`, `conversion-and-content` and `site-search-and-findability` during research. To add another existing capability for ecommerce, add it to that `conditional_skills` rule and run:

```bash
python -B scripts/validate-flows.py
python -B scripts/validate-runtime-foundation.py
```

## Task context

The manager routes on:

- `intent`: build/redesign/rebuild/improve/fix/polish;
- `website_type`: corporate, ecommerce, education, government, hospitality, news, real-estate, saas, startup, portfolio, nonprofit, landing, or a future type;
- `mode`: visual-prototype, interactive-prototype, production-candidate, production;
- `risk`: project-defined risk label;
- `features`: active behavior such as auth, forms, search, dashboard, motion or i18n.

Flow matching stays intentionally small. Domain and feature detail belongs in conditional skill routing, not in a giant manager prompt.

## Stage contract

Each stage declares:

- `id` and owning `agent` role;
- `required_skills`;
- `conditional_skills` driven by task context;
- stage gates;
- purpose.

Role `default_skills` are always merged by the Skill Resolver and cannot be excluded. Flow-required skills are also mandatory for that stage.

The Development Manager executes only the active stage. It blocks stage skipping and records specialist run IDs in the managed checkpoint.

## Replanning

Replanning is **not retry**. A decision requires an explicit signal, remaining replan budget and a matching policy.

An applied replan:

- must originate from the active stage;
- targets an explicit stage;
- may add/drop only non-mandatory skills;
- increments `flow.revision`;
- records replan history;
- invalidates the target stage and downstream completion only;
- never grants higher authority.

Use `--no-apply-replan` when you only want a diagnostic decision without mutating the persisted managed run.

## Schema

Portable contract: `schemas/flow.schema.json`.

Runtime enforcement is dependency-free in `runtime/flow.py::validate_flow_document`, so the core runtime does not require a JSON Schema library.

## Development Manager

`runtime/manager.py::DevelopmentManagerAgent` owns A→Z routing but not specialist knowledge. Stage runs receive only their resolved skill graph plus role defaults, preserving progressive disclosure.

Managed runs can be resumed by `manager_run_id`; active stage, completed stages, stage run IDs, replan count/history and flow revision are restored from checkpoints.
