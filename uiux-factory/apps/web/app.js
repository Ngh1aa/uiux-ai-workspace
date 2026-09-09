/* ============================================================
   app.js — UIUX Factory Workbench Console 2.0 (Client Studio)
   - Dark/Light theme switching & persistence
   - Trending Web Inspiration patterns loader
   - Live smart routing (mirrors router.py with 37+ skills)
   - Auto-save drafts (localStorage)
   - Pipeline job runner & real-time stage progress
   - Device frame switcher (Desktop, Tablet, Mobile)
   - Inline modal artifact viewer (Markdown, CSS, JSON)
   - Submit → Factory pipeline
   - Poll job + render stages, logs, artifacts, preview
   - Export Review Pack → import Creative Directive → stage-aware revision
   ============================================================ */

(() => {
  "use strict";

  function detectApiBase() {
    if (window.UIUX_BRIDGE_URL) return window.UIUX_BRIDGE_URL.replace(/\/$/, "") + "/api";
    if (location.protocol === "http:" || location.protocol === "https:") {
      return "/api";
    }
    return "http://127.0.0.1:8788/api";
  }

  const BRIDGE = detectApiBase();
  const DRAFT_KEY = "uiux-console-draft-v2";
  const JOB_HISTORY_KEY = "uiux-console-jobs-v2";
  const THEME_KEY = "uiux-studio-theme";

  const els = {
    themeToggle: document.getElementById("theme-toggle"),
    form: document.getElementById("prompt-form"),
    prompt: document.getElementById("prompt"),
    counter: document.getElementById("prompt-counter"),
    clearBtn: document.getElementById("clear-prompt"),
    chips: document.querySelectorAll(".chip"),
    submitBtn: document.getElementById("submit-btn"),
    submitSub: document.getElementById("submit-sub"),
    aiRadio: document.getElementById("ai-radio-wrap"),
    aiStatus: document.getElementById("ai-status"),
    bridgeStatus: document.getElementById("bridge-status"),
    bridgeInfo: document.getElementById("bridge-info"),
    smartDomain: document.getElementById("smart-domain"),
    smartDomainReason: document.getElementById("smart-domain-reason"),
    smartClarity: document.getElementById("smart-clarity"),
    smartClarityTips: document.getElementById("smart-clarity-tips"),
    smartSkillCount: document.getElementById("smart-skill-count"),
    smartSkillMeta: document.getElementById("smart-skill-meta"),
    stagePlan: document.getElementById("stage-plan"),
    refUrls: document.getElementById("ref-urls"),
    addRef: document.getElementById("add-ref-url"),
    autoInspiration: document.getElementById("auto-inspiration"),
    inspirationTarget: document.getElementById("inspiration-target"),
    jobEmpty: document.getElementById("job-empty"),
    jobCard: document.getElementById("job-card"),
    jobId: document.getElementById("job-id"),
    jobPrompt: document.getElementById("job-prompt"),
    jobStatus: document.getElementById("job-status-badge"),
    stageTimeline: document.getElementById("stage-timeline"),
    progressFill: document.getElementById("pipeline-progress-fill"),
    artifacts: document.getElementById("artifacts"),
    artifactList: document.getElementById("artifact-list"),
    logsWrap: document.getElementById("logs-wrap"),
    logs: document.getElementById("job-logs"),
    previewWrap: document.getElementById("preview-wrap"),
    previewFrame: document.getElementById("preview-frame"),
    previewContainer: document.getElementById("preview-container"),
    chromeUrl: document.getElementById("chrome-url"),
    refreshPreview: document.getElementById("refresh-preview-btn"),
    brandName: document.getElementById("brand-name"),
    brandPersonality: document.getElementById("brand-personality"),
    brandAvoid: document.getElementById("brand-avoid"),
    tokensJson: document.getElementById("tokens-json"),
    inspirePills: document.querySelectorAll(".inspire-pill"),
    deviceBtns: document.querySelectorAll(".device-btn"),
    artifactModal: document.getElementById("artifact-modal"),
    modalFilename: document.getElementById("modal-filename"),
    modalContent: document.getElementById("modal-content"),
    modalOpenRaw: document.getElementById("modal-open-raw"),
    modalCloseBtn: document.getElementById("modal-close-btn"),
  };

  // -----------------------------------------------------------
  // Theme Management (Dark / Light)
  // -----------------------------------------------------------
  function initTheme() {
    const saved = localStorage.getItem(THEME_KEY) || "dark";
    document.documentElement.setAttribute("data-theme", saved);
  }

  function toggleTheme() {
    const current = document.documentElement.getAttribute("data-theme") || "dark";
    const next = current === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    try { localStorage.setItem(THEME_KEY, next); } catch {}
  }

  if (els.themeToggle) {
    els.themeToggle.addEventListener("click", toggleTheme);
  }
  initTheme();

  // -----------------------------------------------------------
  // Device Frame Viewport Switcher
  // -----------------------------------------------------------
  if (els.deviceBtns) {
    els.deviceBtns.forEach(btn => {
      btn.addEventListener("click", () => {
        const vp = btn.dataset.viewport;
        els.deviceBtns.forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        if (els.previewContainer) {
          els.previewContainer.setAttribute("data-viewport", vp);
        }
      });
    });
  }

  // -----------------------------------------------------------
  // Trending Inspiration Patterns
  // -----------------------------------------------------------
  async function loadInspirationPatterns() {
    try {
      const res = await fetch(`${BRIDGE}/inspiration`, { cache: "no-store" });
      if (!res.ok) return;
      const data = await res.json();
      if (data && data.patterns && data.patterns.length) {
        const container = document.getElementById("inspiration-pills");
        if (container) {
          container.innerHTML = data.patterns.map(p => `
            <button type="button" class="inspire-pill" data-pattern="${escapeHtml(p.id)}" data-tags="${escapeHtml(p.description)}">
              <span class="pill-dot" style="background:${p.preview_accent || 'var(--accent)'};"></span>
              <strong>${escapeHtml(p.name)}</strong> · ${escapeHtml(p.category)}
            </button>
          `).join("");
          bindInspirationClicks();
        }
      }
    } catch {}
  }

  function bindInspirationClicks() {
    document.querySelectorAll(".inspire-pill").forEach(pill => {
      pill.addEventListener("click", () => {
        const tags = pill.dataset.tags || "";
        const name = pill.querySelector("strong")?.textContent || "";
        const cur = els.prompt.value.trim();
        const addition = `Áp dụng phong cách ${name} (${tags}).`;
        if (!cur.includes(name)) {
          els.prompt.value = cur ? `${cur}\n\n${addition}` : addition;
          updateCounter();
          updateSmartPreview();
          saveDraft();
          els.prompt.focus();
        }
      });
    });
  }
  bindInspirationClicks();
  loadInspirationPatterns();

  function installCreativeReviewPanel() {
    if (!els.jobCard || document.getElementById("creative-review-panel")) return;
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = "./creative-review.css";
    document.head.appendChild(link);

    const panel = document.createElement("section");
    panel.id = "creative-review-panel";
    panel.className = "creative-review-panel";
    panel.hidden = true;
    panel.setAttribute("aria-labelledby", "creative-review-title");
    panel.innerHTML = `
      <div class="creative-review-copy">
        <span class="creative-review-kicker">04 · Creative review</span>
        <strong id="creative-review-title">Handoff cho Creative Director</strong>
        <p>Xuất screenshot + design evidence, review cùng ChatGPT, rồi import directive để Factory chỉ rebuild từ stage cần sửa.</p>
      </div>
      <div class="creative-review-actions">
        <button type="button" class="creative-review-export" id="export-review-pack">Export Review Pack</button>
        <button type="button" class="creative-review-import" id="import-creative-directive">Import Creative Directive</button>
        <input id="creative-directive-file" type="file" accept="application/json,.json" hidden />
      </div>
      <div class="creative-review-status" id="creative-review-status" role="status" aria-live="polite">
        Upload Review Pack vào chat với Creative Director, rồi đưa file directive trở lại đây.
      </div>`;
    const jobHead = els.jobCard.querySelector(".job-head");
    jobHead?.insertAdjacentElement("afterend", panel);

    els.reviewPanel = panel;
    els.reviewStatus = panel.querySelector("#creative-review-status");
    els.exportReview = panel.querySelector("#export-review-pack");
    els.importReview = panel.querySelector("#import-creative-directive");
    els.directiveFile = panel.querySelector("#creative-directive-file");
  }

  installCreativeReviewPanel();

  // -----------------------------------------------------------
  // Draft & Form Autosave
  // -----------------------------------------------------------
  function loadDraft() {
    try {
      const raw = localStorage.getItem(DRAFT_KEY);
      return raw ? JSON.parse(raw) : {};
    } catch { return {}; }
  }

  function saveDraft() {
    try {
      const draft = {
        prompt: els.prompt.value,
        brandName: els.brandName?.value || "",
        brandPersonality: els.brandPersonality?.value || "",
        brandAvoid: els.brandAvoid?.value || "",
        tokensJson: els.tokensJson?.value || "",
        autoInspiration: Boolean(els.autoInspiration?.checked),
        inspirationTarget: Number(els.inspirationTarget?.value || 2),
        refUrls: Array.from(document.querySelectorAll(".ref-row input")).map(i => i.value),
        savedAt: Date.now(),
      };
      localStorage.setItem(DRAFT_KEY, JSON.stringify(draft));
    } catch {}
  }

  function applyDraft() {
    const d = loadDraft();
    if (!d || Object.keys(d).length === 0) return;
    if (els.prompt) els.prompt.value = d.prompt || "";
    if (els.brandName) els.brandName.value = d.brandName || "";
    if (els.brandPersonality) els.brandPersonality.value = d.brandPersonality || "";
    if (els.brandAvoid) els.brandAvoid.value = d.brandAvoid || "";
    if (els.tokensJson) els.tokensJson.value = d.tokensJson || "";
    if (els.autoInspiration && typeof d.autoInspiration === "boolean") {
      els.autoInspiration.checked = d.autoInspiration;
    }
    if (els.inspirationTarget && [1, 2].includes(Number(d.inspirationTarget))) {
      els.inspirationTarget.value = String(d.inspirationTarget);
    }
    (d.refUrls || []).forEach(u => addRefRow(u));
    updateCounter();
  }

  function appendJobHistory(jobId, status) {
    try {
      const list = JSON.parse(localStorage.getItem(JOB_HISTORY_KEY) || "[]");
      const item = { id: jobId, status, at: Date.now() };
      const idx = list.findIndex(j => j.id === jobId);
      if (idx >= 0) list[idx] = item; else list.unshift(item);
      localStorage.setItem(JOB_HISTORY_KEY, JSON.stringify(list.slice(0, 15)));
    } catch {}
  }

  // -----------------------------------------------------------
  // Smart Routing Live Preview
  // -----------------------------------------------------------
  function updateSmartPreview() {
    const goal = (els.prompt ? els.prompt.value : "").trim();
    if (!goal) {
      els.smartDomain.textContent = "—";
      els.smartDomainReason.textContent = "Nhập prompt để suy luận…";
      els.smartClarity.textContent = "—";
      els.smartClarityTips.textContent = "Đợi prompt…";
      els.smartSkillCount.textContent = "—";
      els.smartSkillMeta.textContent = "37+ skills sẵn sàng trong hệ thống";
      els.stagePlan.innerHTML = '<li class="muted">Nhập brief để hệ thống lập kế hoạch quy trình…</li>';
      return;
    }

    const plan = UiuxRouter.plan(goal);
    const domainLabel = {
      ecommerce: "Ecommerce / Bán lẻ",
      corporate: "Corporate / B2B",
      education: "Education / Học viện",
      agency: "Agency / Studio Sáng tạo",
    }[plan.domain] || plan.domain;

    els.smartDomain.textContent = domainLabel;
    els.smartDomainReason.textContent = plan.domainScore
      ? `Phát hiện ${plan.domainScore} tín hiệu ngành chuyên biệt trong prompt`
      : "Mặc định chuẩn Corporate / B2B hiện đại";
    els.smartClarity.textContent = `${plan.clarity} / 6`;
    const tips = UiuxRouter.clarityTips(goal);
    els.smartClarityTips.innerHTML = tips.map(t => `• ${escapeHtml(t)}`).join("<br/>");
    els.smartSkillCount.textContent = `${plan.totalSkills}`;
    els.smartSkillMeta.textContent = `trong 10 bước · ${plan.domainSkills.length} skill chuyên biệt ngành`;

    els.stagePlan.innerHTML = plan.stages.map(s => {
      const lbl = UiuxRouter.stageLabel(s.stage);
      const skillsText = s.skills.map(k => k.path.replace("/SKILL.md", "")).join(", ");
      const domainCls = s.applyDomain ? " is-domain" : "";
      const dot = s.applyDomain ? `<span style="color:var(--accent);font-weight:700;">●</span> ` : "";
      return `<li class="${domainCls}">
        <div class="stage-name">${escapeHtml(s.stage)}</div>
        <div><strong>${dot}${escapeHtml(lbl)}</strong><div class="skill-paths">${escapeHtml(skillsText) || '<em>—</em>'}</div></div>
      </li>`;
    }).join("");
  }

  function escapeHtml(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }

  // -----------------------------------------------------------
  // Reference URL inputs
  // -----------------------------------------------------------
  function addRefRow(value = "") {
    if (!els.refUrls) return;
    const row = document.createElement("div");
    row.className = "ref-row";
    const input = document.createElement("input");
    input.type = "url";
    input.placeholder = "https://dribbble.com/shots/... hoặc https://site.com";
    input.value = value;
    input.setAttribute("aria-label", "Reference URL");
    input.addEventListener("input", saveDraft);
    const btn = document.createElement("button");
    btn.type = "button";
    btn.textContent = "×";
    btn.title = "Xoá URL";
    btn.setAttribute("aria-label", "Xoá reference URL");
    btn.addEventListener("click", () => { row.remove(); saveDraft(); });
    row.append(input, btn);
    els.refUrls.appendChild(row);
  }

  if (els.addRef) {
    els.addRef.addEventListener("click", () => { addRefRow(); saveDraft(); });
  }

  // -----------------------------------------------------------
  // Inputs & Counter
  // -----------------------------------------------------------
  function updateCounter() {
    if (!els.prompt || !els.counter) return;
    const len = els.prompt.value.length;
    els.counter.textContent = `${len.toLocaleString("vi-VN")} ký tự`;
  }
  if (els.prompt) {
    els.prompt.addEventListener("input", () => {
      updateCounter();
      updateSmartPreview();
      saveDraft();
    });
  }

  if (els.clearBtn) {
    els.clearBtn.addEventListener("click", () => {
      if (!confirm("Xoá toàn bộ bản nháp và form?")) return;
      if (els.prompt) els.prompt.value = "";
      if (els.brandName) els.brandName.value = "";
      if (els.brandPersonality) els.brandPersonality.value = "";
      if (els.brandAvoid) els.brandAvoid.value = "";
      if (els.tokensJson) els.tokensJson.value = "";
      if (els.refUrls) els.refUrls.innerHTML = "";
      localStorage.removeItem(DRAFT_KEY);
      updateCounter();
      updateSmartPreview();
    });
  }
  ["brandName", "brandPersonality", "brandAvoid", "tokensJson"].forEach(k => {
    els[k]?.addEventListener?.("input", saveDraft);
  });
  els.autoInspiration?.addEventListener("change", saveDraft);
  els.inspirationTarget?.addEventListener("change", saveDraft);

  if (els.chips) {
    els.chips.forEach(c => c.addEventListener("click", () => {
      els.prompt.value = c.dataset.prompt || "";
      updateCounter();
      updateSmartPreview();
      saveDraft();
      els.prompt.focus();
    }));
  }

  // -----------------------------------------------------------
  // Bridge Health
  // -----------------------------------------------------------
  async function checkHealth() {
    try {
      const res = await fetch(`${BRIDGE}/health`, { cache: "no-store" });
      if (!res.ok) throw new Error(res.status);
      const data = await res.json();
      const aiOk = data.ai && data.ai.configured;
      els.bridgeStatus.dataset.state = "ok";
      els.bridgeStatus.querySelector(".status-text").textContent =
        `Bridge sẵn sàng · ${data.creative_review?.stage_aware_revision ? "Creative Review ready" : "Python OK"}`;
      els.bridgeInfo.textContent = new URL(BRIDGE, location.origin).host;
      els.bridgeStatus.querySelector(".status-text").textContent =
        `Bridge sẵn sàng · ${data.creative_review?.stage_aware_revision ? "Creative Review ready" : "Python OK"}`;
      els.bridgeInfo.textContent = new URL(BRIDGE, location.origin).host;

      const aiRadio = document.querySelector('input[name="engine"][value="ai"]');
      const wrap = document.getElementById("ai-radio-wrap");
      if (!aiOk) {
        if (aiRadio) aiRadio.disabled = true;
        if (wrap) wrap.classList.add("disabled");
        if (els.aiStatus) els.aiStatus.innerHTML = "Chưa cấu hình API Key trong <code>.env.local</code> — sử dụng Deterministic Engine.";
      } else {
        if (aiRadio) aiRadio.disabled = false;
        if (wrap) wrap.classList.remove("disabled");
        if (els.aiStatus) els.aiStatus.textContent = `AI sẵn sàng · Nhà cung cấp: ${data.ai.providers.join(", ")}`;
      }
    } catch (e) {
      els.bridgeStatus.dataset.state = "bad";
      els.bridgeStatus.querySelector(".status-text").textContent =
        "Không kết nối được bridge (port 8788).";
      if (els.submitBtn) els.submitBtn.disabled = true;
    }
  }

  // -----------------------------------------------------------
  // Submit Job
  // -----------------------------------------------------------
  function buildDesignContext() {
    const ctx = {};
    const brandName = els.brandName?.value?.trim?.();
    if (brandName) ctx.brand_name = brandName;
    const personality = els.brandPersonality?.value?.trim?.();
    if (personality) {
      ctx.personality = personality.split(/[,\n;]+/).map(s => s.trim()).filter(Boolean);
    }
    const avoid = els.brandAvoid?.value?.trim?.();
    if (avoid) ctx.avoid = avoid.split(/[,\n;]+/).map(s => s.trim()).filter(Boolean);
    const tokensRaw = els.tokensJson?.value?.trim?.();
    if (avoid) ctx.avoid = avoid.split(/[,\n;]+/).map(s => s.trim()).filter(Boolean);
    const tokensRaw = els.tokensJson?.value?.trim?.();
    if (tokensRaw) {
      try { ctx.tokens = JSON.parse(tokensRaw); } catch {}
    }
    const urls = Array.from(document.querySelectorAll(".ref-row input"))
      .map(i => i.value.trim()).filter(Boolean);
    if (urls.length) ctx.reference_urls = urls.slice(0, 4);
    ctx.auto_inspiration = Boolean(els.autoInspiration?.checked);
    ctx.inspiration_target = Math.max(0, Math.min(2, Number(els.inspirationTarget?.value || 2)));
    return ctx;
  }

  if (els.form) {
    els.form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const prompt = els.prompt.value.trim();
      if (!prompt) {
        alert("Vui lòng nhập mục tiêu dự án.");
        els.prompt.focus();
        return;
      }
      const engine = document.querySelector('input[name="engine"]:checked')?.value || "template";
      const designContext = buildDesignContext();

      els.submitBtn.disabled = true;
      els.submitBtn.querySelector(".btn-label").textContent = "Đang khởi động studio…";

      try {
        const res = await fetch(`${BRIDGE}/run`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ prompt, engine, design_context: designContext }),
        });
        if (!res.ok) {
          const err = await res.json().catch(() => ({ error: `HTTP ${res.status}` }));
          throw new Error(err.error || `HTTP ${res.status}`);
        }
        const job = await res.json();
        openJob(job);
        appendJobHistory(job.id, "queued");
      } catch (err) {
        alert("Không thể chạy job: " + err.message);
      } finally {
        els.submitBtn.disabled = false;
        els.submitBtn.querySelector(".btn-label").textContent = "Bắt đầu Pipeline Thiết kế";
      }
    });
  }

  // -----------------------------------------------------------
  // Job Tracker & Timeline
  // -----------------------------------------------------------
  let pollTimer = null;
  let lastLogTail = "";
  let currentJobId = null;
  let currentProjectSlug = null;
  let pollDelay = 1200;

  const PIPELINE_STAGES = [
    "research", "ux_ia", "art_direction", "design_contract", "design_system",
    "implementation_plan", "visual_composition", "implementation", "browser_qa", "visual_qa", "repair"
  ];

  function setCreativeReviewVisible(visible, message = "") {
    if (!els.reviewPanel) return;
    els.reviewPanel.hidden = !visible;
    if (message && els.reviewStatus) els.reviewStatus.textContent = message;
  }

  function openJob(job) {
    currentJobId = job.id;
    lastLogTail = "";
    if (els.jobEmpty) els.jobEmpty.classList.add("hidden");
    if (els.jobCard) els.jobCard.classList.remove("hidden");
    if (els.jobId) els.jobId.textContent = job.id;
    if (els.jobPrompt) els.jobPrompt.textContent = job.prompt;
    setJobStatus(job.status);
    renderTimeline([], job.status === "queued" ? null : "research");
    updateProgressBar(0);
    if (els.artifacts) els.artifacts.setAttribute("hidden", "");
    if (els.artifactList) els.artifactList.innerHTML = "";
    if (els.logsWrap) els.logsWrap.setAttribute("hidden", "");
    if (els.logs) els.logs.textContent = "";
    if (els.previewWrap) els.previewWrap.setAttribute("hidden", "");
    setCreativeReviewVisible(false);
    currentProjectSlug = null;
    startPolling();
  }

  function setJobStatus(status) {
  function setJobStatus(status) {
    if (!els.jobStatus) return;
    const s = status || "queued";
    els.jobStatus.textContent = s;
    els.jobStatus.dataset.status = s;
  }

  function updateProgressBar(percent) {
    if (els.progressFill) {
      els.progressFill.style.width = `${Math.min(100, Math.max(0, percent))}%`;
    }
  }

  function makeTimelineHtml(stages, status) {
    const doneSet = new Set((stages || []).filter(s => s !== "repair"));
    const totalCount = PIPELINE_STAGES.length - 1; // repair is conditional
    const progressPercent = Math.round((doneSet.size / totalCount) * 100);
    updateProgressBar(status === "completed" ? 100 : progressPercent);

    return PIPELINE_STAGES.map((k, i) => {
      const label = UiuxRouter.stageLabel(k);

      const isDone = doneSet.has(k);
      const isActive = (i === doneSet.size) && status === "running";
      const isFailed = status === "failed" && i === doneSet.size;
      let icon, state;
      if (isFailed) { icon = "✕"; state = "failed"; }
      else if (isDone) { icon = "✓"; state = "done"; }
      else if (isActive) { icon = "◐"; state = "active"; }
      else { icon = "○"; state = "todo"; }
      return `<li data-state="${state}">
        <span class="icon">${icon}</span>
        <span class="name"><strong>${escapeHtml(k)}</strong> — ${escapeHtml(label)}</span>
        <span class="meta">${escapeHtml(state)}</span>
      </li>`;
    }).join("");
  }

  function renderTimeline(stages, status) {
    if (els.stageTimeline) {
      els.stageTimeline.innerHTML = makeTimelineHtml(stages, status);
    }
  }

  async function pollOnce() {
    if (!currentJobId) return;
    try {
      const res = await fetch(`${BRIDGE}/jobs/${currentJobId}`, { cache: "no-store" });
      if (!res.ok) {
        if (res.status === 404) { stopPolling(); return; }
        throw new Error(`HTTP ${res.status}`);
      }
      const job = await res.json();
      setJobStatus(job.status);
      renderTimeline(job.completed_stages || [], job.status);

      if (job.output_tail && job.output_tail !== lastLogTail) {
        lastLogTail = job.output_tail;
        if (els.logs) {
          els.logs.textContent = job.output_tail;
          if (els.logsWrap) els.logsWrap.removeAttribute("hidden");
          els.logs.scrollTop = els.logs.scrollHeight;
        }
      }
      if (job.artifacts && job.artifacts.length) {
        renderArtifacts(job.artifacts);
      }

      if (job.status === "completed" || job.status === "failed") {
        if (job.project_slug) {
          currentProjectSlug = job.project_slug;
          renderPreview(currentProjectSlug);
        }
        appendJobHistory(currentJobId, job.status);
        stopPolling();
        if (job.status === "failed") {
        if (job.status === "failed") {
          if (els.logs) {
            els.logs.textContent += `\n\n[JOB FAILED]\n${job.error || "Unknown failure"}`;
          }
          els.jobStatus.title = (job.error || "").toString();
        } else if (job.creative_review_ready) {
          setCreativeReviewVisible(
            true,
            job.mode === "creative_revision"
              ? "Revision đã PASS QA. Có thể export pack mới để mình review vòng tiếp theo."
              : "Export pack này và gửi vào chat với mình; sau đó import creative-directive.json để sửa đúng stage."
          );
        }
        }
      }
    } catch (err) {
      console.warn("Poll status check:", err);
    }
  }

  const ARTIFACT_ALLOWLIST = new Set([
    "design-contract.json", "design-system.json", "implementation-plan.json",
    "visual-composition.json", "visual-brain.json", "reference-dna.json",
    "DESIGN.md", "tokens.css", "quality-loop.json", "browser-report.json",
    "creative-directive.json", "creative-revision.json",
  ]);

  function renderArtifacts(names) {
    if (!els.artifacts || !els.artifactList) return;
    els.artifacts.removeAttribute("hidden");
    els.artifactList.innerHTML = names.map(n => {
    if (!els.artifacts || !els.artifactList) return;
    els.artifacts.removeAttribute("hidden");
    els.artifactList.innerHTML = names.map(n => {
      if (!ARTIFACT_ALLOWLIST.has(n) && !/^references\/reference-[a-f0-9]{12}-(desktop|mobile)\.png$/.test(n)) return "";
      const label = n.includes("/") ? n.split("/").pop() : n;
      return `<button type="button" class="artifact-item" data-name="${escapeHtml(n)}">${escapeHtml(label)}</button>`;
    }).join("");
      const label = n.includes("/") ? n.split("/").pop() : n;
      return `<button type="button" class="artifact-item" data-name="${escapeHtml(n)}">${escapeHtml(label)}</button>`;
    }).join("");

    els.artifactList.querySelectorAll(".artifact-item").forEach(btn => {
      btn.addEventListener("click", () => viewArtifact(btn.dataset.name));
    });
  }

  async function viewArtifact(name) {
    if (!currentJobId) return;
    const url = `${BRIDGE}/jobs/${currentJobId}/artifacts/${name}`;
    try {
      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const ct = res.headers.get("Content-Type") || "";
      if (ct.includes("image/")) {
        window.open(url, "_blank");
      } else {
        const text = await res.text();
        const kind = name.endsWith(".md") ? "markdown" : (name.endsWith(".css") ? "css" : "json");
        openArtifactModal(name, text, kind, url);
      }
      }
    } catch (err) {
      alert("Không tải được artifact: " + err.message);
    }
  }

  // -----------------------------------------------------------
  // Inline Artifact Viewer Modal
  // -----------------------------------------------------------
  function openArtifactModal(filename, text, kind, rawUrl) {
    if (!els.artifactModal) return;
    els.modalFilename.textContent = filename;
    els.modalOpenRaw.href = rawUrl;

    if (kind === "markdown") {
      els.modalContent.innerHTML = `<div class="md-rendered">${renderMarkdownSimple(text)}</div>`;
    } else {
      els.modalContent.innerHTML = `<pre><code>${escapeHtml(text)}</code></pre>`;
    }
    els.artifactModal.removeAttribute("hidden");
  }

  function closeArtifactModal() {
    if (els.artifactModal) {
      els.artifactModal.setAttribute("hidden", "");
    }
  }

  if (els.modalCloseBtn) {
    els.modalCloseBtn.addEventListener("click", closeArtifactModal);
  }
  if (els.artifactModal) {
    els.artifactModal.addEventListener("click", (e) => {
      if (e.target === els.artifactModal) closeArtifactModal();
    });
  }
  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && els.artifactModal && !els.artifactModal.hasAttribute("hidden")) {
      closeArtifactModal();
    }
  });

  function renderMarkdownSimple(md) {
    return md
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/^### (.+)$/gm, "<h3>$1</h3>")
      .replace(/^## (.+)$/gm, "<h2>$1</h2>")
      .replace(/^# (.+)$/gm, "<h1>$1</h1>")
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
      .replace(/\*([^*]+)\*/g, "<em>$1</em>")
      .replace(/\n\n/g, "</p><p>")
      .replace(/^/, "<p>").replace(/$/, "</p>");
  }

  // -----------------------------------------------------------
  // Preview
  // -----------------------------------------------------------
  function renderPreview(slug) {
    if (!slug) return;
  function renderPreview(slug) {
    if (!slug) return;
    const url = `${BRIDGE}/preview/${slug}/`;
    if (els.previewWrap) els.previewWrap.removeAttribute("hidden");
    if (els.previewLink) els.previewLink.href = url;
    if (els.previewFrame) els.previewFrame.src = url;
    if (els.chromeUrl) els.chromeUrl.textContent = url;
  }

  if (els.refreshPreview) {
    els.refreshPreview.addEventListener("click", () => {
      if (currentProjectSlug) {
        const url = `${BRIDGE}/preview/${currentProjectSlug}/?t=${Date.now()}`;
        if (els.previewFrame) els.previewFrame.src = url;
      }
    });
  }

  async function exportReviewPack() {
    if (!currentJobId || !els.exportReview) return;
    const button = els.exportReview;
    const previous = button.textContent;
    button.disabled = true;
    button.textContent = "Đang đóng gói…";
    try {
      const res = await fetch(`${BRIDGE}/jobs/${currentJobId}/review-pack`, { cache: "no-store" });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ error: `HTTP ${res.status}` }));
        throw new Error(err.error || `HTTP ${res.status}`);
      }
      const blob = await res.blob();
      const href = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = href;
      anchor.download = `uiux-review-pack-${currentJobId}.zip`;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(href);
      els.reviewStatus.textContent = "Review Pack đã xuất. Gửi ZIP này vào chat với mình để review visual thật.";
    } catch (err) {
      els.reviewStatus.textContent = `Không export được: ${err.message}`;
    } finally {
      button.disabled = false;
      button.textContent = previous;
    }
  }

  async function importCreativeDirective(file) {
    if (!file || !currentJobId) return;
    try {
      const text = await file.text();
      const directive = JSON.parse(text);
      if (directive.source_run_id !== currentJobId) {
        throw new Error(`Directive dành cho run ${directive.source_run_id || "không xác định"}, không phải ${currentJobId}.`);
      }
      if (directive.status === "approved") {
        els.reviewStatus.textContent = "Creative Director đã APPROVE — không cần rebuild.";
        return;
      }
      if (!Array.isArray(directive.revise) || directive.revise.length === 0) {
        throw new Error("Directive revise nhưng không có hạng mục REVISE.");
      }

      els.importReview.disabled = true;
      els.reviewStatus.textContent = "Đang route creative review về đúng owner stage…";
      const res = await fetch(`${BRIDGE}/jobs/${currentJobId}/creative-directive`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(directive),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ error: `HTTP ${res.status}` }));
        throw new Error(err.error || `HTTP ${res.status}`);
      }
      const revisionJob = await res.json();
      appendJobHistory(revisionJob.id, "queued");
      openJob(revisionJob);
    } catch (err) {
      els.reviewStatus.textContent = `Creative Directive không hợp lệ: ${err.message}`;
    } finally {
      els.importReview.disabled = false;
      els.directiveFile.value = "";
    }
  }

  els.exportReview?.addEventListener("click", exportReviewPack);
  els.importReview?.addEventListener("click", () => els.directiveFile?.click());
  els.directiveFile?.addEventListener("change", () => importCreativeDirective(els.directiveFile.files?.[0]));

  function startPolling() {
    stopPolling();
    pollDelay = 1200;
    isPolling = true;
    const tick = async () => {
      if (!isPolling) return;
      await pollOnce();
      if (isPolling && currentJobId) {
        pollDelay = Math.min(pollDelay * 1.15, 5000);
      }
        pollTimer = setTimeout(tick, pollDelay);
      }
    };
    pollTimer = setTimeout(tick, 100);
  }

  function stopPolling() {
  function stopPolling() {
    isPolling = false;
    if (pollTimer) { clearTimeout(pollTimer); pollTimer = null; }
  }

  // -----------------------------------------------------------
  // Auto-resume Latest Job
  // -----------------------------------------------------------
  async function loadLatestJob() {
    try {
      const res = await fetch(`${BRIDGE}/latest`, { cache: "no-store" });
      if (!res.ok) return;
      const data = await res.json();
      if (data && data.run_id) {
        const job = {
          id: data.run_id,
          status: data.run.status || "queued",
          prompt: data.run.goal || "",
        };
        openJob(job);
      }
    } catch (err) {
      console.warn("Failed to load latest job:", err);
    }
  }

  // -----------------------------------------------------------
  // Initialization
  // -----------------------------------------------------------
  applyDraft();
  updateCounter();
  updateSmartPreview();
  checkHealth();
  setInterval(checkHealth, 25000);
  loadLatestJob();
})();
