---
name: research-lite
description: |
  Nghiên cứu người dùng gọn khi không có đội nghiên cứu: chọn phương pháp theo quyết định cần đưa ra, nghiên
  cứu bàn giấy, phỏng vấn ngắn, thử nghiệm 5 người, khảo sát nhỏ, tổng hợp bằng nhóm ghi chú và gắn nhãn
  mức bằng chứng. Dùng khi brief thiếu thông tin người dùng, khi cần kiểm một giả định trước khi vẽ, hoặc
  khi phải phân biệt điều đã biết với điều đang đoán.
---

# Nghiên cứu gọn

## Mục đích

Đủ bằng chứng để ra **một quyết định thiết kế cụ thể**, với chi phí nhỏ nhất, và nói thật mức chắc chắn.
Không nhằm tạo báo cáo dày.

Đi cùng: [`design-thinking-lite`](../design-thinking-lite/SKILL.md) (bước Hiểu và Kiểm chứng),
[`audience-intent-and-top-tasks`](../audience-intent-and-top-tasks/SKILL.md), các template trong
[`templates/ux/`](../templates/ux/README.md).

## Quy tắc trung thực

1. Mỗi phát hiện có nhãn mức bằng chứng (bảng dưới). Không nâng nhãn khi viết tóm tắt.
2. AI không phỏng vấn người dùng. Mô phỏng người dùng bằng AI chỉ tạo **giả thuyết** (`HEURISTIC_ONLY`).
3. Ý kiến của khách hàng, sếp, đội bán hàng là bằng chứng loại "người trong cuộc", không phải "người dùng".
4. Năm người thử phát hiện phần lớn lỗi dùng nghiêm trọng, nhưng không phải mẫu thống kê: không viết
   "80% người dùng" từ 5 người.

| Nhãn | Nghĩa | Ví dụ |
|---|---|---|
| `QUAN_SÁT` | Đã thấy người dùng thật làm | 4/5 người bấm nhầm "Lưu nháp" khi muốn gửi |
| `SỐ_LIỆU` | Từ analytics, log, khảo sát có cỡ mẫu nêu rõ | 62% phiên trên điện thoại (GA4, 30 ngày, 12.400 phiên) |
| `NGƯỜI_TRONG_CUỘC` | Từ khách hàng, đội hỗ trợ, đội bán | Đội hỗ trợ nói phần lớn cuộc gọi hỏi về hạn nộp |
| `BÀN_GIẤY` | Từ nghiên cứu đã công bố, đối thủ, chuẩn ngành | NN/g: người dùng quét theo hình chữ F trên trang nhiều chữ |
| `HEURISTIC_ONLY` | Suy luận, walkthrough bằng persona, mô phỏng AI | Có thể phụ huynh không hiểu chữ "sơ khảo" |
| `PLANNED_VALIDATION` | Chưa kiểm, đã có kế hoạch kiểm | Sẽ thử với 5 phụ huynh tuần sau |

## 1. Chọn phương pháp theo quyết định

Bắt đầu bằng câu: **"Kết quả nghiên cứu này sẽ làm mình chọn A hay B?"** Không trả lời được thì chưa cần
nghiên cứu.

| Cần biết | Phương pháp | Chi phí | Chi tiết |
|---|---|---|---|
| Ngành, đối thủ, thói quen chung | Nghiên cứu bàn giấy | 1–3 giờ | [desk-research.md](references/desk-research.md) |
| Vì sao họ làm vậy, hoàn cảnh, nỗi lo | Phỏng vấn ngắn 20–30 phút, 5–8 người | 2–4 ngày | [interviews-and-tests.md](references/interviews-and-tests.md) |
| Họ có dùng được không | Thử nghiệm 5 người mỗi nhóm trên mẫu thử | 2–3 ngày | [interviews-and-tests.md](references/interviews-and-tests.md) |
| Bao nhiêu người như vậy | Khảo sát ngắn hoặc số liệu có sẵn | 1 tuần | [surveys-and-synthesis.md](references/surveys-and-synthesis.md) |
| Nhãn, điều hướng có hiểu không | Phân loại thẻ, thử cây | 1–2 ngày | skill [`information-architecture`](../information-architecture/SKILL.md) |
| Phương án nào dễ hiểu hơn | Thử 5 giây, so sánh hai bản | 1 ngày | [interviews-and-tests.md](references/interviews-and-tests.md) |

Phỏng vấn cho biết **vì sao**; thử nghiệm cho biết **dùng được không**; khảo sát cho biết **bao nhiêu**.
Đừng dùng khảo sát để hỏi "bạn có thích tính năng X không".

## 2. Tuyển người (bối cảnh Việt Nam)

- Tuyển theo **hành vi**, không chỉ nhân khẩu học: "đã đóng học phí online trong 3 tháng qua" tốt hơn
  "phụ huynh 30–45 tuổi".
- Kênh thường dùng: nhóm Zalo và Facebook của trường hoặc cộng đồng, danh sách khách hàng của khách (xin
  phép trước), người quen của người quen (tránh người quen trực tiếp và nhân viên của khách).
- Quà cảm ơn tương xứng thời gian (thẻ cào, voucher), nói rõ trước.
- Xin đồng ý ghi âm hoặc quay màn, nói rõ lưu ở đâu, ai xem, xoá khi nào. Không ghi số điện thoại, tên đầy
  đủ vào ghi chú tổng hợp.
- Trẻ em dưới 16 tuổi: cần phụ huynh đồng ý và có mặt.

## 3. Tổng hợp

1. Mỗi quan sát một ghi chú: ai (mã người, không tên), làm gì hoặc nói gì, ở màn nào.
2. Gom ghi chú giống nhau thành nhóm (affinity), đặt tên nhóm bằng câu, không bằng một từ.
3. Mỗi nhóm thành một phát hiện có: số người gặp, mức nghiêm trọng, nhãn bằng chứng, trích dẫn tiêu biểu.
4. Mỗi phát hiện dẫn tới một **đề xuất thiết kế** hoặc một **câu hỏi mới**.

Chi tiết và mẫu bảng: [surveys-and-synthesis.md](references/surveys-and-synthesis.md).

## Sản phẩm giao

```markdown
## Quyết định cần đưa ra
## Phương pháp, người tham gia (mã, nhóm, cách tuyển), thời gian
## Phát hiện
| # | Phát hiện | Số người | Mức nghiêm trọng | Nhãn bằng chứng | Trích dẫn | Đề xuất |
## Điều chưa biết và kế hoạch kiểm tiếp (PLANNED_VALIDATION)
```

## Dùng sai thường gặp

- Hỏi người dùng muốn tính năng gì rồi làm đúng danh sách đó.
- Câu hỏi dẫn dắt: "Bạn thấy nút này dễ bấm đúng không?"
- Bỏ người nói khác ý mình khỏi tổng hợp.
- Viết "người dùng muốn" khi nguồn là khách hàng hoặc AI.
- Nghiên cứu xong không đổi gì trong thiết kế.
