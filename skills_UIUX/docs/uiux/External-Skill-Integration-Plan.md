# External UI/UX Specialist Integration

Checked: 2026-09-06 (Asia/Ho_Chi_Minh)

## Phase classification

- Scope: `system`
- Type: `research / implementation / remediation / verification / release / post-release verification`
- Risk: `medium`
- Mode: `production`
- Baseline: `35673d3983f51182ed2212590f55351908b36e03`
- PR: `#14`
- Final PR head: `a1cd2a22db72c73fa04a7dcc0f52ab499ece3f22`
- Release merge commit: `bcfecfc3d7e36314f27adad716e393c41fe2ce9b`
- PR-head validation: GitHub Actions `34026738306` = `success`
- Post-merge validation: GitHub Actions `34026784186` = `success`
- Release authorization: explicitly authorized by user on 2026-09-06.

## Skill Activation Plan

| Task | Trigger/risk | Skill | Expected impact | Verification |
|---|---|---|---|---|
| Preserve project truth and precedence | system-level library mutation | `project-context` | external sources cannot override local contracts | inspect current core docs and final diff |
| Prevent context overload | multiple external skill families | `adaptive-skill-routing-and-context-budget` | progressive references instead of global loading | routing/profile/eval review |
| Preserve lifecycle ownership | external capabilities | `website-delivery-pipeline` | no parallel lifecycle orchestrator | catalog/pipeline review |
| Avoid duplicate capabilities and audit coverage | external skills overlap local owners | `skill-authoring-and-governance` | narrow adapters + explicit full/partial coverage state | pinned-source comparison + validators |

## Released capability set

The released external-specialist layer contains four requested source families:

1. Anthropic Frontend Design → `visual-taste-calibration` + `visual-design-direction` handoff.
2. Vercel Web Design Guidelines + React Best Practices → `web-ui-code-review` + two progressive references.
3. Design Extractor/Auditor → `reference-extraction-and-design-audit` + extraction schema.
4. UX Writing & Content Design → `ux-writing-and-microcopy` + `content-design-and-question-design` handoff.

Figma-specific additions introduced during the initial PR #14 implementation were removed before release. Pre-existing generic reference-analysis behavior outside this PR was preserved.

## Source locks

| Source | Locked ref | License observed | Local mode |
|---|---|---|---|
| `anthropics/claude-plugins-official` → `frontend-design` | `85cce0381e7860082641b59d961a2b8c368b8b79` | Apache-2.0 | `ADAPT_WITH_ATTRIBUTION` |
| `vercel-labs/agent-skills` → `web-design-guidelines`, `react-best-practices` | `063bee94c3f4df8453406c830b0a7df0f2860278` | MIT | `ADAPT_WITH_ATTRIBUTION` |
| `vercel-labs/web-interface-guidelines` | `e3d624baaf29dc1fc645aff3e38f03e564d2d6b1` | MIT | `ADAPT_WITH_ATTRIBUTION` |
| `billhector/design-skills` | `afee427d8f1e2d9deb004a96bcaa8391c572c9f5` | MIT | `ADAPT_WITH_ATTRIBUTION` |
| `hueyexe/frontend-agent-skills` → `ux-writing-content-design` | `2841c079dd8a9c634882227194dc42e25227710d` | MIT | `ADAPT_WITH_ATTRIBUTION` |

Detailed provenance remains in `vendor/external-uiux/SOURCE-LOCKS.md`.

## Coverage audit — have the upstream skills been copied in full?

**FACT: No. None of the four source families is a full copy in the current release.** The current architecture intentionally uses local synthesis/progressive disclosure rather than vendoring the complete upstream packages.

| Source family | Coverage state | Present locally | Material upstream content not copied locally |
|---|---|---|---|
| Anthropic Frontend Design | `PARTIAL_ADAPTED` | subject-matter grounding, anti-template critique, one memorable commitment, typography/structure/motion restraint, two-pass calibration | exact full upstream guidance such as explicit line-length/serif-leading rules, complete generated-style tell list, CSS specificity warning, and the full writing-in-design section |
| Vercel Web Interface Guidelines | `PARTIAL_ADAPTED` | high-value semantics/focus/forms/text/media/motion/copy/performance routing | many exact command rules across safe areas, theming, locale/i18n, hydration, pointer/drag, typographic mechanics, precise form rules, anti-pattern list and terse file:line review contract |
| Vercel React Best Practices | `PARTIAL_ADAPTED` | 8-category priority model and representative checks | upstream contains 70 individual rule files with detailed incorrect/correct examples and rule-specific context; these are not fully copied |
| Design Extractor/Auditor | `PARTIAL_ADAPTED` | token/layout/component/responsive/dark-mode/source-attribution extraction and project audit | mandatory Firecrawl workflow, screenshot/download commands, exact DESIGN.md/Tailwind templates, automatic Tailwind migration, global design library/index workflow, detailed contrast/colorblind simulation and suggested-color automation |
| UX Writing & Content Design | `PARTIAL_ADAPTED` | task/state-first copy, consequence labels, Avoid→Explain→Resolve, state matrix, sensitive-state restraint, accessibility/localization basics | large default-recommendation/override table, required-question decision system, critique severity framework, detailed decision framework, full voice/tone system, deeper frontend/ARIA specifics, complete quality checklist, and four upstream reference files (`anti-patterns`, `checklists`, `decision-prompts`, `principle-cards`) |

### Interpretation

`PARTIAL_ADAPTED` does not mean the integration is broken. It means the release optimized for context efficiency and local ownership rather than literal completeness. If a future requirement is **full upstream preservation**, the appropriate architecture is to vendor the complete pinned packages under `vendor/external-uiux/` with their license/notice obligations while keeping the current local adapters as narrow routers, so the full corpus exists without being loaded into every task.

## Requirement coverage

| ID | Requirement | OWNER_PHASE | Status | Verification |
|---|---|---|---|---|
| EXT-001 | Anthropic visual-taste integration | implementation | DONE_VERIFIED | local adapter/reference + source pin + CI |
| EXT-002 | Vercel web UI + React/Next review integration | implementation | DONE_VERIFIED | local adapter/references + source pins + CI |
| EXT-003 | Remove Figma additions introduced by PR #14 | remediation | DONE_VERIFIED | final PR diff + CI |
| EXT-004 | Design extraction/audit integration | implementation | DONE_VERIFIED | local adapter/schema + source pin + CI |
| EXT-005 | UX writing/microcopy integration | implementation | DONE_VERIFIED | local adapter/reference + source pin + CI |
| EXT-006 | Reproducible source provenance | implementation | DONE_VERIFIED | source locks |
| EXT-007 | Final PR-head verification | verification | DONE_VERIFIED | Actions `34026738306` success |
| EXT-008 | Merge to main | release | DONE_VERIFIED | merge `bcfecfc3d7e36314f27adad716e393c41fe2ce9b` |
| EXT-009 | Post-merge verification | release | DONE_VERIFIED | Actions `34026784186` success |
| EXT-010 | Audit whether upstream skills are fully copied | post-release verification | DONE_VERIFIED | pinned-source file/package comparison; all four = `PARTIAL_ADAPTED` |

## Phase result

`PASSED`

- DUE-NOW `BLOCKED = 0`
- DUE-NOW `UNACCOUNTED = 0`
- `PENDING_FUTURE_PHASE = 0`

The released repository is valid and verified, but it must not be described as containing full copies of the four external skill families.
