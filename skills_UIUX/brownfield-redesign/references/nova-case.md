# Ca gốc: Nova v6 (PR #76, 26/10/2026)

Yêu cầu: dùng repo này nâng cấp toàn bộ giao diện của Nova, một prototype ngân hàng HTML/CSS/JS có nhiều
test Playwright. Repo dẫn tới cỡ L, cổng duyệt hướng, duyệt độc lập; phần thiết kế được làm đúng quy
trình. Phần thực thi trên code thì không.

## Số đo của nhánh

`overlay-check.py --base main --head claude/nova-v6-giao-dien` trên repo Nova:

```
ERROR   overlay-ratio: Thêm 456 dòng CSS nhưng chỉ xoá hoặc sửa 0 dòng CSS cũ
ERROR   new-layer: assets/nova-v6.css: File CSS mới 456 dòng được nạp sau cùng (app.html, figma-export.html)
ERROR   important: Tăng ròng 699 `!important`
ERROR   dom-patch: assets/nova-v6.js: File JS mới tìm phần tử đã render rồi chèn hoặc sửa HTML
ERROR   untouched-owners: Dự án có 37 file CSS cũ nhưng nhánh này không sửa hay xoá file nào
```

## Người dùng thấy gì

- Mất chất pastel iOS: hướng được chọn dùng nền trung tính và card mực đậm; pastel chỉ còn trong thanh
  Money Horizon.
- Màn vẫn trống và nhiều chữ: renderer cũ không đổi, CSS mới chỉ đổi màu và khoảng cách trên markup cũ.
- Duyệt độc lập chấm 3.05/5 với 7 lỗi chặn, nhiều lỗi do lớp đè va với cascade cũ (biểu đồ bị cắt trong
  khối cuộn, nhãn trên nền gradient không đủ tương phản).

## Vì sao repo dẫn tới kết quả đó

| Nguyên nhân trong repo | Hệ quả |
|---|---|
| Không có quy trình cho sản phẩm đã có code; track "Cải thiện UI đang có" ghi "giữ thương hiệu và hành vi" và trỏ tới 4 gạch đầu dòng | Claude hiểu "giữ" là không đụng code |
| `AGENTS.md` mục 5 "giữ thay đổi gọn, không tiện tay sửa chỗ khác", "không xoá file quan trọng" viết cho repo này nhưng không nói rõ phạm vi | Áp nhầm sang dự án khách: không dám xoá CSS cũ |
| `frontend-implementation` chỉ nói "giữ hành vi đang chạy", "không rebuild khi không cần", không nói khi nào phải thay | Mọi thay đổi đều nghiêng về thêm, không sửa |
| Starter kit, `brand.css`, pattern `pt-*` giả định trang mới | Không có cách lắp vào Nova ngoài một lớp đè |
| `TASTE.md` đứng trên mọi phong cách; không có bước ghi ADN sản phẩm | Gu chung "ít màu, nền trung tính" xoá pastel của Nova |
| Không có test nào phân biệt hành vi với giao diện | Sợ làm đỏ test giao diện, chọn đè để test cũ vẫn xanh |
| Không có kiểm tra đo việc phủ đè | Mọi kiểm tra xanh dù nhánh không sửa dòng CSS cũ nào |

Skill [`brownfield-redesign`](../SKILL.md) và `overlay-check.py` sinh ra để chặn đúng chuỗi này.
