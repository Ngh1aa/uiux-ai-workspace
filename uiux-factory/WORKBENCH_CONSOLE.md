# UIUX Factory · Workbench Console

Giao diện nhập prompt thân thiện cho UIUX Factory. Người dùng mở trình duyệt,
nhập yêu cầu bằng tiếng Việt (hoặc tiếng Anh), hệ thống tự:

1. Suy luận **domain** (ecommerce, corporate, education, agency).
2. Đánh giá **độ rõ** của brief và đề xuất cải thiện.
3. Lên **kế hoạch 10 bước** pipeline + skill nào sẽ được route cho mỗi bước.
4. Người dùng bấm **Chạy pipeline**.
5. Console theo dõi job theo thời gian thực, hiển thị log, artifacts, preview iframe.

## Khởi động

```powershell
.\scripts\start_workbench_console.ps1
```

Mặc định:
- **Bridge** (Python, factory core) chạy ở `http://127.0.0.1:8788`
- **Console** (static + reverse proxy) chạy ở `http://127.0.0.1:5174`
- Log ở `.bridge-start.*.log` và `.console-start.*.log`

Cổng có thể đổi qua biến môi trường `UIUX_CONSOLE_PORT` và `UIUX_BRIDGE_URL`.

Mở <http://localhost:5174/> và bắt đầu.

## Cấu trúc

```
apps/web/
├── index.html         # Giao diện chính (nền trắng + gradient đỏ-cam)
├── styles.css         # Theme tokens, components
├── skills-router.js   # Mirror của core/skills/router.py cho UI preview
├── app.js             # Logic: drafts, submit, polling, artifacts, preview
└── server.py          # Static server + reverse proxy /api/* → bridge
```

`/api/*` được proxy sang bridge:
- `/api/health`       → `GET /health`
- `/api/run`          → `POST /run` (full pipeline)
- `/api/intelligence` → `POST /intelligence` (chỉ Design Intelligence)
- `/api/jobs/<id>`    → `GET /jobs/<id>`
- `/api/jobs/<id>/artifacts/<file>` → `GET /jobs/<id>/artifacts/<file>`
- `/api/latest`       → `GET /latest`
- `/api/preview/<project>/<...>` → `GET /preview/<project>/<...>` (qua iframe)

## Phím tắt trong UI

- Click chip mẫu → tự điền prompt.
- Bản nháp tự lưu vào `localStorage` của origin.
- Engine `template` chạy mặc định, không cần key.
- Engine `ai` chỉ bật khi `.env.local` đã cấu hình Groq/Gemini.

## Engine & giới hạn

Tham khảo [FREE_BRAIN.md](FREE_BRAIN.md) và [V3_SPRINT_1.md](V3_SPRINT_1.md).

Tóm tắt:
- `template` (mặc định): chạy Full pipeline V2, render từ preset template, không tốn chi phí.
- `ai`: gọi Groq/Gemini để tạo prototype tùy biến (≤6 trang). Cần `.env.local` với key.

## Tích hợp sức mạnh hệ thống (để "thông minh nhất có thể")

Console hiển thị minh bạch các lớp trí tuệ:

| Lớp | Nguồn | Vai trò |
| --- | --- | --- |
| Domain inference | `core/skills/router.py::infer_domain` | Tự phát hiện ecommerce/corporate/education/agency |
| Clarity score | `apps/web/skills-router.js` | Đánh giá brief có đủ thông tin không |
| Skill routing | Mirror của `AdaptiveSkillRouter` | Liệt kê skill nào được dùng cho mỗi stage |
| Multi-brain | MetaGPT 14 agents (Aria, Mira, Rhea, Sora, Nora, Felix…) | Chạy song song nhiều chuyên gia |
| Self-repair | VisualCritic → RepairAgent loop (≤3 lần) | Tự sửa nếu QA fail |
| Brand DNA | Reference Analyzer + Design System Architect | Trích xuất DNA từ URL/ảnh |

## Phát triển / mở rộng

- Mở `apps/web/index.html` và `apps/web/styles.css` để chỉnh UI.
- Mở `apps/web/skills-router.js` nếu thêm skill mới (giữ đồng bộ với `core/skills/router.py`).
- Mở `apps/web/app.js` để chỉnh flow polling / artifact viewer.
- Sau khi đổi, console reload là đủ — không cần restart server.
