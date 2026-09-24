# AI cloud và đánh giá implementation_plan.md

Đánh giá ngày 09/09/2026. Kế hoạch gốc ở workspace được giữ nguyên. Theo yêu cầu mới nhất, **bỏ Ollama**, không cài hay tải model local.

## Kết luận khả thi

| Hạng mục | Quyết định triển khai |
|---|---|
| Router miễn phí | Groq/Gemini với key, model và danh sách fallback do người dùng cấu hình. Không provider ngầm, không nâng gói, không đổi sang model ngoài cấu hình. |
| Cam kết 0 đồng | Không thể bảo đảm bằng code cho tài khoản cloud: billing/free tier thuộc nhà cung cấp. Mặc định chưa bật cloud; prototype hiện có vẫn chạy không gọi LLM. |
| Nâng tư duy thiết kế | Policy do UIUX Factory viết, tham khảo skill frontend-design công khai và skills_UIUX; không tuyên bố có prompt nội bộ Claude. |
| DESIGN.md | Xuất chín mục theo quy ước OpenDesign, kèm tokens.css và nguồn/trạng thái token. Không tự biến Markdown thành PPTX. |
| Coder không template | Engine `ai` tạo tối đa 6 trang HTML/CSS/JS theo brief, qua kiểm tra file và browser. Giữ engine `template` tương thích V2 và dùng khi chưa cấu hình AI. |
| DeepSeek Design canvas/template | Chưa tích hợp: giấy phép hiện tại yêu cầu chấp thuận riêng cho ngữ cảnh agency/thương mại. Không sao chép code/template vào sản phẩm. |
| DeepSeek Harness | Plugin bridge độc lập trong `plugins/dsh-uiux-designer`, dùng API tool công khai; không phụ thuộc iPolloWork. |
| Tự sửa đến 9/10 | Thay bằng tối đa 2 lần sửa và QA kỹ thuật có evidence. Không gán điểm thẩm mỹ từ kiểm tra DOM hay cam kết mọi output đạt 9/10. |
| Model nhỏ như nghìn tỷ tham số | Không có cơ sở để cam kết. Skill routing giới hạn context, không thay đổi năng lực thực tế của model. |

Model và hạn mức trong bản kế hoạch cần được kiểm tra lại. Gemini 2.0 đã ngừng phục vụ; Groq cũng có lịch ngừng các model cũ. Router yêu cầu model ID cấu hình rõ ràng để tránh khóa vào tên đã lỗi thời.

Nguồn đối chiếu: [Gemini lifecycle](https://ai.google.dev/gemini-api/docs/deprecations), [Groq lifecycle](https://console.groq.com/docs/deprecations), [public frontend-design skill](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md), [OpenDesign package convention](https://github.com/nexu-io/open-design/tree/main/design-systems), [iPolloWork license](https://github.com/Devin-AXIS/deepseek-design/blob/main/LICENSE), [Harness tool contract](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/cookbook/adding-a-tool.md).

## Cấu hình

Tạo `uiux-factory/.env.local` (được Git ignore). Dùng tài khoản free tier đã kiểm tra billing; không đưa key vào chat, Workbench, file DESIGN.md hoặc Git.

```dotenv
UIUX_FREE_TIER_CONFIRMED=1
# Thứ tự thử; chỉ thêm provider đã có tài khoản/key và đã kiểm tra free tier.
UIUX_CLOUD_PROVIDERS=groq
GROQ_API_KEY=replace-locally
UIUX_GROQ_MODEL=openai/gpt-oss-120b
# Tùy chọn thêm gemini vào danh sách trên:
# GEMINI_API_KEY=replace-locally
# UIUX_GEMINI_MODEL=gemini-2.5-flash
# UIUX_PROVIDER_UX_IA=gemini
# UIUX_PROVIDER_IMPLEMENTATION=groq
```

Tên model trên là ví dụ đã đối chiếu tài liệu tại thời điểm đánh giá, không phải xác nhận hạn mức của tài khoản. Groq/Gemini dùng REST tương thích chat completions: [Groq](https://console.groq.com/docs/openai), [Gemini](https://ai.google.dev/gemini-api/docs/openai).

```powershell
.\.venv\Scripts\python.exe -m scripts.check_free_provider
# Chỉ gọi thật khi cấu hình free tier đã sẵn sàng:
.\.venv\Scripts\python.exe -m scripts.check_free_provider --live
.\.venv\Scripts\python.exe run.py "Thiết kế website studio với trang chủ và dịch vụ" --engine ai --context docs/examples/design-context-v3.json
```

Workbench có lựa chọn **AI tùy biến · Groq / Gemini đã cấu hình**. API `POST /run` nhận `engine: "ai"`; mặc định vẫn là `template`. Backend đọc `.env.local` khi tạo job, không gửi key về browser. Tài khoản chưa cấu hình trả lỗi trước khi tạo job.

## Flow và giới hạn

Reference Analyzer → Design System Architect → phân tích bằng chứng → UX plan → Art Direction → Coder → Browser QA → tối đa 2 lần Repair.

Màn hình `/uiux` bắt đầu bằng một ô nhập yêu cầu, tự lưu nháp và cho phép thêm thương hiệu, ảnh, reference khi cần. Direction chỉ được khóa theo preset khi người dùng chủ động chọn. AI có thể đề xuất màu chính/font còn thiếu theo brief; giá trị đã cung cấp hoặc suy ra từ nguồn thương hiệu được giữ nguyên. Các đề xuất này luôn ghi nguồn AI và cần review, không được coi là guideline chính thức.

Các stage AI dùng skill router/compiler hiện có, ghi nguồn skill và `provider-usage.json` không chứa key/prompt/response. Mỗi run tối đa 12 HTTP requests, 90 giây/request, response tối đa 2 MB. Chỉ fallback khi lỗi kết nối hoặc HTTP 429/502/503/504; lỗi key/model/dữ liệu phải được sửa, không thử provider khác một cách mù quáng.

AI tạo file static có route contract và đường dẫn giới hạn; không chạy shell, npm install hay script build do model đề xuất. CSS token thương hiệu được chèn từ contract. Preview AI dùng CSP sandbox, chặn network/iframe/form submit; Browser QA dùng cùng chính sách. Các draft giữ trong thư mục run riêng. Hết lượt sửa mà vẫn lỗi thì run FAILED, giữ artifact để kiểm tra.

Output AI là **prototype static**. Không tự tạo CMS, database, thanh toán, production backend hay source Next.js. Chưa có vision critic đánh giá screenshot; `aesthetic_score` luôn null và cần người xem hình. Tokens/font availability, nội dung chính thức, SEO hoàn chỉnh, accessibility và interaction nghiệp vụ cần QA trước khi đưa vào production. Canvas/Point & Edit vẫn thuộc sprint sau.

`DESIGN.md` và `tokens.css` có ở thư mục run, DESIGN.md cũng đi vào output frontend. Đã kiểm tra cấu trúc chín mục; chưa nhập thử vào app OpenDesign hay xuất slides/PPTX.

## Kiểm tra

```powershell
.\.venv\Scripts\python.exe -m unittest scripts.test_design_intelligence_v3 scripts.test_free_brain -v
.\.venv\Scripts\python.exe -m scripts.test_workbench_v3
```

`test_free_brain` chạy HTTP transport giả lập để kiểm tra rate-limit fallback, lỗi xác thực, budget và bảo mật log. Integration dùng provider fixture được ghi rõ trong artifact, nhưng skill compilation, MetaGPT BrowserQA, Chromium, phát hiện overflow và vòng sửa là chạy thật. Kết quả này không chứng minh chất lượng của model cloud. Hiện cloud chưa bật, chưa xác minh live inference.
