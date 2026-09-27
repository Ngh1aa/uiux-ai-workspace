# Task Contract V1

Status: **ACTIVE**  
Introduced by: **A2 — Task Contract + Goal Interpreter**

The Task Contract is the structured interpretation of a user's natural-language UI/UX task. It does not replace the original user request; it makes routing and constraints explicit and inspectable.

## Fields

- `intent` — `build`, `redesign`, `rebuild`, `improve`, `fix`, or `polish`.
- `scope` — affected UI surface(s) inferred from explicit scope language or bounded UI terms.
- `preserve` — existing behavior/assets/direction the user explicitly asks to keep.
- `forbidden` — changes the user explicitly prohibits.
- `references` — explicit URLs or reference phrases supplied by the user.
- `authority` — requested authority inferred from explicit task language; `unspecified` when no authority request is present.
- `task_contract_version` — currently `1.0`.

The existing website/domain/product/mode/risk/features classification remains part of the same task context.

## Authority safety

Natural-language authority is a request, never an escalation mechanism.

The Development Manager computes effective authority as the lower of:

1. the caller/tool authority cap; and
2. an explicitly inferred Task Contract authority.

Therefore:

- `Chỉ audit UI, không sửa code` can reduce `branch_write` to `read_only`;
- `Deploy production after QA` can record `release` as the requested authority;
- the same production phrase cannot raise a caller capped at `branch_write` to `release`.

This preserves the runtime-policy rule: **Never escalate authority implicitly.**

## Focused-intent routing

`improve`, `fix`, and `polish` are first-class intents because `flows/existing-ui-improvement.json` explicitly matches them. A2 aligns the Goal Interpreter with that flow so focused UI work no longer falls through to `build`.

A3 owns change-surface classification (`MICRO`, `FOCUSED`, `PAGE`, `REDESIGN`, `PRODUCT`). A2 does not introduce that adaptive-flow policy.

## Examples

`Sửa hero Nova đẹp hơn, giữ nguyên animation hiện tại.`

- intent: `fix`
- scope: `hero`
- preserve: `animation hiện tại`
- authority: `unspecified`

`Polish mobile nav; do not change information architecture.`

- intent: `polish`
- scope: `mobile-nav`
- forbidden: `information architecture`

`Cải thiện hero, tham khảo https://example.com chỉ về animation.`

- intent: `improve`
- scope: `hero`
- references: `https://example.com`

Reference semantics such as “use only for motion, not layout” are captured more deeply by A11 Reference DNA; A2 only preserves the supplied reference and keeps reference clauses from accidentally expanding change scope.
