# UIUX AI Workspace

[![Checks](https://github.com/Ngh1aa/uiux-ai-workspace/actions/workflows/checks.yml/badge.svg)](https://github.com/Ngh1aa/uiux-ai-workspace/actions/workflows/checks.yml)

Bộ não thiết kế cá nhân để Claude thiết kế website và app đẹp hơn, đúng gu hơn ngay từ bản đầu.

Cách dùng: trong chat, bảo Claude *"dùng repo uiux-ai-workspace để thiết kế …"*. Claude clone repo,
đọc [`START-HERE.md`](START-HERE.md) rồi làm theo.

## Bên trong có gì

| Phần | Vai trò |
|---|---|
| [`START-HERE.md`](START-HERE.md) | Cửa vào duy nhất: bước 0 tiếp nhận thương hiệu, rồi 4 bước Claude làm theo |
| [`BRAND-BRIEF.template.md`](BRAND-BRIEF.template.md) | Brand brief cho từng khách hàng |
| [`TASTE.md`](TASTE.md) | Gu thiết kế và các lỗi không được lặp lại |
| [`TASTE-LOG.md`](TASTE-LOG.md) | Nhật ký lỗi có thật, nguồn để cập nhật gu |
| [`CRAFT.md`](CRAFT.md) | Số liệu cốt lõi, danh sách cấm kiểu AI generic, ảnh và icon |
| [`foundations/`](foundations/README.md) | Kiến thức nền: bố cục và mật độ, Gestalt, chữ tiếng Việt, màu OKLCH, chuyển động, ảnh, tham khảo theo loại màn |
| [`GLOSSARY.md`](GLOSSARY.md) | Bảng thuật ngữ và quy tắc viết tiếng Việt |
| [`WORKFLOWS.md`](WORKFLOWS.md) | Quy trình theo cỡ việc, từ sửa nhỏ tới sản phẩm mới |
| [`skills_UIUX/`](skills_UIUX/README.md) | Các skill UI/UX và script soát trang đã dựng |
| [`design-system/`](design-system/README.md) | Design system có test: token DTCG, 25 component, 30 pattern, font tiếng Việt, ví dụ app, `check-brand.py`, `oklch-scale.py` |
| [`benchmarks/`](benchmarks/README.md) | Bộ đề chuẩn (5 đề) và [kết quả các lần chạy](benchmarks/REPORT.md) |

## Kiểm tra tự động

Mỗi pull request chạy hai nhóm kiểm tra trong [`checks.yml`](.github/workflows/checks.yml):

- `foundation`: cấu trúc skill, test bộ soát tĩnh, link nội bộ trong mọi file Markdown và bảng
  kết quả bộ đề chuẩn.
- `release-candidate`: token, độ tương phản, CSS và test của design system, lớp thương hiệu của
  starter, và soát starter kit trong trình duyệt.

Khi `design-system/` thay đổi, [`design-system.yml`](.github/workflows/design-system.yml) chụp và
soát design system trên ba trình duyệt.

Chạy tay trên máy:

```sh
python skills_UIUX/scripts/validate-skills.py
python scripts/check-links.py
python design-system/scripts/validate.py
python design-system/scripts/check-brand.py design-system/starter/brand.css
```

## Lịch sử

Repo từng có cả hệ thống chạy tự động (UIUX Factory, MetaGPT, agent bên ngoài, 27 workflow CI).
Phần đó đã được gỡ khỏi `main` vì không dùng tới; bản đầy đủ còn ở nhánh
[`archive/v1-truoc-khi-gon`](https://github.com/Ngh1aa/uiux-ai-workspace/tree/archive/v1-truoc-khi-gon).

Tháng 10/2026 repo được gọn thêm một lần: gỡ khoảng 50 skill nghiên cứu, chiến lược, đo lường,
vận hành và quản trị, cùng bộ chạy tự động còn sót (flows, profiles, prompts, evals, vendor,
designlib, tài liệu lịch sử và bằng chứng). Bản trước khi gọn ở nhánh
[`archive/truoc-khi-gon-lan-2`](https://github.com/Ngh1aa/uiux-ai-workspace/tree/archive/truoc-khi-gon-lan-2).

## Licensing

Unless a file or folder says otherwise:

| What | License |
|---|---|
| Code, skills (`SKILL.md`), design tokens, CSS components, the icon sprite, scripts, tests, and code samples inside documentation | [Apache License 2.0](LICENSE) |
| Documentation in `design-system/docs/`, and review screenshots in `design-system/examples/*/review/` | [CC BY 4.0](LICENSE-DOCS) |
| Fonts in `design-system/fonts/` | SIL Open Font License 1.1 (license file next to each font) |
| Other third-party material | Their original licenses, see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) |

Suggested attribution: *"uiux-ai-workspace" by Ngh1aa, Apache-2.0 / CC BY 4.0, https://github.com/Ngh1aa/uiux-ai-workspace*. Keep the [NOTICE](NOTICE) file in redistributions. Third-party names, logos and trademarks shown in examples are not licensed by this repository.

Never copy or adapt files from Anthropic's source-available skills (`docx`, `pdf`, `pptx`, `xlsx`, `doc-coauthoring`) into this repository; their terms forbid redistribution and derivative works.

This is a practical summary, not legal advice.
