# Lần chạy 2026-10-24-v1: mốc gốc

Lần chạy đầu tiên của bộ đề, làm theo `START-HERE.md` với repo sau #222 và #223 (starter kit,
taste-check). Người làm và người chấm là cùng một agent, nên điểm là `agent-heuristic` và có thể
cao hơn thực tế.

## Kết quả

| Đề | Cỡ | Soát | Hard fail | TB | Ngưỡng |
|---|---|---|---|---|---|
| 01 Landing xưởng gốm | M | 0 lỗi | 0 | 3.7 | Đạt |
| 02 App đặt sân, 5 màn | L | 0 lỗi | 0 | 3.8 | Chưa đạt (cần TB ≥ 4.0, không chiều nào < 3.5) |
| 03 Dashboard kho | M | 0 lỗi | 1 (HF-5) | 3.8 | Chưa đạt |

Chiều yếu nhất ở cả ba đề: **7 Tương tác, phản hồi** và **10 Tay nghề, dấu ấn** (đều 3).

## Lỗi bắt được trong lúc làm

Đây là những lỗi xuất hiện ở bản đầu tiên của từng đề, đã sửa trước khi chấm.

| Đề | Lỗi | Ai bắt |
|---|---|---|
| 01 | Section mất lề, chữ sát mép màn trên điện thoại | Nhìn ảnh (script chưa có luật) |
| 01 | Logo và nút gọi trên điện thoại nhỏ hơn 44px | taste-check |
| 02 | Chữ phụ trên dải số liệu chỉ đạt 3.9:1 khi đổi sang thương hiệu sáng hơn | taste-check |
| 02 | Khung giờ trống khác màu giữa Trang chủ và Chi tiết | Nhìn ảnh |
| 02 | Nút bị khoá mang tông be ấm lệch nền | Nhìn ảnh |
| 03 | Dải số liệu tràn, bảng bị cắt, tiêu đề gãy dòng trên điện thoại | taste-check |
| 03 | Cột "Đủ bán" bị khung bảng cắt mất ở 1280px | Nhìn ảnh (script chưa có luật) |
| 03 | Ở 1024px thanh bên chiếm chỗ, hai cột vỡ hết | taste-check sau khi thêm khổ 1024px |

Số vòng chụp và sửa: 01 ba vòng, 02 ba vòng, 03 sáu vòng.

## Repo được sửa nhờ lần chạy này

- **taste-check** thêm luật: chữ sát mép màn hẹp, chữ bị khung cha cắt mất, dòng cuối một chữ;
  bỏ báo nhầm cho đường kẻ đơn, thanh tràn viền và phần chỉ dành cho trình đọc màn hình.
- **starter kit**: chữ trên dải số liệu luôn đủ tương phản với mọi màu thương hiệu; token nút bị
  khoá theo tông lạnh; thanh bên trang web cao hết trang; dưới 1200px trang web xếp một cột.
- **Bộ đề và CI** soát thêm khổ 1024px.

## Quy trình

- `visual-design-direction` đòi hồ sơ quyết định JSON và so sánh A/B có người chấm. Quá nặng cho
  một lần làm cá nhân nên lần này bỏ qua; mỗi đề chỉ có một phương án.
- Thứ thật sự giúp: `TASTE.md`, starter kit, taste-check và việc mở ảnh chụp ra nhìn. Ba lỗi lớn
  nhất đều phát hiện bằng mắt trước khi script có luật tương ứng.

## Việc nên làm trước lần chạy sau

1. Starter kit thêm mẫu trạng thái cho trang web (đang tải, dữ liệu cũ, lỗi từng khối).
2. Làm rõ cách tạo dấu ấn riêng cho từng dự án khi dùng starter kit, để app không chỉ là bản đổi màu.
3. Mẫu tương tác sâu hơn: chọn trực tiếp từ danh sách, tổng tiền luôn thấy được ở màn đặt.
4. Có một người chấm độc lập (người thật hoặc agent không tham gia làm) cho lần chạy sau.
