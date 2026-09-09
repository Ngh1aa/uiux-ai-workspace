/* Workbench-side preview of the canonical skills_UIUX flow.
   Backend flow-plan.json remains authoritative; this file exists so the user
   can see likely routing before a run starts. */
(function (global) {
  "use strict";

  const BASE_BY_STAGE = {
    research: [
    research: [
      ["project-context/SKILL.md", "Giữ sự thật và ràng buộc của dự án"],
      ["product-discovery/SKILL.md", "Xác định đối tượng, vấn đề, JTBD, phạm vi"],
      ["adaptive-skill-routing-and-context-budget/SKILL.md", "Route skill theo task/context"],
      ["design-reference-research-and-benchmark/SKILL.md", "Nghiên cứu reference có bằng chứng"],
      ["ux-benchmarking-and-metrics/SKILL.md", "Benchmarking đối thủ & tiêu chuẩn thiết kế"],
      ["website-audit-and-redesign/SKILL.md", "Audit preserve/change khi applicable"],
      ["audience-intent-and-top-tasks/SKILL.md", "Ưu tiên audience intent và top tasks"],
      ["information-architecture/SKILL.md", "Information architecture và findability"],
    ],
    ],
    ux_ia: [
      ["project-context/SKILL.md", "Không biến inference thành project truth"],
      ["audience-intent-and-top-tasks/SKILL.md", "Map top tasks"],
      ["information-architecture/SKILL.md", "Page roles, taxonomy, navigation"],
      ["journey-driven-content-and-layout/SKILL.md", "Journey → content/layout"],
      ["ux-research-and-journey/SKILL.md", "Journey evidence và assumptions"],
    ],
    art_direction: [
    art_direction: [
      ["visual-design-direction/SKILL.md", "Visual grammar có rationale"],
      ["brand-distinctiveness-and-visual-signature/SKILL.md", "Digital signature ngoài logo/màu"],
      ["visual-taste-calibration/SKILL.md", "KEEP / REVISE / REMOVE anti-template"],
      ["design-system-and-components/SKILL.md", "Direction phải implementable"],
      ["asset-media-and-art-direction/SKILL.md", "Media/crop/icon direction"],
      ["motion-and-microinteractions/SKILL.md", "Ngôn ngữ chuyển động & micro-interactions"],
      ["experience-principles-and-signature-moments/SKILL.md", "Khoảnh khắc tạo ấn tượng thị giác"],
    ],
    ],
    design_contract: [
      ["visual-design-direction/SKILL.md", "Khóa direction vào canonical contract"],
      ["brand-distinctiveness-and-visual-signature/SKILL.md", "Khóa recognizable cues"],
      ["design-system-and-components/SKILL.md", "Ràng buộc downstream"],
    ],
    design_system: [
    design_system: [
      ["design-system-and-components/SKILL.md", "Tokens/components/states"],
      ["brand-distinctiveness-and-visual-signature/SKILL.md", "Brand behavior trong system"],
      ["responsive-and-device-strategy/SKILL.md", "Responsive contracts"],
      ["accessibility/SKILL.md", "Accessible component contracts"],
      ["interaction-patterns-and-form-ux/SKILL.md", "Interaction states và forms"],
      ["brand-guidelines/SKILL.md", "Token gắn với brand truth"],
    ],
    ],
    implementation_plan: [
      ["frontend-architecture-and-refactoring/SKILL.md", "Frontend boundaries"],
      ["frontend-implementation/SKILL.md", "Implementation strategy"],
      ["ai-agent-coding-guardrails/SKILL.md", "Bounded coding + verification"],
    ],
    visual_composition: [
    visual_composition: [
      ["visual-design-direction/SKILL.md", "Page-role composition matrix"],
      ["brand-distinctiveness-and-visual-signature/SKILL.md", "Cross-page recognition"],
      ["visual-taste-calibration/SKILL.md", "Challenge generic composition"],
      ["interaction-patterns-and-form-ux/SKILL.md", "Task/state behavior in composition"],
      ["ui-craft-and-visual-qa/SKILL.md", "Pre-code craft sanity"],
      ["responsive-and-device-strategy/SKILL.md", "Explicit mobile transformation"],
    ],
    ],
    visual_qa: [
      ["ui-craft-and-visual-qa/SKILL.md", "Macro → micro craft review"],
      ["visual-taste-calibration/SKILL.md", "Generic-AI feel calibration"],
      ["brand-distinctiveness-and-visual-signature/SKILL.md", "Recognition QA"],
      ["visual-regression-and-design-drift/SKILL.md", "Cross-route evidence"],
      ["accessibility/SKILL.md", "Accessibility acceptance boundary"],
    ],
    repair: [
      ["ui-improvement/SKILL.md", "Root-cause repair"],
      ["web-ui-code-review/SKILL.md", "Review owner/code before patch"],
      ["visual-taste-calibration/SKILL.md", "Repair interchangeable UI"],
      ["interaction-patterns-and-form-ux/SKILL.md", "Repair states/recovery"],
      ["responsive-and-device-strategy/SKILL.md", "Repair by device"],
      ["accessibility/SKILL.md", "Prevent accessibility regression"],
    ],
  };

  const DOMAIN_SKILLS = {
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

  const SIGNALS = {
    ecommerce: ["ecommerce", "e-commerce", "shop", "store", "bán hàng", "giỏ hàng", "checkout", "sản phẩm"],
    education: ["education", "school", "university", "academy", "trường", "giáo dục", "tuyển sinh"],
    government: ["government", "public sector", "ministry", "dịch vụ công", "chính phủ", "cơ quan nhà nước"],
    hospitality: ["hotel", "resort", "hospitality", "khách sạn", "khu nghỉ dưỡng", "đặt phòng", "nhà hàng"],
    news: ["news", "magazine", "publisher", "tin tức", "tạp chí", "báo điện tử"],
    "real-estate": ["real estate", "property", "apartment", "bất động sản", "căn hộ", "chung cư"],
    saas: ["saas", "software platform", "web app", "dashboard", "phần mềm", "nền tảng"],
    startup: ["startup", "incubator", "accelerator", "khởi nghiệp"],
    portfolio: ["portfolio", "creative studio", "case study site", "showcase", "hồ sơ năng lực"],
    nonprofit: ["nonprofit", "ngo", "charity", "foundation", "phi lợi nhuận", "từ thiện"],
    landing: ["landing page", "campaign page", "microsite", "trang đích"],
    corporate: ["corporate", "company website", "business website", "doanh nghiệp", "công ty", "b2b", "enterprise"],
  };

  function inferDomain(goal) {
    const text = (goal || "").toLowerCase();
    let best = "generic";
    let bestScore = 0;
    for (const [domain, tokens] of Object.entries(SIGNALS)) {
      let score = 0;
      for (const token of tokens) if (text.includes(token)) score += 1;
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
    if (/(trang|page|checkout|dashboard|portfolio|tuyển sinh|booking|search|form)/i.test(text)) score += 1;
    if (/(sang trọng|tối giản|editorial|chuyên nghiệp|ấm áp|thân thiện|sáng tạo|luxury|minimal|precise|playful)/i.test(text)) score += 1;
    if (/(không|avoid|do not|tránh|ưu tiên|priority|audience|đối tượng)/i.test(text)) score += 1;
    return Math.min(6, score);
  }

  function route(stage, goal, domain) {
    const map = new Map();
    for (const [path, reason] of BASE_BY_STAGE[stage] || []) map.set(path, { path, reason, source: "base" });
    const domainStages = new Set(["research", "ux_ia", "art_direction", "design_system", "visual_composition", "implementation", "visual_qa"]);
    if (domainStages.has(stage)) {
      for (const [path, reason] of DOMAIN_SKILLS[domain] || []) {
        if (!map.has(path)) map.set(path, { path, reason, source: "domain" });
      }
    }
    return Array.from(map.values());
  }

  function plan(goal) {
    const { domain, score } = inferDomain(goal);
    const clarity = clarityScore(goal);
    const stages = [
      "research", "ux_ia", "art_direction", "design_contract", "design_system",
      "implementation_plan", "visual_composition", "implementation", "browser_qa", "visual_qa",
    ];
    const result = {
      domain,
      domainScore: score,
      clarity,
      domainSkills: DOMAIN_SKILLS[domain] || [],
      stages: stages.map(stage => ({
        stage,
        skills: route(stage, goal, domain),
        applyDomain: (DOMAIN_SKILLS[domain] || []).length > 0,
      })),
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
    const text = (goal || "").trim();
    const tips = [];
    if (text.length < 45) tips.push("Bổ sung mục tiêu, audience và task chính");
    if (!/(trang|page|checkout|dashboard|portfolio|booking|form|search|tuyển sinh)/i.test(text)) tips.push("Nêu page roles hoặc primary journey");
    if (!/(sang trọng|tối giản|editorial|chuyên nghiệp|ấm áp|thân thiện|sáng tạo|luxury|minimal|precise|playful)/i.test(text)) tips.push("Nêu personality/visual direction mong muốn");
    if (!/(không|avoid|do not|tránh)/i.test(text)) tips.push("Nêu ít nhất một điều cần tránh để giảm generic output");
    if (!tips.length && text) tips.push("Brief đủ rõ để Visual Brain khóa direction và gate");
    return tips;
  }

  global.UiuxRouter = { plan, inferDomain, clarityScore, stageLabel, clarityTips };
})(window);

/* Workbench interaction bridge.
   This lives in the already-loaded self-hosted script so the security policy
   stays script-src 'self' and the existing app.js does not need a second API. */
(function () {
  "use strict";
  const KEY = "uiux-workbench-visual-controls-v1";
  const originalFetch = window.fetch.bind(window);

  function controls() {
    return {
      auto: document.getElementById("auto-inspiration"),
      target: document.getElementById("inspiration-target"),
      refs: document.getElementById("ref-urls"),
    };
  }

  function save() {
    const { auto, target } = controls();
    if (!auto || !target) return;
    try {
      localStorage.setItem(KEY, JSON.stringify({
        auto: auto.checked,
        target: Number(target.value) || 2,
      }));
    } catch {}
  }

  function restore() {
    const { auto, target } = controls();
    if (!auto || !target) return;
    try {
      const value = JSON.parse(localStorage.getItem(KEY) || "{}");
      if (typeof value.auto === "boolean") auto.checked = value.auto;
      if ([1, 2].includes(Number(value.target))) target.value = String(value.target);
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
        if (target) payload.design_context.inspiration_target = Number(target.value) || 2;
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
