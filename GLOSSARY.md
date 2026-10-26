# Bảng thuật ngữ

Repo viết bằng tiếng Việt và giữ một số thuật ngữ tiếng Anh vì chúng là tên trong code, công cụ hoặc chuẩn.
Bảng này chốt **một cách gọi** cho mỗi khái niệm để tài liệu, skill và lời giao cho khách thống nhất.

## Quy tắc viết

1. **Ưu tiên tiếng Việt** khi có từ phổ thông, ai trong nghề cũng hiểu: "bố cục" thay "layout", "khoảng
   cách" thay "spacing", "lưới" thay "grid", "nguyên mẫu" hoặc "mẫu thử" thay "prototype".
2. **Giữ tiếng Anh** khi đó là tên riêng trong code hoặc công cụ (`token`, `data-screen`, `taste-check`),
   tên chuẩn (WCAG, DTCG, OKLCH) hoặc tên tính năng hệ điều hành (Dynamic Type, predictive back). Viết trong
   dấu `code` nếu là tên trong code.
3. **Lần đầu xuất hiện trong một trang**, thuật ngữ khó viết kèm nghĩa: "card nổi bật (hero card)",
   "lớp phủ (scrim)". Từ lần thứ hai dùng một cách gọi.
4. **Không trộn nửa câu Anh nửa câu Việt**: "Khi user scroll xuống, show toast" viết lại thành "Khi người
   dùng cuộn xuống, hiện thông báo nổi (toast)".
5. Lời giao cho khách hàng không dùng thuật ngữ nội bộ (`data-part`, "primitive"). Viết điều khách thấy.

## Thuật ngữ

### Quy trình

| Gọi là | Tiếng Anh | Nghĩa |
|---|---|---|
| Brand brief | brand brief | Tài liệu tiếp nhận thương hiệu khách, theo `BRAND-BRIEF.template.md` |
| Cỡ việc (XS, S, M, L, XL) | task size | Cách repo chia quy trình theo độ lớn việc, xem `WORKFLOWS.md` |
| Khung vấn đề | problem framing | Ai, hoàn cảnh, mục tiêu, câu "Làm sao để" |
| Câu "Làm sao để" | How might we | Câu hỏi thiết kế không chứa giải pháp |
| Việc chính | top task | Điều người dùng đến để làm, không phải tên trang |
| Persona giả định | proto-persona | Chân dung người dùng dựng từ giả định, phải kiểm lại |
| Luồng | user flow | Chuỗi bước người dùng đi để xong một việc |
| Luồng chính | happy path | Luồng không lỗi, không rẽ nhánh |
| Khung dây | wireframe | Bản vẽ cấu trúc chưa có màu và chữ thật |
| Mẫu thử | prototype | Bản bấm được để kiểm chứng |
| Đi thử theo kịch bản | walkthrough | Đi từng bước một nhiệm vụ để tìm chỗ vướng |
| Phản biện thiết kế | critique | Đánh giá theo rubric, có lý do |
| Rubric | rubric | Bảng chấm chất lượng, xem `design-critique-and-rationale` |
| Trượt cứng | hard-fail | Lỗi làm bài không đạt dù điểm trung bình cao |
| Bàn giao | handoff | Gói tài liệu cho đội dựng: trạng thái, token, hành vi |
| Đề chuẩn | benchmark | Bộ đề cố định để đo repo sau mỗi lần nâng cấp, trong `benchmarks/` |
| Mức bằng chứng | evidence level | `QUAN_SÁT`, `SỐ_LIỆU`, `HEURISTIC_ONLY`, `PLANNED_VALIDATION`…, xem `research-lite` |

### Bố cục và thị giác

| Gọi là | Tiếng Anh | Nghĩa |
|---|---|---|
| Bố cục | layout | Cách chia và sắp xếp vùng trên màn |
| Lưới, cột, rãnh, lề | grid, column, gutter, margin | Xem `foundations/layout-and-density.md` |
| Mật độ | density | Lượng thông tin trên một đơn vị diện tích: thoáng, vừa, gọn |
| Khoảng trắng chủ động, bị động | active, passive whitespace | Trống có chủ đích, và trống vì thiếu nội dung |
| Điểm nhìn | focal point | Thứ mắt thấy đầu tiên, mỗi màn một |
| Thứ bậc thị giác | visual hierarchy | Thứ tự mắt đọc, xem `foundations/gestalt-and-hierarchy.md` |
| Thang chữ | type scale | Tỉ lệ giữa các cỡ chữ |
| Card nổi bật | hero card | Khối nền đậm làm điểm nhấn, tối đa một mỗi màn |
| Hướng nghệ thuật | art direction | Quyết định về ảnh, minh hoạ, phong cách hình |
| Dấu ấn | signature | Thứ lặp lại giúp nhận ra thương hiệu, xem `SIGNATURE.md` |
| Điểm ngắt | breakpoint | Bề rộng mà bố cục đổi |
| Khung nhìn | viewport | Vùng trình duyệt đang hiển thị |
| Artboard, canvas | artboard, canvas | Khung vẽ chứa nhiều màn để trình bày, đánh dấu bằng `data-screen` |

### Hệ thống thiết kế

| Gọi là | Tiếng Anh | Nghĩa |
|---|---|---|
| Hệ thống thiết kế | design system | `design-system/`: token, component, pattern, tài liệu |
| Token | design token | Giá trị có tên (màu, khoảng cách, cỡ chữ), định dạng DTCG |
| Tầng nguyên thuỷ | primitive | Giá trị thô như `color.jade.700`; màn không dùng trực tiếp |
| Tầng ngữ nghĩa | semantic | Vai trò như `action.primary.bg`; đổi theo chế độ màu |
| Component | component | Thành phần giao diện nhỏ: nút, ô nhập, badge (`components.css`) |
| Pattern | pattern | Khối ghép từ component có cấu trúc sẵn (`patterns.css`), xem `design-system/patterns/` |
| Mẫu theo loại màn | screen pattern | Cách dựng từng loại màn, xem `design-system/starter/PATTERNS.md` |
| Starter | starter kit | Màn mẫu để mượn cấu trúc, `design-system/starter/` |
| Chế độ sáng, tối | light, dark mode | |
| Tương phản | contrast | Tỉ lệ độ sáng chữ và nền, tối thiểu 4,5:1 cho chữ thân |
| Vùng chạm | touch target | Tối thiểu 44 × 44 px |

### Thành phần và trạng thái

| Gọi là | Tiếng Anh | Nghĩa |
|---|---|---|
| Nút hành động chính | primary button, CTA | Một nút chính mỗi vùng |
| Nhãn trạng thái | badge | Luôn có chữ và icon, không chỉ màu |
| Thẻ lọc | chip | |
| Thanh tab | tab bar | Điều hướng đáy trên điện thoại, tối đa 5 mục |
| Sheet đáy | bottom sheet | |
| Lớp phủ | scrim | Lớp tối sau sheet, modal |
| Thông báo nổi | toast | Tự ẩn, cho việc đã xong; lỗi cần xử lý dùng banner |
| Thanh thông báo | banner | Thông báo nằm trong bố cục |
| Khung xương | skeleton | Khối giữ chỗ khi đang tải |
| Trạng thái rỗng | empty state | |
| Thanh bước | stepper | |
| Chữ trên giao diện | microcopy, UX writing | Nhãn nút, lỗi, gợi ý |

### Kỹ thuật và kiểm tra

| Gọi là | Tiếng Anh | Nghĩa |
|---|---|---|
| Soát gu | taste-check | Script `taste-check.cjs` soát lỗi thị giác trên trang đã dựng |
| Dàn lại | reflow | Nội dung xếp lại không tràn ngang ở 320 px (WCAG 1.4.10) |
| Đường cong chuyển động | easing | Xem `foundations/motion.md` |
| Giảm chuyển động | reduced motion | Cài đặt hệ điều hành, phải tôn trọng |
| Cỡ chữ động | Dynamic Type | Tên tính năng iOS, giữ nguyên |
| Vùng an toàn | safe area | Vùng không bị tai thỏ, thanh hệ thống che |
| Tràn viền | edge-to-edge | Android vẽ dưới thanh hệ thống |
| Quay lại dự đoán | predictive back | Tên tính năng Android, giữ nguyên |
