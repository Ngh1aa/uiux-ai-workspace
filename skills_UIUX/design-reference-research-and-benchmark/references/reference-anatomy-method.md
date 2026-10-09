# Reference anatomy theo quyết định và page role

Owner: design-reference-research-and-benchmark. Nạp khi chọn reference hoặc cần giải thích cách chuyển nguyên tắc thành thiết kế. Dữ liệu anatomy theo ngành tiếp tục thuộc visual-design-direction; không tạo catalog cạnh tranh.

## Ba nguồn làm ba việc khác nhau

- Cùng ngành: từ vựng, câu hỏi mua hàng, phạm vi, bằng chứng, quy ước. Một convention có thể cần giữ để dễ hiểu.
- Cùng page role/tác vụ: cấu trúc so sánh, tìm kiếm, detail, form, queue. Không mặc định homepage là entry point.
- Craft khác ngành: tương quan chữ/hình, nhịp, crop, grid, motion. Không lấy giải thưởng làm bằng chứng usability.

Shortlist theo coverage của quyết định; không áp quota cố định. Khi không có reference đúng ngành, ghi giới hạn và điều kiện chuyển từ tác vụ tương tự.

## Một anatomy record đủ để quyết định

Ghi URL + ngày + page/state + viewport + capture/source ref + loaded/partial/blocked. Nếu spinner, cookie overlay che nội dung, lazy image chưa tải hoặc iframe trống: ghi phạm vi quan sát; không đánh giá phần chưa thấy.

| Thuộc tính | Điều phải quan sát | Cách chuyển thành hypothesis |
|---|---|---|
| Vai trò trang | Ai đến từ đâu, đang cần quyết định gì? | Thứ tự nội dung theo câu hỏi đó |
| Main claim / CTA / proof | Claim nào có bằng chứng cạnh nó; CTA đòi cam kết gì? | Nội dung đủ để hành động trước CTA |
| Layout | Quan hệ bên trong các vùng và đối tượng, không chỉ số section | So sánh đồng thời hay đọc tuần tự? Mobile cần đổi thứ tự nào? |
| Typography | Family khai báo/đã tải nếu đo được; size, line-height, weight, measure; vai trò body/UI/meta | Scale đề xuất cho độ dài nội dung của project, không chép H1 của hãng |
| Density / spacing | Trường thông tin thấy cùng lúc; nhóm gần nhau; khoảng nghỉ giữa nhiệm vụ | Dày tại vùng ra quyết định, thoáng ở vùng định hướng; không phủ một density toàn site |
| Visual object | Product view, ảnh người/vật, chart, document, diagram hay chữ; chi tiết nào có nghĩa? | Đối tượng mà project có thể làm thật và người đọc hiểu được |
| Mobile / state | Crop, thứ tự ưu tiên, mất cột, thao tác/focus/error | Không gọi ảnh dashboard desktop thu nhỏ là mobile UX |

Phân biệt **observed** (đo/read-back), **interpreted** (lý do có thể hiệu quả) và **proposed** (áp dụng cho project). Nếu không đo được font, ghi UNKNOWN. Tên asset, quyền tải và quyền tái sử dụng là ba việc khác nhau.

## Quyết định chuyển nguyên tắc

- ADOPT: cùng nhiệm vụ và điều kiện phù hợp; ghi nguyên tắc, không sao chép branded layout/copy.
- ADAPT: nhiệm vụ tương tự nhưng content/brand/thiết bị/assets khác; nêu chính xác phần thay đổi.
- REJECT: không giúp quyết định, phụ thuộc asset không có, hiểu sai sản phẩm hoặc không đáp ứng constraints. Ghi rõ giới hạn theo project; không biến thành cấm serif/gradient/ảnh trên mọi site.

Mỗi transfer ghi: quan sát → rationale → áp dụng vào page/state/thuộc tính → điều không copy → cách kiểm chứng. “Inspired by X” không đủ. Phân tích ví dụ tại [bốn tình huống](../examples/research-to-design-cases.md); tất cả là fixture minh họa, không là commercial proof.

## Sang design

Bàn giao theo page role. Dùng nguồn và decision IDs trong `source.ref`/reference transfers của Design Contract hiện có. Hướng khác nhau cần khác type/density/visual object khi trục đó tự do. Palette/font user gợi ý không tự trở thành constraint cứng; constraint rõ phải được giữ.

Không đặt mặc định mọi reference tốt đều cần ít chữ, nhiều khoảng trắng, ba card hoặc một hero lớn. Chấm shortlist chỉ để hỗ trợ giải thích fit; không dùng tổng điểm che critical mismatch.
