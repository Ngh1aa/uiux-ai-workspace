# Lần chạy 2026-10-24-v2: sau vòng cải tiến 1

Vòng cải tiến 1 thêm vào repo ba thứ mà lần chạy v1 chỉ ra là còn thiếu:

- mẫu trạng thái từng khối cho trang web (`design-system/starter/web-states.html`);
- hướng dẫn tạo dấu ấn riêng (`design-system/starter/SIGNATURE.md`) cùng biến chữ tiêu đề và hoạ tiết
  trong starter kit;
- mẫu chọn nhanh ngay trong danh sách và thanh tổng tiền luôn thấy (màn 8 trong `mobile.html`).

Lần chạy này **sửa tiếp từ bản v1** theo các hướng dẫn mới, không làm lại từ đầu. Người làm và người
chấm vẫn là cùng một agent.

## So với v1

| Đề | v1 TB | v2 TB | v1 | v2 |
|---|---|---|---|---|
| 01 Landing | 3.7 | 3.9 | Đạt | Đạt |
| 02 App | 3.8 | 4.0 | Chưa đạt | Đạt (L) |
| 03 Dashboard | 3.8, có HF-5 | 4.0 | Chưa đạt | Đạt |

Hai chiều yếu của v1 (tương tác và dấu ấn) lên từ 3 thành 4 ở cả ba đề.

## Dấu ấn đã làm theo SIGNATURE.md

| Đề | Vật gốc | Cần gạt đã đổi ngoài màu |
|---|---|---|
| 01 Landing | Bàn xoay gốm | Hình khối (góc lệch), hoạ tiết (vòng xoay), tương tác (chọn lớp và ca) |
| 02 App | Vạch kẻ sân | Hình khối (góc 12px), hoạ tiết (vạch sân), số liệu (giờ chơi kiểu bảng tỉ số), tương tác (chọn khung trong danh sách) |
| 03 Dashboard | Hàng mũi đan | Hình khối (góc 20px), hoạ tiết (đan chéo), số liệu (thanh tồn kho như mũi len) |

## Lỗi bắt được trong lúc làm

| Đề | Lỗi | Ai bắt |
|---|---|---|
| Starter | Tiêu đề khối lỗi bị luật màu chữ phụ đè, hiện xám | Nhìn ảnh |
| Starter | Hai sắc navy gần như giống nhau bị tính thành hai nhóm màu | taste-check (báo nhầm, đã sửa cách gom màu) |
| 02 | Thanh tổng tiền nổi nằm dưới thanh tab, che nút đặt | Nhìn ảnh |
| 02 | Khung giờ ở Trang chủ là nút nhưng bấm không có tác dụng | Đọc lại mã khi xem ảnh |
| 02 | Tên sân làm link chỉ cao 19px | taste-check |
| 03 | Tiêu đề mới gãy dòng trên điện thoại | taste-check |

## Còn yếu

- **Chữ (4) ở landing vẫn 3:** starter kit chỉ có một họ chữ chạy được không cần mạng. Muốn thêm chữ
  tiêu đề có cá tính thì phải đóng gói thêm font có giấy phép mở vào `design-system/fonts/`.
- Điểm vẫn do agent tự chấm sau khi tự làm. Nên có người chấm độc lập trước khi tin con số 4.0.
- Trạng thái của dashboard đang trình bày như bản thiết kế riêng ở cuối trang.
