# Track theo nền tảng và track đặc thù

Mở khi việc thuộc một nền tảng hoặc track dưới đây; [WORKFLOWS.md](../WORKFLOWS.md) chỉ giữ bảng chọn.

## Track theo nền tảng

| Nền tảng | Đọc thêm | Lưu ý quan trọng nhất |
|---|---|---|
| iOS | [iOS spec sheet](../skills_UIUX/mobile-app-design/references/ios/ios-spec-sheet.md) · [`ios-app-design`](../skills_UIUX/mobile-app-design/references/ios/README.md) | Dùng control hệ thống trước; Dynamic Type; vuốt-lùi không bao giờ bị chặn |
| Android | [Android spec sheet](../skills_UIUX/mobile-app-design/references/android/android-spec-sheet.md) · [`android-app-design`](../skills_UIUX/mobile-app-design/references/android/README.md) | Edge-to-edge, predictive back, window size classes |
| Cả hai | [Mobile patterns playbook](../skills_UIUX/mobile-app-design/references/mobile-patterns-playbook.md) | Chung ý nghĩa, khác "chrome": không ép iOS và Android giống hệt nhau |
| Web marketing | [`responsive-and-device-strategy`](../skills_UIUX/responsive-and-device-strategy/SKILL.md) | Mobile không phải desktop thu nhỏ |
| Web app / dashboard | [Web app patterns](../skills_UIUX/ui-craft-and-visual-qa/references/web-app-patterns.md) · [`data-tables-and-enterprise-ux`](../skills_UIUX/data-tables-and-enterprise-ux/SKILL.md) · [`data-visualization-and-dashboard-ux`](../skills_UIUX/data-visualization-and-dashboard-ux/SKILL.md) | Mật độ cao nhưng quét được; bàn phím là công dân hạng nhất |
| Demo trên trình duyệt cho app | [`mobile-web-preview`](../skills_UIUX/mobile-app-design/references/web-preview/README.md) | Bằng chứng trình duyệt không chứng minh app native |

## Track đặc thù

| Track | Khi nào | Bắt đầu từ |
|---|---|---|
| **Chỉ review / audit** | Cần đánh giá, chưa sửa | [rubric](../skills_UIUX/design-critique-and-rationale/references/quality-bar-rubric.md) + [`ux-laws-and-heuristics`](../skills_UIUX/design-critique-and-rationale/references/ux-laws/README.md) |
| **Cải thiện UI đang có** | Sửa và trau chuốt (Polish), giữ bố cục và hành vi | Chọn XS–S theo bảng cỡ việc, dùng [`ui-craft-and-visual-qa`](../skills_UIUX/ui-craft-and-visual-qa/SKILL.md#cải-thiện-giao-diện-hiện-có); sửa ở token và CSS component đang có, không thêm lớp đè |
| **Redesign sản phẩm có code** | Thiết kế lại, làm mới, nâng cấp một sản phẩm đã có code chạy được | L (hoặc M nếu một khu vực nhỏ) + [`brownfield-redesign`](../skills_UIUX/brownfield-redesign/SKILL.md): kiểm kê code cũ, ghi ADN, lưới test hành vi, thay tại nguồn và xoá code bị thay, soát bằng `overlay-check.py`. Website cần audit IA, SEO thì thêm `website-audit-and-redesign` |
| **Soát prototype** | Bản HTML/CSS/JS cần demo được | Theo cỡ việc tương ứng + [`ui-craft-and-visual-qa`](../skills_UIUX/ui-craft-and-visual-qa/SKILL.md#soát-prototype); thử đường demo và ghi tác vụ mô phỏng |
| **Design system** | Thêm token, component, hoặc dựng hệ thống mới | [`design-system/`](../design-system/README.md) · [platform mapping](../design-system/docs/platform-mapping.md) · [`design-system-and-components`](../skills_UIUX/design-system-and-components/SKILL.md) |
| **Portfolio** | Làm lại portfolio / định vị nghề | Như cỡ M, cộng [`design-reference-research-and-benchmark`](../skills_UIUX/design-reference-research-and-benchmark/SKILL.md) |
| **AI trong sản phẩm** | Tính năng có AI tạo nội dung/quyết định | [`human-ai-interaction-design`](../skills_UIUX/human-ai-interaction-design/SKILL.md) |
