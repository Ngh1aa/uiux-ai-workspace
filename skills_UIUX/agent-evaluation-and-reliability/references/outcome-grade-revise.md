# Outcome grade & revise

Source adaptation:
`anthropics/claude-cookbooks@c5ff1dc523e28d9b8fbd5c6ecd63204e20b8a0ed/managed_agents/README.md`

Use this loop when an agent/pipeline output must become reliably acceptable rather than merely complete once.

## Loop

1. **Do** — produce one bounded outcome.
2. **Observe** — collect deterministic/runtime/rendered evidence.
3. **Grade** — compare the outcome against an explicit rubric and allow `unknown` where evidence is missing.
4. **Locate owner** — identify the earliest responsible stage.
5. **Revise** — change that owner, not a downstream symptom.
6. **Re-run affected checks**.
7. **Stop** when the rubric passes or a real blocker is explicit.

## Good graders

Prefer outcome evidence:
- build/tests/runtime state;
- rendered screenshots;
- accessibility/performance checks;
- file/state contracts;
- source-backed research claims.

Use model/human judgment for:
- visual hierarchy;
- domain fit;
- trust/clarity;
- anti-template quality.

## Independence

When practical, the grader should not be the same role that authored the outcome. This reduces self-confirmation and makes failure reports more useful.

## Human gate

Keep a human approval step for:
- irreversible release/merge policy when required;
- regulated/high-consequence business decisions;
- subjective visual sign-off when the project explicitly requires it.

## Version comparison

For material prompt/skill/router changes:
- compare new vs previous behavior on representative tasks;
- record regressions, not just wins;
- roll back or narrow the trigger when the new version harms unrelated tasks.

Do not claim general reliability from one successful revision loop.
