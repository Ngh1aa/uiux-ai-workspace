---
name: skill-authoring-and-governance
description: |
  Reviews, creates and maintains SKILL.md packages in this UI/UX library. Use when adding a new
  capability, splitting an oversized skill, improving discovery descriptions, reducing overlap,
  adding progressive-disclosure resources, profiles or evals, or updating skills after standards change.
---

# Skill Authoring & Governance

## Goal

Mỗi skill phải **discoverable, actionable, composable, testable và context-efficient**.

## Authoring workflow

1. Search existing skill catalog trước khi tạo mới.
2. Define capability boundary: decision nào skill này sở hữu?
3. Write third-person `description` nêu rõ **what + when + trigger vocabulary**.
4. Keep `SKILL.md` focused on decisions/workflow/output/gates.
5. Move detailed knowledge/code/examples sang resource khi nó không luôn cần.
6. Link resource trực tiếp từ `SKILL.md`; tránh reference chain sâu.
7. Add at least representative positive, negative/near-miss và complex eval cases cho capability quan trọng.
8. Run structural validators + representative agent evals trước merge.
9. Update catalog/profile nếu capability cần được routed/cài.

## Reliability feedback rule

Khi một project/user/reviewer phát hiện **obvious generalizable failure** mà skill/routine hiện tại lẽ ra phải ngăn được, skill maintenance không được dừng ở việc sửa wording chung chung.

Phải review theo chain:

```text
observed failure
→ owning skill/checklist/gate
→ why existing wording/gate allowed skip behavior
→ concrete hardening
→ regression eval/task
→ validator/eval execution
→ release note / version update when material
```

Nếu failure có thể tái tạo bằng deterministic check (ví dụ rendered visibility/state contrast/shared-route coverage), ưu tiên thêm deterministic guard/checklist contract bên cạnh judgment guidance.

Không được tuyên bố “đã ngăn tái diễn” nếu chưa có ít nhất một regression mechanism có thể exercise lại failure mode. Skill instruction giúp giảm rủi ro; nó không tạo guarantee tuyệt đối nếu project không chạy required verification.

## Package pattern

```text
skill-name/
├── SKILL.md
├── references/      # optional deep knowledge
├── checklists/      # optional deterministic review gates
├── examples/        # optional concrete examples
└── scripts/         # optional deterministic helpers
```

Không tạo folder/resource rỗng để “đúng template”.

## Frontmatter rules

- `name`: lowercase letters/numbers/hyphens, <=64 chars, match folder name.
- `description`: non-empty, <=1024 chars, third person, what + when.
- Không dùng reserved/model/vendor name trong `name`.
- Metadata phải stable; time-sensitive facts nằm trong reference với verify-current rule khi cần.

## Progressive disclosure rules

- Target `SKILL.md` body <500 lines; ngắn hơn nữa nếu capability cho phép.
- Main file phải đủ để agent quyết định bước tiếp theo mà chưa cần load encyclopedia.
- Resource file có tên mô tả nội dung; tránh `notes.md`, `misc.md`.
- Scripts nên giải quyết deterministic work, không chỉ wrap prompt khác.
- Helper script lớn nên được gọi như black box (`--help`/documented contract) trước khi đọc source; chỉ load source khi cần sửa/diagnose nó.

## Overlap test

Tạo skill mới chỉ khi capability boundary khác rõ. Nếu >70% workflow/rules trùng skill hiện có, ưu tiên extend/refactor.

Trước khi import một external skill, ghi rõ:

```text
capability gap
local owner hiện tại
upstream source + immutable ref + license
ADOPT / ADAPT / REJECT
context cost
verification/eval
```

Không bulk-copy vì repo upstream nổi tiếng; curation > collection.

## Anti-rationalization and red flags

For high-consequence workflow skills, add a short `Common rationalizations` or `Red flags` section when it materially prevents skip behavior.

Good examples:

| Rationalization | Reality |
|---|---|
| “Build pass nên không cần screenshot.” | Build verifies compilation, not rendered pixels. |
| “Task nhỏ nên khỏi đọc project truth.” | Small edits can still violate tokens/behavior/brand. |
| “Retry thêm lần nữa chắc được.” | A repeated identical failure needs diagnosis, not wording changes. |
| “Rule đã có rồi nên user-caught regression chỉ cần sửa project.” | Nếu QA vẫn bỏ lọt một obvious generalizable defect, rule/gate/eval chưa đủ reliable. |

Do not add these sections mechanically when there is no real skip/failure pattern.

## Evaluation

Chấm outcome hơn exact path. Evals nên có:
- task realistic;
- expected outcomes;
- must-not failure modes;
- deterministic assertions khi có thể;
- rubric cho judgment dimensions;
- regression cases cho behavior đã ổn hoặc failure đã được harden.

For material skill changes, prefer a controlled comparison when feasible:

```text
new skill vs old skill
or
with skill vs without skill
```

Track pass rate/score first; then compare tokens/context, duration, retries and tool calls. A skill is not better merely because it produces a longer workflow.

Use multiple trials when variance matters. Keep the environment comparable and do not tune the grader to a preferred choreography.

## V2 resources

- [Authoring standard](references/v2-authoring-standard.md)
- [Review gate](checklists/review-gate.md)
- [Good package example](examples/good-skill-layout.md)

## Acceptance criteria

- Trigger không quá broad/vague.
- Workflow action-oriented, không textbook.
- Output + quality gate rõ.
- Không duplicate capability vô lý.
- Progressive resources có reason và link rõ.
- Relevant eval/profile/catalog được cập nhật.
- Generalizable user-caught regression có concrete prevention mechanism + regression eval khi applicable.
- External source có pin/license/provenance nếu material guidance được adopt.
- `python scripts/validate-skills.py` và `python scripts/validate-v2.py` pass.
