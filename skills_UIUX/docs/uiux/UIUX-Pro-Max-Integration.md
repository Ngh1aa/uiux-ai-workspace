# UI UX Pro Max Integration — Implementation Record

Date: 2026-09-06
PR: #12
Branch: `feat/vendor-uiux-pro-max-design-intelligence`

## Phase classification

| Dimension | Value |
|---|---|
| Scope | `system` |
| Type | `implementation / remediation` |
| Risk | `medium` |
| Mode | `production_candidate` |
| Release authority | `no_release` — PR only, no merge/deploy |

## Skill Activation Plan

| Task | Trigger / risk | Skill | Expected impact | Verification |
|---|---|---|---|---|
| Preserve project truth and local precedence | external corpus may override local rules | `project-context` | explicit source hierarchy and conflict rule | bridge/prompt review |
| Keep context bounded | very large vendored corpus | `adaptive-skill-routing-and-context-budget` | retrieval rather than preload | routing rules + near-miss eval |
| Integrate into lifecycle | installed skill could become orphan capability | `website-delivery-pipeline` | conditional phase/routing insertion | pipeline + profile install smoke |
| Build maintainable new skill | new capability + external resources | `skill-authoring-and-governance` | scoped bridge/resources/evals/validation | validators + eval tasks |
| Learn upstream usage semantics | user requested effective reuse, not raw copy | upstream `ui-ux-pro-max` skill | smallest search mode, retry-once, stack detection, persistence rules | prompt/bridge behavior contract |

## Skills USED

| Skill | Trigger | Requirement applied | Change created | Verification | Evidence |
|---|---|---|---|---|---|
| `project-context` | external recommendations vs project truth | project/source truth precedes generic skill defaults | precedence + conflict policy in bridge/prompt | source review | `FACT` |
| `adaptive-skill-routing-and-context-budget` | 100% database is too large for prompt context | minimal graph + progressive disclosure | adaptive knowledge retrieval rules | near-miss eval + source retrieval smoke | `FACT` |
| `website-delivery-pipeline` | capability must be lifecycle-routable | route smallest conditional graph | Phase 4B + whole-site graph insertion | pipeline review + CI | `FACT` |
| `skill-authoring-and-governance` | creating a first-class capability | scoped SKILL, resources, deterministic adapter, evals | `design-intelligence-retrieval` package | `validate-skills.py`, `validate-v2.py`, eval harness | `FACT` |
| upstream `ui-ux-pro-max` | effective use of copied corpus | smallest search mode, query contract, retry once, detect stack, no fabricated result, persistence caution | augmentation prompt + bridge policies | source/installed query smoke | `FACT` |

## System reality

| Capability | Reality | Evidence |
|---|---|---|
| Vendored upstream skill snapshot | `REAL` | all 7 upstream skill packages copied at pinned SHA |
| Full upstream engine/database | `REAL` | complete `src/ui-ux-pro-max` snapshot under vendor + integrity validator |
| Search/reasoning execution in source repo | `REAL` | CI source retrieval smoke |
| Search/reasoning execution after profile install | `REAL` | CI installs professional-core into `/tmp` and queries through installed bridge |
| Automatic quality improvement in downstream websites/apps | `UNKNOWN` until project-specific implementation + rendered QA | retrieval recommendations are not outcome proof |
| Production release of this library change | `N/A` in this phase | user did not authorize merge/release |

## Decision Log

### D-01 — Vendor the complete upstream system
**Evidence label:** `FACT`

Decision: copy all seven upstream skill packages and the complete `src/ui-ux-pro-max` engine/data/templates/tests snapshot rather than selectively re-authoring its database.

Reason: user explicitly requested full coverage; keeping the upstream snapshot intact preserves search/reasoning/data relationships and provenance.

Impact: repository size grows materially, but consumer context does not because the corpus is retrieved on demand.

### D-02 — Keep vendor verbatim and local behavior outside it
**Evidence label:** `EVIDENCE_BACKED_INFERENCE`

Decision: `vendor/ui-ux-pro-max/` is upstream-owned; `design-intelligence-retrieval/` owns local adaptation.

Reason: avoids silent fork drift and makes upstream upgrades reviewable.

### D-03 — Retrieval, not preload
**Evidence label:** `FACT`

Decision: the complete database is installed but never loaded wholesale into prompt context.

Applied behavior:
- system direction → `--design-system`;
- focused concern → explicit `--domain`;
- implementation concern → detected `--stack`;
- retry once if empty/off-topic;
- then stop and record `no verified match`.

### D-04 — Design Contract remains canonical
**Evidence label:** `EVIDENCE_BACKED_INFERENCE`

Decision: upstream persisted `design-system/<project>/MASTER.md` and page overrides are candidate retrieval artifacts, not a second project source of truth.

Reason: `skills_UIUX` already has phase-aware Design Contract and project-truth precedence. Two authoritative design systems would create silent drift.

### D-05 — No blind canonical prompt version bump
**Evidence label:** `PROFESSIONAL_HYPOTHESIS`

Decision: add `DESIGN-INTELLIGENCE-AUGMENTED-REDESIGN-PROMPT.md` as a conditional module instead of renaming `MASTER-PROMPT-V7.2` to a new version solely because a knowledge source was added.

Reason: retrieval is conditional and should not force every implementation task through external design intelligence.

### D-06 — Install vendor as a dependency of the bridge
**Evidence label:** `FACT`

Finding: existing installers copied only root skill folders. Without installer changes, a consumer project would receive the bridge but not the database/engine.

Decision: `professional-core` and `prototype-uiux` include `design-intelligence-retrieval`; installers copy `vendor/ui-ux-pro-max` whenever that bridge is selected, track it as a managed resource, and remove generated Python cache.

Verification: installed-project CI smoke queries through `.claude/skills/design-intelligence-retrieval/scripts/query.py`.

### D-07 — Phase-aware ledger model
**Evidence label:** `FACT`

Conflict: older ChatGPT Project text uses three requirement states; current repository canonical lifecycle uses four states.

Decision: this implementation record follows current repository truth:
`DONE_VERIFIED / N/A_JUSTIFIED / PENDING_FUTURE_PHASE / BLOCKED`.

## Requirement Coverage Ledger

| ID | Requirement | OWNER_PHASE | Status | Verification | Evidence / rationale |
|---|---|---|---|---|---|
| R-01 | Copy all upstream skill packages | implementation | `DONE_VERIFIED` | vendor workflow + integrity validation | seven packages present |
| R-02 | Copy complete upstream search/database system | implementation | `DONE_VERIFIED` | vendor files + source search smoke | full `src/ui-ux-pro-max` snapshot |
| R-03 | Preserve license/provenance/version | implementation | `DONE_VERIFIED` | LICENSE, UPSTREAM.md, version lock | pinned upstream SHA |
| R-04 | Add local retrieval/orchestration bridge | implementation | `DONE_VERIFIED` | SKILL validator + source query | bridge + adapter exist |
| R-05 | Learn upstream usage and implement a suitable prompt | implementation | `DONE_VERIFIED` | prompt review + eval tasks | query mode/retry/stack/persistence policies applied |
| R-06 | Route capability through catalog/lifecycle/context budget | implementation | `DONE_VERIFIED` | catalog/pipeline/README review | conditional routing recorded |
| R-07 | Make installed consumer profiles receive the vendor dependency | implementation | `DONE_VERIFIED` | actual `/tmp` profile install + installed query smoke | CI run 34020833658 passed |
| R-08 | Add positive, negative/near-miss and complex retry/stack coverage | verification | `DONE_VERIFIED` | eval schema/validator + eval harness smoke | three new task fixtures |
| R-09 | Validate structural/profile/vendor/install integration | verification | `DONE_VERIFIED` | GitHub Actions | Validate Skills run 34020833658 PASS |
| R-10 | Create reviewable PR | handoff | `DONE_VERIFIED` | GitHub PR | PR #12 open, not merged |
| R-11 | Merge/release to `main` | release | `N/A_JUSTIFIED` | authority check | no merge/release authorization in current request |

## Verification evidence

Observed PASS before PR creation in GitHub Actions run `34020833658`:
- SKILL.md structure;
- V5 profiles/packs/project configs/evals/resources;
- vendor integrity;
- source retrieval smoke;
- dry-run core profile installer;
- actual professional-core install;
- installed bridge + vendor engine presence;
- installed retrieval query;
- project installer/bootstrap smoke;
- provider-neutral eval harness smoke.

Final branch/PR CI must still be green after this documentation commit before the implementation phase is called PASSED.

## Handoff

- Review PR #12.
- Do not edit files inside `vendor/ui-ux-pro-max/` for local policy changes; change the bridge/prompt instead.
- To update upstream, review a new immutable SHA, inspect code/data/provenance/license/search diff, rerun all gates, then update the version lock.
- Do not merge/release without explicit authorization.
