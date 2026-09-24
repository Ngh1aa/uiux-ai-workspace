---
name: ux-writing-and-microcopy
description: Designs and reviews product microcopy, action labels, form help, empty/loading/success/error states, notifications and UI terminology as part of the interaction system. Use when interface words materially affect comprehension, action, trust, recovery, accessibility or localization; complements content-design-and-question-design.
---

# UX Writing & Microcopy

## Boundary

This skill owns **string/state-level product UX copy**. `content-design-and-question-design` remains the broader owner for content structure, question design and form information sequencing. `conversion-and-content` remains the owner for marketing/value-proposition content.

Use this skill when the words are part of the interaction itself.

## Core model

`user task → UI state/pattern → copy → system response → next/recovery action`

Do not write isolated strings without the surrounding state when that context changes meaning.

## Workflow

1. Read user task, product goal, brand voice and system reality.
2. Identify the UI pattern/state: label, hint, CTA, validation, error, banner, modal, empty state, loading, success, notification, confirmation.
3. Map the short conversation: entry → instruction → action → feedback → next step → inverse/recovery.
4. Draft accurate/useful copy before shortening or adding personality.
5. Make action labels consequence-revealing when the outcome matters.
6. For errors use `Avoid → Explain → Resolve`.
7. Check stress/sensitivity/trust; remove humor or brand flourish when stakes make it harmful.
8. Make copy implementable with visible/programmatic labels, error associations, live status where needed and localization-safe strings.
9. Verify in the actual component/layout; short copy that clips or loses meaning is not successful.

## Default rules

- Prefer useful over clever.
- Persistent label > placeholder-only label.
- Button/link text names the outcome when consequence matters.
- `Continue`, `Submit`, `OK`, `Save` are acceptable only when context makes the outcome unambiguous.
- Errors say what happened in user terms and what the user can realistically do next.
- Empty states explain what is empty and offer the next useful action when one exists.
- Success feedback confirms the action/consequence; do not celebrate routine high-stakes operations excessively.
- Loading copy sets expectation only when delay is noticeable/meaningful.
- Notifications should justify interruption with relevance or actionability.
- Sensitive data requests explain why the information is needed when that is not obvious.
- Avoid idioms and ultra-compressed strings that break localization or comprehension.

## State-copy matrix

For material flows, account for applicable states:

| State | User question | Copy job |
|---|---|---|
| Default | What can I do? | label/action clarity |
| Helper | What format/constraint matters? | concise guidance |
| Loading | Is it working? | status/expectation |
| Success | What happened? | confirmation/consequence/next step |
| Empty | Why is nothing here? | orientation + next useful action |
| Validation | What must I change? | field-specific correction |
| Error | What failed and how do I recover? | explanation + recovery |
| Permission | Why is this needed? | purpose + consequence |
| Destructive | What will be lost? | explicit scope + safe cancel |
| Offline/retry | What can I do now? | recovery/alternative |

Do not invent states that the real system cannot support; coordinate with `system-reality-and-production-readiness` when recovery depends on backend capability.

## Output

For a flow/component, use:

```text
Component/state:
User task:
Current copy:
Recommended copy:
Reason:
Implementation/a11y note:
Localization note:
Verification:
```

For a design system, capture terminology, CTA patterns, error structure and state-copy patterns rather than a giant string dump.

## Hard rules

- Do not manipulate users with misleading urgency, hidden consequences or friendly language that masks a harmful business goal.
- Do not improvise legal/medical/financial/compliance wording that requires professional approval.
- Do not use humor in payment failure, security, identity, consent or other stressful states unless explicitly justified and reviewed.
- Do not report conversion improvement without outcome data.
- Do not treat tone preference as more important than comprehension, trust or recovery.

## Progressive reference

Read [references/ux-writing-and-microcopy.md](references/ux-writing-and-microcopy.md) for deeper patterns adapted from `hueyexe/frontend-agent-skills` pinned in `vendor/external-uiux/SOURCE-LOCKS.md`.

## Acceptance criteria

- Copy supports a real user task/state.
- Consequential actions are explicit enough for the context.
- Applicable failure/empty/loading/success states are covered.
- Recovery copy matches real system capabilities.
- Accessibility/localization implications are accounted for.
- Recommendations are verified in the actual UI when layout/interaction matters.
