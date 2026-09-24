# Agent Runtime Intelligence Source Locks

Checked: 2026-09-07 (Asia/Ho_Chi_Minh)

This registry covers external agent-engineering sources reviewed for V5.3. They are **pinned knowledge sources**, not parallel orchestrators. Local owners remain authoritative after project truth and passed artifacts.

| Source | Locked ref | License observed | Reviewed capability | Local adoption |
|---|---|---|---|---|
| `affaan-m/ECC` | `e04ea0b9cc8248686edf5ac751cadff550e162b8` | MIT | agent harness action/observation/recovery contracts; agent failure introspection; browser QA safety | `ADAPT_WITH_ATTRIBUTION` |
| `mattpocock/skills` | `3cca18b368ae95cdbdebbff572ccafa662551015` | MIT | feedback-loop-first debugging; spec-vs-standards code review; conversation→spec synthesis; project glossary discipline | `ADAPT_WITH_ATTRIBUTION` |
| `anthropics/skills` | `41bbe19d1a1a7eaab5e7bb9050a417e5c6cffc8f` | per-skill Apache-2.0 for reviewed `mcp-builder`, `webapp-testing`, `skill-creator` | MCP tool quality, black-box webapp helpers, with-skill/baseline eval methodology | `ADAPT_WITH_ATTRIBUTION` |
| `vercel-labs/agent-skills` | `063bee94c3f4df8453406c830b0a7df0f2860278` | MIT | deterministic skill discovery index + immutable artifact digest/release pattern | `ADAPT_WITH_ATTRIBUTION` |

## Decisions

### ECC

**ADOPT:** stable/narrow tool schemas; deterministic observation shape; actionable error recovery; micro-tools for high-risk actions; failure capture before blind retry; browser QA defaults to read-only; no visual baseline means inconclusive rather than PASS.

**ADAPT:** ECC-specific commands/hooks/tool names are removed. `skills_UIUX` keeps its own authority model, phase gates, provider-neutral runtime and existing UI/UX verification owners.

**REJECT:** importing ECC as a second orchestrator, bulk-copying its skill catalog, or treating generic performance thresholds as universal project gates.

### Matt Pocock skills

**ADOPT:** build a tight red-capable feedback loop before debugging theory; minimise repro; use multiple falsifiable hypotheses; distinguish spec fidelity from standards quality; preserve a project glossary when terminology materially affects work.

**ADAPT:** the existing `code-review-and-release` owner remains canonical; the two-axis idea becomes independent review axes inside the local release workflow. Conversation→spec ideas feed existing Project Truth / Design Contract / Requirement Ledger artifacts rather than a new issue-tracker dependency.

**REJECT:** repo-specific triage labels, issue-tracker setup assumptions and local vocabulary that do not belong to UI/UX consumers.

### Anthropic skills

**ADOPT:** schema-first MCP tool definitions, read/destructive/idempotent/open-world annotations where the chosen SDK supports them, actionable errors, black-box helper preference to protect context budget, and with-skill vs baseline/old-skill comparison when evaluating skill changes.

**ADAPT:** reviewed content is synthesized into local contracts/eval rules. Anthropic's repo has per-skill licensing, so no repository-wide license assumption is made.

**REJECT:** copying any skill whose local license is absent/restrictive or whose workflow duplicates an existing local owner without measurable benefit.

### Vercel agent-skills

**ADOPT:** deterministic skill artifact generation, metadata validation, SHA-256 digests and a machine-readable discovery index.

**ADAPT:** local implementation is Python/stdlib and validation-only first. V5.3 does not auto-publish releases or change consumer install contracts.

**REJECT:** mutable remote discovery as project truth and automatic distribution without a separately authorized release phase.

## Update policy

Changing a pin requires:
1. inspect upstream diff and license/terms;
2. re-check overlap and local ownership;
3. record `ADOPT / ADAPT / REJECT` deltas;
4. update only materially justified local files;
5. run structural/runtime/eval validation;
6. merge/release only with explicit authorization.
