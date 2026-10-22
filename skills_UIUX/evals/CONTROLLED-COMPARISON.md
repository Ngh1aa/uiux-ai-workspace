# Controlled skill comparison

Canonical execution remains provider-neutral: adapters run tasks and the existing
`scripts/eval-harness.py` validates/aggregates results. No separate orchestrator,
paid-provider call or automatic human-validation claim is introduced here.

## Predeclare and freeze

1. Choose concrete decision tasks, representative positive/near-miss/complex cases,
   response contract and rubric **before** reading outputs.
2. Freeze/hash brief, fixture, response contract, rubric and the exact skill files
   supplied. Baseline has no added skill context; candidate has only the relevant
   owner/resources. Both keep the same task, facts, tools and output constraints.
3. Use clean isolated agent contexts per attempt. Counterbalance dispatch/order;
   do not show an agent the other arm or the held-out answer key.
4. Keep model/settings/tool availability comparable. If the host does not expose
   exact model, sampling or reasoning settings, record this explicitly and report
   an exploratory pilot, not a tightly controlled causal model experiment.
5. Use at least two repetitions per task/arm for an initial pilot where available;
   this is a starting design, not a statistical power claim. Preserve all attempts,
   failures and exclusions with reasons. Do not rerun only the losing condition.

## Grade observable outcomes

Randomize labels for a reviewer who has not seen the arm mapping. Preserve rubric,
raw responses and per-criterion observations/artifact references. Deterministic checks
can establish state/contract facts; expert/model review can evaluate decision rationale.
Human usability and preference require their own evidence. A protocol-only task cannot
be graded as visually verified, even if its reasoning is sound.

Each JSONL row keeps the normal ADAPTER-CONTRACT fields and adds:

```json
{
  "pair_id": "repeat-01",
  "condition": "baseline",
  "environment": {
    "brief_sha256": "64 lowercase hex characters",
    "response_contract_sha256": "64 lowercase hex characters",
    "rubric_sha256": "64 lowercase hex characters",
    "model": "actual identity or inherited-host-default-unreported",
    "settings": {"reasoning": "reported setting or unreported", "output_constraint": "same declared limit"},
    "tools": ["same declared tools"]
  },
  "graders": {"agent_rubric": {"artifact": "review.json", "limitations": "not human research"}}
}
```

Use `condition=candidate` in the other file. Pair identity is `(task_id,pair_id)`.
Do not reuse a response across repetitions. The harness rejects missing/duplicate pairs
or mismatched briefs/contracts/rubrics/settings/tools; it checks declarations, not
authenticity. Store output and skill digests with the evidence packet and inspect them.

```sh
python -B skills_UIUX/scripts/eval-harness.py compare --baseline baseline.jsonl --candidate candidate.jsonl --json
```

Report sample size, per-task outcomes, regressions/ties and grader limitations.
Small-sample score differences are descriptive. Do not publish statistical significance,
causal uplift, universal design superiority, real-user preference or learner mastery
without a study that supports those claims. An unchanged score is a valid result.
