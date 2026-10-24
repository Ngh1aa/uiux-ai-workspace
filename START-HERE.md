# Bắt đầu từ đây

Repo này là bộ não thiết kế cá nhân: khi được nhờ thiết kế website hoặc app, Claude dùng nó để
chọn đúng quy trình, đọc đúng skill và tự soát chất lượng trước khi giao.

Không đọc cả repo. Chỉ cần 4 bước dưới đây, thường khoảng 5–8 file.

## 1. Đọc gu thiết kế

Đọc [`TASTE.md`](TASTE.md) trước tiên. Đây là các nguyên tắc chủ repo đã chốt qua nhiều dự án;
áp dụng ngay từ bản đầu, không đợi bị nhắc.

## 2. Xác định cỡ việc và flow

Mở [`WORKFLOWS.md`](WORKFLOWS.md), trả lời bảng câu hỏi ở mục 1 để ra cỡ việc (XS, S, M, L, XL).
Mỗi cỡ có sẵn các bước, skill cần đọc, thứ phải giao và ngưỡng chất lượng.

Cần chi tiết theo từng chặng thì mở file flow tương ứng trong
[`skills_UIUX/flows/`](skills_UIUX/flows/README.md) và đi lần lượt từng chặng.

## 3. Chỉ đọc đúng skill được chỉ định

Mỗi skill là một thư mục `skills_UIUX/<tên-skill>/` có file `SKILL.md`. Chỉ đọc những skill mà
cỡ việc hoặc flow liệt kê. Thư mục `references/` trong skill chỉ mở khi `SKILL.md` bảo cần.

Danh sách đầy đủ: [`skills_UIUX/SKILL-CATALOG.md`](skills_UIUX/SKILL-CATALOG.md).

## 4. Dựng từ starter kit, rồi tự soát

- Bắt đầu từ [starter kit](design-system/starter/README.md): chọn loại màn trong
  [`PATTERNS.md`](design-system/starter/PATTERNS.md), chép màn mẫu tương ứng trong `mobile.html`
  hoặc `web.html`, đổi thương hiệu trong `brand.css`. Dự án có bộ nhận diện riêng thì theo dự án,
  nhưng vẫn giữ cấu trúc token theo vai trò.
- Chạy script soát theo gu trên trang đã dựng và sửa hết lỗi:

  ```sh
  node skills_UIUX/ui-craft-and-visual-qa/scripts/taste-check.cjs <trang.html> --screenshot qa/
  ```

- Soát tiếp theo [rubric chất lượng](skills_UIUX/design-critique-and-rationale/references/quality-bar-rubric.md):
  kiểm các lỗi bắt buộc (hard fail) trước, rồi chấm từng chiều.
- Luôn mở ảnh chụp ra nhìn ở cỡ điện thoại và cỡ máy tính. Script và đọc code không thay cho nhìn màn.

## Khi giao kết quả

- Nói ngắn: đã làm gì, chỗ nào còn chưa kiểm chứng được (người dùng thật, thiết bị thật).
- Sau mỗi dự án, nếu chủ repo sửa đi sửa lại một điểm, ghi điểm đó vào `TASTE.md` để lần sau
  không lặp lại.

## Bản đồ repo

| Thư mục | Có gì |
|---|---|
| `TASTE.md` | Gu thiết kế và các lỗi không được lặp lại |
| `WORKFLOWS.md` | Quy trình theo cỡ việc |
| `skills_UIUX/` | 116 skill UI/UX, flow, prompt, kiến thức, bộ kiểm tra `designlib/` |
| `design-system/` | Token DTCG, 19 component CSS, font, ví dụ app |
| `design-system/starter/` | Starter kit: màn mẫu app và web, quy tắc theo loại màn |
| `benchmarks/` | Bộ 3 đề chuẩn để đo repo có giúp thiết kế tốt hơn sau mỗi lần nâng cấp |
| `docs/` | Ghi chép nâng cấp và bằng chứng các lần thử |
| `AGENTS.md` | Quy tắc làm việc chung cho AI |
