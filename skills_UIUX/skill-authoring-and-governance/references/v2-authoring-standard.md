# V2 Skill Authoring Standard

## Description quality

Good description trả lời trong 1–3 câu:
- skill làm gì;
- khi nào trigger;
- domain/object vocabulary user thường dùng.

Bad: `Helps with design.`
Good: `Audits and redesigns existing websites while preserving valuable content, URLs and behavior. Use before visual redesign, IA consolidation or migration work.`

## Main-file budget

Main file nên giống runbook/table-of-contents:
- goal;
- prerequisites;
- decisions;
- workflow;
- resource routing;
- outputs;
- acceptance criteria;
- anti-patterns quan trọng.

Nếu có nhiều code samples, reference tables hoặc dài >500 lines, tách resource.

## Resource routing

Main skill phải nói **khi nào đọc** resource:

```markdown
- Need keyboard/dialog specifics? Read [interaction reference](references/interaction.md).
- Before release run [QA checklist](checklists/gate.md).
- Need a concrete output shape? Read [example](examples/report.md).
```

## Time-sensitive knowledge

Không ghi “current/latest” như fact vĩnh viễn. Viết:
`Verify current official guidance before applying version-specific thresholds.`

## Evals

Capability mới đáng kể cần tối thiểu 3 representative eval concepts:
1. positive trigger;
2. near-miss/negative trigger;
3. complex composition/failure case.

Không overfit expected tool sequence. Grade artifact/outcome.
