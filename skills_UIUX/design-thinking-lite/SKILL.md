---
name: design-thinking-lite
description: |
  Quy trình tư duy thiết kế gọn cho việc cỡ M trở lên: hiểu người dùng, chốt vấn đề bằng câu "Làm sao để",
  tạo ít nhất ba hướng khác bản chất, chọn bằng tiêu chí đã ghi trước, làm mẫu thử nhỏ nhất và kiểm chứng.
  Dùng trước khi vẽ màn đầu tiên, khi brief chỉ nói giải pháp ("làm cái app"), hoặc khi nhóm cãi nhau về
  giao diện mà chưa thống nhất vấn đề.
---

# Tư duy thiết kế gọn

## Mục đích

Ngăn hai lỗi đắt nhất: **giải đúng vấn đề sai** và **chỉ nghĩ ra một phương án**. Skill này không phải
một buổi workshop; nó là năm bước có giới hạn thời gian, mỗi bước để lại một sản phẩm nhỏ đọc lại được.

Đi cùng: [`research-lite`](../research-lite/SKILL.md) khi cần bằng chứng,
[`audience-intent-and-top-tasks`](../audience-intent-and-top-tasks/SKILL.md) khi cần xếp hạng việc chính,
[`ux-structure-and-flow-design`](../ux-structure-and-flow-design/SKILL.md) sau khi chốt hướng.

## Ngân sách theo cỡ việc

| Cỡ | Hiểu | Định nghĩa | Ý tưởng | Mẫu thử | Kiểm chứng |
|---|---|---|---|---|---|
| M | Đọc brief, 15 phút | 1 câu "Làm sao để" | 3 hướng phác | Wireframe màn quyết định | Walkthrough 5 kịch bản |
| L | Bàn giấy + 3–5 cuộc nói chuyện nếu có | 1–3 câu | 3–5 hướng | Mẫu bấm được 3 màn | 5 người mỗi nhóm người dùng, hoặc `PLANNED_VALIDATION` |
| XL | Như L + bản đồ giả định | Nguyên tắc trải nghiệm | 5+ hướng, chọn 2 đi tiếp | Mẫu luồng chính | Kế hoạch kiểm chứng có người thật |

Cỡ XS và S bỏ qua skill này.

## 1. Hiểu

Mục tiêu: biết **ai**, **đang ở hoàn cảnh nào**, **muốn đạt điều gì**, và **hiện đang làm thế nào**.

- Viết lại brief thành ba câu, không có tên tính năng.
- Liệt kê điều đã biết, điều đoán, điều chưa biết. Mỗi dòng có nhãn: `ĐÃ CÓ BẰNG CHỨNG`, `GIẢ ĐỊNH`, `CHƯA BIẾT`.
- Tìm cách người dùng đang giải quyết hôm nay (giấy, Zalo, Excel, gọi điện). Đối thủ thật thường là thói
  quen cũ, không phải sản phẩm khác.
- Cần thêm bằng chứng thì chạy [`research-lite`](../research-lite/SKILL.md).

Sản phẩm: bảng ba cột trên, cùng [proto-persona](../templates/ux/proto-persona.md) nếu cỡ L trở lên.

## 2. Định nghĩa

Biến điều đã hiểu thành câu hỏi thiết kế dạng **"Làm sao để [ai] [đạt điều gì] khi [hoàn cảnh], mà
không [rào cản hoặc đánh đổi]?"**

| Quá rộng | Vừa | Quá hẹp |
|---|---|---|
| Làm sao để giáo dục tốt hơn? | Làm sao để phụ huynh bận rộn biết con cần nộp gì tuần này mà không phải hỏi giáo viên? | Làm sao để thêm nút "Nhắc tôi" vào trang bài tập? |

Kiểm tra câu hỏi:

- Không chứa tên giải pháp (app, chatbot, dashboard).
- Có người cụ thể và hoàn cảnh cụ thể.
- Có thể có ít nhất ba câu trả lời khác bản chất.
- Đo được khi xong ("phụ huynh trả lời đúng câu hỏi trong 10 giây").

Sản phẩm: [problem statement](../templates/ux/problem-statement.md) một trang với câu "Làm sao để" và
thước đo thành công.

## 3. Tạo ý tưởng

**Ít nhất ba hướng khác bản chất**, không phải ba màu của một bố cục. Hướng khác bản chất là khác ở một
trong các trục:

| Trục | Ví dụ ba hướng cho "phụ huynh biết con cần nộp gì" |
|---|---|
| Kênh | Tin nhắn Zalo tóm tắt mỗi tối / trang web mở từ QR / màn trong app trường |
| Nhịp | Đẩy chủ động / người dùng kéo khi cần / chỉ báo khi sắp trễ |
| Mức tự động | Liệt kê việc / gợi ý thứ tự / tự đặt lịch nhắc |
| Ai làm | Phụ huynh tự xem / con đánh dấu xong / giáo viên xác nhận |

Với mỗi hướng ghi: một câu mô tả, một phác thảo (khung chữ nhật đủ), điều nó giỏi, điều nó tệ, giả định
rủi ro nhất.

Tránh: chọn ngay hướng đầu tiên nghĩ ra; hướng "kết hợp tất cả"; phán đẹp xấu ở bước này.

## 4. Chọn và làm mẫu thử

Ghi **tiêu chí trước khi chấm** để không chọn theo cảm tình. Mặc định:

| Tiêu chí | Câu hỏi |
|---|---|
| Giải đúng câu "Làm sao để" | Người dùng đạt kết quả nhanh hơn, ít lỗi hơn? |
| Hợp hoàn cảnh | Dùng được trên điện thoại, lúc bận, mạng yếu? |
| Rủi ro giả định | Giả định rủi ro nhất có kiểm được rẻ không? |
| Chi phí làm | Đội làm được trong phạm vi brief? |
| Khác biệt | Có lý do để nhớ thương hiệu này không? |

Chấm 1–5, ghi lý do một dòng. Hướng thắng đi tiếp; hướng thua giữ lại trong ghi chú, vì có khi phần tốt
của nó ghép được.

Mẫu thử nhỏ nhất kiểm được giả định rủi ro nhất: có khi chỉ là một màn tĩnh và một câu hỏi, không cần cả luồng.

## 5. Kiểm chứng

- Có người thật: theo [usability test plan](../templates/ux/usability-test-plan.md), 5 người mỗi nhóm.
- Chưa có người thật: walkthrough 5 kịch bản bằng proto-persona, ghi kết quả là `HEURISTIC_ONLY` và lập
  kế hoạch kiểm chứng `PLANNED_VALIDATION`. Không gọi đó là "người dùng thấy".
- Kết quả quay lại bước 2 nếu câu "Làm sao để" sai, bước 3 nếu hướng sai, bước 4 nếu chỉ chi tiết sai.

## Sản phẩm giao

```markdown
## Khung vấn đề
- Ai, hoàn cảnh, mục tiêu (3 câu, không tên tính năng)
- Đã biết / Giả định / Chưa biết
- Làm sao để …? Thước đo: …

## Các hướng đã cân nhắc
| Hướng | Mô tả | Giỏi | Tệ | Giả định rủi ro | Điểm |

## Hướng chọn và lý do
## Mẫu thử và cách kiểm chứng (kết quả hoặc PLANNED_VALIDATION)
```

## Dùng sai thường gặp

- Làm đủ năm bước như nghi lễ cho một màn cỡ S.
- Ba "hướng" chỉ khác màu hoặc vị trí nút.
- Viết persona đầy chi tiết đời tư nhưng không có hoàn cảnh sử dụng.
- Gọi ý kiến của khách hàng (người trả tiền) là ý kiến của người dùng.
- Bỏ bước kiểm chứng vì "thời gian gấp" mà không ghi lại là chưa kiểm.
