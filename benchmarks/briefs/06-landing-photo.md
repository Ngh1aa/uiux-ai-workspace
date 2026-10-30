# Đề 6: Landing page homestay "Nhà Gỗ Thông" có ảnh thật

**Thêm vào:** 2026-10-31

**Cỡ việc:** M (một trang). **Ngưỡng rubric:** không hard fail, trung bình ≥ 3.5, không chiều nào < 3.

Đề landing thứ hai, khác đề 01 ở chỗ **phải dùng ảnh thật**, để đo phần chữ, màu, ảnh và chuyển động theo
[`owner-picks.md`](../../foundations/owner-picks.md). Đề 01 giữ nguyên để so với các lượt cũ.

## Bối cảnh

Nhà Gỗ Thông là homestay nhỏ ở Trại Mát, Đà Lạt, bốn phòng gỗ giữa đồi thông. Khách chủ yếu là cặp đôi và nhóm
bạn 25–35 tuổi ở TP.HCM, tìm thấy qua Instagram và TikTok, mở trang trên điện thoại.

**Việc chính của khách:** xem phòng trông thế nào, giá bao nhiêu, rồi đặt phòng.

## Nội dung bắt buộc (dùng đúng chữ và số dưới đây)

- Tên: Nhà Gỗ Thông. Câu định vị: "Bốn căn nhà gỗ, một đồi thông, sáng nào cũng có sương."
- Bốn phòng:
  | Phòng | Số khách | Giá một đêm |
  |---|---|---|
  | Gác Sương | 2 người | 950.000 ₫ |
  | Hiên Thông | 2 người | 1.150.000 ₫ |
  | Nhà Đồi | 4 người | 1.650.000 ₫ |
  | Nhà Suối | 4 người | 1.850.000 ₫ |
- Giá đã gồm bữa sáng và xe đón từ ga Trại Mát. Cuối tuần (thứ Sáu, thứ Bảy) cộng 200.000 ₫ mỗi đêm.
- Nhận phòng 14:00, trả phòng 11:00.
- Hai câu hỏi thường gặp: "Có cho mang thú cưng không?" (Có, phòng Nhà Đồi và Nhà Suối, tối đa một chó
  hoặc mèo) và "Từ trung tâm Đà Lạt đi bao xa?" (8 km, khoảng 20 phút xe máy).
- Địa chỉ: 12 Trại Mát, phường 11, Đà Lạt. Điện thoại: 0903 456 789.

## Ảnh

- Bắt buộc dùng ảnh thật: ít nhất một ảnh lớn đầu trang và một ảnh cho mỗi phòng. Ảnh nằm cùng thư mục bài làm
  (không gọi ảnh từ host ngoài), tối ưu cỡ (`srcset`, có `width`, `height`, `alt`).
- Chưa có ảnh của khách thì dùng ảnh kho có giấy phép dùng tự do (ví dụ Unsplash), ghi mã ảnh và giấy phép trong
  `NOTES.md`. Không ảnh AI, không ảnh có người nhận ra được mặt.

## Yêu cầu

- Một nút đặt phòng chính, xuất hiện ở đầu trang và cuối trang. Đặt phòng chọn phòng, ngày nhận, số đêm, số khách
  (không quá sức chứa phòng), họ tên, số điện thoại, hiện tổng tiền đã cộng phụ thu cuối tuần, có bước xác nhận và
  màn kết quả theo `TASTE.md`.
- Chọn 1–2 trang trong [`owner-picks.md`](../../foundations/owner-picks.md) làm chuẩn chữ, màu và ảnh; ghi tên
  trong kế hoạch thị giác. Tối đa 3 hiệu ứng kể chuyện lấy từ
  [`motion-recipes`](../../foundations/motion-recipes/index.html), có bản tĩnh khi giảm chuyển động.
- Đọc tốt ở 390px và 1280px, cả chế độ sáng và tối.
- Theo `TASTE.md`.

## Giao

Một file `06-landing-photo/index.html` trong thư mục lần chạy, ảnh và font trong cùng thư mục. Được nạp CSS của
`design-system/`.
