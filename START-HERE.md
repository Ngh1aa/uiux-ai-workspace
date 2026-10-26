# Bắt đầu từ đây

Repo này là bộ não thiết kế cá nhân: khi được nhờ thiết kế website hoặc app, Claude dùng nó để
chọn đúng quy trình, đọc đúng skill và tự soát chất lượng trước khi giao.

**Đây là đường đi duy nhất.** File này và [`WORKFLOWS.md`](WORKFLOWS.md) quyết định đọc gì và làm gì.
Không đọc cả repo. Nếu một skill nói khác hai file này về quy trình hay thứ tự đọc thì theo
hai file này.

## 0. Tiếp nhận thương hiệu khách hàng

Mỗi dự án khách hàng bắt đầu bằng một brand brief theo
[`BRAND-BRIEF.template.md`](BRAND-BRIEF.template.md): khách đưa gì (mức A–D), logo, màu, font,
giọng điệu, tham khảo, dấu ấn riêng.

- Điền từ tài liệu và lời mô tả có sẵn. Thiếu thì ghi giả định và làm tiếp; chỉ hỏi khi thiếu
  thật sự chặn việc (mức D, hoặc không biết làm web hay app).
- Khách đã có design system riêng thì dùng của khách; repo này chỉ còn là checklist chất lượng.
- Việc nhỏ (cỡ XS, S) trên một dự án đã có brief thì đọc lại brief, không làm lại.

## 1. Đọc gu thiết kế và chuẩn tay nghề

Đọc [`TASTE.md`](TASTE.md): các nguyên tắc chủ repo đã chốt qua nhiều dự án; áp dụng ngay từ bản
đầu. Brief của khách thắng `TASTE.md` ở những chỗ hai bên khác nhau.

Từ cỡ S trở lên, đọc thêm [`CRAFT.md`](CRAFT.md): số liệu cốt lõi, danh sách cấm các mặc định làm
thiết kế trông như AI làm, và chính sách ảnh, icon. Màn desktop hoặc nhiều màn trên canvas thì đọc thêm
[`foundations/layout-and-density.md`](foundations/layout-and-density.md).

## 2. Xác định cỡ việc

Mở [`WORKFLOWS.md`](WORKFLOWS.md), trả lời bảng câu hỏi ở mục 1 để ra cỡ việc (XS, S, M, L, XL).
Mỗi cỡ ghi sẵn bước làm, skill cần đọc, thứ phải giao và ngưỡng chất lượng. Danh sách skill ở
đó là đủ; không đọc thêm skill ngoài danh sách trừ khi việc thật sự cần và nói rõ lý do.

## 3. Chỉ đọc đúng skill được chỉ định

Mỗi skill là một thư mục `skills_UIUX/<tên-skill>/` có file `SKILL.md`. Thư mục `references/`
trong skill chỉ mở khi `SKILL.md` hoặc `WORKFLOWS.md` bảo cần.

## 4. Lên kế hoạch, dựng, rồi tự soát

- **Trước khi viết code**, viết khối kế hoạch thị giác ở mục 1 của `CRAFT.md` (chữ, màu theo vai
  trò, hình khối, phác bố cục, một điểm táo bạo, ba điểm khác starter), đối chiếu với danh sách cấm
  và sửa kế hoạch nếu chạm mặc định. Việc cỡ XS bỏ qua bước này.
- Bắt đầu từ [starter kit](design-system/starter/README.md): chọn loại màn trong
  [`PATTERNS.md`](design-system/starter/PATTERNS.md) và mượn **cấu trúc** màn mẫu trong
  `mobile.html`, `web.html`, `desktop.html` hoặc `landing.html`. Màu, font, bo góc của starter chỉ là chỗ
  giữ chỗ. Lấp từng vùng bằng khối có sẵn trong
  [thư viện pattern](design-system/patterns/README.md) thay vì tự chế card.
- Thương hiệu: chép `brand.css` vào thư mục dự án, điền theo brand brief, rồi soát:

  ```sh
  python3 design-system/scripts/check-brand.py <thư-mục-dự-án>/brand.css
  ```

- Tạo dấu ấn riêng theo [`SIGNATURE.md`](design-system/starter/SIGNATURE.md): đổi ít nhất 3 thứ
  ngoài màu. Không giao một bản starter kit chỉ đổi màu.
- Soát trang đã dựng ở cỡ điện thoại **và** máy tính, sáng và tối (mặc định 390 px và 1280 px):

  ```sh
  node skills_UIUX/ui-craft-and-visual-qa/scripts/taste-check.cjs <trang.html> --screenshot qa/
  ```

  Website thì thêm khổ máy tính bảng, màn lớn và phép thử phóng to (tràn ngang ở 320 px):
  `--width 390 --width 768 --width 1280 --width 1440 --reflow`. Màn app desktop và artboard canvas
  thêm `--height 900 --layout strict` để khoảng trống thừa, nội dung dồn một bên, thang chữ phẳng và
  card nổi bật mỏng thành lỗi (xem [`layout-and-density.md`](foundations/layout-and-density.md)).

  Script còn bắt ảnh, font, CSS tải lỗi, và chạy axe-core (soát khả năng tiếp cận) nếu có cài cùng
  chỗ với Playwright (`npm install axe-core@4`). Dòng `axe:` cuối kết quả cho biết axe có chạy
  không; chưa chạy thì ghi rõ khi giao.
- Sửa hết lỗi, rồi soát tiếp theo
  [rubric chất lượng](skills_UIUX/design-critique-and-rationale/references/quality-bar-rubric.md):
  hard fail trước, rồi chấm từng chiều.
- Mở ảnh chụp ra nhìn từng màn. Script và đọc code không thay cho nhìn màn.
- Bấm thử tác vụ chính, quay lại sửa và xác nhận lại; đối chiếu số lượng, tổng tiền, ngày giờ
  giữa các màn theo `WORKFLOWS.md`. Soát giao diện không thay cho kiểm tra luồng và dữ liệu.
- Việc cỡ M trở lên: nhờ một lượt soát độc lập trước khi giao. Nếu có thể tạo agent phụ, giao cho
  nó ảnh chụp, brief và rubric (không giao lý do thiết kế) để chấm như người lạ; nếu không, tự
  chấm lại sau khi đọc lại brief và ghi rõ là tự chấm.

### Khi không chạy được taste-check

Script cần Playwright và tự tìm nó ở các chỗ thường có. Không thấy thì nó in cách xử lý. Theo thứ tự:

1. Cài ngoài repo rồi chạy lại:
   `npm install --prefix /tmp/pw playwright@1 && npx --prefix /tmp/pw playwright install chromium`,
   sau đó đặt `NODE_PATH=/tmp/pw/node_modules`.
2. Mạng chặn, không cài được: mở trang bằng trình duyệt có sẵn trong phiên (trình duyệt tích hợp
   hoặc Claude in Chrome), chụp 390 px và 1280 px ở cả sáng và tối, soát bằng mắt theo checklist
   trong `TASTE.md`.
3. Luôn chạy thêm bản soát tĩnh, không cần cài gì:

   ```sh
   node skills_UIUX/ui-craft-and-visual-qa/scripts/static-check.cjs <trang.html>
   ```

Khi giao, ghi rõ đã soát bằng cách nào và phần nào chưa soát được. Không nói "đã đạt" khi
mới chỉ soát tĩnh.

## Khi giao kết quả

- Nói ngắn: đã làm gì, đã soát bằng cách nào, chỗ nào còn chưa kiểm chứng được (người dùng thật,
  thiết bị thật, trình đọc màn hình).
- Sau mỗi dự án, nếu chủ repo sửa đi sửa lại một điểm, ghi điểm đó vào `TASTE.md` để lần sau
  không lặp lại.

## Bản đồ repo

| Thư mục | Có gì |
|---|---|
| `BRAND-BRIEF.template.md` | Bước 0: tiếp nhận thương hiệu khách hàng |
| `TASTE.md` | Gu thiết kế và các lỗi không được lặp lại |
| `CRAFT.md` | Số liệu cốt lõi, danh sách cấm, kế hoạch thị giác, ảnh và icon |
| `foundations/` | Kiến thức nền: bố cục, lưới, mật độ, tham khảo theo loại màn (mở theo việc, không đọc hết) |
| `WORKFLOWS.md` | Quy trình và danh sách skill theo cỡ việc (nguồn định tuyến duy nhất) |
| `skills_UIUX/` | 40 skill UI/UX và script soát chất lượng |
| `design-system/` | Token DTCG, 25 component CSS, font, ví dụ app, `scripts/check-brand.py` |
| `design-system/starter/` | Starter kit: màn mẫu app và web, quy tắc theo loại màn |
| `design-system/patterns/` | 30 pattern ghép sẵn (card nổi bật, số liệu, nội dung, quy trình, chuyển đổi, trạng thái) |
| `benchmarks/` | Bộ 3 đề chuẩn để đo repo có giúp thiết kế tốt hơn sau mỗi lần nâng cấp |
| `AGENTS.md` | Quy tắc làm việc chung cho AI |
