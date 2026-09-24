# Agent Runtime Foundation Upgrade

Checked: 2026-09-07 (Asia/Ho_Chi_Minh)

## Phase classification

- Scope: `system`
- Type: `implementation / QA / release / post-release verification`
- Risk: `medium`
- Mode: `production`
- Phase-start `main`: `f098e6a94aaf3f026a810bc30073df67eb653cc2`
- Recovery PR: `#16`, head `7373bf9201b7ad3d52eea2753a78809beb5b1562`
- Recovery merge commit: `c8a2d07ad360bc887b687288beff1d3d7aa7f76e`
- Recovery post-merge validation: GitHub Actions `34073614108` = `success`
- Implementation branch: `feat/v5-2-agent-runtime-foundation`
- V5.2 PR: `#17`
- Implementation commit: `69724b9fd65a8df0f56ae2c8231da2054da73346`
- Final PR head: `a6cc9997fc15246c67894fcebfeff3f9e46a9e70`
- V5.2 merge commit: `49e5ad978cbce21df2398385b2a58b019252923b`
- V5.2 post-merge validation: GitHub Actions `34073654070` = `success`
- Release authorization: explicitly authorized by user on 2026-09-07.

The phase intentionally recovered the red `main` first, verified that recovery, then released V5.2 from the already-validated runtime head. No core skill-tree reorganization was introduced.

## Skill Activation Plan

| Task | Trigger/risk | Skill | Expected impact | Verification |
|---|---|---|---|---|
| protect current architecture | system library change | `project-context` | preserve root skill/install contracts | repo/source inspection |
| smallest knowledge graph | context/runtime expansion | `adaptive-skill-routing-and-context-budget` | no 13 new broad skills | catalog + runtime boundary |
| lifecycle/gates | multi-phase system work | `website-delivery-pipeline` | phase-aware truth and no false release | ledger + CI |
| safe code/runtime work | executable scripts + state | `ai-agent-coding-guardrails` | scoped tools, checkpoints, verification | runtime smoke |
| authoring boundary | risk of skill proliferation | `skill-authoring-and-governance` | runtime concerns stay outside SKILL.md unless they own a decision | no duplicate skills |
| reliability | new harness behavior | `agent-evaluation-and-reliability` | regression/capability tasks | eval validator |
| rendered QA integration | Playwright adapter | `testing-strategy` | rendered evidence contract | node syntax + adapter docs |
| tool authority | executable actions | `security-and-privacy` | least privilege / fail closed | permission smoke |

## USED skill evidence

| Skill | Trigger | Requirement applied | Change created | Verification | Evidence |
|---|---|---|---|---|---|
| `project-context` | library architecture is source-of-truth | inspect before restructure | root skills untouched; runtime added beside them | structural CI | runtime is additive |
| `adaptive-skill-routing-and-context-budget` | context bloat risk | installed != active | explicit selected-skill context manifest + telemetry | runtime smoke | `runtime/agent.py` |
| `website-delivery-pipeline` | system/multi-phase work | phase-aware gates, truthful system reality | release only after recovery + exact-head/post-merge validation | CI + ledger | this document |
| `ai-agent-coding-guardrails` | executable tool/state layer | scoped writes, no destructive defaults, verify | tool registry + checkpoint + harness | runtime smoke | `runtime/agent.py` |
| `skill-authoring-and-governance` | 13 topics could become 13 skills | do not duplicate capability | no new SKILL.md packages for tools/runtime | catalog unchanged | runtime/integration folders |
| `agent-evaluation-and-reliability` | new agent behavior | capability + regression coverage | 4 runtime eval tasks | `validate-v2.py` | `evals/tasks/runtime-*` |
| `testing-strategy` | rendered QA | browser evidence is separate from judgment | optional Playwright capture adapter | Node syntax check | `integrations/playwright/` |
| `security-and-privacy` | tools can mutate state | least privilege + no implicit authority escalation | 4-level risk/authority gate + trace redaction | denied critical-action smoke | `runtime/runtime-policy.json` |

## Requirement Coverage Ledger

| ID | Requirement | Owner phase | Status | Verification / evidence |
|---|---|---|---|---|
| AR-01 | Context Engineering becomes measurable context selection, not larger prompts | implementation | DONE_VERIFIED | context manifest + char/token telemetry |
| AR-02 | Skill routing remains smallest-graph and no mass skill proliferation | implementation | DONE_VERIFIED | no new broad skills; V5.1 routing remains owner |
| AR-03 | Tool Calling gets a stable risk/authority contract | implementation | DONE_VERIFIED | tool registry + permission smoke |
| AR-04 | MCP gets an optional current-v2 adapter boundary | implementation | DONE_VERIFIED | syntax-checked adapter + dependency/runtime truth documented |
| AR-05 | Single-agent harness exists without forcing a model provider | implementation | DONE_VERIFIED | provider-neutral harness + CLI smoke |
| AR-06 | Evals cover new runtime behaviors | QA | DONE_VERIFIED | 4 new eval tasks + existing validator |
| AR-07 | Playwright captures rendered evidence for downstream QA | implementation | DONE_VERIFIED | adapter syntax + manifest contract; browser E2E remains environment-specific |
| AR-08 | Figma MCP/Code Connect has an explicit project-truth/reuse boundary | implementation | DONE_VERIFIED | Figma adapter docs + component-map evidence shape |
| AR-09 | Multi-agent starts with role/authority/handoff boundaries, not 5 duplicate libraries | implementation | DONE_VERIFIED | research/implementation/qa roles + serial handoff trace |
| AR-10 | GitHub/n8n automation cannot silently grant authority | implementation | DONE_VERIFIED | n8n boundary doc + existing Actions remain external trigger |
| AR-11 | Tracing/observability records tool/permission/run events with redaction | implementation | DONE_VERIFIED | JSONL trace + summarizer |
| AR-12 | Agent security/permissions fail closed on critical actions | QA | DONE_VERIFIED | runtime permission smoke |
| AR-13 | Durable workflow foundation supports local resume without overclaiming | implementation | DONE_VERIFIED | atomic local checkpoint + resume smoke |
| AR-14 | Full distributed durable execution (Temporal-class) | future production runtime | PENDING_FUTURE_PHASE | only if a real long-running consumer requires it |
| AR-15 | Real Figma MCP end-to-end test | future integration QA | PENDING_FUTURE_PHASE | requires supported client/account/project |
| AR-16 | Real Playwright browser matrix against a consumer project | future integration QA | PENDING_FUTURE_PHASE | requires runnable consumer project |
| AR-17 | Real autonomous model-provider adapter | future adapter phase | PENDING_FUTURE_PHASE | provider selection intentionally not imposed |
| AR-18 | Merge/release to `main` | release | DONE_VERIFIED | PR #17 merged as `49e5ad978cbce21df2398385b2a58b019252923b`; post-merge run `34073654070` succeeded |

## Decision Log

### D-01 — Runtime is not a new skill pack
**FACT:** the current library already has context/routing/eval/testing/security owners.

**Decision:** add `runtime/` and `integrations/` instead of 13 new `SKILL.md` packages.

**Impact:** lower context noise and clearer ownership.

### D-02 — Provider-neutral harness
**Decision:** the repository owns execution safety/state/tool contracts; a model/provider adapter owns reasoning.

**Impact:** no lock-in to one model runtime and evals remain comparable.

### D-03 — MCP v2
**EVIDENCE_BACKED_INFERENCE:** official MCP Python SDK documentation checked on 2026-09-06 states v2 is the stable line and uses `MCPServer` rather than v1 `FastMCP`.

**Decision:** optional adapter targets `mcp>=2,<3`; core CI syntax-checks it unless the dependency is intentionally installed.

### D-04 — Figma is context, not production-code truth
**EVIDENCE_BACKED_INFERENCE:** current official Figma docs describe MCP as structured design context and Code Connect as code-component mapping enrichment.

**Decision:** Figma mappings feed `reference-analysis-and-design-to-code`; actual project source/Design Contract remain higher precedence.

### D-05 — Local checkpoint is not Temporal
**Decision:** implement atomic local resume now; keep distributed durability `PENDING_FUTURE_PHASE`.

**Impact:** useful failure recovery without false production claim.

### D-06 — Release sequencing
**FACT:** `main` was red before recovery PR #16.

**Decision:** merge and verify #16 first, then retarget #17 to `main`, merge #17 with an expected-head guard, then require post-merge validation.

**Impact:** the released V5.2 state is based on a green recovery baseline and a separately verified runtime release.

## System Reality

| Surface | Reality |
|---|---|
| context/permission/trace/checkpoint runtime | REAL |
| provider-neutral plan executor | REAL |
| autonomous model reasoning | NOT BUNDLED |
| MCP | OPTIONAL / external dependency |
| Playwright | OPTIONAL / external dependency |
| Figma MCP/Code Connect | EXTERNAL |
| n8n | EXTERNAL |
| distributed durable workflows | NOT IMPLEMENTED |

## Phase gate

`PASSED`.

Evidence:
- recovery merge `c8a2d07ad360bc887b687288beff1d3d7aa7f76e` → GitHub Actions `34073614108` = `success`;
- V5.2 exact head `a6cc9997fc15246c67894fcebfeff3f9e46a9e70` → push/PR validation = `success`;
- V5.2 merge `49e5ad978cbce21df2398385b2a58b019252923b` → GitHub Actions `34073654070` = `success`;
- DUE-NOW blockers = 0.
