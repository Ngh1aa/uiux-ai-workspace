# Example — Good progressive-disclosure package

```text
form-ux/
├── SKILL.md
├── references/
│   └── validation-and-recovery.md
├── checklists/
│   └── form-gate.md
└── examples/
    └── multi-step-lead-form.md
```

`SKILL.md` không chứa 300 dòng ARIA/HTML sample. Nó nói:
- khi nào form cần multi-step;
- field grouping/validation/recovery principles;
- khi nào đọc reference;
- trước release chạy checklist;
- example chỉ đọc khi cần concrete output.

Đây là progressive disclosure: agent không trả context cost cho detail không liên quan task hiện tại.
