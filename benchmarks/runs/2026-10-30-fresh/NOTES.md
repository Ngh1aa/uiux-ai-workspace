# Lượt 2026-10-30-fresh

Lượt làm mới đầu tiên theo TASTE sau PR #238 và #239 (checker có luật `demo-note`, `small-text`, `left-bar`,
`decor-overlap`, `fixed-overlap`, `subtitle`). Mỗi đề do một agent ngữ cảnh sạch dựng, không xem lượt cũ.
Ghi chú riêng từng đề (kế hoạch thị giác, phần chạy giả lập, dữ liệu giữ chỗ) ở `<đề>/NOTES.md`.

## Quy trình

1. Agent dựng đề, tự soát bằng static-check, flow-check, taste-check và kịch bản Playwright.
2. Runner chính thức (`benchmarks/run.cjs`) lần đầu: 01–03 đạt; 04 tràn ở 1024/390/320, 05 tràn 7px ở 320.
3. Điều phối viên xem ảnh, yêu cầu: bỏ mục tự thêm (02 tab Đã qua, 05 Chi tiết bài tập), sửa nội dung lòi
   quanh thanh tab (02), bỏ hai dòng ghi chú kỳ ở 04. Agent sửa; chạy lại runner: 5/5 PASS.

## Điểm cần chủ repo quyết

- Hai quy tắc chạm nhau ở 02 (tab Đã qua) và 05 (Chi tiết bài tập): bỏ mục tự thêm thì còn mảng trống.
  Hiện giữ màn gọn và để cảnh báo `void`.
- 04 dưới 1024px: khung desktop nằm trong vùng cuộn ngang, không làm bố cục điện thoại.

## Chưa kiểm

axe-core, trình đọc màn hình, chữ phóng 200%, thiết bị và app native thật, người dùng thật. Điểm là
agent-heuristic, chưa có chủ repo duyệt.
