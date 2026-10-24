# UIUX AI Workspace

[![Checks](https://github.com/Ngh1aa/uiux-ai-workspace/actions/workflows/checks.yml/badge.svg)](https://github.com/Ngh1aa/uiux-ai-workspace/actions/workflows/checks.yml)

Bộ não thiết kế cá nhân để Claude thiết kế website và app đẹp hơn, đúng gu hơn ngay từ bản đầu.

Cách dùng: trong chat, bảo Claude *"dùng repo uiux-ai-workspace để thiết kế …"*. Claude clone repo,
đọc [`START-HERE.md`](START-HERE.md) rồi làm theo.

## Bên trong có gì

| Phần | Vai trò |
|---|---|
| [`START-HERE.md`](START-HERE.md) | Cửa vào duy nhất: 4 bước Claude làm theo |
| [`TASTE.md`](TASTE.md) | Gu thiết kế và các lỗi không được lặp lại |
| [`WORKFLOWS.md`](WORKFLOWS.md) | Quy trình theo cỡ việc, từ sửa nhỏ tới sản phẩm mới |
| [`skills_UIUX/`](skills_UIUX/README.md) | 116 skill UI/UX, flow theo loại việc, prompt, kiến thức, bộ kiểm tra `designlib/` |
| [`design-system/`](design-system/README.md) | Design system mẫu có test: token DTCG, 19 component, font tiếng Việt, ví dụ app |
| [`benchmarks/`](benchmarks/README.md) | Bộ 3 đề chuẩn và [kết quả các lần chạy](benchmarks/REPORT.md) |
| [`docs/`](docs/) | Ghi chép các lần nâng cấp và bằng chứng thử nghiệm |

## Kiểm tra tự động

Mỗi pull request chạy hai nhóm kiểm tra trong [`checks.yml`](.github/workflows/checks.yml):

- `foundation`: cấu trúc skill, tên skill trong flow, profile/pack/eval, dữ liệu vendor, test bộ
  kiểm tra thiết kế, link nội bộ trong mọi file Markdown và bảng kết quả bộ đề chuẩn.
- `release-candidate`: token, độ tương phản, CSS và test của design system.

Khi `design-system/` thay đổi, [`design-system.yml`](.github/workflows/design-system.yml) chụp và
soát design system trên ba trình duyệt.

Chạy tay trên máy:

```sh
cd skills_UIUX
python scripts/validate-skills.py
python scripts/validate-v2.py
python -m pytest -q tests
cd ..
python scripts/check-links.py
python design-system/scripts/validate.py
```

## Lịch sử

Repo từng có cả hệ thống chạy tự động (UIUX Factory, MetaGPT, agent bên ngoài, 27 workflow CI).
Phần đó đã được gỡ khỏi `main` vì không dùng tới; bản đầy đủ còn ở nhánh
[`archive/v1-truoc-khi-gon`](https://github.com/Ngh1aa/uiux-ai-workspace/tree/archive/v1-truoc-khi-gon).
Các tài liệu cũ nằm trong `docs/history/` và `skills_UIUX/docs/history/`.

## Licensing

Unless a file or folder says otherwise:

| What | License |
|---|---|
| Code, skills and prompts (`SKILL.md`, flows), design tokens, CSS components, the icon sprite, scripts, tests, and code samples inside documentation | [Apache License 2.0](LICENSE) |
| Documentation in `docs/`, `design-system/docs/`, and review screenshots in `design-system/examples/*/review/` | [CC BY 4.0](LICENSE-DOCS) |
| Fonts in `design-system/fonts/` and `skills_UIUX/vendor/ui-ux-pro-max/skills/ui-styling/canvas-fonts/` | SIL Open Font License 1.1 (license file next to each font) |
| `skills_UIUX/vendor/` and every Git submodule | Their original licenses, see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) |

Suggested attribution: *"uiux-ai-workspace" by Ngh1aa, Apache-2.0 / CC BY 4.0, https://github.com/Ngh1aa/uiux-ai-workspace*. Keep the [NOTICE](NOTICE) file in redistributions. Third-party names, logos and trademarks shown in examples are not licensed by this repository.

Never copy or adapt files from Anthropic's source-available skills (`docx`, `pdf`, `pptx`, `xlsx`, `doc-coauthoring`) into this repository; their terms forbid redistribution and derivative works.

This is a practical summary, not legal advice.
