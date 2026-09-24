---
name: experimentation-interpretation
description: Interprets completed product/UX experiment results for ship, kill, iterate or rerun decisions using confidence intervals, practical effect size, p-values or Bayesian outputs, multiple/sequential testing, variance reduction, segments, ratio/network effects and dashboard reconciliation. Use after an experiment has data; use analytics-and-experimentation before launch for hypothesis/design/tracking.
---

# Experimentation Interpretation

## Boundary

This skill owns **post-result interpretation**:

`result panel/raw output → method check → uncertainty/effect size → guardrails → multiplicity/segments → decision → learning`

`analytics-and-experimentation` owns metric definition, instrumentation and pre-run experiment design. This skill does not invent missing statistics or overrule the project's data/experiment owner.

## Workflow

### 1. Verify result context

Before deciding, capture:

- experiment hypothesis and pre-registered primary metric;
- control/treatment variants and allocation;
- sample size and test duration/window;
- statistical method actually used (fixed-horizon, sequential/always-valid, Bayesian, other/UNKNOWN);
- point estimate plus confidence/credible interval when available;
- guardrail outcomes;
- planned segments vs post-hoc slices;
- variance-reduction method such as CUPED if used;
- source/result-panel pointer and date.

Missing method metadata stays `UNKNOWN`. Do not translate a dashboard badge into statistical certainty.

### 2. Read uncertainty before celebrating the point estimate

For frequentist results, interpret the interval and practical magnitude together:

- interval entirely on beneficial side → evidence of directional effect; still judge whether the lower plausible effect is worth the cost/risk;
- interval entirely on harmful side → evidence of harm for that metric;
- narrow interval around negligible effect → useful near-null result;
- wide interval spanning meaningful harm and benefit → inconclusive, not a weak win/loss.

For Bayesian results, use the platform's credible interval/probability framing as documented; do not apply frequentist wording to it.

### 3. Interpret significance correctly

A p-value is not the probability that the treatment works and does not measure effect size. Read it with the interval, effect magnitude and pre-committed decision rule.

If the test was repeatedly inspected, determine whether the method supports sequential/always-valid inference. If not, flag peeking risk rather than silently accepting the displayed threshold.

### 4. Check multiplicity and exploration

Look for multiple:

- variants;
- metrics;
- segments;
- time windows;
- repeated analyses.

Prefer pre-registered primary metric/segment for shipping claims. Corrections such as family-wise-error or false-discovery-rate control may be appropriate depending on the experiment design; do not choose a correction after seeing which one makes the result significant.

Post-hoc segment effects are normally **hypotheses for follow-up**, not standalone ship evidence.

### 5. Check advanced interpretation concerns only when applicable

- **Variance reduction/CUPED:** verify pre-period covariates exist and methodology is documented; narrower uncertainty is useful, not license to cherry-pick adjusted/unadjusted results.
- **Ratio metrics:** ensure the analysis method handles numerator/denominator covariance appropriately; naive independent treatment can misstate uncertainty.
- **Network/interference effects:** if users affect one another, ordinary independent-unit assumptions may fail; surface this as a design/interpretation limitation.
- **Novelty/primacy/time trends:** inspect time series when available before extrapolating a transient effect.
- **Dashboard mismatch:** reconcile population, attribution window, metric definition, filters, timezone, identity stitching and delayed events before claiming one system is wrong.

### 6. Make the decision explicit

Use one of:

`SHIP | KILL | ITERATE | RERUN / GATHER_MORE_DATA | NO_DECISION`

Record:

```text
Primary result:
Uncertainty / practical magnitude:
Guardrails:
Method/multiplicity concerns:
Segment findings:
Decision:
Why:
What this result does NOT prove:
Next learning / regression coverage:
```

## Hard rules

- No result data → no experiment interpretation claim.
- Statistical significance ≠ practical significance.
- No “95% chance it works” from a frequentist p-value/CI.
- Do not cherry-pick a secondary metric/segment after the primary result disappoints.
- Do not call a wide interval a win because the point estimate is positive.
- Do not claim a causal result for populations/periods not supported by the experiment.
- If experiment and dashboard disagree, reconcile definitions before choosing the preferred number.

## Progressive reference

Read [references/experimentation-interpretation.md](references/experimentation-interpretation.md) when deeper statistical interpretation is needed. It is a local synthesis informed by the pinned Rampstack source recorded in `vendor/cross-functional-intelligence/SOURCE-LOCKS.md`.

## Acceptance criteria

- Method, source, sample/window and primary metric are explicit or UNKNOWN.
- Interval/effect magnitude is interpreted before a shipping conclusion.
- Guardrails and multiplicity/segment risks are accounted for.
- Result interpretation distinguishes evidence from exploratory findings.
- Decision includes limitations and next action.
