# Checklist thiết kế Prototype UI/UX (HTML/CSS/JS) — Đẹp, Ấn tượng, Thân thiện người dùng

> Phạm vi: dành cho việc tạo prototype trình diễn (không backend, không production, không SEO/pháp lý/dev handoff). Trọng tâm 100% vào **trải nghiệm thị giác + hành vi tương tác** mà người xem cảm nhận được ngay khi mở prototype lên.

---

## GIAI ĐOẠN 1 — HIỂU TRƯỚC KHI VẼ

### 1.1 Đối tượng & bối cảnh
- [ ] Đối tượng xem prototype là ai? (khách hàng cuối, sếp/stakeholder duyệt ý tưởng, nhà đầu tư, hay chính người dùng thật để test?) → quyết định độ "trình diễn" vs độ "thật"
- [ ] Cảm xúc muốn người xem có được trong 3 giây đầu là gì? (tin cậy? phấn khích? sang trọng? vui vẻ?) — viết ra 1 câu, dùng làm kim chỉ nam cho mọi quyết định thị giác sau này
- [ ] Loại website là gì (landing/e-commerce/dashboard/portfolio/app landing...) → lấy đúng bộ layout chuẩn tương ứng, không dùng khuôn chung

### 1.2 Định hướng phong cách (Style decision)
- [ ] Đã chốt 3 tính từ mô tả phong cách (VD: tối giản – tự tin – ấm áp) chưa? Mọi lựa chọn màu/font/animation sau này phải chiếu theo 3 từ này
- [ ] Đối thủ/thị trường đang design theo hướng nào? → chọn **khác biệt có chủ đích** hoặc **theo chuẩn ngành để tạo tin cậy**, không trộn lẫn nửa vời
- [ ] Có đang rơi vào phong cách mặc định/"AI-generated look" không? (nền cream + serif + cam đất; nền đen + neon; card bo góc giống hệt nhau + shadow xám nhạt giống hệt nhau; nhãn ALL-CAPS ở mọi heading...) — nếu có, chủ động phá vỡ ít nhất 1–2 điểm mặc định đó

### 1.3 User flow cho bản demo
- [ ] Xác định rõ **kịch bản trình diễn** (demo path): người xem sẽ đi qua đúng những màn hình/thao tác nào để thấy được điểm ấn tượng nhất? (không cần dựng hết mọi trang phụ nếu không nằm trong kịch bản demo)
- [ ] Vẽ nhanh user flow của kịch bản đó: điểm bắt đầu → các bước → điểm kết (khoảnh khắc "wow" hoặc màn hình hoàn tất)
- [ ] Xác định đâu là **1 khoảnh khắc trọng tâm** (hero moment) của cả prototype — nơi dồn công sức animation/chi tiết nhiều nhất, thay vì dàn trải đều

---

## GIAI ĐOẠN 2 — ÁP DỤNG UX LAWS (rà từng cái, không bỏ sót)

- [ ] **Hick's Law** — số lựa chọn trong menu/nav có bị nhiều quá không? Rút gọn còn tối đa 5–7 mục chính
- [ ] **Fitts's Law** — CTA chính đủ to, đủ xa các nút phụ để không bấm nhầm? Vùng chạm ≥44px trên bản mobile?
- [ ] **Jakob's Law** — vị trí các thành phần quen thuộc (logo góc trái, giỏ hàng góc phải, search có icon kính lúp) có bị "sáng tạo lại" một cách khó hiểu không?
- [ ] **Miller's Law** — danh sách/lựa chọn hiển thị cùng lúc có vượt quá ~7 mục không? Nếu có, nhóm lại hoặc phân trang
- [ ] **Gestalt – Proximity & Similarity** — các phần tử liên quan có được nhóm gần nhau bằng khoảng cách? Mọi nút cùng chức năng có cùng 1 style xuyên suốt?
- [ ] **Von Restorff Effect** — CTA/điểm quan trọng nhất trên mỗi màn hình có thực sự nổi bật hơn hẳn phần còn lại (màu, kích thước, khoảng trắng xung quanh)?
- [ ] **Doherty Threshold** — mọi phản hồi tương tác (hover, click, chuyển trang) có xảy ra trong <400ms để cảm giác "mượt", không bị đơ?
- [ ] **Peak-End Rule** — màn hình/khoảnh khắc cuối cùng của kịch bản demo (VD: trang cảm ơn, trạng thái hoàn tất) có được đầu tư kỹ, để lại ấn tượng tốt cuối cùng?
- [ ] **Aesthetic-Usability Effect** — thiết kế đẹp có đang che giấu một luồng thao tác thực ra rắc rối không? (đẹp nhưng vẫn phải hợp lý)
- [ ] **Zeigarnik Effect** — nếu có flow nhiều bước (onboarding, checkout demo), có progress bar/chỉ báo tiến trình để tạo động lực hoàn thành không?

---

## GIAI ĐOẠN 3 — HỆ THỐNG THỊ GIÁC (phần quyết định "đẹp & ấn tượng")

### 3.1 Màu sắc
- [ ] Bảng màu: primary, secondary, accent, neutral (grayscale 8–10 bậc), semantic (success/error/warning) — mỗi màu có vai trò rõ, không chọn theo cảm tính
- [ ] Có **đúng 1 điểm nhấn màu** (accent) dùng nhất quán cho mọi CTA/điểm cần chú ý, không rải màu nhấn lung tung
- [ ] Contrast đủ đọc rõ (kiểm tra bằng mắt thật kỹ ở cả 2 chế độ sáng/tối nếu có) — chữ mờ trên nền là lỗi thị giác rất dễ bị chê

### 3.2 Typography
- [ ] Font thể hiện đúng 3 tính từ phong cách đã chốt ở 1.2 (không chọn font mặc định hệ thống nếu muốn "ấn tượng")
- [ ] Tối đa 2 họ font, có type scale rõ ràng (H1→H6, body, caption) với tỉ lệ nhất quán (~1.25–1.333)
- [ ] Heading dùng làm điểm nhấn thị giác thật sự (kích thước, độ đậm, cách dòng) — không xử lý qua loa như văn bản thường phóng to
- [ ] Line-length đoạn văn dài giới hạn ~65–80 ký tự, line-height 1.5–1.6 cho body

### 3.3 Layout & bố cục
- [ ] Grid & spacing nhất quán toàn bộ prototype (không mỗi màn hình một kiểu canh lề)
- [ ] Khoảng trắng đủ "thở", đặc biệt quanh hero và CTA chính — đây là yếu tố tạo cảm giác cao cấp/chuyên nghiệp rõ rệt nhất
- [ ] Hierarchy thị giác: làm squint test (nheo mắt/làm mờ ảnh chụp màn hình) để kiểm tra mắt có bị dẫn đúng thứ tự ưu tiên không
- [ ] Đối chiếu đúng layout chuẩn theo loại site (landing/e-commerce/dashboard/blog/portfolio...) đã xác định ở 1.1

### 3.4 Hình ảnh, icon, chi tiết trang trí
- [ ] Phong cách ảnh/illustration/icon nhất quán xuyên suốt (không trộn ảnh thật với illustration hoạt hình tuỳ tiện)
- [ ] Ảnh minh hoạ đúng với nội dung/ngành, không dùng ảnh stock chung chung vô hồn — đây là điểm khiến prototype trông "rẻ tiền" nhanh nhất
- [ ] Có ít nhất 1 chi tiết thị giác riêng biệt, đặc trưng cho brief này (không copy nguyên khuôn từ site khác) để tạo dấu ấn ghi nhớ

---

## GIAI ĐOẠN 4 — TƯƠNG TÁC & CHUYỂN ĐỘNG (phần làm prototype "sống")

Đây là phần khác biệt lớn nhất giữa 1 bản thiết kế tĩnh và 1 prototype HTML/CSS/JS ấn tượng — đừng bỏ qua.

- [ ] Xác định **1 khoảnh khắc chuyển động chính** (page load sequence, hero reveal, hoặc 1 tương tác đặc biệt) để dồn sự tinh tế vào — không rải animation đều khắp mọi thứ (dễ gây rối mắt và trông "AI-generated")
- [ ] Hover state cho mọi phần tử có thể click: nút, card, link — có phản hồi rõ ràng (đổi màu/scale nhẹ/shadow), thời gian transition 150–300ms, easing tự nhiên (ease-out/ease-in-out, tránh linear)
- [ ] Trạng thái focus (khi Tab bằng bàn phím) có hiển thị rõ ràng, không bị `outline: none` mà không thay thế
- [ ] Scroll-triggered animation (nếu dùng) chỉ áp dụng có chọn lọc — không phải section nào cũng fade-slide-up giống hệt nhau (đây là dấu hiệu "template AI" rất rõ)
- [ ] Vi tương tác (micro-interaction) có ý nghĩa: nút submit có phản hồi loading → success rõ ràng; toggle/switch có animation mượt; input có feedback khi nhập đúng/sai
- [ ] Cursor tương tác (nếu dùng custom cursor/hiệu ứng theo chuột) chỉ nên dùng khi thực sự phù hợp phong cách, không lạm dụng gây rối
- [ ] Chuyển trang/chuyển section mượt, không giật cục — test bằng cách thao tác thật, không chỉ nhìn code

---

## GIAI ĐOẠN 5 — COMPONENT & TRẠNG THÁI ĐẦY ĐỦ

- [ ] Mỗi component lặp lại (button, card, input, badge...) đã đủ trạng thái cần cho kịch bản demo: default, hover, active, focus, disabled (nếu có xuất hiện trong demo)
- [ ] Empty state (nếu demo có phần danh sách/kết quả) được thiết kế riêng, không để trống trơn hoặc lỗi vỡ layout
- [ ] Loading state (skeleton hoặc spinner) cho các thao tác cần chờ trong kịch bản demo (dù giả lập bằng JS `setTimeout`)
- [ ] Trạng thái lỗi/thành công của form (nếu có form trong demo) có thiết kế rõ ràng, đúng tone thương hiệu

---

## GIAI ĐOẠN 6 — RESPONSIVE (nếu demo cần đa thiết bị)

- [ ] Xác định rõ: prototype này chỉ cần đẹp trên desktop để trình chiếu, hay cần responsive thật để người xem tự mở trên điện thoại? (quyết định trước để không tốn công thừa)
- [ ] Nếu cần responsive: kiểm tra tối thiểu ở 3 mốc — mobile (~375px), tablet (~768px), desktop (~1440px)
- [ ] Thứ tự ưu tiên nội dung trên mobile có hợp lý không (cái gì lên trước, cái gì ẩn/gộp lại)
- [ ] Vùng chạm mobile ≥44px, chữ không nhỏ hơn 16px cho nội dung chính

---

## GIAI ĐOẠN 7 — TỰ PHẢN BIỆN TRƯỚC KHI CHỐT (bắt buộc, đừng bỏ qua)

- [ ] **Squint test**: nheo mắt nhìn từng màn hình — điểm nào được chú ý đầu tiên có đúng ý đồ không?
- [ ] **5-giây test**: cho người ngoài cuộc xem 5 giây rồi hỏi họ hiểu trang này là gì/làm gì — có đúng như kỳ vọng?
- [ ] **"Bớt 1 món trang sức"**: nhìn lại toàn bộ, có chi tiết/hiệu ứng nào dư thừa, không phục vụ mục đích rõ ràng, nên bỏ bớt để phần còn lại nổi bật hơn không?
- [ ] **Đối chiếu 3 tính từ phong cách** đã chốt ở bước 1.2 — thiết kế cuối có thực sự toát lên đúng 3 tính từ đó không?
- [ ] **So với đối thủ**: đặt cạnh nhau, prototype của mình có điểm nào rõ ràng ấn tượng/khác biệt hơn không, hay chỉ "ổn, giống mọi site khác"?
- [ ] **Test thao tác thật** (không chỉ xem file thiết kế tĩnh): tự thao tác toàn bộ kịch bản demo bằng chuột/cảm ứng thật, xem có chỗ nào giật, lệch, chậm, khó bấm không
- [ ] **Content thật**: đã thay hết placeholder/lorem ipsum bằng nội dung thật hoặc gần thật chưa? Test với chữ tiếng Việt có dấu, tên/số dài nhất có thể để chắc không vỡ layout
- [ ] Có ít nhất 1 người khác xem thử và phản hồi thẳng thắn trước khi coi là bản cuối

---

## Bảng ghi nhớ nhanh: 5 điểm hay bị bỏ sót khiến prototype trông "chưa tới"

| Vấn đề thường gặp | Cách khắc phục |
|---|---|
| Mọi section đều fade-slide-up giống hệt nhau | Chỉ chọn 1 khoảnh khắc chính để làm animation nổi bật, còn lại giữ tĩnh hoặc rất tinh tế |
| Ảnh stock chung chung, không ăn nhập nội dung | Chọn ảnh/illustration đúng ngành, đúng cảm xúc đã chốt ở bước 1.1 |
| Card/button đều bo góc + shadow giống hệt mọi trang khác đã thấy | Chọn 1 chi tiết bo góc/shadow/border có chủ đích riêng cho brief này |
| CTA không nổi bật rõ giữa các nút khác | Dùng Von Restorff Effect: 1 màu accent duy nhất, chỉ dành riêng cho CTA chính |
| Hover/transition bị giật hoặc không có | Chuẩn hoá transition 150–300ms, easing ease-out, áp dụng nhất quán mọi phần tử tương tác được |

