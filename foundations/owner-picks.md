# Website chủ repo chọn là đẹp

Chủ repo gửi 9 trang này ngày 30/10/2026, kèm lý do "còn có animation nữa". Đây là chuẩn gu cho **website
thương hiệu và landing**, đứng trên mọi tham khảo ngoài khác trong [`reference-gallery.md`](reference-gallery.md).
Số đo lấy từ CSS và thư viện chạy thật trên trang, đo ở 1440×900. Không chép logo, ảnh, chữ hay bố cục nguyên
trang. Lấy nguyên tắc và con số. Bản dựng lại các chuyển động: [`motion-recipes/index.html`](motion-recipes/index.html).

## 1. Từng trang

| Trang | Ngành | Điều làm nó đẹp | Học gì |
|---|---|---|---|
| [spykercars.com](https://spykercars.com/) | Xe thể thao | Đen trắng tuyệt đối; chữ condensed in hoa 56 và 120 px, khoảng dòng 0,85; ảnh đặt lệch, so le | Một họ chữ hẹp làm tiêu đề; bố cục lệch kiểu tạp chí; logo vẽ nét khi mở trang |
| [halcyon.co.nz](https://www.halcyon.co.nz/) | Đèn chiếu sáng | Giao diện đổi sáng tối theo giờ trong ngày (sáng, ngày, chiều, đêm); ảnh sản phẩm tách lớp trên nền xám | Biến ý tưởng của ngành thành tương tác của cả trang |
| [aoiofficial.com/vn](https://aoiofficial.com/vn/) | Thời trang sưu tầm | Hai ảnh dọc chia đôi màn; đoạn tuyên bố chữ có chân đặt giữa; hàng sản phẩm cuộn ngang | Ảnh mang màu, giao diện chỉ đen trắng; chữ có chân cho câu tuyên bố, không chân cho nút |
| [wedding.s-tmro.com](https://wedding.s-tmro.com/) | Thiệp cưới | Ảnh bị cắt bởi một đường cong lớn; mỗi tiêu đề có đúng một chữ viết tay; chữ nền mờ chạy ngang | Một chi tiết mềm (đường cong, chữ viết tay) trên khung rất thẳng |
| [bcgbuildingdesign.com.au](https://www.bcgbuildingdesign.com.au/) | Thiết kế nhà | Chỉ hai màu nâu và kem; một họ chữ; ảnh ghim lại rồi nở to phủ phần chữ khi cuộn | Bảng màu lấy từ vật liệu của ngành; chữ trồi lên từng dòng |
| [jyuutaku-family.co.jp](https://www.jyuutaku-family.co.jp/) | Bất động sản | Nền trời và toà nhà đứng yên; card trắng trôi lên, so le trái phải; chữ Latin lớn mảnh giữa màn | Chiều sâu bằng hai tốc độ cuộn; nhãn tiếng Anh nhỏ trên tiêu đề tiếng bản địa |
| [houseofyellow.nl](https://houseofyellow.nl/) | Agency nội dung | Một màu vàng nhạt trên gần đen; video cắt nhanh sau logo có chữ tự xếp lại; đoạn tuyên bố sáng dần từng chữ khi cuộn | Một màu thương hiệu dùng triệt để; nhịp đọc theo nhịp cuộn |
| [corekara.co.jp/…/conference](https://corekara.co.jp/scratch/20260826_conference/) | Sự kiện | Đen và một màu xanh điện; ô màu sau chữ như bút dạ; dải xanh quét qua đổi màu cả section; tiêu đề dọc khổng lồ | Kiểu in ấn: chữ dọc, đường kẻ mảnh; đổi màu section bằng chuyển động |
| [dod.camp](https://www.dod.camp/) | Đồ cắm trại | Kem ấm, mực đen, một màu cam gỉ; "STAY CRAZY." to; ảnh trại nở từ khung nhỏ ra tràn màn | Cửa hàng vẫn có chất thương hiệu; mọi chữ 12–16 px, giãn chữ nhẹ, rất dễ đọc |

## 2. Điểm chung của 9 trang

1. **Ít màu.** Đen trắng hoặc trung tính ấm, cộng tối đa một màu nhấn. Màu đến từ ảnh.
2. **Một họ chữ, chênh cỡ rất lớn.** Tiêu đề 56–120 px, khoảng dòng 0,85–1,0, giãn chữ âm nhẹ. Chữ thường 12–16 px.
   Cả trang một họ chữ. Không chêm một từ nghiêng có chân hay chữ viết tay vào tiêu đề: chủ repo thấy "font
   khác nhau" và "AI" (vòng 6 của [thử lại đề 01](../benchmarks/trials/2026-10-30-landing-owner-picks/README.md)).
3. **Ảnh thật là nhân vật chính.** Ảnh tràn màn hoặc đặt lệch, ít card, ít viền, bo góc 0–6 px hoặc nút viên.
4. **Một ý tưởng của ngành thành tương tác:** đèn theo giờ, chữ logo tự xếp lại, chữ dọc kiểu in ấn, ảnh trại nở ra.
   Đây là "chữ ký thị giác" trong [`composition.md`](composition.md) §2, và là thứ các lượt benchmark còn thiếu.
5. **Chuyển động gắn với cuộn, chậm và mềm.** Hai nhịp tách bạch:
   - **Nhịp kể chuyện:** chữ, ảnh, section hiện ra trong 0,8–1,4 s.
   - **Nhịp thao tác:** rê chuột, nút, menu phản hồi trong 0,15–0,4 s.
6. **Cuộn mượt.** 6/9 trang dùng Lenis. Cuộn mượt làm các hiệu ứng theo cuộn trông liền mạch.
7. **Lưới lệch và khoảng trắng chủ động.** Chữ nhỏ bám mép, khối lớn lệch tâm, section này khác hình section kia.

## 3. Con số chuyển động

| Việc | Thời lượng | Đường cong | Thấy ở |
|---|---|---|---|
| Chữ trồi lên từng dòng | 0,8–1,2 s, mỗi dòng trễ 60–100 ms | `power3.out` ≈ `cubic-bezier(.215,.61,.355,1)` | BCG |
| Khối hiện ra (mờ + trượt lên) | 1,4 s | `cubic-bezier(.165,.84,.44,1)` | Jyuutaku |
| Chuyển cảnh mềm, ảnh lớn | 1–1,6 s | `cubic-bezier(.4,.4,0,1)` | Wedding |
| Ảnh nở, đổi màu section, chữ sáng dần | Theo vị trí cuộn, không theo giờ | `linear` theo cuộn | DOD, BCG, HOY, Corekara |
| Bắt đầu chạy | Khi mép trên khối qua 75–90% chiều cao màn | | BCG, DOD |
| Rê chuột, gạch chân, nút | 0,3–0,4 s | `cubic-bezier(.25,1,.5,1)`; gạch chân `cubic-bezier(.625,.05,0,1)` | DOD, Spyker |
| Đổi trang, mở menu | 0,6–0,7 s | `power3.inOut`; `cubic-bezier(1,0,0,1)` | BCG, Jyuutaku |
| Màn chờ có logo | Trang gốc 3–6 s | Vẽ nét hoặc chữ trồi | Spyker, DOD, BCG, Jyuutaku |

## 4. Không lấy theo

- **Chữ 8–10,8 px** ở AOI, HOY, Corekara. TASTE giữ tối thiểu 12 px; lấy cảm giác tinh tế bằng chữ in hoa giãn
  0,06–0,08em ở 12 px.
- **Màn chờ 3–6 s.** Giữ dưới 1,2 s, chỉ lần đầu trong phiên, bỏ hẳn khi bật giảm chuyển động.
- **Nút chỉ có icon hoặc chữ quá nhỏ cho điện thoại.** Vẫn 44 px.
- **Chuyển động không có bản tĩnh.** Mọi công thức phải có trạng thái cuối hiện ngay khi bật giảm chuyển động.

## 5. Khi dựng website hoặc landing

1. Chọn 1–2 trang ở bảng §1 gần ngành hoặc gần cảm giác brief cần; ghi tên vào khối kế hoạch thị giác.
2. Chốt ý tưởng ngành sẽ thành tương tác (§2 mục 4) trước khi chọn màu.
3. Lấy công thức chuyển động từ [`motion-recipes/index.html`](motion-recipes/index.html), mỗi trang tối đa 3 công thức.
4. Màn app và quản trị không áp phần này: ở đó chuyển động vẫn chỉ để phản hồi thao tác ([`motion.md`](motion.md)).
