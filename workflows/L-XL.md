# Cỡ L và XL: bước chi tiết

Mở khi việc đã được xếp cỡ L hoặc XL theo [WORKFLOWS.md](../WORKFLOWS.md). Cỡ M không cần đọc file này.

### L — Khu vực sản phẩm, làm lại

Như **M**, cộng thêm:

1. **Đánh giá hiện trạng** và so 3–5 sản phẩm tham chiếu (trích nguyên tắc, không sao chép bề mặt).
   Thiếu hiểu biết về người dùng thì thêm [`research-lite`](../skills_UIUX/research-lite/SKILL.md).
2. **Kiến trúc thông tin** và mô hình điều hướng cho toàn khu vực.
3. **Hướng thị giác**: 4–7 thuộc tính thị giác có biểu hiện cụ thể, ma trận vai trò trang, màn hình.
   Nền tảng lý do nằm trong [`foundations/`](../foundations/README.md).
   Hướng chỉ được nhân rộng sau [cổng duyệt hướng](../WORKFLOWS.md#cổng-duyệt-hướng-m-l-xl).
4. **Thử trên 3 màn hình khác bản chất** trước khi nhân rộng.
5. **Critique 3 vòng** (xem rubric): tự review → review chéo theo vai trò → review "người lạ" chỉ nhìn ảnh.
6. Kiểm nhất quán xuyên màn hình (ảnh đặt cạnh nhau).

- Sản phẩm đã có code: [`brownfield-redesign`](../skills_UIUX/brownfield-redesign/SKILL.md) là bắt buộc;
  bước "đánh giá hiện trạng" ở trên gồm cả kiểm kê code cũ và bảng ADN của skill đó.
- Skill thêm: [`website-audit-and-redesign`](../skills_UIUX/website-audit-and-redesign/SKILL.md) hoặc
  [`mobile-app-design`](../skills_UIUX/mobile-app-design/SKILL.md) ·
  [`design-reference-research-and-benchmark`](../skills_UIUX/design-reference-research-and-benchmark/SKILL.md) ·
  [`information-architecture`](../skills_UIUX/information-architecture/SKILL.md)
- Giao: tất cả của M, cộng bản đánh giá hiện trạng, hướng thị giác, ma trận màn hình, ảnh nhất quán xuyên màn hình.
- Ngưỡng: trung bình ≥ 4, không chiều nào < 3.5, không hard-fail.

### XL — Sản phẩm mới / chưa có design system

Như **L**, cộng thêm:

1. **Khám phá**: vấn đề, đối tượng, giả định rủi ro nhất, cách kiểm chứng, theo
   [`design-thinking-lite`](../skills_UIUX/design-thinking-lite/SKILL.md) mức XL và
   [`research-lite`](../skills_UIUX/research-lite/SKILL.md).
2. **Nguyên tắc trải nghiệm** (3–5 câu, có đánh đổi rõ ràng).
3. **Track Design System** (xem [tracks](tracks.md)) chạy song song từ tuần đầu.
4. **Kế hoạch kiểm chứng** với người dùng thật; khi chưa có người thật thì ghi `PLANNED_VALIDATION`.

- Skill thêm: [`audience-intent-and-top-tasks`](../skills_UIUX/audience-intent-and-top-tasks/SKILL.md) ·
  [`experience-principles-and-signature-moments`](../skills_UIUX/experience-principles-and-signature-moments/SKILL.md) ·
  [`design-system-and-components`](../skills_UIUX/design-system-and-components/SKILL.md)
- Ngưỡng: như L, cộng design system qua `validate.py` (contrast, parity sáng/tối).
