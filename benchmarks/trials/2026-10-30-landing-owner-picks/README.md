# Thử lại đề 01 theo 9 website chủ repo chọn

- Loại: thử một đề, `fresh`; không phải lượt benchmark đủ 5 đề nên không vào `REPORT.md`.
- Đề: [01 Landing xưởng gốm](../../briefs/01-landing.md). So với lượt [2026-10-30-fresh](../../runs/2026-10-30-fresh/)
  mà chủ repo nhận xét "xấu quá".
- Người làm: một agent mới, chỉ đọc START-HERE, TASTE, CRAFT và
  [`foundations/owner-picks.md`](../../../foundations/owner-picks.md), không mở `benchmarks/runs/`.
  Agent điều phối soát lại ảnh, sửa một chỗ (nút "Đặt chỗ" sát chữ tiêu đề ở 390 px) và quay video.
- Chấm: `agent-heuristic`, chưa có người duyệt độc lập. **Hướng thị giác: `CHƯA DUYỆT`** cho tới khi chủ repo xem.

## Thay đổi so với lượt trước

| | Lượt 30/10 | Lượt này |
|---|---|---|
| Tham chiếu | Starter kit | BCG, DOD, Corekara trong owner-picks |
| Tiêu đề 1280 px | ~40 px | ~110 px, khoảng dòng ~0,95 |
| Màu | Xanh men ngọc trầm, nhiều card viền | Nền đất xám, một màu men lam Bát Tràng, gần như không card |
| Chữ ký thị giác | Không có | Men lam chảy xuống thân cốc theo cuộn; cùng hình giọt men lặp ở section xanh, icon lớp Tráng men và chữ "Đất Nung" cuối trang |
| Chuyển động | Không | Chữ trồi từng dòng; men chảy và bàn xoay quay theo cuộn; men tràn đổi màu section "Một buổi học" |

## Kết quả soát

- `taste-check` 390/1280, sáng/tối, reflow 320: 0 lỗi, 8 cảnh báo `subtitle` (hai câu trả lời Hỏi đáp mà đề bắt buộc).
- `static-check`, `flow-check`: đạt. Luồng đặt chỗ chạy bằng kịch bản Playwright (form, khoá nút có lý do, xác nhận, màn "Đã đặt chỗ").
- axe-core chưa chạy.

## Ảnh và video

- [`shots/so-sanh-truoc-sau.jpg`](shots/so-sanh-truoc-sau.jpg)
- [`shots/dat-nung-desktop.mp4`](shots/dat-nung-desktop.mp4), [`shots/dat-nung-mobile.mp4`](shots/dat-nung-mobile.mp4): cuộn hết trang, chuyển động bật.
- Ảnh từng vị trí cuộn và các sheet đặt chỗ trong [`shots/`](shots/).

Điểm yếu còn lại ghi ở [`01-landing/NOTES.md`](01-landing/NOTES.md).
