/* ============================================================
   skills-router.js — Mirror của core/skills/router.py để hiển thị
   cho người dùng TRƯỚC khi chạy pipeline. Đây là "trí thông minh"
   của console: biết được hệ thống sẽ làm gì với prompt hiện tại.
   ============================================================ */

(function (global) {
  "use strict";

  // Trùng với core/skills/router.py — giữ đơn giản (chỉ phần dùng cho UI)
  const BASE_BY_STAGE = {
    research: [
      ["project-context/SKILL.md", "Giữ sự thật và ràng buộc của dự án"],
      ["product-discovery/SKILL.md", "Xác định đối tượng, vấn đề, JTBD, phạm vi"],
      ["design-reference-research-and-benchmark/SKILL.md", "Nghiên cứu reference có bằng chứng"],
      ["ux-benchmarking-and-metrics/SKILL.md", "Benchmarking đối thủ & tiêu chuẩn thiết kế"],
    ],
    ux_ia: [
      ["ux-research-and-journey/SKILL.md", "Nền tảng journey & task analysis"],
      ["information-architecture/SKILL.md", "Phân cấp, taxonomy, điều hướng"],
      ["audience-intent-and-top-tasks/SKILL.md", "Ưu tiên intent người dùng"],
      ["journey-driven-content-and-layout/SKILL.md", "Map journey → cấu trúc nội dung"],
    ],
    art_direction: [
      ["visual-design-direction/SKILL.md", "Ngữ pháp thị giác, hierarchy"],
      ["visual-taste-calibration/SKILL.md", "Chống generic/template"],
      ["brand-guidelines/SKILL.md", "Dịch brand truth thành quy tắc thị giác"],
      ["asset-media-and-art-direction/SKILL.md", "Định hướng media/ảnh/icon"],
      ["motion-and-microinteractions/SKILL.md", "Ngôn ngữ chuyển động & micro-interactions"],
      ["experience-principles-and-signature-moments/SKILL.md", "Khoảnh khắc tạo ấn tượng thị giác"],
    ],
    design_contract: [
      ["project-context/SKILL.md", "Giữ truth trong canonical contract"],
      ["visual-design-direction/SKILL.md", "Mang direction đã duyệt vào ràng buộc"],
      ["design-system-and-components/SKILL.md", "Định ràng buộc implementation"],
    ],
    design_system: [
      ["design-system-and-components/SKILL.md", "Tokens, components, variants, states"],
      ["brand-guidelines/SKILL.md", "Token gắn với brand truth"],
      ["responsive-and-device-strategy/SKILL.md", "Quy tắc responsive"],
      ["accessibility/SKILL.md", "Accessibility trong component contract"],
      ["component-driven-development/SKILL.md", "Kiến trúc component module"],
      ["design-system-governance-and-adoption/SKILL.md", "Quy chuẩn token & consistency"],
    ],
    implementation_plan: [
      ["frontend-architecture-and-refactoring/SKILL.md", "Quy hoạch ranh giới frontend"],
      ["frontend-implementation/SKILL.md", "Triển khai theo design đã duyệt"],
      ["ai-agent-coding-guardrails/SKILL.md", "Slice & verify trước khi ship"],
    ],
    visual_composition: [
      ["visual-design-direction/SKILL.md", "Direction → composition cấp trang"],
      ["visual-taste-calibration/SKILL.md", "Chống generic/interchangeable"],
      ["responsive-and-device-strategy/SKILL.md", "Mobile/tablet transformation"],
      ["asset-media-and-art-direction/SKILL.md", "Anchor thị giác cho trang"],
      ["trust-credibility-and-transparency/SKILL.md", "Bằng chứng & tín hiệu tin cậy"],
      ["ux-laws-and-heuristics/SKILL.md", "Luật UX (Fitts, Hick, Miller, Jakob)"],
    ],
    implementation: [
      ["frontend-implementation/SKILL.md", "Semantic + verify"],
      ["ai-agent-coding-guardrails/SKILL.md", "Chống unsafe AI code"],
      ["design-system-and-components/SKILL.md", "Dùng token canonical"],
      ["responsive-and-device-strategy/SKILL.md", "Responsive tường minh"],
      ["accessibility/SKILL.md", "Semantic/focus/keyboard baseline"],
      ["motion-and-microinteractions/SKILL.md", "Animation mượt & hover feedback"],
      ["state-feedback-and-error-recovery/SKILL.md", "Phản hồi trạng thái (loading/empty/error)"],
    ],
    browser_qa: [
      ["testing-strategy/SKILL.md", "Risk-based verification"],
      ["ui-craft-and-visual-qa/SKILL.md", "QA render thật, không tin build"],
      ["accessibility/SKILL.md", "Accessibility baseline"],
      ["visual-regression-and-design-drift/SKILL.md", "Screenshot = bằng chứng"],
      ["web-quality-and-performance/SKILL.md", "Hiệu năng web & visual polish"],
    ],
    visual_qa: [
      ["ui-craft-and-visual-qa/SKILL.md", "Đánh giá craft render"],
      ["visual-taste-calibration/SKILL.md", "Phát hiện generic"],
      ["visual-regression-and-design-drift/SKILL.md", "So sánh evidence"],
      ["accessibility/SKILL.md", "Accessibility trong acceptance"],
    ],
    repair: [
      ["ui-improvement/SKILL.md", "Diagnose → preserve → route → repair"],
      ["frontend-implementation/SKILL.md", "Sửa implementation có kiểm soát"],
      ["ai-agent-coding-guardrails/SKILL.md", "Giữ repair bounded"],
      ["visual-taste-calibration/SKILL.md", "Sửa visual generic"],
      ["responsive-and-device-strategy/SKILL.md", "Sửa theo device"],
      ["accessibility/SKILL.md", "Không regress accessibility"],
    ],
  };

  const DOMAIN_SKILLS = {
    ecommerce: [["ecommerce-website/SKILL.md", "Playbook ecommerce discover → checkout"]],
    corporate: [["corporate-website/SKILL.md", "Playbook corporate/B2B"]],
    education: [["education-website/SKILL.md", "Playbook giáo dục"]],
    agency: [
      ["corporate-website/SKILL.md", "Playbook corporate cho B2B credibility"],
      ["conversion-and-content/SKILL.md", "Proof + CTA cho agency"],
    ],
  };

  const OPTIONAL_BY_SIGNAL = [
    {
      signals: ["redesign", "thiết kế lại", "website cũ", "legacy"],
      path: "website-audit-and-redesign/SKILL.md",
      reason: "Audit website cũ trước khi redesign",
      stages: ["research", "ux_ia"],
    },
    {
      signals: ["search", "tìm kiếm", "findability"],
      path: "site-search-and-findability/SKILL.md",
      reason: "Search/findability quan trọng",
      stages: ["ux_ia", "visual_composition", "implementation"],
    },
    {
      signals: ["form", "lead", "đăng ký", "tuyển sinh", "checkout", "giỏ hàng"],
      path: "interaction-patterns-and-form-ux/SKILL.md",
      reason: "Form/transactional là trọng tâm",
      stages: ["ux_ia", "design_system", "implementation"],
    },
  ];

  function inferDomain(goal) {
    const text = (goal || "").toLowerCase();
    const signals = {
      ecommerce: ["ecommerce", "e-commerce", "thương mại điện tử", "marketplace", "shop", "shopee", "giỏ hàng", "checkout", "sản phẩm", "bán"],
      education: ["education", "school", "academy", "trường học", "trường", "học sinh", "tuyển sinh", "phụ huynh", "giáo dục"],
      agency: ["agency", "digital agency", "marketing", "seo", "quảng cáo", "creative studio", "sáng tạo"],
      corporate: ["corporate", "company", "doanh nghiệp", "công ty", "b2b", "enterprise", "technology", "công nghệ", "ngân hàng", "tài chính"],
    };
    let best = "corporate";
    let bestScore = 0;
    for (const [domain, tokens] of Object.entries(signals)) {
      let score = 0;
      for (const t of tokens) if (text.includes(t)) score++;
      if (score > bestScore) { bestScore = score; best = domain; }
    }
    return { domain: best, score: bestScore };
  }

  function clarityScore(goal) {
    const text = (goal || "").trim();
    let score = 0;
    if (text.length > 30) score += 1;
    if (text.length > 80) score += 1;
    if (text.length > 200) score += 1;
    const tokens = ["trang chủ", "sản phẩm", "dịch vụ", "liên hệ", "blog", "landing", "dashboard", "ecommerce", "saas", "portfolio", "checkout", "giỏ hàng", "tuyển sinh", "case study"];
    let hits = 0;
    for (const t of tokens) if (text.toLowerCase().includes(t)) hits++;
    if (hits >= 1) score += 1;
    if (hits >= 3) score += 1;
    if (/(sang trọng|tối giản|hiện đại|trẻ trung|chuyên nghiệp|ấm áp|thân thiện|sáng tạo)/i.test(text)) score += 1;
    return Math.min(6, score);
  }

  function route(stage, goal, domain) {
    const text = (goal || "").toLowerCase();
    const map = new Map();
    for (const [path, reason] of BASE_BY_STAGE[stage] || []) {
      map.set(path, { path, reason, source: "base" });
    }
    if (["research","ux_ia","art_direction","design_system","implementation_plan","visual_composition","implementation","visual_qa","repair"].includes(stage)) {
      for (const [path, reason] of DOMAIN_SKILLS[domain] || []) {
        if (!map.has(path)) map.set(path, { path, reason, source: "domain" });
      }
    }
    for (const rule of OPTIONAL_BY_SIGNAL) {
      if (!rule.stages.includes(stage)) continue;
      if (rule.signals.some(s => text.includes(s.toLowerCase()))) {
        if (!map.has(rule.path)) map.set(rule.path, { path: rule.path, reason: rule.reason, source: "signal" });
      }
    }
    return Array.from(map.values());
  }

  function plan(goal) {
    const { domain, score } = inferDomain(goal);
    const clarity = clarityScore(goal);
    const stages = [
      "research","ux_ia","art_direction","design_contract","design_system",
      "implementation_plan","visual_composition","implementation","browser_qa","visual_qa"
    ];
    const result = {
      domain, domainScore: score, clarity,
      domainSkills: DOMAIN_SKILLS[domain] || [],
      stages: stages.map(s => ({
        stage: s,
        skills: route(s, goal, domain),
        applyDomain: ["research","ux_ia","art_direction","design_system","implementation_plan","visual_composition","implementation","visual_qa"].includes(s),
      })),
    };
    let total = 0;
    for (const s of result.stages) total += s.skills.length;
    result.totalSkills = total;
    return result;
  }

  // Pretty labels cho UI
  const STAGE_LABELS = {
    research: "Nghiên cứu",
    ux_ia: "UX & IA",
    art_direction: "Đạo diễn thị giác",
    design_contract: "Hợp đồng thiết kế",
    design_system: "Hệ thống thiết kế",
    implementation_plan: "Kế hoạch triển khai",
    visual_composition: "Bố cục thị giác",
    implementation: "Code frontend",
    browser_qa: "QA trên trình duyệt",
    visual_qa: "Phản biện thị giác",
    repair: "Tự sửa",
  };

  function stageLabel(s) {
    return STAGE_LABELS[s] || s;
  }

  function clarityTips(goal) {
    const tips = [];
    const text = (goal || "").trim();
    if (text.length < 30) tips.push("Prompt quá ngắn — bổ sung mục tiêu và phong cách");
    if (text.length > 0 && text.length < 100) tips.push("Có thể nói rõ hơn về đối tượng hoặc ngành");
    const hasPages = /trang|page|giao diện/i.test(text);
    if (!hasPages) tips.push("Liệt kê các trang chính (trang chủ, sản phẩm, giỏ hàng…)");
    const hasStyle = /(sang trọng|tối giản|hiện đại|trẻ trung|chuyên nghiệp|ấm áp|thân thiện|sáng tạo|cao cấp|luxury|minimal|modern)/i.test(text);
    if (!hasStyle && text.length > 0) tips.push("Thêm phong cách thị giác (sang trọng, tối giản, hiện đại…)");
    if (tips.length === 0 && text.length > 0) tips.push("Brief rõ ràng — hệ thống đủ thông tin để chạy");
    return tips;
  }

  global.UiuxRouter = { plan, inferDomain, clarityScore, stageLabel, clarityTips };
})(window);
