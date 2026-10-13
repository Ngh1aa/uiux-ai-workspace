# Decision provenance and controlled comparisons

Canonical normative owner: `../SKILL.md`. Đây là công cụ thực hiện, không phải một visual direction song song hoặc preset bắt buộc.

## Constraint ledger

| Axis | Hard constraint / starting suggestion / free | Source | Design consequence |
|---|---|---|---|
| Palette | phân loại theo đúng lời user | brief / verified guideline | accent roles, available alternatives |
| Font | kiểm family, rights, glyphs; suggestion không tự trở thành lock | brief / project fonts | reading and technical roles |
| Composition | mặc định free nếu chưa có preserve contract | buyer job / evidence | first anchor and decision object |
| Scale / spacing / density | free hoặc project tokens | project / retrieved rule / hypothesis | numeric desktop/mobile roles |
| Imagery / motion | rights, truth and accessibility boundaries | asset reality / task | selected source/treatment/budget |

## Numeric knowledge boundary

Repo có generic retrieved readability rules trong `vendor/ui-ux-pro-max/engine/data/ux-guidelines.csv` (mobile body 16px minimum, body line-height 1.5–1.75, modular scale example 12/14/16/18/24/32). `vendor/ui-ux-pro-max/skills/design-system/references/primitive-tokens.md` có type scale 12–48px, 4px spacing base; `semantic-tokens.md` minh họa component/section/page spacing roles. Engine density tiers có candidate spacing scales. Đây là generic examples, không phải hero size hoặc section rhythm riêng cho industrial, hospitality hay portfolio.

Đừng lấy 64px hero / 80px section / 1280px container làm default liên project. Chọn số từ content thật: longest headline, paragraph length, proof object size, entry decision, navigation footprint, viewport height và mobile transformation. Lưu measured size, wrap, first decision object's position và critique ở cùng viewport. Document readability checks không phải công thức chứng minh đẹp.

## Controlled comparison

`Layout isolation`: giữ buyer, content, CTA, assets, viewport, palette/font/radius/density như nhau; chỉ đổi composition để kiểm câu hỏi về layout. Đây là một thí nghiệm hẹp, không thay cho khám phá art direction.

`Direction exploration` (v2): giữ audience/content/claims/CTA/state/assets/viewports, đổi có ý nghĩa typography, density và visual-object anatomy trên các trục không bị user khóa. Numeric thresholds trong checker là sanity floor để tránh đổi 0.1px rồi gọi là một direction khác, không phải công thức thẩm mỹ. Typeface có thể giữ nếu type hierarchy/measure khác có ý nghĩa; density phải thể hiện trong gap/padding, không chỉ đổi enum. Object phải khác anatomy, không chỉ tên. Mọi trục bị khóa cần user-source + reason. Palette không bắt buộc đổi để tránh nhầm branding với chất lượng.

So sánh bằng câu hỏi đã định trước: người đọc nhận ra offer/fit nhanh không; proof nào là dominant; next action nằm ở đâu; mobile có mất scope/evidence không; có cần đổi logo/copy là dùng được cho ngành khác không. Chụp và mở ảnh. Ghi preference là heuristic nếu không có practitioners.

Contract v2 giữ questions và criteria trong `comparison_protocol`. CLI tạo reviewer packet không chứa đáp án/mapping; facilitator giữ mapping và counterbalance order. Câu trả lời chỉ được summarize khi đủ candidate/question pairs, có element cụ thể và đúng capture digest. Vắng observations → PLANNED_VALIDATION; agent observations → HEURISTIC_ONLY. Tổng criteria tách comprehension/distinctiveness, tách human/agent; không tạo beauty score/winner. Review cùng tác giả không trở thành blind independent trial chỉ vì nhãn đã randomize.

Nếu muốn kiểm tác động của prompt/knowledge tới model, dùng factorial 2×2: constrained vs free skin, usual context vs focused rules plus decision provenance. Cùng model/settings, brief, assets và viewport; đổi nhãn ngẫu nhiên, ít nhất hai repetitions mỗi cell nếu có quyền provider. Không gọi một agent tự chọn hai layout là causal evidence về model.

## Applied-rule ledger

| Material decision | Rule source + line/section | Prompt role | Actual value/composition | Alternative | Evidence / uncertainty |
|---|---|---|---|---|---|

`LOADED`, `RETRIEVED`, `ADOPTED`, `RENDERED`, `REVIEWED` là năm trạng thái khác nhau. Manifest routing chỉ chứng minh trạng thái routed. PASS technical QA không tự nâng các trạng thái khác.

## Runtime path

Canonical data: `../data/design-knowledge.json`; shared lookup: `uiux-factory/core/skills/design_knowledge.py`. Structured identity selects subject knowledge; page role selects decision anatomy and numeric candidates. Không chọn style trước buyer question. Không freeze một family/font/palette trong data này.

Canonical decision checker: `../scripts/check-design-decisions.py`, schema/model owner `uiux-factory/core/skills/design_decisions.py`. External packet exports active-stage workflow; managed provider loads the bounded foundation/profile/index and can retrieve one role through a read-only tool. Shared context budget includes loaded knowledge. No eager research-stage dataset, no authority escalation.

For a PAGE/REDESIGN/PRODUCT comparison, document regions, their contents/relationships and mobile grouping. Topology fingerprints ignore alternative names, anchor prose and ordering of unchanged regions. This specifically rejects an A/B that only reverses architecture and service-fit sections. It does not score beauty and cannot independently prove a declared topology matches pixels. Review the actual captures.

Scope comparison to representative page roles. A rollout page may set `comparison_required=false` and `inherited_from` to a representative route in the same contract; it still has numeric values, decision traces and inspected desktop/mobile captures of its selected composition. The contract cannot disable every comparison unless an explicit user composition-preservation constraint applies. User-source attribution and inspection remain reviewer declarations; the checker cannot independently authenticate them.

Useful commands from Factory root:

```bash
python -B skills_UIUX/visual-design-direction/scripts/check-design-decisions.py --schema
python -B skills_UIUX/visual-design-direction/scripts/check-design-decisions.py --root <target-root> --phase design
python -B skills_UIUX/visual-design-direction/scripts/check-design-decisions.py --root <target-root> --phase rendered
python -B skills_UIUX/visual-design-direction/scripts/evaluate-design-comparison.py --root <target-root> --route / --seed 27
python -B skills_UIUX/visual-design-direction/scripts/evaluate-design-comparison.py --root <target-root> --plan docs/uiux/comparison-plan.json --observations docs/uiux/comparison-observations.json
```
