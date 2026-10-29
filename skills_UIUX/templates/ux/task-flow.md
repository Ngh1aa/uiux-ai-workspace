# Task flow: <task inside one screen or a short sequence>

Use when a single screen holds several steps (filters, multi-field form, editor) and the user flow is too coarse.

| Step | User intent | User action | System response | Feedback shown | Can fail? → recovery |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |

## Cognitive load check

- Things the user must remember between steps:
- Decisions the user must make without enough information:
- Steps that could be defaulted, pre-filled or removed:

## Interruption check

What happens if the user leaves at each step (phone call, app switch, timeout)? Is input kept?

## Kiểm luồng khi bàn giao

Theo [FLOW.md](../../../FLOW.md), ghi PASS / FAIL / UNKNOWN riêng: đường vào và kết quả;
Back và bản nháp; sửa rồi xác nhận lại; đối tượng/vai trò; số tiền/ngày/trạng thái;
lỗi và khôi phục; kiểm hậu quả. Kèm lệnh/test/ảnh và phần chưa kiểm, không dùng ảnh thay test hành vi.
