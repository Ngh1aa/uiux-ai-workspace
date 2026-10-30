# 04-multi-role: Răng Xinh, ghi chú giao

Cỡ việc L, track web app / dashboard. Duyệt hướng: **CHƯA DUYỆT** (không có người duyệt trong lượt này).

## Kế hoạch thị giác (CRAFT.md mục 1)

```text
Ngành và vật gốc:      nha khoa gia đình; vật gốc là sổ hẹn theo ghế (cột = ghế, hàng = giờ) dán ở quầy lễ tân
Một câu cảm giác:      sạch, mát, bình tĩnh như phòng khám vừa lau, đọc nhanh như bảng hẹn ở quầy
Chữ:                   tiêu đề Be Vietnam Pro 700, 28/36 (số lớn 44/48); thân Manrope 15/1.55; có tiếng Việt: có (cả hai có dấu và ₫)
Màu theo vai trò:      nền #f2f6f5, bề mặt #ffffff, chữ #13201e, thương hiệu #0b6e66 (xanh ngọc men răng),
                       nhấn = đỏ cảnh báo của token feedback.danger chỉ cho dị ứng và xung đột
Hình khối:             bo 14px cho mọi card, 10px cho control; phẳng, không bóng; viền 1px chỉ ở bảng lịch
Bố cục màn chính:      [thanh bên 224 | thanh trên 64: ngày, tài khoản/Đổi vai trò]
                       [Lịch hôm nay ......... ô tìm bệnh nhân  Đặt lịch]
                       [lưới lịch 8 cột: Giờ | Ghế 1 | Ghế 2 | Ghế 3 ][cột 4: Sắp đến + Khung trống
                                                                        hoặc form Đặt lịch có xung đột]
Lưới và mật độ:        1280: 12 cột, gutter 24, mật độ gọn; lưới lịch và cột phải giãn hết chiều cao khung
Card nổi bật:          chỉ ở màn Doanh thu: nhãn "Doanh thu tháng 10 đến 28/10"; 186.200.000 đ; +8,6% so với cùng kỳ tháng 9
Một điểm táo bạo:      khối "Dị ứng: Penicillin" nền đỏ nhạt, viền đỏ đủ bốn cạnh, chữ 32px, tách riêng khỏi hồ sơ
Ba điểm khác starter:  1. xanh ngọc thay navy, bo 14 thay 24  2. Manrope + Be Vietnam Pro thay một font
                       3. thanh bên có nhãn (224px) thay rail icon, lịch dạng lưới ghế × giờ
Đã đối chiếu mục 2:    không nền kem/đất nung, không gradient, không eyebrow IN HOA (bỏ th uppercase của starter),
                       không thanh màu trái (dị ứng dùng viền đủ bốn cạnh), không " · ", không card lồng card nổi bật
```

## Ma trận vai trò × màn × quyền

| Màn / chức năng | Lễ tân (Nguyễn Thảo) | Bác sĩ (BS. Phan Minh Đức) | Chủ phòng khám (Lê Quỳnh Anh) |
|---|---|---|---|
| Lịch hôm nay (xem) | Có, là màn chính | Có, mục thứ hai trên thanh bên | Có, mục thứ hai trên thanh bên |
| Đặt lịch, xếp khách vãng lai | Có (nút Đặt lịch, ô trống, Xếp khách) | Ẩn (không nút, ô không bấm) | Ẩn |
| Bệnh nhân tiếp theo (hồ sơ, dị ứng) | Ẩn | Có, là màn chính | Ẩn |
| Gọi bệnh nhân, Bắt đầu khám, Lưu ghi chú | Ẩn | Có | Ẩn |
| Doanh thu (doanh thu, lấp ghế, lượt huỷ, biểu đồ) | Ẩn trên thanh bên; mở bằng liên kết thì hiện trạng thái không có quyền | Ẩn, cùng trạng thái không có quyền | Có, là màn chính |
| Đổi vai trò (menu tài khoản trên thanh trên) | Có | Có | Có |

Ẩn = không có mục trên thanh bên và không có nút. Mở thẳng đường dẫn tới trang bị ẩn (khung 4) thì hiện
trạng thái không có quyền với Quay lại (về màn vừa rời, ở khung 4 là Lịch hôm nay) và Đổi vai trò.

## Bốn khung (data-screen)

1. `#s-reception` Lễ tân: lịch hôm nay. Mở sẵn form Đặt lịch cho khách vãng lai vào Ghế 1 lúc 9:30 (đã có Lâm Gia Bảo) để thấy xung đột: ô bị trùng viền đỏ trên lưới, khối xung đột trong form kèm ba khung trống gần nhất để chọn.
2. `#s-doctor` Bác sĩ: bệnh nhân tiếp theo. Bắt đầu khám khoá tới khi Gọi bệnh nhân, có lý do gắn aria-describedby.
3. `#s-owner` Chủ phòng khám: Doanh thu. Ghế 3 ở trạng thái rỗng (chưa đủ 7 ngày dữ liệu).
4. `#s-denied` Lễ tân mở trang Doanh thu qua liên kết: không có quyền + bảng quyền theo vai trò; Quay lại về Lịch hôm nay.

Mỗi khung là một phiên app độc lập (state riêng), cùng một mã render: đổi vai trò ở bất kỳ khung nào sẽ đổi thanh bên, màn chính và quyền ngay trong khung đó.

## Phần mô phỏng (không có backend)

- Toàn bộ dữ liệu nằm trong JS của trang; đặt lịch, gọi bệnh nhân, bắt đầu khám, lưu ghi chú chỉ đổi state trong trang, tải lại là mất.
- Giờ hiện tại cố định 9:15 thứ Ba 28/10 (Hồ Ngọc Mai muộn 15 phút); khung trước 9:30 là "Đã qua".
- Đổi vai trò không hỏi mật khẩu/PIN; quyền chỉ kiểm ở phía giao diện. Quyền thật phải kiểm ở máy chủ.
- Tên khách vãng lai "Ngô Thanh Tâm", tỉ lệ lấp ghế từng ghế (Ghế 1 81%, Ghế 2 75%), doanh thu từng ngày trong biểu đồ là số giữ chỗ (tổng 1–28/10 khớp 186.200.000 đ, ngày 28 khớp 3.450.000 đ).
- Ngày 28/10 ghi "thứ Ba" theo đề; 12/09 ghi "thứ Sáu" theo lịch 2025 cho cùng năm.

## Kiểm

- static-check: 0 lỗi. flow-check --mode prototype: tĩnh PASS, 0 lỗi (luồng UNKNOWN như mọi trang có JS).
- check-brand.py brand.css: ĐẠT.
- taste-check --layout strict, 1280×800 và 1440, sáng và tối: 0 lỗi; còn 4 cảnh báo "5 nhóm màu" ở màn lịch lễ tân (giữ: bốn trạng thái lượt khám đề bắt buộc cộng màu xung đột, mỗi màu gắn trạng thái thật bằng chip có chữ và icon).
- scenarios.cjs chạy bằng Playwright (Chromium cục bộ, 1280×800): 9/9 PASS, không lỗi JS.
- Đã xem ảnh render 1280 sáng/tối và 1440 sáng.
- Chưa kiểm: axe-core (không cài), trình đọc màn hình thật, người dùng thật. Hướng thị giác CHƯA DUYỆT.
