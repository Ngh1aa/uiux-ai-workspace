# Cross-Functional Intelligence Source Locks

Checked: 2026-09-06 (Asia/Ho_Chi_Minh)

| Source | Locked ref | License observed | Reviewed capability | Local adoption |
|---|---|---|---|---|
| `assimovt/productskills` | `66f9cee5868d6daf9cf106b4a74090428d6fa83e` | MIT | product positioning, RICE/blocker-enabler prioritization, appetite/scope cutting, metrics/counter-metrics, experiment design | `ADAPT_WITH_ATTRIBUTION` |
| `mindtheproduct/skills` | `3fb3d46092c4149d1653fc317aed77d63f2a98ca` | MIT | `make-the-call`: translate asks → stress-test evidence/blind spots/impact → pick what matters | `ADAPT_WITH_ATTRIBUTION` |
| `ai-vita/skills` | `dda98df83ec242cf32c208a0a78b759f0b3e658b` | MIT | page CRO and marketing copywriting patterns | `ADAPT_WITH_ATTRIBUTION` |
| `rampstackco/claude-skills` | `a67dd34c609f034c0cfd736a348659bbdf1605bf` | MIT | experimentation analytics/result interpretation: CI, p-values, multiplicity, sequential testing, CUPED, HTE, ratio/network effects, dashboard reconciliation | `ADAPT_WITH_ATTRIBUTION` |
| `addyosmani/agent-skills` | `48cb1168aeaaa70dfc2bbf709eddfa2a8ed8129a` | MIT | context engineering, dependency-aware planning, vertical slices, checkpoints | `ADAPT_WITH_ATTRIBUTION` |
| `mblode/agent-skills` | `0a639b1ef3b75aa6cc945e778fb1486def1d41bf` | MIT | `seo-program`: current search demand, question maps, content briefs, monitoring/evidence discipline | `ADAPT_WITH_ATTRIBUTION` |

## Decisions

### ProductSkills

**ADOPT:** reality-grounded positioning order; explicit evidence/confidence in prioritization; blocker/enabler lens; outcome/counter-metric thinking.

**ADAPT:** RICE is optional when inputs are defensible, not a mandatory scoring oracle. Appetite/scope ideas are adapted to UI/UX risk. Upstream edge-frequency shortcuts are not allowed to cut accessibility, security, privacy, destructive-flow or other high-consequence requirements.

**REJECT AS ABSOLUTE:** invented Reach/Impact/Effort, universal cycle-duration rules, or any rule that treats mandatory requirements as low-scoring optional work.

### Mind the Product

**ADOPT:** solution request → underlying problem; evidence/blind-spots/impact stress test; leverage/reversibility/strategic-ground lenses; human decision ownership.

**ADAPT:** original interactive turn/stage rules become project-evidence-driven when an autonomous project phase has sufficient source material. Missing voices remain UNKNOWN rather than forcing synthetic dialogue.

### ai-vita marketing skills

**ADOPT:** CRO diagnostic ordering, traffic/message-match awareness, value/proof/objection/CTA structure, clarity/customer-language copy principles.

**ADAPT:** CRO recommendations are hypotheses until backed by project research/analytics/experiments. Product-state strings remain owned by `ux-writing-and-microcopy`.

**REJECT AS EVIDENCE:** any implication that applying a page pattern itself proves conversion improvement.

### Rampstack experimentation analytics

**ADOPT:** uncertainty/effect magnitude before point-estimate celebration; correct p-value framing; multiplicity/sequential-method checks; pre-registered vs post-hoc segment distinction; CUPED/ratio/network/dashboard reconciliation awareness.

**ADAPT:** platform-specific statements are treated as time-sensitive and must be reverified if used. High-stakes/statistically ambiguous decisions escalate to a qualified data owner rather than being automated by a checklist.

### Addy Osmani agent skills

**ADOPT:** context hierarchy/trust, dependency mapping, vertical slicing, checkpoints and explicit verification.

**ADAPT:** no hard context-percentage or line-count threshold is treated as universal. Existing `skills_UIUX` project-context, lifecycle, Design Contract and release rules remain authoritative.

### mblode SEO Program

**ADOPT:** current-source numbers only; source/scope/date evidence table; natural-language question maps; short decision-shaped briefs; NO_DATA instead of fabricated metrics; separation of demand research from technical implementation.

**ADAPT:** upstream vendor-specific statistics/AI-search claims are not copied as durable facts. Current exact claims must be reverified when material.

## Local capability mapping

| Local owner | External source contribution |
|---|---|
| `product-strategy-and-prioritization` | ProductSkills |
| `product-decision-and-stakeholder-framing` | Mind the Product |
| `conversion-and-content` | ai-vita page CRO + copywriting |
| `analytics-and-experimentation` | ProductSkills metrics/experiment design |
| `experimentation-interpretation` | Rampstack experimentation analytics |
| `search-demand-and-content-briefing` | mblode SEO Program |
| `seo-strategy` | clarified technical/on-page boundary after SEO Program review |
| `ai-agent-coding-guardrails` | Addy context/planning/vertical-slice discipline |

Changing any locked ref requires a source/license/behavior diff review, overlap check and representative eval/validator rerun before release.
