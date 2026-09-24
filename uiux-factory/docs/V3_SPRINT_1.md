# V3 Sprint 1 — Design System Architect + Reference Analyzer

Sprint này triển khai nền tảng Design Intelligence, theo thứ tự trong brief. Canvas, Inspector, Point & Edit, Multi Draft, Brand Memory và Agency Workflow thuộc các sprint tiếp theo.

Phần nâng cấp từ `implementation_plan.md` bổ sung router AI cloud, DESIGN.md và plugin Harness; xem [FREE_BRAIN.md](FREE_BRAIN.md). Ollama được bỏ theo yêu cầu.

## Sử dụng

Mở nhanh toàn bộ Workbench bằng `./scripts/start_design_workbench.ps1` từ Factory. Script khởi động hai dịch vụ nền, tái sử dụng cổng của đúng project nếu đã chạy, và ghi log riêng. Dùng `-Foreground` nếu muốn giữ terminal Bolt ở chế độ tương tác.

Màn hình đầu có một ô nhập brief, gợi ý yêu cầu, reference và thương hiệu tùy chọn. Khi cloud đã cấu hình, nút chính dùng engine AI. Khi chưa cấu hình, nút ghi rõ **Chuẩn bị bản thiết kế** và chỉ chạy Design Intelligence. Người dùng có thể mở studio chi tiết để chọn direction hoặc prototype mẫu.

Trong `uiux-factory`:

```powershell
.\.venv\Scripts\python.exe -u apps\bridge\server.py
```

Trong `bolt.diy`, terminal khác:

```powershell
npx --yes pnpm@9.14.4 install --frozen-lockfile
npx --yes pnpm@9.14.4 dev
```

Mở <http://localhost:5173/uiux>, chọn **Brand & System**:

1. Nhập tên, personality, guideline và các điều cần tránh.
2. Dán design-system JSON hoặc CSS token hiện có trong mục Import.
3. Thêm logo/screenshot khi có; thêm URL ở ô Reference hoặc Website hiện có.
4. Chọn **Phân tích Brand DNA & Reference**. Bước này chạy độc lập, chưa tạo frontend.
5. Review token, nguồn, xung đột, dữ liệu chưa xác định và screenshot reference.
6. Chọn direction rồi Build. Build phân tích lại context hiện tại, không âm thầm dùng kết quả cũ.

Workbench lưu bản nháp input vào localStorage của origin hiện tại; không phải hệ thống Brand Memory nhiều project. Artifact và ảnh tham khảo được lưu theo run trên máy. Khi bridge restart, job đang chạy không tự khôi phục trong giao diện; artifact đã ghi vẫn giữ trong `runs/`.

Reference Analyzer không cần Brave API key. Web Search vẫn sử dụng cơ chế Brave/fallback hiện có. Nếu dùng Brave, đặt key thật trong `bolt.diy/.env.local`, không phải file `bolt.diy.env.local` ở thư mục cha; không commit key.

## CLI

```powershell
.\.venv\Scripts\python.exe run.py "Thiết kế website ngân hàng cao cấp" --context docs/examples/design-context-v3.json --intelligence-only
```

File ví dụ chứa dữ liệu minh họa, không phải guideline của một ngân hàng thật. Bỏ `--intelligence-only` để chạy pipeline hiện có đến frontend và quality loop. CLI đọc được UTF-8 có hoặc không có BOM từ PowerShell.

## Hợp đồng dữ liệu và thứ tự ưu tiên

`DesignContext` nhận:

| Field | Ý nghĩa |
| --- | --- |
| `brand_name`, `personality`, `avoid` | Định hướng người dùng khai báo |
| `guideline` | Nội dung guideline dạng text |
| `tokens` | JSON gọn theo brief hoặc `foundations` từ hợp đồng hiện có |
| `existing_code` | CSS token source do người dùng dán vào; không thực thi code |
| `existing_website` | URL website thương hiệu hiện tại |
| `reference_urls` | Tối đa 4 URL đã chọn để đo |
| `assets` | Tối đa 4 logo/screenshot PNG, JPEG, WebP; 2 MB/ảnh, tối đa 20 megapixel |

Ví dụ JSON gọn:

```json
{
  "colors": {"primary": "#006D6A", "accent": "#90321E"},
  "typography": {"heading": "Inter", "body": "Inter"},
  "radius": {"card": "16px", "button": "8px"},
  "motion": {"style": "subtle-premium", "duration": "180ms"}
}
```

Giá trị JSON được ưu tiên hơn guideline, guideline hơn CSS cũ, CSS hơn font đo từ website cũ. Giá trị bị thay thế được ghi trong `brand.conflicts`. Nhãn `confirmed` nghĩa là giá trị đã được cung cấp rõ ràng; không phải xác minh quyền sở hữu hoặc chứng nhận guideline chính thức. Import lại canonical JSON giữ nhãn `factory_default`/`derived` đã có.

Parser guideline nhận các dòng `Primary:`, `Accent:`, `Heading font:`, `Body font:`, `Card radius:`, `Motion:`. Các đoạn văn khác được giữ làm context và ghi nhận cần review, không giả vờ hiểu toàn bộ PDF/brand book.

CSS parser nhận các custom property có vai trò rõ như `--brand-primary`, `--color-primary`, `--color-brand-primary`, `--brand-accent`, `--color-accent`, `--font-heading`, `--font-body`, `--font-family-display`, `--font-family-body`, `--radius-card`, `--radius-button`, `--motion-duration`. Đây là trích xuất khai báo, không phải đánh giá toàn bộ cascade/media query hay thực thi Tailwind/TypeScript config.

Màu/font của competitor không được tự biến thành token thương hiệu. Logo/screenshot chỉ cung cấp kích thước, hash và palette lấy mẫu; không suy diễn font chính xác, personality, hình học logo hay bố cục từ palette. Chưa có vision model hoặc OCR trong sprint này.

## Output và tích hợp

Trong `runs/<id>/`:

- `design-context.json`: input gốc, gồm asset đã cung cấp.
- `reference-dna.json`: URL, trạng thái, thời điểm, quan sát có nguồn, pattern suy ra có giới hạn và các điều chưa biết.
- `references/*.png`: viewport desktop 1440×1000 và mobile 390×844.
- `design-system.json`: schema `0.3.0`, giữ `foundations`, components, patterns, gates của V2 và thêm `brand`.
- `skill-context/` và `events.jsonl`: skill path/SHA và bằng chứng chạy qua MetaGPT Team.

`DesignSystemArchitect` tái sử dụng action/hợp đồng của DesignSystemAgent. Agent cũ vẫn dùng được. Reference evidence đi vào Research/Art Direction; Brand DNA và reference principles tiếp tục đi vào Visual Composition. Frontend nhận token canonical, xuất JSON/CSS và dùng màu thương hiệu, font, radius, motion duration cho static/Next source. Companion palette được ghi `derived`; supplied primary không bị thay thế. Font file/licensing không được tự tải hoặc xác nhận.

Mỗi lần chạy pipeline có thư mục generated riêng theo run ID để tránh ghi đè draft đã review. Bridge gắn job với đúng run, không lấy nhầm project mới nhất của một job khác. Các tên section cũ/mới của Composer V2 được ánh xạ theo cùng vai trò khi Frontend Engineer kiểm tra hợp đồng.

`final_visual_lock` vẫn false sau phân tích. Thu thập token không đồng nghĩa với approval hoặc kiểm chứng accessibility trong trình duyệt.

## API local

- `POST /intelligence`: `{ "prompt": "...", "design_context": { ... } }`, trả `202` cùng job ID.
- `POST /run`: giữ payload V2 và nhận thêm `design_context` tùy chọn.
- `GET /jobs/<id>`: mode, status, active stage, tên artifact đã có.
- `GET /jobs/<id>/artifacts/design-system.json`
- `GET /jobs/<id>/artifacts/reference-dna.json`
- `GET /jobs/<id>/artifacts/references/<capture>.png`

Bridge phục vụ tại `127.0.0.1:8788`. Origin được phép mặc định: `localhost:5173`, `127.0.0.1:5173`; có thể thêm một origin bằng `UIUX_WORKBENCH_ORIGIN`. API giới hạn body 12 MB và không cung cấp endpoint đọc file tùy ý. JSON không hợp lệ trả lỗi; không ghi key/asset body vào thông báo validation.

## Giới hạn đo reference

Browser riêng không dùng phiên đăng nhập cá nhân. HTTP request đi qua connector kiểm tra IP công khai khi kết nối, gồm cả redirect; chặn địa chỉ private/local, credential trong URL, WebSocket và request không phải GET. Mỗi URL có giới hạn thời gian, số request và dung lượng tải. Site yêu cầu đăng nhập, chống bot hoặc vượt giới hạn có thể `partial`/`unavailable`.

Motion output chỉ mô tả CSS transition/animation declaration. Không đánh giá được chất lượng timing, hover, focus, menu mở hoặc mọi route từ hai viewport. Screenshot không phải kết quả visual approval. Dữ liệu thiếu được giữ nguyên là thiếu; không thay bằng mô tả đoán từ tên website.

API browser dùng dependency Playwright đã có. Tham khảo [BrowserContext](https://playwright.dev/python/docs/api/class-browsercontext) và [Page](https://playwright.dev/python/docs/api/class-page).

## Kiểm tra

```powershell
# uiux-factory
.\.venv\Scripts\python.exe -m unittest scripts.test_design_intelligence_v3 -v
.\.venv\Scripts\python.exe -m scripts.test_design_experience_v2
.\.venv\Scripts\python.exe -m scripts.test_workbench_v3

# bolt.diy
npx --yes pnpm@9.14.4 exec tsc --noEmit
npx --yes pnpm@9.14.4 run build
```

Browser integration test cần hai server đang chạy, dùng URL công khai `example.com` và ghi screenshot QA trong `runs/v3-workbench-qa/`. Unit/integration suite kiểm tra ưu tiên token, import/export, giới hạn nguồn tham khảo, palette ảnh, CSS injection, DNS/redirect private, phạm vi artifact, section contract và computed style trong Chromium.

## Phạm vi frontend hiện tại

Renderer frontend V2 vẫn là prototype ecommerce với nội dung/mô hình sản phẩm mẫu. Sprint này không biến nó thành generator production đa ngành; ngân hàng/trường học dùng được bước Design Intelligence, nhưng renderer theo domain và business data thật cần sprint riêng. Không coi điểm Visual Critic tự động của một fixture ecommerce là chứng nhận chất lượng cho mọi website.
