# Cross-Functional Intelligence Upgrade

Checked: 2026-09-06 (Asia/Ho_Chi_Minh)

## Phase classification

- Scope: `system`
- Type: `research / implementation / verification / release / post-release verification`
- Risk: `medium`
- Mode: `production`
- Baseline `main`: `279c9e01ca85779fa4af2d60551fb9b1e0d16111`
- Branch: `feat/cross-functional-product-growth-intelligence`
- PR: `#15` — merged
- Implementation commit: `201642e6857dd26994002facfa70b029a35a1bc4`
- Final PR head: `1743c137849223fccdf0681b93fda156f652939a`
- Merge commit: `9591b238b1b0700aff6fed8deb79d13b6535d143`
- Implementation push validation: GitHub Actions `34032698500` = `success`
- Implementation PR validation: GitHub Actions `34032720908` = `success`
- Final-head push validation: GitHub Actions `34032869876` = `success`
- Final-head PR validation: GitHub Actions `34032872075` = `success`
- Post-merge validation: GitHub Actions `34033674244` = `success`
- Release authorization: explicitly authorized by user on 2026-09-06.

## Skill Activation Plan

| Task | Trigger/risk | Skill | Expected impact | Verification |
|---|---|---|---|---|
| Preserve project truth while extending a system-level library | external disciplines can override local owners | `project-context` | local source-of-truth/precedence remains authoritative | baseline/final diff review |
| Keep new knowledge conditional | six external source families can cause context bloat | `adaptive-skill-routing-and-context-budget` | route only the active cross-functional decision | catalog/router + near-miss evals |
| Preserve lifecycle ownership | PM/growth/engineering sources can become parallel orchestrators | `website-delivery-pipeline` | `skills_UIUX` remains the only lifecycle OS | architecture/collision review |
| Decide extend vs new skill | overlap with discovery, conversion, analytics, SEO, guardrails | `skill-authoring-and-governance` | four new boundaries; existing owners extended where overlap is high | validators + overlap review |
| Ground external claims | time-sensitive/quantitative source material | `evidence-provenance-and-research-ops` | exact SHAs/licenses/adoption decisions and UNKNOWN/NO_DATA discipline | source-lock ledger |
| Protect routing/outcome behavior | new specialists can trigger too broadly | `agent-evaluation-and-reliability` | positive + near-miss capability tasks | eval schema/harness + CI |

## Skill Usage Ledger

| Skill | Trigger | Requirement applied | Change created | Verification | Evidence |
|---|---|---|---|---|---|
| `project-context` | system external integration | project truth above generic advice | new skills preserve precedence/UNKNOWN | source/diff review | baseline project docs |
| `adaptive-skill-routing-and-context-budget` | context/collision risk | smallest active decision graph | product/growth/search/experiment routing + near-misses | validators/evals | updated router |
| `website-delivery-pipeline` | lifecycle collision | no second orchestrator | cross-functional capabilities remain specialists/packs | architecture review | catalog/source-lock docs |
| `skill-authoring-and-governance` | capability overlap | distinct owner + progressive reference + eval | 4 new skills; analytics/conversion/SEO/guardrails extended | validators | skill packages/evals |
| `evidence-provenance-and-research-ops` | external research | source/date/confidence/limitations | exact pins, licenses, NO_DATA/UNKNOWN rules | provenance review | source-lock ledger |
| `agent-evaluation-and-reliability` | routing/reliability | representative capability/near-miss cases | 6 new eval tasks | eval harness/CI | `evals/tasks/cross-functional-*` |

## Source research and locks

### FACT — ProductSkills

Pinned `assimovt/productskills@66f9cee5868d6daf9cf106b4a74090428d6fa83e` (MIT). Reviewed positioning, prioritization, scope-cutting, metrics and experiment-design skills. Adopted competitive-alternative-first positioning, evidence/confidence in prioritization, blocker/enabler lens, appetite/scope thinking, counter-metrics and pre-run hypothesis discipline. RICE is optional and UNKNOWN quantitative inputs are never fabricated.

### FACT — Mind the Product

Pinned `mindtheproduct/skills@3fb3d46092c4149d1653fc317aed77d63f2a98ca` (MIT). Reviewed `make-the-call`: translate solution asks to underlying problems; stress-test evidence/blind spots/impact; use leverage/reversibility/strategic-ground lenses while the authorized human owns the final call. Interactive turn requirements are adapted to project-evidence mode rather than synthetic dialogue.

### FACT — ai-vita marketing skills

Pinned `ai-vita/skills@dda98df83ec242cf32c208a0a78b759f0b3e658b` (MIT). Reviewed `page-cro` and `copywriting`: page/traffic context, value proposition, CTA/hierarchy, proof, objections/friction and customer-language copy. Integrated into `conversion-and-content`; best-practice findings remain hypotheses until measured.

### FACT — Rampstack experimentation analytics

Pinned `rampstackco/claude-skills@a67dd34c609f034c0cfd736a348659bbdf1605bf` (MIT). Reviewed result interpretation covering CIs, p-values, multiple/sequential testing, CUPED, heterogeneous treatment effects, ratio/network effects and dashboard reconciliation. Created separate post-result owner `experimentation-interpretation`.

### FACT — Addy Osmani agent skills

Pinned `addyosmani/agent-skills@48cb1168aeaaa70dfc2bbf709eddfa2a8ed8129a` (MIT). Reviewed context engineering and planning/task breakdown: context hierarchy/trust, conflict handling, dependency graphs, vertical slices and checkpoints. Extended existing `ai-agent-coding-guardrails` rather than adding a duplicate coding lifecycle.

### FACT — mblode SEO Program

Pinned `mblode/agent-skills@0a639b1ef3b75aa6cc945e778fb1486def1d41bf` (MIT). Reviewed `seo-program`: current demand data, question maps, decision-shaped briefs, evidence tables, no-data discipline and monitoring. Added `search-demand-and-content-briefing`; narrowed `seo-strategy` to technical/on-page implementation. Vendor-specific/time-sensitive claims are not copied as durable facts.

Detailed source/adoption ledger: `vendor/cross-functional-intelligence/SOURCE-LOCKS.md`.

## Architecture

```text
skills_UIUX CORE OS
  project-context → adaptive router → website-delivery-pipeline
  Design Contract / evidence / QA / release
        ↓
LOCAL UI/UX OWNERS
        ↓
CONDITIONAL CROSS-FUNCTIONAL SPECIALISTS
  product-decision-and-stakeholder-framing
  product-strategy-and-prioritization
  conversion-and-content (upgraded)
  analytics-and-experimentation (upgraded, pre-run)
  experimentation-interpretation (post-result)
  search-demand-and-content-briefing
  seo-strategy (technical/on-page)
  ai-agent-coding-guardrails (upgraded)
        ↓
PINNED EXTERNAL KNOWLEDGE / PROVENANCE
```

No external source becomes project truth or a second lifecycle orchestrator.

## Capability changes

### New
- `product-decision-and-stakeholder-framing`
- `product-strategy-and-prioritization`
- `experimentation-interpretation`
- `search-demand-and-content-briefing`
- `packs/product-growth-intelligence.json`
- `vendor/cross-functional-intelligence/*`

### Extended
- `conversion-and-content` → message match, CRO diagnostic, proof/objection/CTA and testable hypotheses.
- `analytics-and-experimentation` → outcome/counter-metric tree, tracking and pre-run experiment design.
- `seo-strategy` → technical/on-page boundary; brittle universal metadata/link quotas removed.
- `ai-agent-coding-guardrails` → context trust/budget, dependency-aware tasks, vertical slices/checkpoints.
- `adaptive-skill-routing-and-context-budget` → cross-functional routing and near-miss logic.
- `professional-core` / `prototype-uiux` → product-decision/strategy coverage; professional core also includes search/experiment-result owners.

## Collision rules

- `product-discovery` discovers problem/audience/JTBD; `product-decision...` resolves ambiguous solution asks; `product-strategy...` ranks/scopes once evidence is sufficient.
- `conversion-and-content` owns marketing-page argument; `ux-writing-and-microcopy` retains state/string product copy.
- `analytics-and-experimentation` is pre-run; `experimentation-interpretation` is post-result.
- `search-demand-and-content-briefing` researches demand/brief; `seo-strategy` implements technical/on-page SEO.
- `ai-agent-coding-guardrails` is proportional; tiny fixes do not trigger planning ceremony.

## Verification

Final PR head `1743c137849223fccdf0681b93fda156f652939a` passed both push and pull-request `Validate Skills` workflows. Verified steps include:

- SKILL.md structure;
- V5 profiles, packs, project configs, evals and resources;
- vendored design-intelligence integrity;
- design-intelligence retrieval smoke;
- core-profile install and installed dependency smoke;
- project-aware installer/pack dry-run;
- bootstrap/sync smoke;
- provider-neutral eval-harness smoke.

PR #15 was merged using expected-head SHA `1743c137849223fccdf0681b93fda156f652939a` into `main` as `9591b238b1b0700aff6fed8deb79d13b6535d143`. Post-merge `Validate Skills` run `34033674244` completed successfully on that exact merge commit.

## Requirement coverage

| ID | Requirement | OWNER_PHASE | Status | Verification |
|---|---|---|---|---|
| CFI-001 | Product strategy/prioritization intelligence | implementation | DONE_VERIFIED | skill/reference + source pin + CI |
| CFI-002 | Stakeholder/product-call framing | implementation | DONE_VERIFIED | skill/reference + source pin + CI |
| CFI-003 | CRO/marketing copy intelligence | implementation | DONE_VERIFIED | upgraded local owner + source pin + CI |
| CFI-004 | Experiment design + result interpretation | implementation | DONE_VERIFIED | pre/post owners + source pin + CI |
| CFI-005 | Search demand/content brief intelligence | implementation | DONE_VERIFIED | search owner + SEO boundary + CI |
| CFI-006 | Engineering/context/planning complement | implementation | DONE_VERIFIED | upgraded guardrails + CI |
| CFI-007 | Conditional routing/context discipline | implementation | DONE_VERIFIED | router + pack + near-miss evals + CI |
| CFI-008 | Reproducible provenance/licenses | implementation | DONE_VERIFIED | source locks |
| CFI-009 | Representative eval/schema/harness coverage | verification | DONE_VERIFIED | six eval tasks + CI |
| CFI-010 | PR-head CI | verification | DONE_VERIFIED | Actions `34032872075` success |
| CFI-011 | Merge to main | release | DONE_VERIFIED | merge `9591b238b1b0700aff6fed8deb79d13b6535d143` |
| CFI-012 | Post-merge validation | release | DONE_VERIFIED | Actions `34033674244` success |

## Phase result

`PASSED`

- DUE-NOW `BLOCKED = 0`
- DUE-NOW `UNACCOUNTED = 0`
- `PENDING_FUTURE_PHASE = 0`
