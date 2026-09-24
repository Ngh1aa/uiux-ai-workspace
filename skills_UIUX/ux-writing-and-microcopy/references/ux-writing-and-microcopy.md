# UX Writing & Microcopy — Pinned Synthesis

Source reviewed: `hueyexe/frontend-agent-skills@2841c079dd8a9c634882227194dc42e25227710d`, `ux-writing-content-design` (MIT).

This reference adapts its product-copy discipline to `skills_UIUX` project truth, accessibility, system-reality and phase-aware verification.

## Principles

1. Words are interaction material, not decoration.
2. Start from the user's task and legitimate product goal.
3. Prefer comprehension/action/trust/recovery over cleverness.
4. Design the conversation across states, not isolated strings.
5. Put copy in the right component/pattern.
6. Write in actual UI context and constraints.
7. Label actions by consequence when consequence matters.
8. Treat errors as stress/recovery scenarios.
9. Explain sensitive asks and avoid excluding users with unnecessarily narrow choices.
10. Be concise without becoming cryptic.
11. Measure high-stakes copy changes when evidence is needed.
12. Ensure strings work with semantics, accessibility and localization.

## Action labels

Prefer:

```text
verb + object/result
```

Examples of structure:
- `Download report`
- `Create account`
- `Pay 240,000₫`
- `Delete project`

Vague labels can still be valid when the surrounding flow makes the consequence unmistakable. Do not mechanically lengthen every button.

## Forms

- visible label identifies the field;
- hint explains only non-obvious format/constraint/purpose;
- validation is specific to the fix;
- long forms may need an error summary in addition to field-level errors;
- sensitive data requests explain purpose and optionality when applicable.

## Errors — Avoid → Explain → Resolve

### Avoid

Improve labels, constraints, validation timing and interaction so the error is less likely.

### Explain

State the problem in user terms. Avoid raw backend codes and blame.

### Resolve

Offer only actions the system can actually perform: correct, retry, undo, alternate path, wait, or support.

Pattern:

```text
[Problem]. [Specific recovery action].
```

## Empty states

Good empty states answer:

1. what is absent;
2. why/when it matters if not obvious;
3. what useful action is available next.

Do not force a CTA when the user genuinely cannot or need not act.

## Success and loading

Success copy may need to clarify visibility, delivery, billing, permissions or reversibility. Loading copy should not invent exact time estimates unless the system knows them.

## Notifications

Interruption cost should be justified by relevance, urgency or action. A notification that cannot help a decision/action may belong in passive history instead.

## Sensitive/high-stakes moments

Use restrained, explicit language for:

- money/subscription;
- identity/security;
- consent/privacy;
- destructive/irreversible actions;
- health/legal/regulatory contexts.

Friendly tone must never obscure consequence.

## Accessibility / localization

- pair visible text with programmatic labels/descriptions where required;
- errors/status changes need appropriate semantic association/live feedback;
- avoid strings assembled in word order that cannot localize safely;
- allow expansion for Vietnamese/English and future locales;
- do not use color/position alone to communicate message meaning.

## Evaluation

For consequential copy, possible verification includes:

- task-completion/usability testing;
- comprehension checks;
- support/contact reasons;
- funnel/behavioral metrics with user-harm guardrails;
- A/B tests only when experimental risk/traffic justify them.

No outcome data → no claim that new wording improved conversion or retention.
