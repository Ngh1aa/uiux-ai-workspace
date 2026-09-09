/* Workbench-side preview of the canonical skills_UIUX flow.
   Backend flow-plan.json remains authoritative; this file mirrors the current
   GoalInterpreter + professional website flow closely enough for trustworthy
   pre-run routing previews. */
(function (global) {
  "use strict";

  const BASE_BY_STAGE = {
    research: [
      ["project-context/SKILL.md", "Giữ project truth và uncertainty"],
      ["adaptive-skill-routing-and-context-budget/SKILL.md", "Route skill theo task/context"],
      ["website-audit-and-redesign/SKILL.md", "Audit preserve/change khi applicable"],
      ["audience-intent-and-top-tasks/SKILL.md", "Ưu tiên audience intent và top tasks"],
      ["information-architecture/SKILL.md", "Information architecture và findability"],
      ["design-reference-research-and-benchmark/SKILL.md", "Reference intelligence có provenance"],
    ],
    ux_ia: [
      ["project-context/SKILL.md", "Giữ project truth và uncertainty"],
      ["adaptive-skill-routing-and-context-budget/SKILL.md", "Route skill theo task/context"],
      ["website-audit-and-redesign/SKILL.md", "Audit preserve/change khi applicable"],
      ["audience-intent-and-top-tasks/SKILL.md", "Ưu tiên audience intent và top tasks"],
      ["information-architecture/SKILL.md", "Information architecture và findability"],
      ["design-reference-research-and-benchmark/SKILL.md", "Reference intelligence có provenance"],
      ["ux-research-and-journey/SKILL.md", "Journey evidence và assumptions"],
      ["journey-driven-content-and-layout/SKILL.md", "Journey → content/layout"],
    ],
    art_direction: [
      ["ai-agent-coding-guardrails/SKILL.md", "Guardrails trước quyết định thiết kế"],
      ["journey-driven-content-and-layout/SKILL.md", "Journey → content/layout"],
      ["visual-design-direction/SKILL.md", "Visual grammar có rationale"],
      ["brand-distinctiveness-and-visual-signature/SKILL.md", "Digital signature ngoài logo/màu"],
      ["design-system-and-components/SKILL.md", "Direction phải implementable"],
      ["asset-media-and-art-direction/SKILL.md", "Media/crop/icon direction"],
      ["visual-taste-calibration/SKILL.md", "KEEP / REVISE / REMOVE anti-template"],
      ["brand-guidelines/SKILL.md", "Brand rules và consistency"],
    ],
    design_contract: [
      ["ai-agent-coding-guardrails/SKILL.md", "Guardrails trước quyết định thiết kế"],
      ["journey-driven-content-and-layout/SKILL.md", "Journey → content/layout"],
      ["visual-design-direction/SKILL.md", "Khóa direction vào canonical contract"],
      ["brand-distinctiveness-and-visual-signature/SKILL.md", "Khóa recognizable cues"],
      ["design-system-and-components/SKILL.md", "Ràng buộc downstream"],
      ["asset-media-and-art-direction/SKILL.md", "Khóa media/art direction"],
    ],
    design_system: [
      ["ai-agent-coding-guardrails/SKILL.md", "Guardrails trước quyết định thiết kế"],
      ["journey-driven-content-and-layout/SKILL.md", "Journey → content/layout"],
      ["visual-design-direction/SKILL.md", "Visual grammar có rationale"],
      ["brand-distinctiveness-and-visual-signature/SKILL.md", "Brand behavior trong system"],
      ["design-system-and-components/SKILL.md", "Tokens/components/states"],
      ["asset-media-and-art-direction/SKILL.md", "Media/crop/icon direction"],
      ["responsive-and-device-strategy/SKILL.md", "Responsive contracts"],
      ["accessibility/SKILL.md", "Accessible component contracts"],
    ],
    implementation_plan: [
      ["ai-agent-coding-guardrails/SKILL.md", "Bounded coding + verification"],
      ["frontend-implementation/SKILL.md", "Implementation strategy"],
      ["component-driven-development/SKILL.md", "Component boundaries"],
      ["responsive-and-device-strategy/SKILL.md", "Responsive implementation contract"],
      ["frontend-architecture-and-refactoring/SKILL.md", "Frontend architecture boundaries"],
    ],
    visual_composition: [
      ["ai-agent-coding-guardrails/SKILL.md", "Guardrails trước quyết định thiết kế"],
      ["journey-driven-content-and-layout/SKILL.md", "Journey → content/layout"],
      ["visual-design-direction/SKILL.md", "Page-role composition matrix"],
      ["brand-distinctiveness-and-visual-signature/SKILL.md", "Cross-page recognition"],
      ["design-system-and-components/SKILL.md", "Composition dùng canonical system"],
      ["asset-media-and-art-direction/SKILL.md", "Media/crop hierarchy"],
      ["visual-taste-calibration/SKILL.md", "Challenge generic composition"],
      ["responsive-and-device-strategy/SKILL.md", "Explicit mobile transformation"],
    ],
    implementation: [
      ["ai-agent-coding-guardrails/SKILL.md", "Workspace/code guardrails"],
      ["frontend-implementation/SKILL.md", "Semantic implementation"],
      ["component-driven-development/SKILL.md", "Reusable components"],
      ["responsive-and-device-strategy/SKILL.md", "Responsive implementation"],
      ["accessibility/SKILL.md", "Focus/semantics/accessibility"],
    ],
    browser_qa: [
      ["testing-strategy/SKILL.md", "Risk-based browser verification"],
      ["agent-evaluation-and-reliability/SKILL.md", "Evidence/reliability discipline"],
      ["ui-craft-and-visual-qa/SKILL.md", "Rendered evidence hard gate"],
      ["web-ui-code-review/SKILL.md", "Rendered defects → code owner"],
      ["accessibility/SKILL.md", "Accessibility smoke evidence"],
      ["web-quality-and-performance/SKILL.md", "Web quality/performance"],
      ["brand-recognition-and-consistency-qa/SKILL.md", "Brand recognition QA"],
      ["media-crop-and-layout-integrity/SKILL.md", "Media crop/layout integrity"],
      ["visual-regression-and-design-drift/SKILL.md", "Screenshot evidence"],
    ],
    visual_qa: [
      ["testing-strategy/SKILL.md", "Risk-based verification"],
      ["agent-evaluation-and-reliability/SKILL.md", "Evidence/reliability discipline"],
      ["ui-craft-and-visual-qa/SKILL.md", "Macro → micro craft review"],
      ["web-ui-code-review/SKILL.md", "Rendered defects → code owner"],
      ["accessibility/SKILL.md", "Accessibility acceptance boundary"],
      ["web-quality-and-performance/SKILL.md", "Web quality/performance"],
      ["brand-recognition-and-consistency-qa/SKILL.md", "Recognition QA"],
      ["media-crop-and-layout-integrity/SKILL.md", "Media crop/layout integrity"],
      ["visual-taste-calibration/SKILL.md", "Generic-AI feel calibration"],
      ["visual-regression-and-design-drift/SKILL.md", "Cross-route evidence"],
    ],
    repair: [
      ["testing-strategy/SKILL.md", "Regression verification"],
      ["agent-evaluation-and-reliability/SKILL.md", "Evidence/reliability discipline"],
      ["ui-craft-and-visual-qa/SKILL.md", "Rendered quality gate"],
      ["web-ui-code-review/SKILL.md", "Review owner/code before patch"],
      ["accessibility/SKILL.md", "Prevent accessibility regression"],
      ["web-quality-and-performance/SKILL.md", "Prevent web-quality regression"],
      ["brand-recognition-and-consistency-qa/SKILL.md", "Preserve recognition"],
      ["media-crop-and-layout-integrity/SKILL.md", "Repair media/layout integrity"],
      ["ui-improvement/SKILL.md", "Root-cause repair"],
      ["visual-taste-calibration/SKILL.md", "Repair interchangeable UI"],
      ["responsive-and-device-strategy/SKILL.md", "Repair by device"],
      ["state-feedback-and-error-recovery/SKILL.md", "Repair states/recovery"],
    ],
  };

  const RESEARCH_DOMAIN_SKILLS = {
    ecommerce: [
      ["ecommerce-website/SKILL.md", "Commerce discovery → evaluation → transaction"],
      ["conversion-and-content/SKILL.md", "Content/conversion hierarchy"],
      ["site-search-and-findability/SKILL.md", "Search/findability"],
    ],
    education: [
      ["education-website/SKILL.md", "Education journeys/trust"],
      ["trust-credibility-and-transparency/SKILL.md", "Institutional credibility"],
    ],
    government: [
      ["government-and-public-sector-website/SKILL.md", "Public-service task design"],
      ["inclusive-design-and-cognitive-accessibility/SKILL.md", "Broad-audience inclusion"],
    ],
    hospitality: [
      ["hospitality-website/SKILL.md", "Experience/booking journey"],
      ["service-experience-to-digital-journey/SKILL.md", "Service → digital journey"],
      ["conversion-and-content/SKILL.md", "Booking conversion"],
    ],
    news: [
      ["news-and-media-website/SKILL.md", "Editorial hierarchy"],
      ["site-search-and-findability/SKILL.md", "Archive/search discovery"],
    ],
    "real-estate": [
      ["real-estate-and-building-website/SKILL.md", "Property decision objects"],
      ["conversion-and-content/SKILL.md", "High-consideration conversion"],
    ],
    saas: [
      ["saas-website/SKILL.md", "Product-led SaaS storytelling"],
      ["product-discovery/SKILL.md", "Product problem/value"],
      ["complex-workflow-and-progress-ux/SKILL.md", "Complex workflow UX"],
    ],
    startup: [
      ["startup-and-incubator-website/SKILL.md", "Startup positioning"],
      ["conversion-and-content/SKILL.md", "Focused conversion"],
    ],
    portfolio: [["portfolio-website/SKILL.md", "Work-first portfolio storytelling"]],
    nonprofit: [
      ["nonprofit-website/SKILL.md", "Mission/action journey"],
      ["trust-credibility-and-transparency/SKILL.md", "Transparent proof"],
    ],
    landing: [
      ["landing-page/SKILL.md", "Focused landing-page hierarchy"],
      ["conversion-and-content/SKILL.md", "Conversion/content"],
    ],
    corporate: [["corporate-website/SKILL.md", "Corporate/B2B credibility and offering hierarchy"]],
    generic: [],
  };

  const WEBSITE_TYPES = [
    ["ecommerce", ["ecommerce", "e-commerce", "online store", "shop", "store", "bán hàng", "giỏ hàng", "checkout", "sản phẩm"]],
    ["education", ["school", "university", "college", "education", "academy", "trường học", "giáo dục", "tuyển sinh"]],
    ["government", ["government", "public sector", "ministry", "municipal", "chính phủ", "cơ quan nhà nước", "dịch vụ công"]],
    ["hospitality", ["hotel", "resort", "restaurant", "hospitality", "booking", "khách sạn", "khu nghỉ dưỡng", "nhà hàng", "đặt phòng"]],
    ["news", ["news", "magazine", "publisher", "media site", "tin tức", "tạp chí", "báo điện tử"]],
    ["real-estate", ["real estate", "property", "apartment", "building", "bất động sản", "căn hộ", "chung cư"]],
    ["saas", ["saas", "software platform", "web app", "dashboard", "subscription app", "phần mềm", "nền tảng"]],
    ["startup", ["startup", "incubator", "accelerator", "khởi nghiệp", "ươm tạo", "tăng tốc"]],
    ["portfolio", ["portfolio", "case study site", "creative studio", "hồ sơ năng lực", "showcase"]],
    ["nonprofit", ["nonprofit", "ngo", "charity", "foundation", "phi lợi nhuận", "từ thiện"]],
    ["landing", ["landing page", "campaign page", "microsite", "trang đích", "landing"]],
    ["corporate", ["corporate", "company website", "business website", "doanh nghiệp", "công ty", "tập đoàn", "website giới thiệu"]],
  ];

  const FEATURES = [
    ["search", ["search", "site search", "tìm kiếm"]],
    ["forms", ["form", "contact form", "lead form", "checkout", "đăng ký", "liên hệ", "biểu mẫu", "thanh toán"]],
    ["auth", ["login", "sign in", "account", "authentication", "đăng nhập", "tài khoản"]],
    ["dashboard", ["dashboard", "admin panel", "analytics", "bảng điều khiển", "trang quản trị"]],
    ["motion", ["animation", "motion", "microinteraction", "hiệu ứng", "chuyển động"]],
    ["i18n", ["multilingual", "multi-language", "bilingual", "đa ngôn ngữ", "song ngữ"]],
  ];

  const VERTICALS = [
    ["luxury-fragrance", ["perfume", "fragrance", "parfum", "niche scent", "nước hoa", "nuoc hoa"]],
    ["fashion", ["fashion", "clothing", "apparel", "streetwear", "quần áo", "thời trang"]],
    ["beauty-skincare", ["beauty", "skincare", "cosmetics", "mỹ phẩm", "chăm sóc da"]],
    ["electronics", ["electronics", "smartphone", "laptop", "computer store", "điện tử", "điện thoại", "máy tính"]],
    ["furniture-home", ["furniture", "home decor", "interior", "nội thất", "trang trí nhà"]],
    ["grocery-food", ["grocery", "food store", "supermarket", "thực phẩm", "siêu thị"]],
    ["jewelry-luxury", ["jewelry", "jewellery", "watch store", "trang sức", "đồng hồ"]],
    ["hotel-resort", ["hotel", "resort", "khách sạn", "khu nghỉ dưỡng"]],
    ["restaurant", ["restaurant", "cafe", "dining", "nhà hàng", "quán cà phê"]],
    ["higher-education", ["university", "college", "higher education", "đại học", "cao đẳng"]],
    ["school-k12", ["k-12", "international school", "school", "trường quốc tế", "trường học"]],
    ["fintech", ["fintech", "banking", "payments", "payment platform", "ngân hàng", "thanh toán"]],
    ["developer-tools", ["developer tools", "devtool", "api platform", "developer platform"]],
    ["news-publication", ["newspaper", "magazine", "publication", "báo điện tử", "tạp chí"]],
  ];

  const FLOW_STAGE = {
    research: "research",
    ux_ia: "research",
    art_direction: "design",
    design_contract: "design",
    design_system: "design",
    implementation_plan: "implementation",
    visual_composition: "design",
    implementation: "implementation",
    browser_qa: "qa",
    visual_qa: "qa",
    repair: "qa",
  };

  const PROTOTYPE_MODES = new Set(["visual-prototype", "interactive-prototype"]);
  const PROTOTYPE_SKILL = [
    "prototype-visual-experience-qa/SKILL.md",
    "3-second impression, signature moment, anti-generic and 5-second/squint QA",
  ];

  function normalize(goal) {
    return String(goal || "").trim().toLowerCase().replace(/\s+/g, " ");
  }

  function containsAny(text, tokens) {
    return tokens.some(token => text.includes(token));
  }

  function inferDomain(goal) {
    const text = normalize(goal);
    for (const [domain, tokens] of WEBSITE_TYPES) {
      if (containsAny(text, tokens)) {
        return { domain, score: tokens.filter(token => text.includes(token)).length };
      }
    }
    return { domain: "generic", score: 0 };
  }

  function inferVertical(goal) {
    const text = normalize(goal);
    for (const [vertical, tokens] of VERTICALS) {
      if (containsAny(text, tokens)) return vertical;
    }
    return "generic";
  }

  function inferMode(goal) {
    const text = normalize(goal);
    if (containsAny(text, ["production", "go live", "lên production", "chạy thật"])) return "production";
    if (containsAny(text, ["staging", "production candidate", "pre-production"])) return "production-candidate";
    if (containsAny(text, ["mockup", "visual prototype", "chỉ giao diện"])) return "visual-prototype";
    return "interactive-prototype";
  }

  function inferFeatures(goal) {
    const text = normalize(goal);
    return FEATURES.filter(([, tokens]) => containsAny(text, tokens)).map(([name]) => name);
  }

  function clarityScore(goal) {
    const text = String(goal || "").trim();
    let score = 0;
    if (text.length > 30) score += 1;
    if (text.length > 80) score += 1;
    if (text.length > 200) score += 1;
    if (/(trang|page|checkout|dashboard|portfolio|tuyển sinh|booking|search|form)/i.test(text)) score += 1;
    if (/(sang trọng|tối giản|editorial|chuyên nghiệp|ấm áp|thân thiện|sáng tạo|luxury|minimal|precise|playful)/i.test(text)) score += 1;
    if (/(không|avoid|do not|tránh|ưu tiên|priority|audience|đối tượng)/i.test(text)) score += 1;
    return Math.min(6, score);
  }

  function addSkill(map, pair, source) {
    const [path, reason] = pair;
    if (!map.has(path)) map.set(path, { path, reason, source });
  }

  function addFeatureSkills(map, profile, pairs, source) {
    for (const [feature, skillPairs] of pairs) {
      if (!profile.features.includes(feature)) continue;
      for (const pair of skillPairs) addSkill(map, pair, source);
    }
  }

  function conditionalSkills(stage, profile) {
    const map = new Map();
    const flowStage = FLOW_STAGE[stage];

    if (flowStage === "research") {
      for (const pair of RESEARCH_DOMAIN_SKILLS[profile.domain] || []) addSkill(map, pair, "domain");
      if (PROTOTYPE_MODES.has(profile.mode)) addSkill(map, PROTOTYPE_SKILL, "mode");
    }

    if (flowStage === "design") {
      if (["ecommerce", "saas"].includes(profile.domain)) {
        addSkill(map, ["interaction-patterns-and-form-ux/SKILL.md", "Interaction states/forms for this product type"], "domain");
      }
      if (["hospitality", "portfolio", "real-estate"].includes(profile.domain)) {
        addSkill(map, ["experience-principles-and-signature-moments/SKILL.md", "Signature moment for experience-led pages"], "domain");
      }
      addFeatureSkills(map, profile, [
        ["motion", [["motion-and-microinteractions/SKILL.md", "Intentional motion and microinteractions"]]],
        ["i18n", [["localization-and-i18n/SKILL.md", "Localization/i18n constraints"]]],
      ], "feature");
      if (PROTOTYPE_MODES.has(profile.mode)) addSkill(map, PROTOTYPE_SKILL, "mode");
    }

    if (flowStage === "implementation") {
      if (["production", "production-candidate"].includes(profile.mode)) {
        addSkill(map, ["system-reality-and-production-readiness/SKILL.md", "Production reality gate"], "mode");
        addSkill(map, ["testing-strategy/SKILL.md", "Production verification strategy"], "mode");
        addSkill(map, ["web-quality-and-performance/SKILL.md", "Performance and web quality"], "mode");
      }
      if (PROTOTYPE_MODES.has(profile.mode)) addSkill(map, PROTOTYPE_SKILL, "mode");
      addFeatureSkills(map, profile, [
        ["auth", [
          ["authentication-account-and-recovery-ux/SKILL.md", "Authentication/account UX"],
          ["security-and-privacy/SKILL.md", "Security/privacy constraints"],
        ]],
        ["forms", [
          ["complex-forms-and-wizards/SKILL.md", "Complex form behavior"],
          ["state-feedback-and-error-recovery/SKILL.md", "Error/recovery states"],
        ]],
        ["search", [["site-search-and-findability/SKILL.md", "Search/findability implementation"]]],
        ["dashboard", [
          ["data-tables-and-enterprise-ux/SKILL.md", "Enterprise table UX"],
          ["data-visualization-and-dashboard-ux/SKILL.md", "Dashboard visualization UX"],
        ]],
      ], "feature");
    }

    if (flowStage === "qa") {
      if (["production", "production-candidate"].includes(profile.mode)) {
        addSkill(map, ["system-reality-and-production-readiness/SKILL.md", "Production reality verification"], "mode");
        addSkill(map, ["code-review-and-release/SKILL.md", "Release/code review gate"], "mode");
      }
      if (PROTOTYPE_MODES.has(profile.mode)) addSkill(map, PROTOTYPE_SKILL, "mode");
      if (profile.features.includes("motion")) {
        addSkill(map, ["motion-and-microinteractions/SKILL.md", "Motion behavior QA"], "feature");
      }
    }

    return Array.from(map.values());
  }

  function route(stage, goal) {
    const { domain, score } = inferDomain(goal);
    const profile = {
      domain,
      domainScore: score,
      vertical: inferVertical(goal),
      mode: inferMode(goal),
      features: inferFeatures(goal),
    };
    const map = new Map();
    for (const pair of BASE_BY_STAGE[stage] || []) addSkill(map, pair, "base");
    for (const item of conditionalSkills(stage, profile)) {
      if (!map.has(item.path)) map.set(item.path, item);
    }
    return { profile, skills: Array.from(map.values()) };
  }

  function plan(goal) {
    const stages = [
      "research", "ux_ia", "art_direction", "design_contract", "design_system",
      "implementation_plan", "visual_composition", "implementation", "browser_qa", "visual_qa",
    ];
    const first = route("research", goal).profile;
    const result = {
      domain: first.domain,
      domainScore: first.domainScore,
      vertical: first.vertical,
      mode: first.mode,
      features: first.features,
      clarity: clarityScore(goal),
      domainSkills: RESEARCH_DOMAIN_SKILLS[first.domain] || [],
      stages: stages.map(stage => {
        const resolved = route(stage, goal);
        return {
          stage,
          skills: resolved.skills,
          applyDomain: resolved.skills.some(skill => skill.source === "domain"),
          applyMode: resolved.skills.some(skill => skill.source === "mode"),
        };
      }),
    };
    result.totalSkills = result.stages.reduce((sum, stage) => sum + stage.skills.length, 0);
    return result;
  }

  const STAGE_LABELS = {
    research: "Nghiên cứu & reference intelligence",
    ux_ia: "UX / IA & journey",
    art_direction: "Visual direction & signature",
    design_contract: "Canonical Design Contract",
    design_system: "Design system & interactions",
    implementation_plan: "Implementation plan",
    visual_composition: "Visual Brain & page composition",
    implementation: "Frontend implementation",
    browser_qa: "Browser / accessibility smoke",
    visual_qa: "Rendered visual critique",
    repair: "Root-cause repair",
  };

  function stageLabel(stage) { return STAGE_LABELS[stage] || stage; }

  function clarityTips(goal) {
    const text = String(goal || "").trim();
    const tips = [];
    if (text.length < 45) tips.push("Bổ sung mục tiêu, audience và task chính");
    if (!/(trang|page|checkout|dashboard|portfolio|booking|form|search|tuyển sinh)/i.test(text)) tips.push("Nêu page roles hoặc primary journey");
    if (!/(sang trọng|tối giản|editorial|chuyên nghiệp|ấm áp|thân thiện|sáng tạo|luxury|minimal|precise|playful)/i.test(text)) tips.push("Nêu personality/visual direction mong muốn");
    if (!/(không|avoid|do not|tránh)/i.test(text)) tips.push("Nêu ít nhất một điều cần tránh để giảm generic output");
    if (!tips.length && text) tips.push("Brief đủ rõ để Visual Brain khóa direction và gate");
    return tips;
  }

  global.UiuxRouter = {
    plan,
    route,
    inferDomain,
    inferVertical,
    inferMode,
    inferFeatures,
    clarityScore,
    stageLabel,
    clarityTips,
  };
})(window);

/* Workbench interaction bridge.
   Keep inspiration controls and reference-row a11y synchronized with the
   DesignContext contract without exposing research credentials client-side. */
(function () {
  "use strict";
  const KEY = "uiux-workbench-visual-controls-v2";
  const originalFetch = window.fetch.bind(window);

  function controls() {
    return {
      auto: document.getElementById("auto-inspiration"),
      target: document.getElementById("inspiration-target"),
      refs: document.getElementById("ref-urls"),
    };
  }

  function clampTarget(value) {
    return Math.max(1, Math.min(4, Number(value) || 4));
  }

  function save() {
    const { auto, target } = controls();
    if (!auto || !target) return;
    try {
      localStorage.setItem(KEY, JSON.stringify({
        auto: auto.checked,
        target: clampTarget(target.value),
      }));
    } catch {}
  }

  function restore() {
    const { auto, target } = controls();
    if (!auto || !target) return;
    try {
      const value = JSON.parse(localStorage.getItem(KEY) || "{}");
      if (typeof value.auto === "boolean") auto.checked = value.auto;
      if ([1, 2, 3, 4].includes(Number(value.target))) target.value = String(value.target);
    } catch {}
    target.disabled = !auto.checked;
  }

  function labelReferenceRows() {
    const rows = Array.from(document.querySelectorAll(".ref-row"));
    rows.forEach((row, index) => {
      const input = row.querySelector("input");
      const button = row.querySelector("button");
      if (input) input.setAttribute("aria-label", `Reference URL ${index + 1}`);
      if (button) {
        button.setAttribute("aria-label", `Xoá reference ${index + 1}`);
        button.removeAttribute("title");
      }
    });
  }

  window.fetch = function (input, init) {
    try {
      const url = typeof input === "string" ? input : (input && input.url) || "";
      if (init && String(init.method || "GET").toUpperCase() === "POST" && /\/(run|intelligence)$/.test(url) && init.body) {
        const payload = JSON.parse(init.body);
        const { auto, target } = controls();
        payload.design_context = payload.design_context || {};
        if (auto) payload.design_context.auto_inspiration = Boolean(auto.checked);
        if (target) payload.design_context.inspiration_target = clampTarget(target.value);
        init = { ...init, body: JSON.stringify(payload) };
      }
    } catch {}
    return originalFetch(input, init);
  };

  document.addEventListener("DOMContentLoaded", () => {
    restore();
    const { auto, target, refs } = controls();
    auto?.addEventListener("change", () => {
      if (target) target.disabled = !auto.checked;
      save();
    });
    target?.addEventListener("change", save);
    if (refs) {
      new MutationObserver(labelReferenceRows).observe(refs, { childList: true, subtree: true });
      labelReferenceRows();
    }
  });
})();
