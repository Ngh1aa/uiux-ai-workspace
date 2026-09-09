/* ============================================================
   app.js — UIUX Factory Workbench Console (client)
   - Auto-save drafts
   - Live smart routing (theo dõi prompt → kế hoạch 10 bước)
   - Submit → POST /run | /intelligence
   - Poll job + render stages, logs, artifacts, preview
   ============================================================ */

(() => {
  "use strict";

  // Mặc định dùng relative /api/ để qua console proxy → không cần CORS.
  // Đặt window.UIUX_BRIDGE_URL = "http://127.0.0.1:8788" nếu muốn gọi thẳng bridge.
  function detectApiBase() {
    if (window.UIUX_BRIDGE_URL) return window.UIUX_BRIDGE_URL.replace(/\/$/, "");
    // Nếu đang chạy qua console (cùng origin), dùng relative path.
    if (location.protocol === "http:" || location.protocol === "https:") {
      return "/api";
    }
    // file:// fallback gọi thẳng bridge; bridge không có tiền tố /api.
    return "http://127.0.0.1:8788";
  }
  const BRIDGE = detectApiBase();
  const DRAFT_KEY = "uiux-console-draft-v1";
  const JOB_HISTORY_KEY = "uiux-console-jobs-v1";

  const els = {
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
    jobEmpty: document.getElementById("job-empty"),
    jobCard: document.getElementById("job-card"),
    jobId: document.getElementById("job-id"),
    jobPrompt: document.getElementById("job-prompt"),
    jobStatus: document.getElementById("job-status-badge"),
    stageTimeline: document.getElementById("stage-timeline"),
    artifacts: document.getElementById("artifacts"),
    artifactList: document.getElementById("artifact-list"),
    logsWrap: document.getElementById("logs-wrap"),
    logs: document.getElementById("job-logs"),
    previewWrap: document.getElementById("preview-wrap"),
    previewFrame: document.getElementById("preview-frame"),
    refreshPreview: document.getElementById("refresh-preview-btn"),
    brandName: document.getElementById("brand-name"),
    brandPersonality: document.getElementById("brand-personality"),
    brandAvoid: document.getElementById("brand-avoid"),
    tokensJson: document.getElementById("tokens-json"),
  };

  // -----------------------------------------------------------
  // Draft + job history (localStorage)
  // -----------------------------------------------------------
  function loadDraft() {
    try {
      const raw = localStorage.getItem(DRAFT_KEY);
      if (!raw) return {};
      return JSON.parse(raw);
    } catch { return {}; }
  }

  function saveDraft() {
    try {
      const draft = {
        prompt: els.prompt.value,
        brandName: els.brandName.value,
        brandPersonality: els.brandPersonality.value,
        brandAvoid: els.brandAvoid.value,
        tokensJson: els.tokensJson.value,
        refUrls: Array.from(document.querySelectorAll(".ref-row input")).map(i => i.value),
        savedAt: Date.now(),
      };
      localStorage.setItem(DRAFT_KEY, JSON.stringify(draft));
    } catch {}
  }

  function applyDraft() {
    const d = loadDraft();
    if (!d || Object.keys(d).length === 0) return;
    els.prompt.value = d.prompt || "";
    els.brandName.value = d.brandName || "";
    els.brandPersonality.value = d.brandPersonality || "";
    els.brandAvoid.value = d.brandAvoid || "";
    els.tokensJson.value = d.tokensJson || "";
    (d.refUrls || []).forEach(u => addRefRow(u));
    updateCounter();
  }

  function appendJobHistory(jobId, status) {
    try {
      const list = JSON.parse(localStorage.getItem(JOB_HISTORY_KEY) || "[]");
      const item = { id: jobId, status, at: Date.now() };
      const idx = list.findIndex(j => j.id === jobId);
      if (idx >= 0) list[idx] = item; else list.unshift(item);
      localStorage.setItem(JOB_HISTORY_KEY, JSON.stringify(list.slice(0, 10)));
    } catch {}
  }

  // -----------------------------------------------------------
  // Smart routing preview (live)
  // -----------------------------------------------------------
  function updateSmartPreview() {
    const goal = els.prompt.value.trim();
    if (!goal) {
      els.smartDomain.textContent = "—";
      els.smartDomainReason.textContent = "Đợi prompt…";
      els.smartClarity.textContent = "—";
      els.smartClarityTips.textContent = "Đợi prompt…";
      els.smartSkillCount.textContent = "—";
      els.smartSkillMeta.textContent = "Đợi prompt…";
      els.stagePlan.innerHTML = '<li class="muted">Đợi prompt để hệ thống lên kế hoạch…</li>';
      return;
    }
    const plan = UiuxRouter.plan(goal);
    const domainLabel = {
      ecommerce: "Ecommerce",
      corporate: "Corporate / B2B",
      education: "Education",
      agency: "Agency / Studio",
    }[plan.domain] || plan.domain;
    els.smartDomain.textContent = domainLabel;
    els.smartDomainReason.textContent = plan.domainScore
      ? `Phát hiện ${plan.domainScore} tín hiệu ngành trong prompt`
      : "Không phát hiện tín hiệu rõ — mặc định corporate";
    els.smartClarity.textContent = `${plan.clarity} / 6`;
    const tips = UiuxRouter.clarityTips(goal);
    els.smartClarityTips.innerHTML = tips.map(t => `• ${escapeHtml(t)}`).join("<br/>");
    els.smartSkillCount.textContent = `${plan.totalSkills}`;
    els.smartSkillMeta.textContent = `trong ${plan.stages.length} bước · ${plan.domainSkills.length} skill domain`;
    els.stagePlan.innerHTML = plan.stages.map(s => {
      const lbl = UiuxRouter.stageLabel(s.stage);
      const skillsText = s.skills.map(k => k.path.replace("/SKILL.md", "")).join(", ");
      const domainCls = s.applyDomain ? " is-domain" : "";
      const dot = s.applyDomain ? `<span style="color:var(--accent);font-weight:700;">●</span> ` : "";
      return `<li class="${domainCls}">
        <div class="stage-name">${escapeHtml(s.stage)}</div>
        <div>
          <strong>${dot}${escapeHtml(lbl)}</strong>
          <div class="skill-paths">${escapeHtml(skillsText) || '<em>—</em>'}</div>
        </div>
      </li>`;
    }).join("");
  }

  function escapeHtml(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }

  // -----------------------------------------------------------
  // Reference URL rows
  // -----------------------------------------------------------
  function addRefRow(value = "") {
    const row = document.createElement("div");
    row.className = "ref-row";
    const input = document.createElement("input");
    input.type = "url";
    input.placeholder = "https://example.com";
    input.value = value;
    input.addEventListener("input", saveDraft);
    const btn = document.createElement("button");
    btn.type = "button";
    btn.textContent = "×";
    btn.title = "Xoá";
    btn.addEventListener("click", () => { row.remove(); saveDraft(); });
    row.append(input, btn);
    els.refUrls.appendChild(row);
  }

  els.addRef.addEventListener("click", () => { addRefRow(); saveDraft(); });

  // -----------------------------------------------------------
  // Counter + autosave
  // -----------------------------------------------------------
  function updateCounter() {
    const len = els.prompt.value.length;
    els.counter.textContent = `${len.toLocaleString("vi-VN")} ký tự`;
  }
  els.prompt.addEventListener("input", () => {
    updateCounter();
    updateSmartPreview();
    saveDraft();
  });
  els.clearBtn.addEventListener("click", () => {
    if (!confirm("Xoá toàn bộ bản nháp và form?")) return;
    els.prompt.value = "";
    els.brandName.value = "";
    els.brandPersonality.value = "";
    els.brandAvoid.value = "";
    els.tokensJson.value = "";
    els.refUrls.innerHTML = "";
    localStorage.removeItem(DRAFT_KEY);
    updateCounter();
    updateSmartPreview();
  });

  ["brandName","brandPersonality","brandAvoid","tokensJson"].forEach(k => {
    els[k]?.addEventListener?.("input", saveDraft);
  });

  els.chips.forEach(c => c.addEventListener("click", () => {
    els.prompt.value = c.dataset.prompt || "";
    updateCounter();
    updateSmartPreview();
    saveDraft();
    els.prompt.focus();
  }));

  // -----------------------------------------------------------
  // Bridge health
  // -----------------------------------------------------------
  async function checkHealth() {
    try {
      const res = await fetch(`${BRIDGE}/health`, { cache: "no-store" });
      if (!res.ok) throw new Error(res.status);
      const data = await res.json();
      const aiOk = data.ai && data.ai.configured;
      els.bridgeStatus.dataset.state = "ok";
      els.bridgeStatus.querySelector(".status-text").textContent =
        `Bridge sẵn sàng · ${data.python ? "Python OK" : "OK"}`;
      els.bridgeInfo.textContent = new URL(BRIDGE, location.origin).host;
      const radios = document.querySelectorAll('input[name="engine"]');
      if (!aiOk) {
        const aiRadio = document.querySelector('input[name="engine"][value="ai"]');
        const wrap = document.getElementById("ai-radio-wrap");
        aiRadio.disabled = true;
        wrap.classList.add("disabled");
        els.aiStatus.textContent = "Chưa cấu hình Groq/Gemini trong .env.local — chỉ dùng engine template.";
      } else {
        els.aiStatus.textContent = `AI sẵn sàng · ${data.ai.providers.join(", ")}`;
      }
    } catch (e) {
      els.bridgeStatus.dataset.state = "bad";
      els.bridgeStatus.querySelector(".status-text").textContent =
        "Không kết nối được bridge. Hãy chạy apps/bridge/server.py trước.";
      els.submitBtn.disabled = true;
    }
  }

  // -----------------------------------------------------------
  // Submit → POST /run or /intelligence
  // -----------------------------------------------------------
  function buildDesignContext() {
    const ctx = {};
    const brandName = els.brandName.value.trim();
    if (brandName) ctx.brand_name = brandName;
    const personality = els.brandPersonality.value.trim();
    if (personality) {
      ctx.personality = personality.split(/[,\n;]+/).map(s => s.trim()).filter(Boolean);
    }
    const avoid = els.brandAvoid.value.trim();
    if (avoid) ctx.avoid = avoid.split(/[,\n;]+/).map(s => s.trim()).filter(Boolean);
    const tokensRaw = els.tokensJson.value.trim();
    if (tokensRaw) {
      try { ctx.tokens = JSON.parse(tokensRaw); }
      catch { /* ignore — không phải json hợp lệ */ }
    }
    const urls = Array.from(document.querySelectorAll(".ref-row input"))
      .map(i => i.value.trim()).filter(Boolean);
    if (urls.length) ctx.reference_urls = urls.slice(0, 4);
    return ctx;
  }

  els.form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const prompt = els.prompt.value.trim();
    if (!prompt) { alert("Vui lòng nhập prompt."); els.prompt.focus(); return; }
    const engine = document.querySelector('input[name="engine"]:checked').value;
    const mode = "build";

    const designContext = buildDesignContext();
    const endpoint = mode === "intelligence" ? "/intelligence" : "/run";

    els.submitBtn.disabled = true;
    els.submitBtn.querySelector(".btn-label").textContent = "Đang khởi tạo job…";

    try {
      const res = await fetch(`${BRIDGE}${endpoint}`, {
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
      alert("Không submit được: " + err.message);
    } finally {
      els.submitBtn.disabled = false;
      els.submitBtn.querySelector(".btn-label").textContent = "Chạy pipeline";
    }
  });

  // -----------------------------------------------------------
  // Job tracker (poll /jobs/<id>)
  // -----------------------------------------------------------
  let pollTimer = null;
  let lastLogTail = "";
  let currentJobId = null;
  let currentProjectSlug = null;
  let pollDelay = 1500;

  function openJob(job) {
    currentJobId = job.id;
    lastLogTail = "";
    els.jobEmpty.classList.add("hidden");
    els.jobCard.classList.remove("hidden");
    els.jobId.textContent = job.id;
    els.jobPrompt.textContent = job.prompt;
    setJobStatus(job.status);
    renderTimeline([], job.status === "queued" ? null : "research");
    els.stageTimeline.innerHTML = makeTimelineHtml([], job.status);
    els.artifacts.setAttribute("hidden", "");
    els.artifactList.innerHTML = "";
    els.logsWrap.setAttribute("hidden", "");
    els.logs.textContent = "";
    els.previewWrap.setAttribute("hidden", "");
    currentProjectSlug = null;
    startPolling();
  }

  function setJobStatus(status) {
    const b = els.jobStatus;
    b.textContent = status || "queued";
    b.dataset.status = status || "queued";
  }

  function makeTimelineHtml(stages, status) {
    const known = ["research","ux_ia","art_direction","design_contract","design_system","implementation_plan","visual_composition","implementation","browser_qa","visual_qa","repair"];
    const doneSet = new Set((stages || []).filter(s => s !== "repair"));
    const labels = known.map(k => UiuxRouter.stageLabel(k));
    let html = "";
    for (let i = 0; i < known.length; i++) {
      const k = known[i];
      const label = labels[i];
      const isDone = doneSet.has(k);
      const isActive = (i === doneSet.size) && status === "running";
      const isFailed = status === "failed" && i === doneSet.size;
      let icon, state;
      if (isFailed) { icon = "✕"; state = "failed"; }
      else if (isDone) { icon = "✓"; state = "done"; }
      else if (isActive) { icon = "◐"; state = "active"; }
      else { icon = "○"; state = "todo"; }
      html += `<li data-state="${state}">
        <span class="icon">${icon}</span>
        <span class="name">${escapeHtml(k)} — ${escapeHtml(label)}</span>
        <span class="meta">${escapeHtml(state)}</span>
      </li>`;
    }
    return html;
  }

  function renderTimeline(stages, status) {
    els.stageTimeline.innerHTML = makeTimelineHtml(stages, status);
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
        els.logs.textContent = job.output_tail;
        els.logsWrap.removeAttribute("hidden");
        els.logs.scrollTop = els.logs.scrollHeight;
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
          els.jobStatus.title = (job.error || "").toString();
          els.logs.textContent += `\n\n[FAILED]\n${job.error || ""}`;
        }
      }
    } catch (err) {
      console.warn("poll error", err);
    }
  }

  function renderArtifacts(names) {
    els.artifacts.removeAttribute("hidden");
    els.artifactList.innerHTML = names.map(n => {
      const allowed = ["design-system.json","reference-dna.json","DESIGN.md","tokens.css","quality-loop.json","browser-report.json"];
      if (!allowed.includes(n) && !/^references\/reference-[a-f0-9]{12}-(desktop|mobile)\.png$/.test(n)) return "";
      const label = n.includes("/") ? n.split("/").pop() : n;
      return `<button class="artifact-item" data-name="${escapeHtml(n)}">${escapeHtml(label)}</button>`;
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
      } else if (name.endsWith(".md")) {
        const text = await res.text();
        showArtifactModal(name, text, "markdown");
      } else if (name.endsWith(".css")) {
        const text = await res.text();
        showArtifactModal(name, text, "css");
      } else {
        const text = await res.text();
        showArtifactModal(name, text, "json");
      }
    } catch (err) {
      alert("Không đọc được artifact: " + err.message);
    }
  }

  function showArtifactModal(name, text, kind) {
    const win = window.open("", "_blank", "width=900,height=700");
    if (!win) { alert("Trình duyệt chặn popup — vui lòng cho phép."); return; }
    const style = `
      <style>
        body{margin:0;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;background:#fafafa;color:#0a0a0a;}
        header{padding:14px 20px;border-bottom:1px solid #e5e5e7;background:white;display:flex;justify-content:space-between;align-items:center;}
        h1{font-size:14px;margin:0;font-family:monospace;color:#71717a;}
        main{padding:20px;}
        pre{background:#0a0a0a;color:#e4e4e7;padding:18px;border-radius:8px;font-size:12px;white-space:pre-wrap;word-break:break-word;line-height:1.6;}
        .md{background:white;padding:20px;border:1px solid #e5e5e7;border-radius:8px;font-size:14px;line-height:1.6;}
        .md h1,.md h2,.md h3{margin-top:1.4em;font-family:inherit;}
      </style>`;
    const bodyHtml = kind === "markdown" ? `<div class="md">${mdToHtml(text)}</div>` : `<pre>${escapeHtml(text)}</pre>`;
    win.document.write(`<!doctype html><html><head><meta charset="utf-8"/><title>${escapeHtml(name)}</title>${style}</head><body><header><h1>${escapeHtml(name)}</h1><a href="${BRIDGE}/jobs/${currentJobId}/artifacts/${name}" target="_blank">Mở gốc ↗</a></header><main>${bodyHtml}</main></body></html>`);
    win.document.close();
  }

  function mdToHtml(md) {
    return md
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/^### (.+)$/gm, "<h3>$1</h3>")
      .replace(/^## (.+)$/gm, "<h2>$1</h2>")
      .replace(/^# (.+)$/gm, "<h1>$1</h1>")
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
      .replace(/\n\n/g, "</p><p>")
      .replace(/^/, "<p>").replace(/$/, "</p>");
  }

  function renderPreview(slug) {
    if (!slug) return;
    const url = `${BRIDGE}/preview/${slug}/`;
    els.previewWrap.removeAttribute("hidden");
    els.previewFrame.src = url;
  }

  els.refreshPreview.addEventListener("click", () => {
    if (currentProjectSlug) {
      const url = `${BRIDGE}/preview/${currentProjectSlug}/?t=${Date.now()}`;
      els.previewFrame.src = url;
    }
  });

  function startPolling() {
    stopPolling();
    pollDelay = 1500;
    const tick = async () => {
      await pollOnce();
      if (currentJobId) {
        pollDelay = Math.min(pollDelay * 1.2, 6000);
        pollTimer = setTimeout(tick, pollDelay);
      }
    };
    pollTimer = setTimeout(tick, 200);
  }
  function stopPolling() {
    if (pollTimer) { clearTimeout(pollTimer); pollTimer = null; }
  }

  // -----------------------------------------------------------
  // Init
  // -----------------------------------------------------------
  applyDraft();
  updateCounter();
  updateSmartPreview();
  checkHealth();
  setInterval(checkHealth, 30000);

})();