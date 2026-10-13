# Direction comparison specimen

Đây là mẫu kiểm công cụ, không phải template để clone thành website khách hàng. Hai brief minh họa (software governance và industrial modernization), cùng renderer/data owner, hai direction: compact scope matrix và expressive stage chain. Font hệ thống tránh yêu cầu download/license asset; không quy định Arial/Georgia cho project thật.

## Chạy local

Từ Factory root:

```sh
python -m http.server 8092 --bind 127.0.0.1 --directory skills_UIUX/visual-design-direction/examples/direction-study
```

Mở `http://127.0.0.1:8092/?case=enterprise&direction=register`, đổi `case=industrial` hoặc `direction=sequence`. Query sai fallback theo own-property allowlist.

Capture dùng **Playwright + axe đang có** trong môi trường QA, không tự install/provider call:

```sh
node skills_UIUX/visual-design-direction/examples/direction-study/capture.cjs http://127.0.0.1:8092/ /path/to/evidence
```

Node cần resolve `playwright` và `@axe-core/playwright` từ QA/runtime hiện tại; có thể dùng `NODE_PATH` trỏ tới các node_modules đó. Không nâng version trong project chỉ để chạy specimen.

Capture kiểm 2 cases × 2 directions × 8 widths (1440/1280/1024/768/480/390/360/320), cùng facts/action, numeric/render drift, query fallback và keyboard. Axe scan ở1440/390/320. Script không đánh dấu `inspected` hoặc tạo lời đánh giá/human observations.

## Recorded example

[Evidence](../../../../docs/evidence/design-direction-study/README.md) có contract v2, 12 PNG đã mở, plan và observations. Same-author review được ghi heuristic/unblinded; không có practitioners, preference hay causal uplift.

```sh
python -B skills_UIUX/visual-design-direction/scripts/check-design-decisions.py --root docs/evidence/design-direction-study --contract design-decisions.json --phase rendered
python -B skills_UIUX/visual-design-direction/scripts/evaluate-design-comparison.py --root docs/evidence/design-direction-study --contract design-decisions.json --plan enterprise-plan.json --observations enterprise-observations.json
```

Contract/rubric phải được viết trước review trong project thật. File minh họa này ghi lại một sanity trial của công cụ, không tạo tiền lệ sinh answers tự động. `comparison_record` nối đúng plan/observations tới representative route; đổi contract hoặc capture phải tạo lại plan và thực hiện review lại. Chỉ publish reviewer packet + anonymous captures cho người đánh giá; facilitator mapping/criteria không được đưa trước câu trả lời.
