# Skill Version Lock

Checked: 2026-09-07 (Asia/Ho_Chi_Minh)

## V5.3 selective-learning candidate

- Phase-start `main`: `2faf3370a1d858a87557590a19aa3bddc286c08d`
- Branch: `feat/v5-3-selective-learning`
- PR: `#19`
- Scope: `system`
- Type: `implementation / QA`
- Risk: `medium`
- Mode: `production_candidate`
- Release authorization: `no_release`; this phase may open a PR but must not merge to `main` without explicit authorization.
- Reviewed upstream locks:
  - `affaan-m/ECC`: `e04ea0b9cc8248686edf5ac751cadff550e162b8` (MIT)
  - `mattpocock/skills`: `3cca18b368ae95cdbdebbff572ccafa662551015` (MIT)
  - `anthropics/skills`: `41bbe19d1a1a7eaab5e7bb9050a417e5c6cffc8f` (reviewed skills Apache-2.0 individually)
  - `vercel-labs/agent-skills`: `063bee94c3f4df8453406c830b0a7df0f2860278` (MIT)
- Initial implementation commit: `eadf071304d7e4de493241f9af88a69d74fbc476`
- Corrected implementation head: `fb2b4e2d2b0ab12b021602d5ad8ea1cd1b3e74a2`
- Push validation: GitHub Actions `34075756104` = `success`
- PR validation: GitHub Actions `34075758482` = `success`
- Candidate implementation/QA result: `PASSED`; release remains `N/A_JUSTIFIED` until separately authorized.

## Released V5.2 agent runtime foundation

- Phase-start `main`: `f098e6a94aaf3f026a810bc30073df67eb653cc2`
- Recovery PR: `#16`
- Recovery head: `7373bf9201b7ad3d52eea2753a78809beb5b1562`
- Recovery merge commit: `c8a2d07ad360bc887b687288beff1d3d7aa7f76e`
- Recovery post-merge validation: GitHub Actions `34073614108` = `success`
- V5.2 branch: `feat/v5-2-agent-runtime-foundation`
- V5.2 PR: `#17`
- Implementation commit: `69724b9fd65a8df0f56ae2c8231da2054da73346`
- Final PR head: `a6cc9997fc15246c67894fcebfeff3f9e46a9e70`
- Merge commit: `49e5ad978cbce21df2398385b2a58b019252923b`
- Implementation push validation: GitHub Actions `34045466501` = `success`
- Final-head push validation: GitHub Actions `34045571288` = `success`
- Final-head PR validation: GitHub Actions `34045573762` = `success`
- Post-merge validation: GitHub Actions `34073654070` = `success`
- Runtime mode: provider-neutral; core validation does not require a model SDK.
- MCP compatibility check: official MCP Python SDK v2 documentation reviewed 2026-09-06; adapter uses `MCPServer` and keeps MCP optional.
- Figma integration check: official Figma MCP / Code Connect documentation reviewed 2026-09-06; Figma remains external context rather than project source-of-truth.
- Release authorization: explicitly authorized by user on 2026-09-07.

## Released cross-functional intelligence upgrade

- `Ngh1aa/skills_UIUX` baseline: `279c9e01ca85779fa4af2d60551fb9b1e0d16111`
- Branch: `feat/cross-functional-product-growth-intelligence`
- PR: `#15`
- Implementation commit: `201642e6857dd26994002facfa70b029a35a1bc4`
- Final PR head: `1743c137849223fccdf0681b93fda156f652939a`
- Merge commit: `9591b238b1b0700aff6fed8deb79d13b6535d143`
- Implementation push validation: GitHub Actions `34032698500` = `success`
- Implementation PR validation: GitHub Actions `34032720908` = `success`
- Final-head push validation: GitHub Actions `34032869876` = `success`
- Final-head PR validation: GitHub Actions `34032872075` = `success`
- Post-merge validation: GitHub Actions `34033674244` = `success`
- Release authorization: explicitly authorized by user on 2026-09-06.

## External source locks

| Source | Role | Locked ref |
|---|---|---|
| `nextlevelbuilder/ui-ux-pro-max-skill` | vendored design-intelligence skill/data source | `314307f156aeab0c6b567bbaa1ce4e7aabd5a636` |
| `anthropics/claude-plugins-official` | Frontend Design visual-taste source | `85cce0381e7860082641b59d961a2b8c368b8b79` |
| `vercel-labs/agent-skills` | Web Design Guidelines + React Best Practices + reviewed discovery-index source | `063bee94c3f4df8453406c830b0a7df0f2860278` |
| `vercel-labs/web-interface-guidelines` | pinned web-interface rule source | `e3d624baaf29dc1fc645aff3e38f03e564d2d6b1` |
| `billhector/design-skills` | design extraction/audit source | `afee427d8f1e2d9deb004a96bcaa8391c572c9f5` |
| `hueyexe/frontend-agent-skills` | UX writing/content-design source | `2841c079dd8a9c634882227194dc42e25227710d` |
| `assimovt/productskills` | product positioning/prioritization/scope/metrics source | `66f9cee5868d6daf9cf106b4a74090428d6fa83e` |
| `mindtheproduct/skills` | hard product-decision framing source | `3fb3d46092c4149d1653fc317aed77d63f2a98ca` |
| `ai-vita/skills` | page CRO + marketing copy source | `dda98df83ec242cf32c208a0a78b759f0b3e658b` |
| `rampstackco/claude-skills` | experimentation result-interpretation source | `a67dd34c609f034c0cfd736a348659bbdf1605bf` |
| `addyosmani/agent-skills` | coding context/planning/vertical-slice source | `48cb1168aeaaa70dfc2bbf709eddfa2a8ed8129a` |
| `mblode/agent-skills` | search-demand/content-briefing source | `0a639b1ef3b75aa6cc945e778fb1486def1d41bf` |
| `affaan-m/ECC` | agent harness/recovery/browser-QA source | `e04ea0b9cc8248686edf5ac751cadff550e162b8` |
| `mattpocock/skills` | debugging/review/spec/glossary source | `3cca18b368ae95cdbdebbff572ccafa662551015` |
| `anthropics/skills` | reviewed MCP/webapp-testing/skill-eval source; per-skill license applies | `41bbe19d1a1a7eaab5e7bb9050a417e5c6cffc8f` |

Detailed existing UI/UX provenance: `vendor/external-uiux/SOURCE-LOCKS.md`.
Detailed cross-functional provenance: `vendor/cross-functional-intelligence/SOURCE-LOCKS.md`.
Detailed agent-runtime provenance: `vendor/agent-runtime-intelligence/SOURCE-LOCKS.md`.

## Released UI UX Pro Max integration

- PR: `#12`
- Integration merge commit: `130b7a2181760d98fca89fe1acf26a7bbd6794f0`
- Upstream skill tree: `a23882a2d113b30e94adb8a5d3fc35bbc690591e`
- Vendored skill tree: `a23882a2d113b30e94adb8a5d3fc35bbc690591e`
- Upstream engine tree: `a393798fc862de6176d0c3422c16e0dfa3425821`
- Vendored engine tree: `a393798fc862de6176d0c3422c16e0dfa3425821`
- Integration post-merge validation: GitHub Actions `34021619346` = `success`

## Released repository cleanup

- Cleanup PR: `#13`
- Merge commit: `22ddd2ed3352316495bef7b56467caad218cb900`
- Cleanup release verification commit: `35673d3983f51182ed2212590f55351908b36e03`
- Post-release validation: GitHub Actions `34024338827` = `success`

## Released external UI/UX specialist integration

- PR: `#14`
- Baseline: `35673d3983f51182ed2212590f55351908b36e03`
- Final PR head: `a1cd2a22db72c73fa04a7dcc0f52ab499ece3f22`
- Merge commit: `bcfecfc3d7e36314f27adad716e393c41fe2ce9b`
- Release evidence docs commit: `279c9e01ca85779fa4af2d60551fb9b1e0d16111`
- PR-head validation: GitHub Actions `34026738306` = `success`
- Post-merge validation: GitHub Actions `34026784186` = `success`
- Final docs validation: GitHub Actions `34027027106` = `success`

## Adoption policy

- External repositories are pinned knowledge sources, not parallel lifecycle orchestrators.
- Prefer local synthesis/progressive disclosure and extend existing owners when overlap is high.
- Do not fetch mutable upstream `main` during normal project execution as a substitute for a reviewed source update.
- Time-sensitive product/search/platform/statistics claims require current verification when exact details matter.
- Changing any locked ref requires source/license/behavior diff review, overlap/conflict resolution and structural/profile/eval verification before release.
