/* Runtime preset adapter for the Design Workbench.
 * Keeps runtime composition concerns outside the main app.js console controller.
 */
(() => {
  "use strict";

  const STORAGE_KEY = "uiux-runtime-preset-v1";
  const RUNTIME_ARTIFACTS = [
    "runtime-composition.json",
    "flow-plan.json",
    "events.jsonl",
  ];

  function detectApiBase() {
    if (window.UIUX_BRIDGE_URL) return window.UIUX_BRIDGE_URL.replace(/\/$/, "");
    if (location.protocol === "http:" || location.protocol === "https:") return "/api";
    return "http://127.0.0.1:8788";
  }

  const BRIDGE = detectApiBase();
  const nativeFetch = window.fetch.bind(window);
  const select = document.getElementById("runtime-preset");
  const help = document.getElementById("runtime-preset-help");
  let catalog = [];

  function currentPreset() {
    return select?.value || "standard";
  }

  function saveSelection() {
    try { localStorage.setItem(STORAGE_KEY, currentPreset()); } catch {}
  }

  function updateHelp() {
    if (!help) return;
    const selected = catalog.find(item => item.id === currentPreset());
    help.textContent = selected?.description
      || "Preset cố định capability, tools và skill overlays cho toàn bộ run.";
  }

  function renderCatalog(items) {
    if (!select || !Array.isArray(items) || items.length === 0) return;
    const saved = (() => {
      try { return localStorage.getItem(STORAGE_KEY); } catch { return null; }
    })();
    const previous = saved || select.value || "standard";
    catalog = items.filter(item => item && typeof item.id === "string");
    select.innerHTML = catalog.map(item => {
      const label = item.name || item.id;
      return `<option value="${escapeHtml(item.id)}">${escapeHtml(label)}</option>`;
    }).join("");
    select.value = catalog.some(item => item.id === previous) ? previous : "standard";
    saveSelection();
    updateHelp();
  }

  function escapeHtml(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  async function loadCatalog() {
    try {
      const response = await nativeFetch(`${BRIDGE}/health`, { cache: "no-store" });
      if (!response.ok) return;
      const payload = await response.json();
      renderCatalog(payload.runtime_presets || []);
    } catch {}
  }

  select?.addEventListener("change", () => {
    saveSelection();
    updateHelp();
  });

  // Compose the selected runtime into every new Workbench run without coupling
  // the large app.js controller to runtime internals.
  window.fetch = function runtimePresetFetch(input, init = {}) {
    const url = typeof input === "string" ? input : input?.url || "";
    const method = String(init?.method || (typeof input !== "string" ? input?.method : "GET") || "GET").toUpperCase();
    const isFactoryStart = method === "POST" && (
      url === `${BRIDGE}/run` || url === `${BRIDGE}/intelligence`
    );

    if (!isFactoryStart || typeof init.body !== "string") {
      return nativeFetch(input, init);
    }

    try {
      const payload = JSON.parse(init.body);
      if (payload && typeof payload === "object" && !Array.isArray(payload)) {
        payload.runtime_preset = currentPreset();
        return nativeFetch(input, { ...init, body: JSON.stringify(payload) });
      }
    } catch {}
    return nativeFetch(input, init);
  };

  function runtimeArtifactLink(jobId, name) {
    const anchor = document.createElement("a");
    anchor.className = "artifact-item runtime-artifact";
    anchor.dataset.name = name;
    anchor.href = `${BRIDGE}/jobs/${jobId}/artifacts/${name}`;
    anchor.target = "_blank";
    anchor.rel = "noopener noreferrer";
    anchor.textContent = name;
    return anchor;
  }

  async function syncRunRuntimeEvidence() {
    const idNode = document.getElementById("job-id");
    const jobId = idNode?.textContent?.trim() || "";
    if (!/^[a-f0-9]{12}$/.test(jobId)) return;

    try {
      const response = await nativeFetch(`${BRIDGE}/jobs/${jobId}`, { cache: "no-store" });
      if (!response.ok) return;
      const job = await response.json();

      const jobLabel = idNode.closest(".job-id");
      if (jobLabel) {
        let badge = document.getElementById("runtime-job-preset");
        if (!badge) {
          badge = document.createElement("span");
          badge.id = "runtime-job-preset";
          jobLabel.appendChild(badge);
        }
        badge.textContent = ` · preset ${job.runtime_preset || "standard"}`;
      }

      const list = document.getElementById("artifact-list");
      if (!list || !Array.isArray(job.artifacts)) return;
      for (const name of RUNTIME_ARTIFACTS) {
        if (!job.artifacts.includes(name)) continue;
        if (list.querySelector(`[data-name="${name}"]`)) continue;
        list.appendChild(runtimeArtifactLink(jobId, name));
      }
    } catch {}
  }

  loadCatalog();
  syncRunRuntimeEvidence();
  setInterval(syncRunRuntimeEvidence, 2500);
})();
