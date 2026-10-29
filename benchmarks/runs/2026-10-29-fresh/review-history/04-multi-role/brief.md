# Đề 4: Web app quản lý phòng khám nha "Răng Xinh", ba vai trò, desktop

**Thêm vào:** 2026-10-26

**Cỡ việc:** L (một khu vực sản phẩm, nhiều vai trò). **Ngưỡng rubric:** không hard fail, trung bình ≥ 4.0,
không chiều nào < 3.5.

## Bối cảnh

Phòng khám nha khoa ba ghế ở Huế, mở 8:00–20:00. Cả phòng khám dùng chung một web app trên máy tính bàn
1280–1440 px. Ba vai trò mở app với ba câu hỏi khác nhau:

| Vai trò | Người dùng | Câu hỏi khi mở app |
|---|---|---|
| Lễ tân | Nguyễn Thảo | Ai sắp đến, ai đến muộn, ghế nào trống để xếp khách vãng lai? |
| Bác sĩ | BS. Phan Minh Đức | Bệnh nhân tiếp theo là ai, lần trước làm gì, hôm nay làm gì? |
| Chủ phòng khám | Lê Quỳnh Anh | Hôm nay và tháng này doanh thu ra sao, lịch có bị trống nhiều không? |

## Bốn màn bắt buộc

1. **Lễ tân: lịch hôm nay.** Lịch theo ghế và giờ, trạng thái từng lượt (đã đến, đang khám, chưa đến,
   muộn), ô tìm bệnh nhân, nút đặt lịch. Thể hiện **xung đột**: đặt khách vãng lai vào khung đã có người.
2. **Bác sĩ: bệnh nhân tiếp theo.** Thông tin bệnh nhân, tiền sử dị ứng nổi bật, lần khám trước, kế hoạch
   điều trị hôm nay, ghi chú. Hành động: bắt đầu khám, gọi bệnh nhân kế.
3. **Chủ phòng khám: tổng quan.** Doanh thu hôm nay và tháng, tỉ lệ lấp ghế, lượt huỷ, biểu đồ doanh thu
   theo ngày trong tháng. Có **trạng thái rỗng**: một ghế mới thêm chưa có dữ liệu.
4. **Đổi vai trò và phân quyền.** Cùng một khung app, cho thấy mỗi vai trò thấy điều hướng gì và bị ẩn gì.
   Thể hiện **trạng thái không có quyền**: lễ tân mở trang doanh thu.

## Dữ liệu (dùng đúng)

- Ngày: thứ Ba 28/10. Ghế 1 (BS. Đức), Ghế 2 (BS. Hoàng Lan), Ghế 3 (vệ sinh răng, KTV Trần Bảo).
- Lịch sáng: 8:00 Võ Thị Hồng (Ghế 1, trám răng, đã đến); 8:30 Đặng Quốc Việt (Ghế 2, nhổ răng khôn,
  đang khám); 9:00 Hồ Ngọc Mai (Ghế 3, cạo vôi, muộn 15 phút); 9:30 Lâm Gia Bảo, 8 tuổi (Ghế 1, nhổ răng
  sữa, chưa đến); 10:00 Trương Văn Nam (Ghế 2, tái khám niềng, chưa đến); 10:30 Ghế 1 trống.
- Bệnh nhân tiếp theo của BS. Đức: Lâm Gia Bảo, 8 tuổi, mẹ là chị Lâm Thu đi kèm. **Dị ứng: penicillin.**
  Lần trước 12/09: khám tổng quát, chụp phim, hẹn nhổ răng sữa R74. Hôm nay: nhổ R74, gây tê tại chỗ.
- Doanh thu hôm nay đến 10:00: 3.450.000 đ (12 lượt dự kiến cả ngày). Tháng 10 đến hôm nay: 186.200.000 đ,
  cùng kỳ tháng 9: 171.500.000 đ. Tỉ lệ lấp ghế tháng 10: 78%. Lượt huỷ tháng 10: 9.
- Ghế 3 mới đưa vào dùng từ 20/10, chưa đủ 7 ngày dữ liệu.

## Yêu cầu

- Khung 1280 × 800 và 1440 × 900. Một khung app chung (thanh bên, thanh trên), nội dung đổi theo vai trò.
- Mỗi màn trả lời câu hỏi của vai trò đó trong 5 giây. Dị ứng của bệnh nhân không được lẫn vào phần còn lại.
- Đạt `--layout strict` ở 1280 và 1440, sáng và tối. Bàn phím đi hết được lịch và form đặt lịch.
- Đổi thương hiệu cho hợp nha khoa gia đình, không dùng mặc định của starter.
- Qua [cổng duyệt hướng](../../WORKFLOWS.md#cổng-duyệt-hướng-m-l-xl) trên màn lịch lễ tân; không có
  người duyệt thì ghi `CHƯA DUYỆT`.
- Ghi trong `NOTES.md`: ma trận vai trò × màn × quyền; điều gì chỉ mô phỏng (không có backend).

## Giao

Một file `04-multi-role/index.html` chứa cả 4 màn, mỗi màn là một phần tử có `data-screen`.
Được dùng `design-system/starter/desktop.html` và `design-system/patterns/`.
