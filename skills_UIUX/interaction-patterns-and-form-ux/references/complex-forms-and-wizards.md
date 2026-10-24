# Complex Forms & Wizards

> Hướng dẫn con của skill `interaction-patterns-and-form-ux` (trước đây là skill `complex-forms-and-wizards`). Dùng khi: Design multi-step, conditional or high-stakes forms with progress, validation, review, save/resume and recovery. Use for admissions, applications, checkout, booking, CRM, onboarding or document-heavy forms.

## Workflow

1. Inventory data requirements and remove unnecessary fields.
2. Group questions by mental model and dependency.
3. Choose one-page versus multi-step based on complexity and interruption risk.
4. Design progress, conditional branches, back behavior and skipped states.
5. Validate at useful moments while preserving input.
6. Provide review/edit before irreversible submit.
7. Add save/resume, timeout and recovery where the journey warrants it.

## 1. Question audit (before any layout)

For every field ask, and record the answer:

| Field | Who needs it | Why now (not later) | Can we infer / pre-fill? | Required? |
|---|---|---|---|---|

Remove, defer (ask after value is delivered) or pre-fill before designing. The best field is the one you did not ask.

## 2. One page or steps

| Signal | Lean to |
|---|---|
| ≤ ~7 related fields, one topic | Single page |
| Distinct topics, branching, documents, payment | Steps (wizard) |
| Users often interrupted / need documents they may not have | Steps + save/resume |
| Expert repeat users | Single page with sections, keyboard-friendly |

"One thing per page" (GOV.UK) helps for complex public-service style forms; test before assuming it for expert tools.

## 3. Wizard anatomy

- Step indicator with names, not just numbers; shows what remains.
- Back keeps all entered data; browser/system back behaves like in-app back.
- Branches: skipped steps disappear from the indicator rather than showing as incomplete.
- Review page lists every answer with "Change" links that return to review after editing.
- Final action labelled with its consequence ("Submit application", "Pay 1.200.000đ"), not "Next".

## 4. Validation

| Timing | Use for |
|---|---|
| On blur (after leaving a field) | Format errors (email, phone) |
| On submit of step | Required fields, cross-field rules |
| Live while typing | Only for helpful constraints (password rules, character count) |

Error summary at top with links to fields + inline message at the field. Never clear valid input on error. Never disable the submit button without saying why.

## 5. Field patterns (Vietnam-relevant)

- Phone: accept spaces and +84, normalise server-side.
- Name: one "Full name" field unless legally required otherwise; no forced first/last split.
- Address: province/district/ward pickers must allow search; administrative boundaries change, so keep data source updatable.
- Dates: native date pickers on mobile; show format; accept typed dates for birthdays.
- Currency: format with thousands separators as the user types; show the unit.

## 6. Save, resume and timeout

- Long or document-heavy forms autosave drafts and say so.
- Before a session timeout, warn with time to extend; after it, restore the draft.
- Resuming lands on the first incomplete step with a summary of progress.

## Quality gate

- Users know where they are and what remains.
- Back/edit does not destroy valid input.
- Errors preserve context and point to correction.
- Redundant entry is removed unless there is a strong reason.
- Every field passed the question audit.
- Review step exists before irreversible submit.
