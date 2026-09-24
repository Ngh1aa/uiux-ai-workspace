# V5 Eval Adapter Contract

`skills_UIUX` stays model/provider-neutral. A Claude Code, Copilot, Codex, Antigravity or other runner may execute a task differently, but it should emit one JSON object per trial to a JSONL results file.

## Trial result

Required fields:

```json
{
  "task_id": "v5-agent-reliability",
  "trial_id": "trial-001",
  "passed": true,
  "score": 88
}
```

Optional recommended fields:

```json
{
  "graders": {
    "deterministic": {"passed": true, "details": ["build", "tests"]},
    "rubric": {"score": 84},
    "human": {"status": "not-run"}
  },
  "environment": {"agent": "...", "model": "...", "commit": "..."},
  "artifacts": ["path-or-uri"],
  "notes": "Known limitation..."
}
```

## Routing/context telemetry

Recommended for routing/context benchmark tasks:

```json
{
  "routing": {
    "activated_skills": ["project-context", "accessibility", "ui-improvement"],
    "activation_reasons": {
      "project-context": "project truth first",
      "accessibility": "focus trap is a11y concern",
      "ui-improvement": "existing component remediation"
    },
    "skill_context_chars": 12840,
    "reference_context_chars": 3200,
    "total_loaded_context": 16040
  }
}
```

Installed skills are availability, not active context. Context telemetry should measure what was actually loaded.

## Runtime/tool telemetry

When an adapter uses the V5.2 runtime foundation, it may also emit:

```json
{
  "runtime": {
    "run_id": "abc123",
    "agent_role": "implementation",
    "authority": "branch_write",
    "tool_calls": 4,
    "permission_blocks": 0,
    "checkpoint_resumes": 1,
    "trace_artifact": ".uiux-agent-runs/abc123/trace.jsonl"
  }
}
```

Do not put secrets, auth headers, personal data or full sensitive payloads in eval telemetry.

A `permission_blocks` count is not automatically a failure: blocking an unauthorized critical action can be the expected correct outcome.

## Adapter responsibilities

1. Start each reliability trial from a clean comparable environment.
2. Provide the task prompt and project fixture/environment.
3. Let the agent act normally; do not inject hidden success answers.
4. Run deterministic graders after the agent finishes where possible.
5. Run rubric/model/human graders only for dimensions that need judgment.
6. Emit `passed` using the task's declared release threshold/hard-fail policy.
7. Preserve detailed grader evidence outside the aggregate score when useful.
8. Preserve runtime authority and system-reality truth; never report a contract-only action as a real external side effect.

## Harness responsibilities

`scripts/eval-harness.py` validates result shape and aggregates repeated trials. It intentionally does not decide which model/provider to run.

Examples:

```bash
python scripts/eval-harness.py list
python scripts/eval-harness.py validate-results --results results.jsonl
python scripts/eval-harness.py summarize --results results.jsonl --k 3
```

`estimated_pass_at_k` and `estimated_pass_pow_k` use the observed trial success rate as an estimate. They must not be presented as guaranteed population reliability.
