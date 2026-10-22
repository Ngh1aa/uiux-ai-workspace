# Worked synthesis: contradiction and severity

All observations below are **synthetic teaching fixtures**, not sessions, quotations
or analytics. They demonstrate reasoning only. The real research ledger remains empty
until actual evidence is ingested through `research-evidence-pipeline`.

Decision: should an appointment flow prioritize a larger hero or a clearer request state?

| ID | Fixture observation | Interpretation / limit |
|---|---|---|
| S1 | A pending request and a confirmed appointment use the same short label. | Risk of wrong expectation; not evidence a person actually misunderstood it. |
| S2 | A back transition restores defaults over edited contact input. | Reproducible state-loss candidate; verify in runtime. |
| S3 | An author prefers the larger hero. | Aesthetic opinion; cannot establish patient comprehension. |
| S4 | A hypothetical funnel shows fewer review starts after a layout change. | Signal with confounders: traffic, eligibility, instrumentation and time window unknown. |
| S5 | One scenario requires assistive navigation to the error. | Potential severe exclusion even if infrequent; inspect focus/error association. |
| S6 | Another scenario benefits from a readable context image. | Contradicts a blanket image ban, not the need to fix S1/S2. |

Synthesis: prioritize truthful state, input retention and reachable errors. Keep an
image only where it contributes relevant context without displacing the task.
Do not declare “patients prefer no hero” or attach a conversion percentage.

Decision trace: S1/S2/S5 → task completion/recovery risk → inspect source/runtime →
fix state/feedback/focus owner → rerun the same scenarios. S3/S6 → direction
hypothesis → compare matched content/state with declared questions → seek human
calibration. S4 → check event definitions and comparable segments before attributing
a cause. Keep unresolved and contradictory evidence visible.

For actual work, replace each fixture with an evidence ID and explicit source class;
link observation → pattern → interpretation → decision → retest. Do not count fixture
rows as participants, repeated findings or support for clinical policy.
