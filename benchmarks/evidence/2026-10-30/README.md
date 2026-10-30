# Chấm lại theo gu chủ repo, 2026-10-30

Soát lại hai lượt đã đóng băng (`2026-10-29-fresh`, `2026-10-29-iterative-repair`) bằng checker sau PR #238,
rồi xem ảnh và chấm theo [TASTE.md](../../../TASTE.md). Không sửa file nào trong `runs/`; điểm rubric cũ trong
`scores.json` và [REPORT.md](../../REPORT.md) giữ nguyên làm lịch sử.

Người chấm: agent (agent-heuristic), **không độc lập**, chưa có chủ repo duyệt: `CHƯA DUYỆT`.

## Bằng chứng

| File | Nội dung |
|---|---|
| `render/<lượt>--<đề>.json` | `taste-check.cjs` trên CI, 390 px và 1280 px, sáng; đề 04 thêm `--layout strict` |
| `static.json` | `static-check.cjs` trên nguồn trang |

Ảnh dùng để xem là ảnh có sẵn trong `runs/<lượt>/shots/`.

## Kết quả

Đạt theo TASTE nghĩa là không còn lỗi render, không còn lỗi tĩnh thuộc TASTE, và xem ảnh không thấy vi phạm.

| Đề | Lượt | Lỗi render (TASTE) | Lỗi tĩnh (TASTE) | Thấy thêm khi xem ảnh | Theo TASTE |
|---|---|---|---|---|---|
| 01 landing | fresh | 0 | ghi chú bản mẫu ở footer, khai báo CSS chữ 10px | chú thích nghiêng dưới minh hoạ; cột trái mục hỏi đáp trống | Chưa đạt |
| 01 landing | sửa tiếp | ghi chú bản mẫu ×2, hoạ tiết đè chữ | ghi chú bản mẫu | 12 dòng giải thích phụ dưới tiêu đề | Chưa đạt |
| 02 app | fresh | hoạ tiết đè chữ ×4 | ghi chú bản mẫu ×2, khai báo CSS chữ 10px | thanh "Mẫu tương tác…" trên cùng; dòng phụ dưới "Tối nay gần bạn"; nav hiện nhãn mọi tab | Chưa đạt |
| 02 app | sửa tiếp | 0 | ghi chú bản mẫu ×3 | đoạn ghi chú bản mẫu đầu trang; vạch lưới chạy qua chữ trên card nổi bật; nav hiện nhãn mọi tab, viên chạm mép | Chưa đạt |
| 03 dashboard | fresh | ghi chú bản mẫu ×4, chữ < 12 px ×4 | ghi chú bản mẫu ×4 | dòng phụ dưới mọi tiêu đề card; card "Tồn kho theo ngày bán" toàn chữ giải thích; dòng sản phẩm mobile có khoảng trống lớn | Chưa đạt |
| 03 dashboard | sửa tiếp | ghi chú bản mẫu ×2 | ghi chú bản mẫu | "Cập nhật 7:45", "Nghìn đồng, 17/10 tới 23/10", "Ví dụ trạng thái minh hoạ" | Chưa đạt, gần đạt nhất |
| 04 phòng khám | fresh | ghi chú bản mẫu ×4 | ghi chú bản mẫu ×6 | công tắc vai trò trên header; 3 dòng chú thích; mobile một cột dài, chi tiết dính cuối trang | Chưa đạt |
| 04 phòng khám | sửa tiếp | như fresh (tái dùng) | như fresh | như fresh | Chưa đạt |
| 05 native | fresh | ghi chú bản mẫu ×3, chữ < 12 px ×17 | ghi chú bản mẫu | nút cuối form bị tab bar che; nav hiện nhãn mọi tab; ghi chú bản mẫu trong form | Chưa đạt |
| 05 native | sửa tiếp | như fresh | như fresh | như fresh | Chưa đạt |

**0/10 bài đạt theo TASTE**, trong khi bảng cũ ghi 8/10 Đạt. Lỗi lặp lại ở mọi đề là ghi chú bản mẫu trên
màn; kế đến là dòng giải thích phụ, chữ dưới 12 px và nav không theo kiểu viên.

## Lỗi checker lộ ra khi soát lại, đã sửa trong PR này

- `demo-note` bỏ lọt "Bản minh hoạ" vì `\b` của JavaScript không nhận chữ có dấu ở cuối từ. Đã đổi sang
  kiểm tra chữ cái Unicode.
- Tab bar mới của starter làm tràn ngang lượt sửa tiếp đề 02 (markup cũ chưa bọc nhãn). Đã giữ bố cục cũ cho
  markup chưa có `.app-tabbar__label`.

## Checker còn bỏ sót, ghi để làm tiếp

- Chữ nằm ngoài các `data-screen` (đầu trang gallery, footer landing) không được soát render; `static-check`
  vẫn bắt.
- Vạch trang trí vẽ bằng phần tử thật hoặc nền, không qua `::before`/`::after`, chưa được `decor-overlap` bắt
  (lượt sửa tiếp đề 02).
- Nút bị tab bar che trong khung xem trước native (đề 05) chưa được `fixed-overlap` bắt; cần xem cách khung
  dựng thanh tab.
- `static-check` còn hai lỗi trợ năng có từ trước (`aria-prohibited`, `name-mismatch`) ở đề 04 và 05.

## Bước tiếp theo

Chạy một lượt `fresh` mới cho cả 5 đề theo TASTE hiện tại, với checker đã sửa, rồi để chủ repo duyệt ảnh.
