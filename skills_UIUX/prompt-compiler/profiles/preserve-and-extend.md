# Profile — Preserve and Extend

Use when an existing implementation has valuable protected behavior or visual/product DNA, but the task adds or changes meaningful surfaces.

## Compile these contracts

### Preserve levels
Classify each protected owner as applicable:
- `BYTE_EXACT`
- `BEHAVIOR_EXACT`
- `PUBLIC_CONTRACT_EXACT`
- `VISUAL_DNA`
- `CONTENT_DATA`

Do not claim a stronger level than evidence/user intent supports.

### Extension boundary
For every new/changed surface identify:
- owner file/module/component;
- dependencies;
- what may change;
- what may not change;
- whether the value is `PROPOSED`, `VERIFIED`, or another evidence state;
- regression evidence required after implementation.

### Mixed evidence is allowed
One surface may include VERIFIED existing behavior and PROPOSED new composition/content. Evidence status belongs to each material decision, not to the whole section.

## Output emphasis

- current architecture and protected core;
- preserve/change matrix;
- gap analysis;
- new routes/states/components only when goal requires them;
- art direction that preserves intentional DNA without preserving incidental implementation debt;
- regression QA for protected behavior;
- rendered QA for new visual work.

Do not freeze existing DOM/CSS simply because it exists.