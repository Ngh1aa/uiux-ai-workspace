# Đề 3: Dashboard kho cho shop online "Len Nhỏ"

**Cỡ việc:** M (một trang quản trị). **Ngưỡng rubric:** không hard fail, trung bình ≥ 3.5,
không chiều nào < 3.

## Bối cảnh

Len Nhỏ bán len và dụng cụ đan móc online, chủ shop tự quản lý kho. Mỗi sáng chủ shop mở trang
này trên máy tính, đôi khi trên điện thoại, để biết hôm nay phải nhập hàng gì và đơn nào cần gửi.

**Câu hỏi chính:** *Hôm nay tôi cần nhập hàng gì và gửi đơn nào trước?*

## Dữ liệu (dùng đúng)

- Đơn chờ gửi: 14, trong đó 3 đơn quá hạn gửi.
- Doanh thu 7 ngày qua (nghìn đồng): T6 2.150, T7 3.480, CN 4.120, T2 1.890, T3 2.260, T4 2.010,
  T5 2.640. Tổng 18.550.
- Sắp hết hàng:
  | Sản phẩm | Mã | Còn | Bán mỗi ngày | Đủ bán |
  |---|---|---|---|---|
  | Len cotton màu kem | LC-012 | 6 cuộn | 3 | 2 ngày |
  | Kim móc 3,5 mm | KM-035 | 4 cây | 1 | 4 ngày |
  | Len lông cừu màu rêu | LW-207 | 9 cuộn | 2 | 4 ngày |
  | Len cotton màu hồng đất | LC-031 | 15 cuộn | 2 | 7 ngày |
- Đơn quá hạn gửi: #2041 (chị Hà, Đà Nẵng, quá 2 ngày), #2045 (anh Tuấn, Hà Nội, quá 1 ngày),
  #2047 (chị Mai, Cần Thơ, quá 1 ngày).

## Yêu cầu

- Có biểu đồ doanh thu 7 ngày. Theo skill `data-visualization-and-dashboard-ux`.
- Sản phẩm "đủ bán ≤ 2 ngày" và đơn quá hạn phải nổi bật, nhưng không đỏ cả trang.
- Đọc tốt ở 1280px và 390px, cả chế độ sáng và tối, không cuộn ngang.
- Được dùng starter kit, đổi thương hiệu cho hợp shop len. Theo `TASTE.md`.

## Giao

Một file `03-dashboard/index.html` trong thư mục lần chạy.
