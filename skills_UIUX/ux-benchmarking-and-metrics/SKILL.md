---
name: ux-benchmarking-and-metrics
description: Define and measure usability outcomes so redesign quality can be compared over time instead of judged only by appearance. Use for before/after redesigns, critical flows, product health checks or recurring UX measurement.
---

# UX Benchmarking & Metrics

## Goal

Produce a repeatable measurement of how well representative users complete critical tasks, so a redesign can be judged against a documented baseline with honest uncertainty. A benchmark answers "did it get better, by how much, and how sure are we", not "does it look better".

## When not to use

- Defining product analytics events, funnels or A/B test plans: use `analytics-and-experimentation`.
- Reading a finished experiment (ship, kill, iterate): use `experimentation-interpretation`.
- Finding usability problems to fix (formative, small n): use `moderated-usability-testing`.
- Journey or service-level outcome loops across channels: use `journey-outcome-and-service-health`.
- Connecting outcomes to production instrumentation: use `outcome-metrics-and-instrumentation`.

## Prerequisites

- A named decision the benchmark informs (release go/no-go, redesign comparison, quarterly health).
- Top tasks list (see `audience-intent-and-top-tasks`) and the segments that matter.
- Access to a comparable environment for baseline and follow-up rounds.

## Decisions

**Formative or summative.** If the goal is to find and fix problems, it is formative: small samples, iterate, report issues and severity, no percentages with false precision. If the goal is to compare against a baseline, competitor or target, it is summative: fixed protocol, larger sample, confidence intervals. Never mix both in one round and then report formative findings as benchmark numbers.

**Task success definition.** Write the success criterion before any session, as an observable end state (e.g. "order confirmation page reached with correct size and address"), not "user felt done". Decide up front whether partial success counts; default to binary success for benchmarks and record partials as a separate code. Freeze the wording, start state, data and success criterion across rounds; any change breaks comparability and must be logged.

**Questionnaire choice.**
- Post-task ease: SEQ (single 7-point item) after each task. Cheap, sensitive, comparable across tasks.
- Post-study perceived usability: SUS when you need comparability with published norms and history (10 items, 0 to 100 score; a mean around 68 is commonly cited as average, verify current norms in Sauro and Lewis).
- UMUX-Lite (2 items) when survey length is constrained, e.g. in-product intercepts; it tracks SUS closely but report which instrument was used and do not silently mix scales across rounds.
- Do not invent a custom satisfaction scale for a benchmark; you lose norms and reliability.

**Binary success intervals.** Report completion rate with a 95% confidence interval using the adjusted Wald method (Agresti-Coull), which behaves well at small n and near 0% or 100%. Never report "100% success" from 5 users without its interval.

**Task time.** Time only successful attempts for efficiency, or report both and say which. Task times are right-skewed: for small samples report the geometric mean, and compute intervals on log-transformed times.

**Sample size.** Formative: small rounds (often around five per distinct user group) are for discovery, not measurement. Summative: size from the margin of error you can tolerate for the decision. Binary metrics need much larger samples than continuous ones for the same precision; if the budget cannot reach a margin that could change the decision, say so and downgrade to directional.

**Comparison design.** Within-subjects (same people, both designs, counterbalanced order) needs fewer participants but risks learning effects; between-subjects is cleaner for task-learning-heavy flows. Choose before recruiting and state it.

**Product-scale metrics.** For live products, frame with Google HEART (Happiness, Engagement, Adoption, Retention, Task success) and its Goals, Signals, Metrics process. Pick only the HEART categories tied to the decision; one goal can need zero engagement metrics.

**Guardrails.** Every primary metric gets at least one guardrail that would expose gaming: e.g. faster checkout time guarded by error rate and refund contacts; higher engagement guarded by task success and opt-out rate.

## Workflow

1. Select representative critical tasks and user segments. Tie each task to a top task and the decision it informs.
2. Define task success before testing: observable end state, partial-success rule, timeout, assistance rule.
3. Choose metrics that answer a decision: success, completion quality, time, errors and recovery, ease or satisfaction (SEQ, SUS or UMUX-Lite) and relevant behavior analytics. Add guardrails.
4. Capture baseline under documented conditions: device, environment, build, data, moderation mode, sample and recruit criteria.
5. Test comparable tasks after design changes with the same protocol, scripts and success definitions.
6. Pair numbers with qualitative causes: observed failure points, quotes, error codes per task.
7. Report trend, uncertainty and limitations: intervals, sample, what changed in protocol, what the data cannot say.

## Rules

- Do not optimize vanity metrics at the expense of task success.
- Keep task definitions stable across benchmark rounds; version them.
- Segment by device or context only when it materially affects interpretation; small segments inflate noise.
- Treat small samples cautiously; do not fake statistical certainty. No significance claims without a test that fits the design.

## Anti-patterns

- Moving the goalposts: rewording a task or loosening the success criterion in round two, then claiming improvement.
- Reporting means of SUS item scores, or calling a SUS score a percentage.
- "Users loved it": quoting satisfaction while completion dropped.
- Averaging raw task times with a few very long outliers and declaring the new design slower.
- Counting assisted completions as successes because the moderator "only hinted".
- Benchmarking against a competitor on different devices or with different recruit criteria.
- Dashboards full of engagement metrics with no task success metric and no guardrail.
- Five-user test results presented as "80% of users".

## Resources

- Need formulas, sample-size reasoning, HEART worksheet or a filled example? Read [benchmark methods reference](references/benchmark-methods.md).
- Before publishing a benchmark report, run [benchmark gate](checklists/benchmark-gate.md).

## Output

A benchmark report containing:

1. Decision and scope, protocol version, dates, environment, sample and recruit criteria.
2. Task table:

| Task ID | Task (frozen wording) | Success criterion | n | Success % (95% adj. Wald CI) | Geo-mean time, successes (CI) | Mean SEQ | Top failure cause | Change vs baseline |
|---|---|---|---|---|---|---|---|---|

3. Study-level questionnaire score (SUS or UMUX-Lite) with CI and instrument name.
4. Guardrail table: metric, threshold, observed, pass/fail.
5. Limitations and protocol deviations.

## Quality gate

Metrics answer a real product question and use the same success definition before and after the change.

- PASS only if every task has a success criterion written before the first session.
- PASS only if task wording, start state and success criterion are identical across compared rounds, or deviations are logged and comparison is downgraded.
- PASS only if every completion rate is shown with n and a confidence interval.
- PASS only if the questionnaire is a named standard instrument and scoring follows its published method.
- PASS only if each primary metric has at least one guardrail.
- FAIL if formative-round numbers are presented as benchmark percentages.

## Baseline and sources

- Sauro and Lewis, Quantifying the User Experience (adjusted Wald, geometric mean task time, sample size, SUS norms). Verify current norms before quoting thresholds.
- Brooke, SUS (1986); Lewis and colleagues on UMUX-Lite; Sauro on SEQ.
- Rodden, Hutchinson and Fu, Google HEART framework and Goals, Signals, Metrics.
- NN/g task-success guidance and standard usability-measurement practice; ISO 9241-11 (effectiveness, efficiency, satisfaction).
