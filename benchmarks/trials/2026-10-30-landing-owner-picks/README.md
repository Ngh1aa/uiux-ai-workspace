# Thử lại đề 01 theo 9 website chủ repo chọn

- Loại: thử một đề, `fresh`; không phải lượt benchmark đủ 5 đề nên không vào `REPORT.md`.
- Đề: [01 Landing xưởng gốm](../../briefs/01-landing.md); vòng 5 bỏ yêu cầu "không dùng ảnh" theo quyết định chủ repo. So với lượt [2026-10-30-fresh](../../runs/2026-10-30-fresh/)
  mà chủ repo nhận xét "xấu quá".
- Người làm: một agent mới, chỉ đọc START-HERE, TASTE, CRAFT và
  [`foundations/owner-picks.md`](../../../foundations/owner-picks.md), không mở `benchmarks/runs/`.
  Agent điều phối soát lại ảnh, quay video, rồi sửa ba điểm yếu chủ repo chỉ ra: cốc có khối và chất liệu,
  bố cục "Một buổi học" không còn góc trống, cuộn mượt cho chuột (vòng 4 trong NOTES).
- **Vòng 5:** chủ repo chê chữ, ảnh, màu; chọn cho dùng ảnh và hướng DOD / Wedding. Trang được làm lại phần chữ,
  màu, ảnh; chuyển động giữ. Chi tiết ở NOTES, mục "Vòng 5".
- Chấm: `agent-heuristic`, chưa có người duyệt độc lập. **Hướng thị giác: `CHƯA DUYỆT`** cho tới khi chủ repo xem.

## Thay đổi so với lượt trước (vòng 5)

| | Lượt 30/10 | Vòng 5 |
|---|---|---|
| Tham chiếu | Starter kit | DOD và Wedding trong owner-picks (chủ repo chọn) |
| Ảnh | Không (đề cấm) | 7 ảnh thật, ảnh rộng đầu trang và khung vòm như miệng lò nung |
| Chữ | Có chân ~40 px | Không chân hình học 124 px; một từ nghiêng có chân mỗi tiêu đề lớn |
| Màu | Xanh men ngọc trầm, nhiều card viền | Trắng ngà, mực, một màu đất nung |
| Chuyển động | Không | Chữ trồi từng dòng; ảnh đầu trang nở theo cuộn; ảnh vòm hiện từ dưới lên; cuộn mượt cho chuột |

## Kết quả soát

- `taste-check` 390/1024/1280/1440, sáng/tối, reflow 320: 0 lỗi; cảnh báo chỉ còn `subtitle` (câu trả lời Hỏi đáp và dòng "Giá đã gồm…" mà đề bắt buộc).
- `static-check`, `flow-check`: đạt. Luồng đặt chỗ chạy bằng kịch bản Playwright (form, khoá nút có lý do, xác nhận, màn "Đã đặt chỗ").
- axe-core chưa chạy.

## Ảnh và video

- [`shots/so-sanh-truoc-sau.jpg`](shots/so-sanh-truoc-sau.jpg)
- [`shots/dat-nung-desktop.mp4`](shots/dat-nung-desktop.mp4), [`shots/dat-nung-mobile.mp4`](shots/dat-nung-mobile.mp4): cuộn hết trang, chuyển động bật.
- Ảnh từng vị trí cuộn và các sheet đặt chỗ trong [`shots/`](shots/).

Điểm yếu còn lại ghi ở [`01-landing/NOTES.md`](01-landing/NOTES.md).
