# Lò Gốm Mộc: chạy thử quy trình trên một khách hàng giả định

Ví dụ đi trọn đường `START-HERE.md` cho một khách mức C (chỉ có logo): brand brief, kế hoạch thị
giác, `brand.css` riêng, landing page dựng trên khung `starter/landing.html`, ba màn app giữ chỗ.
Mục đích là tìm chỗ repo còn vướng, không phải làm mẫu để chép. Mọi tên, giá, lịch là giả định.

| File | Là gì |
|---|---|
| [`BRAND-BRIEF.md`](BRAND-BRIEF.md) | Bước 0, theo `BRAND-BRIEF.template.md` |
| [`brand.css`](brand.css) | Lớp thương hiệu, qua `check-brand.py` không lỗi ở cả sáng và tối |
| [`landing.html`](landing.html) | Landing page đặt lớp |
| [`app.html`](app.html) | Ba màn app: chọn buổi, chọn số người, phiếu giữ chỗ |
| [`review/`](review/) | Ảnh chụp và kết quả `taste-check` dạng JSON |

## Kế hoạch thị giác (CRAFT.md mục 1)

```text
Ngành và vật gốc:      xưởng gốm Bát Tràng; vật gốc bàn xoay (vòng đồng tâm), vết rạn men
Một câu cảm giác:      chậm, mộc, như một buổi chiều ở xưởng
Chữ:                   tiêu đề Lora 600, 40–68 px, line-height 1,06; thân Be Vietnam Pro 16–18 / 1,55
Màu theo vai trò:      nền #ecebe7, bề mặt #fbfaf7, chữ #1e2421, thương hiệu #2c5a4e, nhấn #9a4a24 (chỉ cho "còn ít chỗ")
Hình khối:             card và ảnh bo 20 px; nút bo tròn hẳn; nhãn số chỗ viền nét đứt như nhãn dán phôi
Bố cục màn chính:      hero lệch: chữ trái 55%, khối men ngọc có vòng bàn xoay phải 45%
                       ngay dưới: lịch lớp dạng bảng, mỗi dòng có số chỗ, giá, nút giữ chỗ
                       rồi lý do, ba bước một buổi, học phí, lời khách, hỏi đáp, lời mời cuối
Một điểm táo bạo:      khối men ngọc với vòng bàn xoay ở hero
Ba điểm khác starter:  1. tiêu đề có chân Lora  2. hoạ tiết vòng đồng tâm  3. số chỗ thành "nhãn lò"
Đã đối chiếu mục 2:    gốm kéo về "nền kem + đất nung" (mặc định bị cấm) -> đổi sang xám tro + men ngọc,
                       đất nung chỉ còn cho cảnh báo; lợi ích viết thành ba bước có số, không phải 3 card icon
```

## Kết quả soát

- `check-brand.py`: 0 lỗi.
- `static-check.cjs`: 0 lỗi (app có 2 liên kết `href="#"` trong mockup).
- `taste-check.cjs`: landing ở 390 và 1280 px, sáng và tối, cộng `--reflow` 320 px: 0 lỗi, 0 cảnh
  báo. App ở 1280 px sáng và tối: 0 lỗi, 0 cảnh báo.
- axe-core **chưa chạy** trong phiên này (không cài được). CI chạy axe trên starter kit.
- Đã nhìn ảnh từng màn ở cả hai chế độ. Chưa thử trên thiết bị thật, chưa có trình đọc màn hình,
  chưa có người dùng thật.

## Repo còn vướng gì: những chỗ chạy thử tìm ra và đã sửa

| Tìm ra | Sửa ở đâu |
|---|---|
| `.ds-fieldset` ghép với `.ds-card` làm mất padding của card, câu hỏi đè lên mép card | `components.css`: reset bằng `:where()`, legend dạng float |
| Nút tròn (`.app-round`) bị tắt vẫn trông như bật | `starter/app.css`: kiểu `aria-disabled` |
| Cảnh báo "dòng cuối một chữ" bắn ở gần như mọi đoạn tiếng Việt vì âm tiết ngắn | `taste-check.cjs`: chỉ cảnh báo khi dòng cuối thật sự chỉ có một từ |
| Font tiêu đề thiếu ký tự ₫, trình duyệt lấy font khác, giá tiền lệch nét | Thêm ₫ vào chuỗi thử font trong `BRAND-BRIEF.template.md` và danh sách cấm của `CRAFT.md` |
| Trang web starter tràn ngang ở 320 px | `starter/app.css`, và `taste-check --reflow` để bắt lỗi này về sau |

Còn hai chỗ script không bắt được, chỉ thấy khi nhìn ảnh: nút "Giữ chỗ" rơi xuống dưới ngày vì
lưới thiếu một cột, và giá tiền không thẳng hàng giữa các dòng. Đó là lý do bước nhìn ảnh vẫn bắt
buộc.

## Còn thiếu để giao thật

- Lora chưa được đóng gói: tự host woff2 (latin + vietnamese) kèm `OFL.txt`, hoặc chọn font tiêu
  đề có ₫.
- Ảnh thật của xưởng thay cho khung giữ chỗ; lời khách thật đã đồng ý.
- Luồng "báo khi có chỗ", trạng thái lỗi thanh toán, trạng thái hết chỗ khi đang giữ.
