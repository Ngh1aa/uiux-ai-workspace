# Nghiên cứu theo quyết định cần đưa ra

Owner: product-discovery. Dùng trước design khi vấn đề/audience/tiêu chí đánh giá còn có thể thay đổi giải pháp. Không ép một nghiên cứu đầy đủ lên bugfix nhỏ.

## Bắt đầu từ điều chưa biết

Tách buyer (chọn/trả tiền), user (thực hiện việc), operator (vận hành), approver (chấp nhận rủi ro); một người có thể giữ nhiều vai. Ghi tình huống kích hoạt, cách thay thế đang dùng, hệ quả sai sót và thông tin cần quyết định. Với ecommerce người mua có thể khác người dùng quà tặng; với dashboard operator có thể không phải người ký hợp đồng.

Chuyển “người dùng muốn giao diện đơn giản” thành “trong tác vụ X, họ cần thấy trường nào để quyết định Y, và thông tin nào có thể mở sau?”. Ưu tiên câu hỏi theo hệ quả nếu sai × mức chưa biết; không dùng số điểm như dữ liệu thực nghiệm.

## Chọn phương pháp, không mặc định đi tìm website đẹp

| Câu hỏi | Phương pháp/nguồn phù hợp | Không thể kết luận từ riêng nguồn đó |
|---|---|---|
| Nhu cầu phát sinh khi nào, giải pháp thay thế là gì? | Interview hỏi sự kiện gần đây, contextual observation; support/review để tạo giả thuyết khi chưa tiếp cận người dùng | Review công khai không đại diện toàn thị trường; lời kể không chứng minh hành vi |
| Người ta làm gì và kẹt ở đâu? | Quan sát tác vụ, usability session, analytics có event definitions và consent phù hợp | Click count không tự giải thích nguyên nhân; interview không thay quan sát thao tác |
| Tên nhóm và đường tìm thông tin có hợp không? | Content inventory, card sorting cho cách nhóm; tree testing cho tìm trong cấu trúc | Tree test không đo toàn bộ UI, visual hierarchy hoặc thẩm mỹ |
| Họ có hiểu sản phẩm, scope và trạng thái không? | Câu hỏi diễn giải bằng lời của họ trên nội dung/prototype, không đưa từ khóa đáp án | Không suy ra họ sẽ mua từ việc hiểu đúng |
| Flow có dùng được không? | Tác vụ thực tế với success/error/recovery, keyboard/mobile khi liên quan | Một lần expert walkthrough không chứng minh task success của người thật |
| Hướng nào được nhớ và thích? | So sánh concept có đảo thứ tự; hỏi nhớ gì và vì sao sau tác vụ xen kẽ | Preference không bằng usability; vài người không phải A/B test định lượng |
| Ngành đòi hỏi điều gì? | Tài liệu chính thức đúng version/jurisdiction, procurement/specification khi liên quan | Vendor claim không phải certification của project |

## Xử lý nguồn và dừng đúng lúc

Ghi source/version/date, audience và phạm vi, phần thực sự đã truy cập, independence/bias và mức tin cậy. Hai bài lặp cùng press release là một nguồn gốc, không phải xác nhận độc lập. Nguồn cũ có thể vẫn phù hợp nguyên tắc; tài liệu API/pháp lý/version phải kiểm tính hiện hành.

Tìm ít nhất một phản chứng cho giả thuyết có ảnh hưởng lớn: nhóm đối tượng khác, workflow ngoại lệ, nguồn bất đồng hoặc phương án trái với direction ban đầu. “Không tìm được phản chứng” không bằng giả thuyết đúng.

Dừng một vòng khi quyết định tiếp theo có đủ cơ sở trong phạm vi rủi ro, các giả định còn lại có cách thử, và tìm thêm nguồn không thay đổi lựa chọn thực tế. Nếu chưa đạt, ghi đúng khoảng trống có thể đảo quyết định; không tiếp tục chỉ để đủ 10 reference. Prototype có thể đi tiếp với giả thuyết rõ; không dùng nó để biện minh một claim production.

## Handoff

Tái sử dụng product brief, assumption log và research decision log. Mỗi câu hỏi ghi decision ID, nguồn phù hợp, kết luận được phép và bằng chứng còn thiếu. Không tạo số KPI hoặc target như thể người dùng đã yêu cầu.

## Nguồn phương pháp

- [GOV.UK — Plan user research](https://www.gov.uk/service-manual/user-research/plan-user-research-for-your-service): phương pháp theo câu hỏi/giai đoạn, các vòng học có thể tác động đến quyết định.
- [NN/g — Triangulation](https://www.nngroup.com/articles/triangulation-better-research-results-using-multiple-ux-methods/): nhiều nguồn/phương pháp để kiểm độ tin cậy, giữ bất đồng thay vì lấy số đông.

Đối chiếu ngày 2026-10-09. Đây là nguồn phương pháp; số mẫu/lịch của một tổ chức không là quy định chung của Factory. Phân biệt so sánh concept định tính và A/B experiment đủ cỡ mẫu.
