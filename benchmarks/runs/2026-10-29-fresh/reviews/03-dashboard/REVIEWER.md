# Hướng dẫn người duyệt

Bạn duyệt một thiết kế mà không biết người làm nghĩ gì. Chỉ dùng các file trong thư mục này.
**Không mở** repo, mã HTML hay CSS, ghi chú hay điểm tự chấm của người làm, kể cả khi có quyền.

## Vòng 1: đọc lạnh (chưa mở brief)

Mở lần lượt các ảnh trong `images/`. Với mỗi ảnh, trả lời ba câu, mỗi câu một đến hai dòng:

1. Màn này để làm gì?
2. Bạn sẽ bấm vào đâu đầu tiên?
3. Điều gì trông sai, rối hoặc thiếu?

Ghi câu trả lời vào `cold` trong `review.json` trước khi đọc brief. Không sửa lại sau khi đọc brief.

## Vòng 2: chấm theo brief và rubric

1. Đọc `brief.md`, rồi `rubric.md`.
2. Soát từng hard fail (HF-1 tới HF-10). Hard fail nào thấy được trên ảnh thì ghi mã, ảnh, và điều thấy.
   Điều không kiểm được từ ảnh (bàn phím, trình đọc màn hình, chữ phóng to) ghi vào `not_checked`.
3. Chấm 10 chiều, từ 1 tới 5. Mỗi điểm dưới 4 cần ít nhất một ghi nhận: chiều, ảnh, phần tử, cách sửa.
4. Ngưỡng của cỡ việc **M**: không hard fail, trung bình ≥ 3.5, không chiều nào < 3.

## Trả về

Chép `review.template.json` thành `review.json`, điền đủ, rồi người làm chạy:

```sh
python3 scripts/review-packet.py verify <thư mục này>
```

Ghi `reviewer.kind` là `expert-review` nếu bạn là người ngoài nhóm làm, `agent-heuristic` nếu bạn là
agent. Agent ở phiên độc lập vẫn là `agent-heuristic`, nhưng được ghi `independent: true`.
