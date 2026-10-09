# Từ bằng chứng đến quyết định thiết kế

Owner: research-synthesis-and-insight-management. Dùng cho desk evidence, support/proxy, nghiên cứu người thật hoặc nhiều loại kết hợp. Không nâng evidence class khi tổng hợp.

## Chuỗi truy vết

`source E → observation → interpretation F → decision D → page/state + property → alternative/tradeoff → verification`

Ví dụ minh họa, không phải kết quả user research:
- E: brief yêu cầu so sánh phạm vi hai gói dịch vụ; đây là constraint, không phải quan sát người mua.
- F: so sánh có thể thuận lợi nếu các thuộc tính tương ứng cùng trục. Đây là diễn giải/hypothesis.
- D: detail đặt inputs/outputs/exclusions theo hàng tương ứng; mobile ưu tiên một nhóm thuộc tính rồi mở phần khác.
- Alternative: đoạn prose tự do; tradeoff là tự nhiên hơn nhưng khó đối chiếu.
- Verify: giao tác vụ chọn gói thỏa hai constraints, hỏi điều gì bị loại trừ; ghi lỗi hiểu phạm vi. Chưa có người thử thì UNKNOWN.

## Cách tổng hợp

1. Tách observation nhỏ, gắn task/context/version và source. Không mã hóa note thành solution quá sớm.
2. Nhóm bằng nhu cầu/cơ chế, không chỉ từ khóa trùng. Giữ reviewer/sản phẩm khác nhau để tránh ghép sai.
3. Ghi evidence ủng hộ và mâu thuẫn cùng finding. Nguồn lặp không tăng sample size.
4. Một lỗi hiếm có hậu quả nặng có thể quan trọng hơn lời khen thường xuyên; báo riêng severity và confidence.
5. Mỗi decision phải chọn giữ, sửa, bỏ hoặc hoãn. Nêu cụ thể content/layout/type/density/media/state thay đổi ở đâu.
6. Nếu nguồn chỉ hỗ trợ vấn đề, không gán solution là validated. Hypothesis thiết kế vẫn cần render và thử đúng phương pháp.

## Dùng artifact đã có

Tái sử dụng evidence ledger và decision log của research-evidence-pipeline; không tạo format song song. `DESK_EVIDENCE` ghi quan sát từ tài liệu/website; `HYPOTHESIS` ghi giả thuyết; session_id bỏ trống khi không có session. Source ref dùng URL/file + anchor ổn định; ngày/phạm vi/giới hạn phải rõ.

Findings ghi quyết định nào có thể thay đổi nếu UNKNOWN được giải quyết. Nếu thiếu nguồn, ghi UNKNOWN và next evidence; không gắn một URL nổi tiếng chỉ để lấp ô.

Dùng [các ví dụ theo loại project](../../design-reference-research-and-benchmark/examples/research-to-design-cases.md) để học cơ chế chuyển, không dùng nội dung fixture như nghiên cứu cho project thật.

## Kiểm nội dung, không chỉ cấu trúc

Một ledger hợp lệ về JSON không chứng minh nguồn được đọc. Một design contract hợp lệ không chứng minh pixels tốt. Hỏi: nếu bỏ finding này thì quyết định nào thay đổi? Nếu không trả lời được, đó có thể chỉ là kiến thức nền; đừng đưa thành insight chính.

Tách comprehension, task performance, meaningful recall/distinctiveness và preference. Chỉ so preference sau khi kiểm hiểu sai/tác vụ quan trọng. Đảo thứ tự concept khi phù hợp; không quy tác động riêng cho font nếu đồng thời đổi layout và hình. Mẫu nhỏ báo từng trường hợp; simulated/expert review không phải participant research.
