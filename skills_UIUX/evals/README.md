# Agent Eval Suite — V5

Mục tiêu của evals là đo xem agent **có tạo outcome UI/UX tốt và ổn định hơn** khi dùng skill library hay không, thay vì chỉ kiểm nó có nhắc lại nội dung `SKILL.md`.

## Task schema

Mỗi `tasks/*.json` gồm:
- `id`: stable identifier;
- `category`: `capability` / `regression`;
- `prompt`: realistic user request;
- `recommended_skills`: skill có khả năng hữu ích, không phải exact tool-call contract;
- `expected_outcomes`: điều output cuối phải đạt;
- `must_not`: failure modes;
- `rubric`: dimensions và trọng số.

## Cách chấm

Ưu tiên:
1. deterministic grader cho file/code/state/render có thể kiểm chính xác;
2. rubric/model grader cho visual/UX/research judgment;
3. human review để calibrate các grader chủ quan và high-value decisions.

Grade outcome trước tool choreography. Không fail chỉ vì agent dùng flow/tool khác nếu outcome hợp lệ.

## Hai suite

- **Capability**: case khó để hill-climb chất lượng; pass rate ban đầu có thể thấp.
- **Regression**: behavior đã làm tốt; mục tiêu gần 100% để chống backslide.

Capability ổn định có thể được promote sang regression suite.

## V5 multi-trial reliability

Một lần pass không chứng minh reliability. Với behavior cần ổn định, chạy nhiều trial độc lập từ clean/comparable environment.

Khái niệm:
- `pass rate`: tỷ lệ trial pass quan sát được;
- `pass@k`: xác suất có ít nhất một success trong k attempts;
- `pass^k`: xác suất tất cả k attempts đều success.

`scripts/eval-harness.py` báo **estimated** pass@k/pass^k từ observed pass rate. Luôn báo số trial và không diễn giải estimate như guarantee.

## Provider-neutral execution

Repo không lock vào một model vendor. Runner/IDE/provider adapter thực thi task và xuất JSONL theo [ADAPTER-CONTRACT.md](ADAPTER-CONTRACT.md).

```bash
python scripts/eval-harness.py list
python scripts/eval-harness.py validate-results --results results.jsonl
python scripts/eval-harness.py summarize --results results.jsonl --k 3
python scripts/eval-harness.py smoke
```

## Structural validation

```bash
python scripts/validate-skills.py
python scripts/validate-v2.py
```

GitHub Actions chạy structural validation, installer smoke và V5 eval-harness smoke. Model execution vẫn do adapter/provider cụ thể thực hiện.
