from __future__ import annotations

from core.contracts.prototype_acceptance_schema import PrototypeRequirement


def _r(
    requirement_id: str,
    stage: int,
    title: str,
    requirement: str,
    mode: str,
    evaluator: str,
    *,
    automation: str = "planned",
    machine_required: bool = False,
    applicability: str = "Applies when the described UI, state, flow or design decision exists.",
    evidence: tuple[str, ...] = (),
    owner: str = "visual_qa",
) -> PrototypeRequirement:
    return PrototypeRequirement(
        id=requirement_id,
        stage=stage,
        title=title,
        requirement=requirement,
        verification_mode=mode,
        evaluator=evaluator,
        automation_status=automation,
        machine_required=machine_required,
        applicability=applicability,
        expectations=[requirement],
        required_evidence=list(evidence),
        owner_stage=owner,
    )


_REQUIREMENTS = [
    _r("P1-01", 1, "Prototype audience", "Xác định rõ đối tượng xem prototype và mức trình diễn so với mức thực tế.", "artifact", "intent-contract", owner="research"),
    _r("P1-02", 1, "Three-second impression", "Ghi rõ cảm xúc muốn người xem có trong khoảng 3 giây đầu và dùng nó làm định hướng thị giác.", "hybrid", "intent-plus-vision", owner="art_direction"),
    _r("P1-03", 1, "Website type", "Xác định đúng loại website để dùng layout phù hợp, không dùng khuôn chung.", "vision", "visual-domain-profile", automation="implemented", machine_required=True, evidence=("semantic visual review",), owner="research"),
    _r("P1-04", 1, "Three style adjectives", "Chốt đúng 3 tính từ phong cách và chiếu màu, font, animation theo chúng.", "hybrid", "style-word-critic", owner="art_direction"),
    _r("P1-05", 1, "Market direction", "Đối chiếu đối thủ/thị trường và chọn khác biệt có chủ đích hoặc chuẩn ngành để tạo tin cậy.", "artifact", "reference-matrix", owner="research"),
    _r("P1-06", 1, "Anti AI-generated look", "Chủ động phát hiện và phá vỡ các pattern AI/template mặc định khi chúng không có lý do domain/brand.", "vision", "semantic-visual-policy", automation="implemented", machine_required=True, evidence=("vision screenshot review",), owner="art_direction"),
    _r("P1-07", 1, "Demo path", "Xác định rõ kịch bản trình diễn qua các màn hình/thao tác quan trọng.", "artifact", "demo-path-contract", owner="ux_ia"),
    _r("P1-08", 1, "Demo user flow", "Mô tả điểm bắt đầu, các bước và điểm kết của kịch bản demo.", "artifact", "demo-flow-contract", owner="ux_ia"),
    _r("P1-09", 1, "Hero moment", "Xác định một khoảnh khắc trọng tâm để dồn craft thay vì dàn trải đều.", "hybrid", "hero-moment-contract", owner="art_direction"),

    _r("P2-01", 2, "Hick's Law", "Giảm hoặc nhóm lựa chọn; menu/nav chính nên tránh quá nhiều lựa chọn cạnh tranh, với 5–7 mục là heuristic ban đầu.", "browser", "choice-pressure-audit", owner="ux_ia"),
    _r("P2-02", 2, "Fitts's Law", "CTA chính đủ lớn, dễ chạm và tách khỏi nút phụ; mobile ưu tiên vùng chạm khoảng 44px.", "browser", "target-acquisition-audit", owner="implementation"),
    _r("P2-03", 2, "Jakob's Law", "Giữ vị trí và interaction grammar quen thuộc khi việc sáng tạo lại không có lợi ích rõ ràng.", "vision", "familiar-pattern-critic", owner="ux_ia"),
    _r("P2-04", 2, "Miller's Law", "Danh sách/lựa chọn lớn phải được nhóm, chia nhỏ hoặc phân trang thay vì tạo áp lực ghi nhớ.", "browser", "choice-grouping-audit", owner="ux_ia"),
    _r("P2-05", 2, "Gestalt proximity and similarity", "Nhóm phần tử liên quan bằng proximity/alignment và giữ style nhất quán cho cùng chức năng.", "vision", "grouping-critic", owner="visual_composition"),
    _r("P2-06", 2, "Von Restorff effect", "CTA hoặc decision object quan trọng nhất phải nổi bật rõ hơn phần còn lại.", "vision", "decision-object-dominance", automation="implemented", machine_required=True, evidence=("semantic route hierarchy",), owner="visual_composition"),
    _r("P2-07", 2, "Doherty feedback", "Phản hồi tương tác phải đủ nhanh để không tạo cảm giác đơ; checklist gốc dùng <400ms như heuristic prototype.", "performance", "interaction-feedback-timing", owner="implementation"),
    _r("P2-08", 2, "Peak-End Rule", "Khoảnh khắc cuối của demo path phải được chăm chút để tạo kết thúc tích cực.", "hybrid", "journey-peak-end-critic", owner="visual_composition"),
    _r("P2-09", 2, "Aesthetic-usability balance", "Thẩm mỹ không được che giấu flow khó hiểu hoặc thao tác rắc rối.", "hybrid", "flow-clarity-critic", owner="ux_ia"),
    _r("P2-10", 2, "Zeigarnik progress", "Flow nhiều bước phải có progress/state indicator khi nó giúp giảm bất định.", "browser", "multi-step-progress-audit", applicability="Applies to multi-step demo flows such as onboarding or checkout.", owner="ux_ia"),

    _r("P3-01", 3, "Color roles", "Bảng màu có primary, secondary, accent, neutral và semantic roles rõ ràng.", "artifact", "design-token-audit", owner="design_system"),
    _r("P3-02", 3, "Single accent discipline", "Accent được dùng có chủ đích cho CTA/điểm cần chú ý, không rải cạnh tranh khắp UI.", "hybrid", "accent-discipline-critic", owner="design_system"),
    _r("P3-03", 3, "Readable contrast", "Nội dung phải đọc rõ trên các surface được sử dụng; automated smoke không được tự nhận là WCAG certification.", "hybrid", "contrast-evidence-audit", owner="visual_qa"),
    _r("P3-04", 3, "Typography matches style", "Typography phải hỗ trợ đúng 3 tính từ phong cách đã chốt.", "vision", "style-word-critic", owner="art_direction"),
    _r("P3-05", 3, "Font system and type scale", "Giữ font system restrained, checklist gốc ưu tiên tối đa 2 họ font và type scale khoảng 1.25–1.333.", "browser", "typography-system-audit", owner="design_system"),
    _r("P3-06", 3, "Heading hierarchy", "Heading phải là điểm nhấn thị giác thực sự chứ không chỉ body text phóng to.", "vision", "heading-hierarchy-critic", owner="visual_composition"),
    _r("P3-07", 3, "Readable text measure", "Đoạn văn dài dùng measure và line-height dễ đọc; checklist gốc dùng 65–80 ký tự và 1.5–1.6 như heuristic.", "browser", "text-measure-audit", owner="implementation"),
    _r("P3-08", 3, "Grid and spacing consistency", "Grid, alignment và spacing rhythm phải nhất quán giữa các màn hình đại diện.", "vision", "visual-spacing-score", automation="implemented", machine_required=True, evidence=("visual critic spacing score",), owner="visual_composition"),
    _r("P3-09", 3, "Purposeful whitespace", "Whitespace phải cải thiện hierarchy, đặc biệt quanh hero và CTA, không chỉ tạo khoảng trống giả premium.", "vision", "whitespace-critic", owner="visual_composition"),
    _r("P3-10", 3, "Squint hierarchy", "Squint/blur review phải cho thấy thứ tự ưu tiên thị giác đúng ý đồ.", "vision", "blurred-screenshot-critic", owner="visual_qa"),
    _r("P3-11", 3, "Layout matches site/domain", "Bố cục phải phù hợp website type, vertical và page role thay vì một layout universal.", "vision", "domain-page-role-fit", automation="implemented", machine_required=True, evidence=("domain/page-role semantic scores",), owner="visual_composition"),
    _r("P3-12", 3, "Media style consistency", "Ảnh, illustration và icon family phải có art direction nhất quán.", "vision", "media-family-critic", owner="art_direction"),
    _r("P3-13", 3, "Domain-relevant media", "Media phải đúng nội dung/ngành và tránh stock chung chung có thể thuộc bất kỳ website nào.", "vision", "media-relevance-policy", automation="implemented", machine_required=True, evidence=("semantic media relevance",), owner="art_direction"),
    _r("P3-14", 3, "Brief-specific visual signature", "Có ít nhất một chi tiết thị giác riêng biệt, đáng nhớ và có lý do từ brief/domain.", "vision", "distinctiveness-policy", automation="implemented", machine_required=True, evidence=("semantic distinctiveness",), owner="art_direction"),

    _r("P4-01", 4, "Primary motion moment", "Chọn một khoảnh khắc chuyển động chính để polish, không rải animation ngang nhau khắp site.", "hybrid", "motion-signature-audit", owner="implementation"),
    _r("P4-02", 4, "Hover feedback", "Mọi phần tử click trong demo có hover feedback rõ; 150–300ms và easing tự nhiên là heuristic checklist.", "interaction", "hover-state-crawler", owner="implementation"),
    _r("P4-03", 4, "Focus visibility", "Keyboard focus phải nhìn thấy rõ và không bị xóa outline mà không có thay thế.", "interaction", "focus-state-crawler", owner="implementation"),
    _r("P4-04", 4, "Selective scroll animation", "Scroll-triggered animation nếu dùng phải có chọn lọc, tránh fade-slide-up đồng loạt kiểu template.", "hybrid", "scroll-motion-audit", applicability="Applies when scroll-triggered animation exists.", owner="implementation"),
    _r("P4-05", 4, "Meaningful microinteraction", "Submit/toggle/input trong demo phải có feedback loading/success/validation phù hợp khi applicable.", "interaction", "interaction-state-crawler", owner="implementation"),
    _r("P4-06", 4, "Cursor restraint", "Custom cursor hoặc mouse-follow effect chỉ được dùng khi phù hợp phong cách và không làm giảm control.", "hybrid", "cursor-rationale-audit", applicability="Applies when a custom cursor or pointer-follow effect exists.", owner="art_direction"),
    _r("P4-07", 4, "Smooth route/section transition", "Chuyển trang/chuyển section trong demo phải được thao tác và đo thực tế, không chỉ suy từ code.", "interaction", "journey-interaction-trace", owner="implementation"),

    _r("P5-01", 5, "Component state completeness", "Component lặp lại trong demo có đủ default, hover, active, focus và disabled khi applicable.", "interaction", "component-state-crawler", owner="implementation"),
    _r("P5-02", 5, "Empty state", "Danh sách/kết quả có khả năng rỗng phải có empty state thiết kế rõ ràng.", "interaction", "empty-state-crawler", applicability="Applies to list/search/result surfaces that can become empty.", owner="implementation"),
    _r("P5-03", 5, "Loading state", "Thao tác có thời gian chờ trong demo phải có skeleton/spinner hoặc feedback tương đương.", "interaction", "loading-state-crawler", applicability="Applies to demo actions that wait before completion.", owner="implementation"),
    _r("P5-04", 5, "Form error and success states", "Form trong demo phải có trạng thái lỗi/thành công rõ và đúng tone thương hiệu.", "interaction", "form-state-crawler", applicability="Applies when the demo path contains a form submission.", owner="implementation"),

    _r("P6-01", 6, "Responsive intent", "Ghi rõ prototype presentation-only hay cần responsive đa thiết bị trước khi triển khai.", "artifact", "responsive-intent-contract", owner="implementation_plan"),
    _r("P6-02", 6, "Three representative widths", "Nếu responsive, kiểm tra ít nhất mobile khoảng 375px, tablet khoảng 768px và desktop khoảng 1440px.", "browser", "browser-viewport-coverage", automation="implemented", machine_required=True, evidence=("BrowserQA viewport screenshots",), applicability="Applies when responsive demonstration is required.", owner="browser_qa"),
    _r("P6-03", 6, "Mobile content priority", "Thứ tự ưu tiên nội dung trên mobile phải biến đổi có chủ đích, không chỉ co nhỏ desktop.", "vision", "responsive-priority-critic", applicability="Applies when responsive demonstration is required.", owner="visual_composition"),
    _r("P6-04", 6, "Mobile target and body size", "Trên mobile, checklist prototype ưu tiên vùng chạm khoảng 44px và nội dung chính không nhỏ hơn 16px.", "browser", "mobile-target-type-audit", applicability="Applies when responsive demonstration is required.", owner="browser_qa"),

    _r("P7-01", 7, "Rendered squint test", "Nheo mắt/làm mờ từng màn hình và xác nhận điểm thắng đầu tiên đúng ý đồ.", "vision", "blurred-screenshot-critic", owner="visual_qa"),
    _r("P7-02", 7, "Five-second outsider test", "Cho một người ngoài cuộc xem khoảng 5 giây và hỏi họ hiểu trang là gì/làm gì; AI không được giả mạo participant evidence.", "manual", "human-five-second-test", automation="manual", machine_required=False, evidence=("participant response",), owner="human_review"),
    _r("P7-03", 7, "Remove one decoration", "Thực hiện pass bớt một chi tiết trang trí không phục vụ mục đích, hoặc giải thích vì sao density hiện tại có chủ đích.", "vision", "decoration-removal-critic", owner="visual_qa"),
    _r("P7-04", 7, "Style-word check", "Đối chiếu render cuối với đúng 3 tính từ phong cách bằng evidence từ type, màu, media, spacing và motion.", "vision", "style-word-critic", owner="visual_qa"),
    _r("P7-05", 7, "Competitive distinctiveness", "Đặt representative screenshots cạnh references và chứng minh khác biệt có chủ đích mà không làm hỏng task clarity.", "vision", "reference-side-by-side-critic", owner="visual_qa"),
    _r("P7-06", 7, "Real demo interaction pass", "Thao tác toàn bộ demo path bằng chuột/bàn phím và touch emulation khi phù hợp, ghi lại giật/lệch/chậm/khó bấm.", "interaction", "journey-interaction-trace", owner="browser_qa"),
    _r("P7-07", 7, "Realistic content stress", "Loại placeholder/lorem và stress layout với nội dung gần thật, tiếng Việt có dấu, tên/số dài.", "browser", "content-stress-audit", owner="browser_qa"),
    _r("P7-08", 7, "Independent human review", "Có ít nhất một người khác xem và phản hồi thẳng thắn trước khi coi là bản cuối; AI không được tự xác nhận mục này.", "manual", "independent-human-review", automation="manual", machine_required=False, evidence=("human review record",), owner="human_review"),
]


def prototype_requirements() -> list[PrototypeRequirement]:
    requirements = [item.model_copy(deep=True) for item in _REQUIREMENTS]
    if len(requirements) != 56:
        raise RuntimeError(f"Prototype checklist registry must contain 56 requirements, got {len(requirements)}")
    ids = [item.id for item in requirements]
    if len(set(ids)) != len(ids):
        raise RuntimeError("Prototype checklist requirement IDs must be unique.")
    return requirements
