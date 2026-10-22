# Verification gates, routing regression và benchmark dự án

Ngày báo cáo: 2026-10-23T05:13:06.782310+07:00. Trạng thái: **LOCAL VERIFIED / PROJECT FINDINGS OPEN**.

## Kết quả sửa Factory

- `check-all.sh`: tiếp tục chạy sau lỗi, tổng hợp đầy đủ và trả exit code 1 nếu có check FAIL; pipeline retrieval không được che lỗi producer. Root không tồn tại bị chặn ngay.
- Browser runner: mặc định yêu cầu mọi engine đã khai báo và axe-core không rỗng; CI bắt buộc Chromium/WebKit/Firefox. `--allow-partial` chỉ dành cho local và kết quả thiếu coverage mang nhãn PARTIAL.
- Báo cáo browser bắt đầu bằng RUNNING và kết thúc PASS/FAIL, giữ lỗi thay vì để lại PASS cũ.
- Routing: technical design-system/software/token foundations không tự biến project thành nonprofit. Các positive case tổ chức/quỹ và nonprofit thật vẫn giữ đúng phân loại.
- Không thêm dependency, skill hoặc tầng runtime. Thêm một eval task cho benchmark và regression ở owner hiện có.

## Kiểm tra đã chạy

- 63 targeted Python tests PASS; 11 browser-gate control-flow tests PASS. Mock browser trong unit tests chỉ chứng minh control flow/exit/report, không phải visual evidence.
- 36/36 aggregate local checks PASS, bao gồm full Factory pytest, skills pytest, structural validators và design-system pytest.
- Browser thực cho design system: **36 cấu hình PASS**, ba engine, hai trang, ba kích thước, hai theme; axe chạy, không bỏ engine.
- Baseline replay giữ failure evidence trong `logs/`. Các case lỗi có chủ đích từng bị gate cũ bỏ lọt nay fail đúng; không làm yếu test để tạo PASS.
- Routing near-miss/positive probes: baseline 4/10 đúng, candidate 10/10 đúng, gồm 5 authored cases lặp hai lần. Đây là regression nhỏ, không phải tỷ lệ chính xác tổng quát.
- Generic real-project dogfood: 12/12 lần qua contract/routing, dùng đúng Factory baseline/candidate source. Golden A20 pins không bị thay đổi.

## Thiết kế benchmark

Protocol được ghi trước khi xem đầu ra tại `protocol.json`; ba target được cố định SHA và giữ working tree sạch. Baseline Factory là `fe04a3f2a559f1c38ddb8fdf8f8f857b7b171e7d`; candidate là nhánh local `fix/verification-gates-routing-benchmark`.

Mỗi dự án có ba route, ba tình huống, viewport 390/1440px, Chromium 156.0.8078.4, axe 4.14.0, light theme, reduced motion. Hai lượt mỗi điều kiện, thứ tự baseline→candidate rồi candidate→baseline. Tổng cộng **72 route observations, 72 scenario assertions**, tất cả scenario được chọn đều hoàn tất.

UI target không thay đổi giữa hai arm. Browser adapter giống nhau; chênh lệch Factory được kiểm tra riêng bằng gate regressions và `routing-report.json`. Kết quả browser là baseline chất lượng hiện tại có lặp lại, không phải thí nghiệm chứng minh Factory tạo thiết kế tốt hơn.

## Chất lượng, lỗi còn sót và thời gian

| Dự án | Điểm visual expert /100 | QA signal /100 | Scenario PASS | Nhóm lỗi mở | Baseline QA giây R1 / R2 | Candidate QA giây R1 / R2 |
|---|---:|---:|---:|---:|---|---|
| nova | 75 | 86.11 | 24/24 | 2 | 14.51 / 9.76 | 14.20 / 9.48 |
| cennext | 82.5 | 83.33 | 24/24 | 1 | 10.36 / 6.60 | 10.05 / 7.49 |
| luxroom | 80 | 86.11 | 24/24 | 3 | 27.45 / 18.62 | 25.80 / 20.52 |

**Điểm visual** là đánh giá một reviewer theo rubric hiện có, dựa trên 18 ảnh route/viewport đã mở và kết quả task, chưa có human calibration. Nova không cần ảnh trang trí, nên media N/A và trọng số còn lại được chuẩn hóa. Dimension/rationale và đủ bảy anti-generic signs nằm trong `expert-review.json`.

**QA signal** chỉ là tỷ lệ check HTTP, overflow, runtime, visible-img media, axe và scenario qua; không phải điểm đẹp hoặc mức tuân thủ WCAG. Tất cả 12 trial còn FAIL ở tiêu chí “mọi check đều PASS” vì lỗi accessibility/overflow. Không lấy điểm trung bình để che lỗi.

Thời gian là wall-clock QA tự động, không phải thời gian người dùng hay thời gian tạo thiết kế. R1 gồm capture/focus; R2 bỏ capture/focus. Chỉ so sánh baseline/candidate trong cùng lượt; không suy ra tăng tốc từ khác biệt nhỏ. Paired harness ghi **6 ties, 0 improvement, 0 regression**, score delta 0.

## Finding và owner

- **N-01 (P1, OPEN)**: Visible labels and accessible names differ on the unusual transaction link and desktop search/profile controls. Owner: Nova canonical renderer/accessibility labels.
- **N-02 (P2, OPEN)**: The mobile Money Horizon timeline triggers scrollable-region-focusable. Owner: Nova timeline component.
- **C-01 (P2, OPEN)**: The G.I.E home link's aria-label omits its visible Engineering, connected tagline across inspected pages. Owner: CENNEXT shared header.
- **L-01 (P2, OPEN)**: Gallery image buttons and cart links have visible text missing from accessible names. Owner: LuxRoom product gallery and shared commerce header.
- **L-02 (P1, OPEN)**: Product dimensional evidence expands the document to 576px at a 390px viewport. The spec-accordions region is 560px wide. Owner: LuxRoom product-detail layout/dimensional graphic.
- **L-03 (P2, OPEN)**: Axe reports target-size at the shared footer email field on desktop cart/checkout. Owner: LuxRoom shared footer.
- **L-04 (NEEDS_REVIEW, UNCONFIRMED_GROUP)**: The canonical focus smoke reports 9 mobile FAIL and 1 NEEDS_REVIEW; desktop has 1 NEEDS_REVIEW. Some recorded hit points are covered by mobile-purchase-bar. A separately refocused quantity control is visible in its screenshot, so these 9 flags are not counted as 9 confirmed bugs. Owner: LuxRoom sticky purchase chrome and keyboard scroll behavior.

Có **6 nhóm vấn đề mở**; nhóm focus L-04 vẫn cần xác minh, không đếm chín smoke flags thành chín bug. LuxRoom PDP được đo lại: viewport 390px, document width 576px, vùng spec-accordions rộng 560px. Ảnh `luxroom-mobile-focus-finding.png` cho thấy một control được refocus vẫn nhìn thấy, nên không tự nâng mọi cảnh báo focus thành finding đã xác nhận.

## Số vòng sửa và giới hạn

- Aggregate gate: 1 batch sửa/retest. Routing: 2 batch (batch đầu còn một case “foundation for the design system”, batch sau qua). Browser gate: 3 batch (strict/report; CI subset; empty axe asset), final 11 test qua.
- UI của ba dự án: **0 vòng sửa được thực hiện**. Chỉ audit benchmark target cố định; chưa đo hiệu quả của một vòng redesign→repair trên từng project.
- Không có participant mới, human task time, usability validation, deploy hoặc causal UI uplift.
- Axe/focus là regression signals; cần manual/assistive-technology review cho các claim tương ứng. Các câu foundation ngoài phạm vi technical phrases đã kiểm thử vẫn chịu giới hạn heuristic.

## Bàn giao

Code còn local, chưa commit/push/PR/merge. `changes.patch` áp lên base SHA nêu trên. Raw reports, protocol, trial JSONL, comparison, source fingerprints và log được giữ trong gói evidence; generated hashes xác nhận byte consistency, không chứng minh nguồn hostile là đáng tin.
