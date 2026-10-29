# Đề 2: App đặt sân cầu lông "Cầu Lông Gần Nhà", 5 màn

**Cỡ việc:** L (5 màn, một luồng trọn vẹn). **Ngưỡng rubric:** không hard fail, trung bình ≥ 4.0,
không chiều nào < 3.5.

## Bối cảnh

App giúp người chơi cầu lông nghiệp dư ở TP.HCM tìm và đặt sân gần nhà sau giờ làm.
Người dùng mở app trên điện thoại, thường lúc 17:00–19:00, cần đặt nhanh trong vài lần chạm.

**Việc chính:** tìm một sân còn trống tối nay, đặt một khung giờ, xem lại lịch đã đặt.

## Năm màn bắt buộc

1. **Trang chủ:** lời chào, lượt đặt sắp tới (nếu có), tìm nhanh "Tối nay gần bạn".
2. **Danh sách sân:** tìm kiếm, lọc theo quận, mỗi sân có khoảng cách, giá, số khung còn trống.
3. **Chi tiết sân:** thông tin sân, tiện ích, lưới khung giờ hôm nay (trống, đã đặt, đang chọn).
4. **Đặt sân:** xác nhận khung giờ, số người, ghi chú, tổng tiền. Thể hiện **trạng thái lỗi**:
   khung 19:00 vừa có người đặt trước, kèm cách chọn khung khác.
5. **Lịch của tôi:** tab Sắp tới và Đã qua. Thể hiện **trạng thái rỗng** ở tab Đã qua.

## Dữ liệu (dùng đúng)

| Sân | Quận | Cách | Giá mỗi giờ | Khung trống tối nay |
|---|---|---|---|---|
| Sân Phú Nhuận | Phú Nhuận | 1,2 km | 120.000 ₫ | 18:00, 20:00, 21:00 |
| Sân Kỳ Hoà | Quận 10 | 2,8 km | 100.000 ₫ | 19:00, 21:00 |
| Sân Tân Định | Quận 1 | 3,5 km | 150.000 ₫ | 20:00 |

- Người dùng: Minh. Lượt đặt sắp tới: Sân Phú Nhuận, thứ Sáu 24/10, 18:00–19:00, sân số 3.
- Tiện ích Sân Phú Nhuận: gửi xe, phòng thay đồ, cho thuê vợt, nước uống.
- Khung giờ hôm nay ở Sân Phú Nhuận: 17:00 đến 22:00, mỗi khung 1 giờ.

## Yêu cầu

- Khung điện thoại 390 × 844, đủ thanh điều hướng giữa các màn chính.
- Được dùng starter kit, nhưng đổi thương hiệu cho hợp app thể thao (không giữ navy).
- Cả chế độ sáng và tối. Theo `TASTE.md`.

## Giao

Một file `02-app/index.html` chứa cả 5 màn, mỗi màn là một phần tử có `data-screen`.
