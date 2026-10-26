# Phỏng vấn ngắn và thử nghiệm với người dùng

## Phỏng vấn ngắn (20–30 phút)

Mục tiêu: hiểu hoàn cảnh và lý do, không hỏi ý kiến về giao diện.

### Khung câu hỏi

1. **Khởi động (3 phút):** "Anh chị kể giúp em một ngày bình thường liên quan tới việc [chủ đề]."
2. **Lần gần nhất (10 phút):** "Lần gần nhất anh chị [làm việc đó] là khi nào? Kể lại từng bước giúp em."
   Hỏi tiếp: "Lúc đó anh chị dùng gì? Có ai giúp không? Chỗ nào mất thời gian nhất?"
3. **Nỗi lo và cách chữa cháy (7 phút):** "Có lần nào việc đó trục trặc không? Anh chị xử lý thế nào?"
4. **Kết (3 phút):** "Nếu có cây đũa thần, anh chị muốn bỏ bớt bước nào?" và "Còn điều gì em nên hỏi
   mà chưa hỏi?"

### Quy tắc hỏi

- Hỏi về **việc đã xảy ra**, không hỏi về tương lai ("anh chị có dùng không").
- Một câu hỏi một ý; im lặng 3–5 giây sau câu trả lời để họ nói thêm.
- Không dẫn dắt: thay "Bạn thấy khó đúng không?" bằng "Phần đó thế nào?".
- Không giải thích thiết kế, không bênh vực.
- Ghi nguyên văn câu đáng chú ý, kèm mã người (P1, P2…).

## Thử nghiệm 5 người

Mục tiêu: tìm chỗ người dùng không làm được việc chính trên mẫu thử. Template đầy đủ:
[usability-test-plan.md](../../templates/ux/usability-test-plan.md).

### Chuẩn bị

- 3–5 nhiệm vụ viết thành **tình huống** có mục tiêu, không nhắc tên nút: "Con chị cần nộp bài trước thứ
  Sáu. Chị kiểm tra xem còn thiếu gì." Không viết "Bấm vào tab Hồ sơ".
- Tiêu chí đạt, đạt một phần, không đạt cho từng nhiệm vụ, ghi trước.
- Thử một lượt với đồng nghiệp để sửa câu chữ.

### Trong buổi

- Mở đầu: "Mình đang thử thiết kế, không thử anh chị. Không có câu trả lời sai."
- Xin họ nghĩ thành lời khi làm.
- Khi họ hỏi "bấm đâu?", hỏi lại "anh chị nghĩ nên bấm đâu?". Chỉ giúp khi họ bế tắc quá thời gian định
  trước, và ghi là "không đạt".
- Ghi: nhiệm vụ, kết quả, thời gian, chỗ do dự, câu nói.

### Mức nghiêm trọng

| Mức | Nghĩa |
|---|---|
| 4, chặn | Không hoàn thành được nhiệm vụ chính |
| 3, nặng | Hoàn thành nhưng sai, hoặc mất nhiều thời gian, bực bội rõ |
| 2, vừa | Do dự, đi vòng nhưng tự gỡ được |
| 1, nhẹ | Góp ý thẩm mỹ, không ảnh hưởng nhiệm vụ |

## Thử 5 giây và so sánh hai bản

- **Thử 5 giây:** cho xem màn 5 giây, che đi, hỏi "màn này để làm gì?", "anh chị nhớ gì?", "nên bấm đâu?".
  Kiểm thứ bậc thị giác (xem [`gestalt-and-hierarchy.md`](../../../foundations/gestalt-and-hierarchy.md)).
- **So sánh hai bản:** đổi thứ tự xem giữa người (nửa xem A trước, nửa xem B trước). Hỏi về nhiệm vụ,
  không hỏi "bản nào đẹp hơn".

## Không có người thật

Walkthrough bằng proto-persona: đi từng nhiệm vụ, ở mỗi màn hỏi "người này thấy gì, hiểu gì, bấm gì, có
thể sai ở đâu". Ghi kết quả `HEURISTIC_ONLY`, kèm kế hoạch thử thật `PLANNED_VALIDATION`.
