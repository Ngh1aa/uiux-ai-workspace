# Duyệt độc lập bằng hồ sơ ảnh

Người làm tự chấm luôn cao hơn thực tế: họ biết mình định làm gì nên nhìn thấy điều đó cả khi màn chưa
nói ra. Duyệt độc lập tách hai việc: **người duyệt chỉ thấy điều người dùng thấy** (ảnh chụp), cùng brief
và rubric, không thấy code, ghi chú hay điểm tự chấm.

## Khi nào bắt buộc

| Cỡ việc | Duyệt độc lập |
|---|---|
| XS, S | Không cần |
| M | Nên có trước khi giao khách |
| L, XL | Bắt buộc ở vòng 3 của [rubric](quality-bar-rubric.md#three-round-critique-l-and-xl) |
| Đề chuẩn trong `benchmarks/` | Bắt buộc để ghi `independent_review: true` |

## Bước 1: chụp và đóng gói

```sh
node skills_UIUX/ui-craft-and-visual-qa/scripts/taste-check.cjs <trang.html> --screenshot qa/
python3 scripts/review-packet.py make --shots qa/ --brief <brief.md> --size L --out review/
```

Thư mục `review/` chỉ có ảnh, brief, rubric, hướng dẫn người duyệt, `manifest.json` (SHA-256 từng ảnh)
và mẫu kết quả. Không chép thêm gì vào đó.

## Bước 2: giao cho người duyệt

**Người thật** (ưu tiên): gửi thư mục, ghi `reviewer.kind: expert-review`.

**Agent ở phiên mới**: mở một agent không mang ngữ cảnh của phiên làm, chỉ đưa đường dẫn hồ sơ và lời
giao dưới đây. Không kể lý do thiết kế, không gợi ý điểm.

```text
Bạn là người duyệt thiết kế độc lập. Chỉ đọc các file trong <đường dẫn hồ sơ>.
Không mở file nào khác trong repo, kể cả khi có quyền. Làm đúng theo REVIEWER.md:
vòng 1 trả lời ba câu đọc lạnh cho từng ảnh trước khi mở brief.md; vòng 2 soát hard fail
và chấm 10 chiều theo rubric.md. Ghi kết quả vào review.json theo review.template.json,
reviewer.kind là agent-heuristic, reviewer.independent là true. Điểm dưới 4 phải có ghi nhận
kèm tên ảnh và cách sửa. Điều không kiểm được từ ảnh ghi vào not_checked.
```

## Bước 3: kiểm và dùng kết quả

```sh
python3 scripts/review-packet.py verify review/
```

Lệnh này bắt: ảnh bị đổi sau khi đóng gói, thiếu câu đọc lạnh, hard fail không trỏ vào ảnh, điểm dưới 4
không có cách sửa. Nó in trung bình, điểm thấp nhất và kết luận đạt hay chưa theo ngưỡng cỡ việc.

So câu trả lời đọc lạnh với ý định trong brief. Lệch ở câu "màn này để làm gì" là lỗi thứ bậc hoặc nội
dung, nặng hơn mọi điểm số. Ghi cả hai điểm (tự chấm và độc lập) vào ghi chú giao; khi chênh nhau từ 0,5
trở lên ở một chiều, chiều đó được sửa trước.

## Giới hạn

- Agent ở phiên mới vẫn là `agent-heuristic`: nó độc lập với người làm nhưng không thay người dùng thật.
- Ảnh tĩnh không chứng minh bàn phím, trình đọc màn hình, chuyển động hay luồng bấm. Các mục đó vẫn cần
  soát riêng và ghi `not_checked` nếu chưa làm.
- Một người duyệt là một ý kiến. Với L và XL, hai người duyệt độc lập tốt hơn một.
