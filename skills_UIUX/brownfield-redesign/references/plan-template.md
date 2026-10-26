# Kế hoạch redesign: <tên dự án>

Chép file này vào `docs/redesign/plan.md` của dự án và điền.

## Yêu cầu và mức thay đổi

- Lời người dùng: "<trích nguyên văn>"
- Mức: Polish / Refresh / **Redesign**
- Nhánh gốc: `<nhánh hoặc commit>` · Nhánh làm: `<nhánh>`

## Giữ nguyên

| Thứ | Vì sao | Test bảo vệ |
|---|---|---|
| Công thức số dư "Safe to spend" | Nghiệp vụ | `nova-flow.spec` "safe to spend" |

## ADN

| Đặc điểm | Giữ / làm tốt hơn / bỏ | Ai chọn bỏ |
|---|---|---|

## Hướng đã duyệt

- Hướng: <tên> · Trạng thái: ĐÃ DUYỆT bởi <ai, ngày> / CHƯA DUYỆT
- ADN: giữ … / đổi … / bỏ …

## Thay thế theo chủ sở hữu

| Chủ sở hữu cũ | Thay bằng | Xoá | Test bảo vệ | Xong |
|---|---|---|---|---|
| `assets/tokens.css` màu nền | token `--surface-*` mới, cùng file | 14 biến màu cũ | axe contrast | ☐ |
| `assets/pastel-dashboard.css` | gộp vào `components/card.css` | cả file + thẻ nạp | home.spec | ☐ |
| renderer `renderHome()` | markup mới: 1 hero, 1 danh sách | khối mô tả lặp | home.spec | ☐ |

## Ngoại lệ ngân sách

| Ngoại lệ | Lý do | Gỡ khi nào |
|---|---|---|

## Test

| Bộ test | Trước | Sau |
|---|---|---|

| Test đã đổi | Trước kiểm | Sau kiểm | Lý do |
|---|---|---|---|

## Kết quả soát

- `overlay-check.py`: <số lỗi, cảnh báo>
- Diff CSS: +<thêm> / -<xoá>; file xoá: <số>
- `taste-check`: <kết quả>
- Phép thử nhận ra hai chiều: ADN còn <có/không>; khác biệt thấy ngay <có/không>
- Duyệt độc lập: <điểm, gồm dòng giữ ADN>
