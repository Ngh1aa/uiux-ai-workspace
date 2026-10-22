# Benchmark Methods Reference

Read this when you need the exact computation for a benchmark metric, need to justify a sample size, are building a HEART worksheet, or want a model of a filled task row.

## 1. Adjusted Wald interval for completion rate

Use for any binary metric (task success, error-free completion). It is the default recommended by Sauro and Lewis for small-sample usability data.

Steps, for x successes out of n attempts at 95% confidence (z = 1.96):

1. p_adj = (x + z^2 / 2) / (n + z^2), which is roughly (x + 1.92) / (n + 3.84).
2. n_adj = n + z^2.
3. Margin = z * sqrt(p_adj * (1 - p_adj) / n_adj).
4. Interval = p_adj plus or minus margin, clipped to 0 and 1.
5. Report the observed rate (x / n) as the point estimate and the adjusted interval beside it.

Reference values (computed with the steps above):

| x / n | Observed | 95% adjusted Wald CI |
|---|---|---|
| 5 / 5 | 100% | about 51% to 100% |
| 6 / 12 | 50% | about 25% to 75% |
| 10 / 12 | 83% | about 54% to 97% |
| 18 / 20 | 90% | about 69% to 98% |

Reading: 5 of 5 users succeeding is consistent with a true rate near 50%. That is why small-sample "100%" claims fail the gate.

## 2. Task time

- Decide before the study whether efficiency is measured on successful attempts only (common) or all attempts with a timeout.
- Task time distributions are right-skewed. For small samples report the geometric mean: exp(mean(ln(t))). It is less pulled by a single slow participant than the arithmetic mean.
- Compute the confidence interval on ln(t) with a t-distribution, then exponentiate the bounds.
- Example: times 62, 75, 80, 95, 110, 240 s give arithmetic mean about 110 s and geometric mean about 99 s.
- Do not compare time across rounds if the task start state or data changed.

## 3. Questionnaires

| Instrument | When | Scoring notes |
|---|---|---|
| SEQ | After each task | Single 7-point item. Report mean with CI per task. Compare tasks against each other and against prior rounds. |
| SUS | End of session, comparable with history or norms | 10 items, alternating positive and negative. Odd items: score minus 1. Even items: 5 minus score. Sum times 2.5 gives 0 to 100. It is not a percentage. Verify current norm tables and grade curves in Sauro and Lewis before labelling a score. |
| UMUX-Lite | Short intercepts, in-product surveys | 2 items. Published regression adjustments exist to put it on a SUS-like scale; verify current guidance and state which version you used. |

Rules: do not drop or reword items of a standardized instrument; translated versions should be validated or flagged as unvalidated.

## 4. Sample-size reasoning

Formative (discovery):
- Small rounds per distinct user group are effective for finding frequent problems; repeat rounds after fixes rather than enlarging one round.
- Report problems, frequency observed and severity. Do not report percentages as population estimates.

Summative (benchmark or comparison):
- Start from the decision: "we need to know whether success is above the 80% target" or "detect a meaningful change from baseline".
- Choose an acceptable margin of error. Binary metrics need many more participants than continuous metrics (SEQ, time) for the same margin.
- Use the sample-size tables or calculators in Sauro and Lewis for the specific design (single proportion against a target, two independent proportions, paired). Do not hardcode a single magic number.
- If budget caps n, compute the margin you will actually get and state it. If that margin straddles the decision threshold, label results directional.

Comparison designs:
- Within-subjects: each participant uses both designs, counterbalance order, fewer participants needed, watch for learning and fatigue.
- Between-subjects: separate groups, more participants, cleaner when tasks teach the domain.

## 5. HEART with Goals, Signals, Metrics

Fill only the rows the decision needs.

| Category | Goal | Signal | Metric | Guardrail |
|---|---|---|---|---|
| Happiness | Users feel checkout is easy | Post-task survey | Mean SEQ on checkout task | Survey response rate does not collapse |
| Engagement | (often not needed for transactional flows) | | | |
| Adoption | New users try saved addresses | Feature first use | % of new accounts saving an address in 7 days | Address errors per order |
| Retention | Buyers come back | Repeat purchase | 90-day repeat purchase rate | Refund rate |
| Task success | Users complete checkout correctly | Order placed with no correction contact | Completion rate, error rate | Support contacts per 100 orders |

Guardrails catch improvements that move the primary metric by harming something else. Write the threshold that would block release before the data arrives.

## 6. Worked example: filled task row (before and after)

Before (weak):

> Checkout: 4 of 5 users succeeded (80%). Users found it easy. Average time 2 minutes.

Problems: no success criterion, no interval, no instrument, arithmetic mean on 5 times, no baseline comparison.

After (benchmark-ready):

| Task ID | Task (frozen wording) | Success criterion | n | Success % (95% adj. Wald CI) | Geo-mean time, successes (CI) | Mean SEQ | Top failure cause | Change vs baseline |
|---|---|---|---|---|---|---|---|---|
| T3 v2 | "Buy the blue running shoe in size 42 and ship it to your work address." | Confirmation page reached with SKU size 42 and work address; no moderator help | 20 | 90% (about 69% to 98%) | 97 s (CI on log scale, reported) | 5.8 of 7 | 2 users missed address switcher below fold | Baseline 50% of 12 (about 25% to 75%); intervals overlap only between about 69% and 75%; protocol identical; report as likely improvement, confirm with significance test fit to design |

Notes on the after row: task wording and criterion are versioned (T3 v2 means wording revision 2, which matched baseline); interval is shown; qualitative cause is attached; the comparison claim is qualified, not overstated.

## 7. Report limitations section prompts

- What protocol or environment changed between rounds?
- Which segments are too small to interpret?
- Which tasks were moderated versus unmoderated?
- What would change the conclusion?
