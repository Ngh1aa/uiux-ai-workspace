# Bằng chứng nâng cấp local

Baseline GitHub main và HEAD: `d7000758c2e2aa273785455ae91d255fe3be04e0`.
Hoàn tất kiểm tra ngày 30/10/2026 (Asia/Bangkok); tên lượt giữ ngày bắt đầu 29/10.

`final-verification.json` tổng hợp kiểm cuối và giới hạn. `flow-qa.json`, các JSON iterative02
và `overlay-check.json` là chẩn đoán ở các bước trước, không thay thế kết quả cuối.
`overlay-scoped.json` áp dụng riêng sản phẩm gom-moc; không dùng nó để tuyên bố toàn toolkit
đều qua audit redesign. Bản toolkit gồm nhiều ví dụ greenfield mới nên toàn-repo diff không phải
một sản phẩm redesign đồng nhất. Threshold checker và các negative tests được giữ.

`history-audit.json` ghi source và hành vi v2 thực: 31 href placeholder; CTA không đổi task state.
Không từ đó suy mọi nút đều chết hoặc gallery phải là prototype. Điểm/ảnh lịch sử giữ nguyên.

Hai run mới có checks/flow-results/render JSON, provenance patch/manifest và ảnh riêng.
Mỗi run có reviews được chọn (hash gắn với ảnh của lượt kiểm) và review-history giữ vòng trước.
Review là agent heuristic độc lập với người làm; reread/known brief/after-brief được ghi đúng
trong hồ sơ, không gọi là nghiên cứu người dùng hay cold read đúng thủ tục.

Các link tương đối trong snapshot brief/rubric vẫn nguyên byte đã được duyệt. Link checker
chỉ dùng context nguồn canonical khi cả nội dung lẫn hash manifest khớp; vẫn kiểm mục tiêu
ở nguồn, không bỏ qua lỗi định tuyến và không sửa hồ sơ đã duyệt.

`reading-paths.json` dùng cùng phép split whitespace trước/sau; `skill-content-map.*`
và test đối chiếu toàn body baseline chứng minh phần sâu được chuyển, không mất năng lực.
Các log delivery và decision-lab-browser đi kèm để tái kiểm. CI của patch, native, backend,
screen reader và duyệt con người vẫn UNKNOWN. Không commit/push/PR/merge/deploy.
