# Experimentation Interpretation — Pinned Synthesis

Source reviewed: `rampstackco/claude-skills@a67dd34c609f034c0cfd736a348659bbdf1605bf` → `experimentation-analytics` (MIT).

This reference adapts result-reading discipline to `skills_UIUX`. It does not reproduce the upstream skill verbatim and must not substitute for a qualified analyst when the statistical method or business decision is high stakes.

## Result-panel minimum

Useful fields when available:

| Field | Why it matters |
|---|---|
| variants + allocation | assignment balance/context |
| N per variant | precision/power context |
| point estimate | best observed effect estimate |
| CI/credible interval | uncertainty |
| absolute + relative lift | practical interpretation |
| method | valid meaning of p/probability/interval |
| guardrails | detect hidden harm |
| pre-registered segments | avoid post-hoc storytelling |
| variance reduction | understand adjusted precision |
| time series | novelty/primacy/assignment anomalies |

A panel that omits important fields is not automatically invalid, but the missing information limits what can be claimed.

## Confidence-interval decision patterns

For a benefit-positive metric:

- `[positive, positive]`: directional evidence; compare lower plausible effect with implementation/risk cost.
- `[negative, negative]`: evidence of harm on that metric.
- `[-tiny, +tiny]`: likely practically negligible within that interval.
- `[meaningful negative, meaningful positive]`: inconclusive.

For harm-positive metrics (errors, churn, latency), reverse the interpretation.

Do not reduce an interval to “significant/not significant”. Magnitude and uncertainty are both decision inputs.

## P-values

A p-value is computed under a null model. It does **not** tell you the probability the treatment is effective and it does not say whether the effect is large enough to matter.

Check:
- pre-committed alpha/decision rule;
- fixed-horizon vs sequential method;
- whether repeated looks/early stopping were supported by the method;
- multiple comparisons.

## Multiple testing

Multiplicity can arise from variants × metrics × segments × windows. Useful strategies include:

- pre-register one primary metric and core population;
- separate confirmatory from exploratory results;
- use appropriate family-wise-error or false-discovery-rate correction when the analysis plan calls for it;
- replicate material post-hoc findings.

Do not select the correction method after seeing results merely to cross a threshold.

## Sequential testing

Classical fixed-horizon inference assumes a planned analysis point. If the team watches results repeatedly and stops opportunistically, false-positive control can degrade. Sequential/always-valid methods are designed for repeated looks, usually with an efficiency cost.

Record which method the platform actually uses instead of assuming from the UI.

## CUPED / variance reduction

Pre-experiment covariates can reduce variance when they predict the outcome. Applicability depends on:
- available pre-period data;
- correlation with the metric;
- correct implementation.

Use the documented adjusted estimate consistently. Do not choose adjusted vs unadjusted based on which one is more favorable.

## Heterogeneous treatment effects

Different segments can react differently. Distinguish:
- pre-registered segments → interpretable evidence within the planned analysis;
- post-hoc slicing → exploratory hypothesis unless independently confirmed.

Before shipping segment-specific behavior, include product/engineering cost and whether targeting is stable/ethical/operationally feasible.

## Ratio metrics

Rates and per-user averages are ratios. Their uncertainty may require methods such as delta-method, bootstrap or model-based estimators that account for numerator/denominator dependence. Do not apply a naive independent variance formula without checking methodology.

## Network/interference effects

If one user's treatment changes another user's outcome (marketplaces, social/collaboration networks, referrals), standard independent-user experiments can be biased. Record interference risk and route back to experiment design/data experts when material.

## Dashboard reconciliation

When experiment and BI metrics differ, compare before escalating:

`metric formula → population → assignment/eligibility → attribution window → timezone → event source → dedup/identity → filters → late data → currency/unit`

Different definitions can make both numbers internally correct.

## Decision language

Prefer:
- “Evidence supports a positive effect of approximately X with interval Y under method Z.”
- “Result is inconclusive across effects we would consider material.”
- “Post-hoc segment result is exploratory and needs confirmation.”

Avoid:
- “The design is proven better.”
- “There is a 96% chance it works” from `p=.04`.
- “No significance means no effect.”
