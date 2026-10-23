# UX knowledge, examples, practice and outcome evaluation

Local evidence snapshot: 2026-10-22. Base: `dcfe2c70093eafab409965cd4948ab79b5366146`.
Branch: `upgrade/ux-knowledge-practice`. This snapshot predates publication.
The PR and Git history record subsequent commit, push and merge status;
the local checks below do not establish deployment.

## Five changes

| Scope | Canonical owner / concrete result | Evidence boundary |
|---|---|---|
| Correct knowledge | `ux-laws-and-heuristics`: corrected Fitts/Hick model wording, Miller/recognition distinction, WCAG AA vs AAA, platform units, feedback/optimistic-state caveats; primary source/scope register | Heuristics do not prescribe universal layouts or prove outcomes |
| Deepen domains | `visual-design-direction/data/domain-workflows.json`: five existing profiles, 26 supported profile/role combinations; actors, objects, candidate states, failure/recovery, metric definitions and guardrails | Authored professional hypotheses, not clinical/compliance/operating policy |
| Annotated examples | [Decision lab](../skills_UIUX/visual-design-direction/examples/decision-lab/index.html): five synthetic weak/considered pairs, one data/renderer owner, purposeful hierarchy and real review/back/validation/filter interactions | Related review tasks deliberately share system patterns; these are not five complete products or universally beautiful templates |
| Compare outcomes | Existing `eval-harness.py compare`, [protocol](../skills_UIUX/evals/CONTROLLED-COMPARISON.md), three new eval tasks and a 12-response exploratory pilot | Paired descriptive evidence about decisions; not visual preference or causal uplift |
| Practice | [Decision exercises](../skills_UIUX/visual-design-direction/references/decision-practice.md): eight stages, five briefs, critique rubric, same-scenario repair/retest and transfer exercise; a worked conflicting-evidence synthesis | No automatic mastery/seniority/certification claim |

The [ownership map](CONTRACT-OWNERSHIP.md) remains authoritative. No new orchestrator,
model provider, production dependency or release authority was added.

## Dogfood workflow defects

The original external-task compiler routed the actual five-part request to
`existing-ui-improvement`, loaded frontend implementation and inferred `nonprofit`
from later README operational content. A dedicated maintenance feature now selects
the existing governance/evaluation capabilities through declarative
`skill-library-maintenance` / read-only `skill-library-audit` flows. Native design
terms inside skill-source maintenance do not accidentally invoke app implementation.
Ordinary websites teaching skills retain website routing.

README fallback now uses the introduction/overview for project identity instead of
scanning CI/policy catalogs as identity. Structured target truth and explicit
overrides retain their precedence. `foundation` in a CI section is not nonprofit
evidence. The regression suite records 5 failures before repair and exercises the
positive, near-miss and read-only cases afterward.

The curated industrial catalog card had no corresponding supported profile role.
The role is now explicit; shared retrieval also filters anatomy/workflow by actual
supported roles. Unknown identities and unsupported combinations receive gaps, not
an unrelated preset. Initial no-role provider packets do not eagerly load deep data.

Malformed eval result/environment objects now fail with validation errors. The
paired comparator rejects missing/duplicate pairs and changed brief, contract,
rubric, model, declared settings or tools; it retains regressions and ties.
Capture receipts are overwritten with RUNNING before a new lab run and FAIL on error,
so a failed attempt cannot leave an old PASS receipt current.

## Reproduce the teaching lab

Serve the **repository root**, so the canonical exercise link is available:

```sh
python -m http.server 4193 --bind 127.0.0.1
```

Open `http://127.0.0.1:4193/skills_UIUX/visual-design-direction/examples/decision-lab/`.
Switch case and variant; hide annotations before critique. The fragile variant
intentionally resets edited input on back. The considered variant retains it.
Commerce includes filter/empty-reset/variant selection; healthcare/portfolio expose
honest missing-contact information. No request, charge or access change is sent.
This example needs no build, remote fonts, images, credentials or backend.

Use an existing Playwright installation and browsers, without changing project
package versions merely to run the specimen:

```sh
node skills_UIUX/visual-design-direction/examples/decision-lab/capture.cjs http://127.0.0.1:4193/skills_UIUX/visual-design-direction/examples/decision-lab/ artifacts/decision-lab
```

The browser matrix is five cases × two variants × three widths (320/390/1280) ×
Chromium/WebKit. It checks status/facts, review focus, retained input or the explicitly
seeded defect, inline validation, filter recovery, selection, query allowlist, local
guide link, overflow, enlarged-text stress and console errors. Enlargement is not
native Dynamic Type or a formal zoom/screen-reader audit. Captures start uninspected;
actual visual review is separate.

## Exploratory paired decision pilot

Three predeclared tasks: navigation/target standards, healthcare pending/recovery,
and transfer into an unsupported industry. Four isolated generation contexts (two
per arm) each answered the same three briefs: 12 responses, six matched task/repeat
pairs. Responses within one generation context can be correlated. Baseline used the brief/response contract;
candidate additionally received frozen relevant skill text and bounded lookup data.
An independent agent reviewed condition-masked artifacts against the frozen rubric.

| Observed result | Baseline | Candidate |
|---|---:|---:|
| Responses passing declared rubric | 6/6 | 6/6 |
| Mean agent-rubric score | 87.5 | 100 |

Mean paired score difference: +12.5 points; six positive score differences, no ties
or regressions in this pilot. Pass-rate difference is zero. These tasks show a ceiling
effect and are insufficient to establish broad capability/reliability. Full raw
responses, frozen inputs/digests, masked reviewer files and observations are in
[pilot evidence](evidence/ux-knowledge-practice/pilot/predeclared.json).

The frozen candidate context records its execution checkpoint, including an older
profile-count sentence in the retrieval guide. That sentence was subsequently
corrected in source; historical inputs were not rewritten. Later editorial/routing
guard refinements are outside this decision pilot. Re-run matched arms to measure
another snapshot rather than retroactively treating these responses as its evidence.

Limitations: exact host model/sampling/reasoning identity is not independently
exposed; the inherited setting is declared, not independently authenticated. One
agent grader has no human calibration; wording may reveal supplied context despite
hidden condition labels. No visual artifacts were produced by the trial agents and
no real users/practitioners participated. No significance, causal Factory improvement,
beauty, patient outcome, conversion lift or learner mastery follows from these scores.

## Verification record

Local execution logs and capture/source digests are retained in
`docs/evidence/ux-knowledge-practice/`. Validation verifies structure, retrieval and
runtime boundaries; only actual inspected captures support the lab's visual review.
Full-suite and final visual-review results are recorded after execution, not inferred
from a generated manifest or the pilot's passing answers.

Final local verification:

- Broad regression: **1,650 passed, 55 skipped**, no failures/errors. Of the skips,
  54 are historical suites intentionally frozen by existing `conftest.py`; one is
  an inherited optional rendered-artifact fixture absent locally.
- After the final narrow routing guard changes: **280 passed, 1 skipped** across
  the affected routing, target-truth, retrieval, provider, design/comparison and
  receipt suites. The broad run began before those final guards; do not present
  both runs as one fresh full-tree execution or add their counts together.
- Owned structure: **116 skills**, **117 eval tasks**, **11 flows** (at that release; 10/2026 adds three flows and merges one skill, see `docs/REVIEW-2026-10.md`); V5 structure,
  Flow OS, runtime foundation and eval-harness smoke passed. Existing long
  prompt/profile warnings remain advisory. Five edited packages also passed the
  authoring quick validator; the two existing `globs` packages use repo validation.
- Browser specimen: **60 cases passed**, with Chromium/WebKit at 320/390/1280.
  Fifteen captures retained; **eight final captures actually opened** and reviewed
  with seven-sign verdicts/locations. The remaining captures stay uninspected.
  See [browser evidence](evidence/ux-knowledge-practice/browser/browser-report.json)
  and [visual review](evidence/ux-knowledge-practice/browser/visual-review.json).
- `git diff --check` passed. At evidence capture, no source commit, push, PR or
  merge had been performed. No new production dependencies, deployment, native
  device run or real-user study was part of this local verification.
