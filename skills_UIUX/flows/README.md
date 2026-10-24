# Flows: lộ trình skill theo loại việc

Mỗi file `flows/*.json` là một lộ trình làm việc: chia việc thành các chặng (thường là
`research` → `design` → `qa`), mỗi chặng ghi rõ skill phải đọc và điều kiện để qua chặng.

Không có chương trình nào chạy các file này. Claude đọc trực tiếp:

1. Chọn cỡ việc và flow theo [`WORKFLOWS.md`](../../WORKFLOWS.md).
2. Mở file flow tương ứng, đi **lần lượt từng chặng**, không nhảy cóc.
3. Ở mỗi chặng, chỉ đọc `SKILL.md` của:
   - mọi skill trong `required_skills`;
   - skill trong `conditional_skills` khi điều kiện `when` khớp với việc đang làm
     (ví dụ `target_platforms: ["ios"]` → thêm `ios-app-design`; `features: ["forms"]`
     → thêm `interaction-patterns-and-form-ux`).
4. Chỉ sang chặng sau khi đã đáp ứng các mục trong `gates` (đọc trường `require`).
   Gate là danh sách việc phải có thật, ví dụ ảnh chụp màn đã render, chứ không phải lời
   tự khẳng định "đã xong".

## Các flow hiện có

| Flow | Dùng khi |
|---|---|
| `micro-ui-change` | Sửa nhỏ một component, màu, khoảng cách, đoạn chữ |
| `existing-ui-improvement` | Cải thiện một phần giao diện đang có |
| `page-ui-work` | Làm hoặc làm lại một trang, một màn, một tính năng |
| `professional-website-redesign` | Làm mới hoặc làm lại cả website |
| `mobile-app-design` | Thiết kế app iOS/Android (chỉ thiết kế, prototype, handoff) |
| `mobile-app-audit` | Soát một app đang có, không sửa |
| `mobile-web-preview` | Prototype app chạy trên trình duyệt để bấm thử |
| `web-app-dashboard` | Dashboard, trang quản trị, công cụ nội bộ |
| `design-system-work` | Dựng, mở rộng hoặc sửa chính design system |
| `design-system-audit` | Soát design system, không sửa |
| `portfolio-career-system` | Portfolio cá nhân và định vị nghề nghiệp |
| `audit-review` | Đánh giá một sản phẩm, không sửa |
| `skill-library-maintenance` | Sửa hoặc thêm skill trong repo này |
| `skill-library-audit` | Soát thư viện skill, không sửa |

Trường `match` trong mỗi file cho biết flow hợp với loại việc nào (nền tảng, đầu ra, ý định).
Một trang web responsive vẫn dùng flow web. Việc vừa web vừa app thì tách thành hai phần,
mỗi phần một flow.

## Thêm hoặc sửa flow

- Flow chỉ tham chiếu tên skill, không chép nội dung skill vào.
- Mọi tên skill trong flow phải tồn tại; `python3 skills_UIUX/scripts/validate-v2.py`
  kiểm tra điều này.
- Schema tham khảo: [`schemas/flow.schema.json`](../schemas/flow.schema.json).
