# Agent Failure Diagnosis & Recovery

Use this reference only when an agent run is repeatedly failing, looping, drifting, exhausting context/tool calls, or acting on stale environment assumptions. It is a progressive resource for `agent-evaluation-and-reliability`; it is **not** a second orchestrator and does not replace framework-specific debugging or normal feature verification.

Source synthesis: ECC `agent-introspection-debugging` + Matt Pocock `diagnosing-bugs`, adapted to `skills_UIUX` project-truth, evidence and authority rules. See `vendor/agent-runtime-intelligence/SOURCE-LOCKS.md`.

## Principle

`capture the failure → build a discriminating feedback loop → diagnose → contained recovery → verify → encode regression`

Blind retry is not recovery.

## 1. Capture before retry

Record:

```text
Task / real objective
Current role + authority
Last successful step
Last failed tool / command
Exact error/symptom
Recent tool-call sequence
Current branch/cwd/service assumptions
Context pressure / repeated notes
Artifacts/logs available
```

Redact secrets, tokens, cookies, authorization headers and personal data before persisting traces or screenshots.

## 2. Classify the failure

Choose the best-supported class; keep uncertainty explicit.

| Class | Typical evidence |
|---|---|
| logic | wrong hypothesis/algorithm; same state produces wrong result |
| state | stale branch/files/checkpoint; expected write/result does not exist |
| environment | service/port/dependency/browser unavailable or mismatched |
| policy/authority | tool/action is correctly denied or release authority is missing |
| context | objective drift, duplicated low-signal context, obsolete assumptions |
| transient | rate limit/network/intermittent external dependency |

Do not call a policy denial a runtime bug and do not call an environment outage a reasoning failure.

## 3. Build a tight feedback loop

Prefer the smallest command/check that can catch the **exact user-visible failure** and turn green when fixed:

1. failing unit/integration/E2E test at the right seam;
2. curl/HTTP fixture against a local/preview service;
3. CLI fixture + expected output;
4. Playwright/browser check for DOM/console/network/visual symptom;
5. captured trace/request replay;
6. minimal throwaway harness;
7. differential old-vs-new comparison;
8. deterministic repeated/stress loop for a flaky failure;
9. git-bisect-compatible command when regression range is known.

A useful loop is:
- **red-capable** — catches this exact failure;
- **deterministic enough** — or has an explicit reproduction rate for flakes;
- **fast enough** to repeat;
- **agent-runnable** without hidden manual steps, unless HITL is declared.

If no valid loop can be built, stop speculation and state what evidence/access is missing.

## 4. Minimise

Shrink the repro one variable at a time. Remove unrelated inputs, components, services, config and steps while re-running the loop.

Done when the remaining parts are materially load-bearing for the failure.

## 5. Generate falsifiable hypotheses

Create 2–5 ranked hypotheses from evidence.

Format:

```text
If <cause> is true, then <specific observation/change> should <predicted result>.
```

Reject hypotheses that cannot make a discriminating prediction.

## 6. Contained recovery

Prefer the smallest reversible action that can validate the leading hypothesis:

1. restate the real objective in one sentence;
2. verify actual filesystem/branch/process/service state;
3. shrink to one failing file/command/route;
4. run one discriminating check;
5. change one variable;
6. retry only after new evidence;
7. stop and escalate when authority, environment, credentials or required business choice is missing.

### Retry contract

A retry must say:

```text
Root-cause hypothesis
What changed since the previous attempt
Safe retry action
Expected evidence
Stop condition
```

Repeating the same action with different wording is not a new attempt.

## 7. Fix + regression

When the correct seam exists:

1. turn the minimal repro into a failing regression check;
2. observe red;
3. apply the smallest root-cause fix;
4. observe green;
5. rerun the original broader feedback loop;
6. remove temporary instrumentation.

If no correct seam exists, report that as an architecture/testability finding instead of adding a shallow false-confidence test.

## 8. Recovery report

```markdown
## Agent Failure Recovery
- Task:
- Failure class:
- Exact symptom:
- Last successful step:
- Feedback loop:
- Root-cause hypothesis:
- Recovery action:
- Evidence after recovery:
- Result: success | blocked
- Regression encoded:
- Follow-up / preventive change:
```

Map `partial`/unverified recovery to the owning phase's canonical ledger state; do not invent a PASS.

## Red flags

- three retries without a changed hypothesis or world-state check;
- debugging from memory while branch/cwd/service state is unverified;
- giant log dumps instead of a discriminating probe;
- changing multiple variables at once;
- calling an authorization denial an error to bypass;
- deleting/resetting user work to “get clean” without explicit authority;
- claiming recovery from one green build when the original user-visible repro was never rerun.

## Verification

- [ ] Failure state captured and secrets redacted.
- [ ] Failure class is evidence-backed or marked uncertain.
- [ ] A red-capable feedback loop exists, or missing evidence/access is explicit.
- [ ] Recovery action is minimal and reversible where possible.
- [ ] Original repro was rerun after the fix.
- [ ] Stable failure becomes a regression test/eval/checklist when justified.
