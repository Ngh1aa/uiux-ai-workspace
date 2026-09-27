# QA Contract Schema

Use this schema to compile `04-QA-REMEDIATION-PROMPT.md` and the QA section of the full build spec.

## 0. QA metadata

- **Target repository:** [...]
- **Target ref:** [...]
- **Current phase:** [...]
- **Responsive scope:** [desktop_only / responsive_all]
- **Release authority:** [spec_only / branch_write / create_pr_only / merge_only / merge_and_deploy]
- **Representative routes/pages:** [...]
- **Critical journey:** [...]

## 1. Evidence rule

Every PASS must have evidence appropriate to the claim.

Examples:

- syntax/compile claim → compiler/syntax check;
- route claim → HTTP/browser navigation;
- visual claim → rendered screenshot/browser review;
- accessibility claim → semantic inspection + Axe/Lighthouse where applicable;
- deployment claim → workflow/deployment evidence;
- protected behavior claim → direct before/after/runtime evidence.

Never equate:

- file existence with feature correctness;
- build success with visual quality;
- CI green with product quality;
- generated screenshot with human-reviewed visual integrity.

## 2. Functional gate

Check only applicable behavior:

- [ ] declared routes resolve;
- [ ] anchors navigate to intended owners;
- [ ] primary CTA/link destinations are correct;
- [ ] forms/states work if in scope;
- [ ] slider/carousel/pagination behavior works;
- [ ] keyboard-triggered behavior works;
- [ ] no critical interaction path is dead.

For each gate record:

```text
STATUS = PASS / FAIL / N/A_JUSTIFIED / BLOCKED
EVIDENCE = [...]
```

## 3. Preserve-regression gate

For every protected contract identify a proof method.

| Protected item | Preserve level | Verification method | Pass criterion |
|---|---|---|---|
| [...] | byte / behavior / API-DOM / visual-DNA / content | hash/runtime/browser/diff/manual | [...] |

Examples:

- byte-for-byte JS → blob/hash equality;
- behavior preservation → same representative runtime outputs;
- DOM/API preservation → selector/route contract checks;
- visual-DNA preservation → before/after screenshot review;
- content preservation → source/data comparison.

## 4. Visual gate

For substantial UI work capture representative rendered evidence.

Inspect:

- hierarchy;
- composition;
- spacing;
- clipping;
- overflow;
- broken media;
- unintended blank regions;
- title/CTA ownership;
- image crop/focal points;
- consistency with the Design Contract;
- anti-template rules;
- signature visual moment.

Automated screenshot capture does not replace visual review.

## 5. Responsive gate

### If `responsive_all`

Verify representative widths appropriate to the product, normally including:

```text
mobile ~390
intermediate/tablet ~768
large desktop ~1440
```

Adjust when the Design Contract declares different widths.

Check:

- [ ] no accidental horizontal overflow;
- [ ] content ordering remains intentional;
- [ ] nav transformation works;
- [ ] media crop remains valid;
- [ ] touch targets are usable;
- [ ] typography remains readable;
- [ ] interactive controls remain reachable.

### If `desktop_only`

Verify declared desktop pressure points. Mark mobile/tablet:

```text
N/A_JUSTIFIED — outside declared responsive scope.
```

Do not claim fully responsive.

## 6. Motion / interaction gate

Check applicable:

- key timeline/scroll checkpoints;
- hover/focus/active states;
- slider normalization/looping;
- state classes;
- pointer-event ownership;
- page transitions;
- custom cursor only when applicable;
- no interaction-blocking overlays;
- choreography remains aligned after content expansion.

For protected timelines, verify exact named ranges/functions rather than “feels smooth.”

## 7. Reduced-motion gate

When motion exists:

- [ ] `prefers-reduced-motion` is honored;
- [ ] critical content remains available;
- [ ] smoothing/parallax/autoplay behavior is reduced or disabled as designed;
- [ ] disabling motion does not create hidden/unreachable content.

## 8. Media gate

Inspect all applicable families:

- hero/editorial;
- cards/listing;
- gallery;
- project/case-study;
- profile;
- product media;
- icons/fonts.

Check:

- [ ] assets resolve;
- [ ] natural dimensions are non-zero;
- [ ] no stretched/squashed media;
- [ ] no accidental subject/focal crop;
- [ ] no vertical slivers or wrong grid ownership;
- [ ] remote asset policy is respected.

## 9. Accessibility gate

At minimum when applicable:

- [ ] semantic headings/landmarks;
- [ ] keyboard navigation;
- [ ] visible focus;
- [ ] skip-link behavior;
- [ ] meaningful alt text;
- [ ] no serious/critical Axe violations on representative routes;
- [ ] contrast checked for key text/CTA surfaces;
- [ ] controls have accessible names;
- [ ] reduced motion works.

If a numeric Lighthouse accessibility budget is declared, record the actual score instead of saying “good.”

## 10. Performance gate

Use only if due now.

Possible checks:

- Lighthouse performance budget;
- image payload/format;
- render-blocking assets;
- unnecessary third-party dependencies;
- animation main-thread pressure;
- static asset 404s.

Mark prototype-only performance work `N/A_JUSTIFIED` when the project contract explicitly excludes it.

## 11. Console/runtime gate

On representative routes:

- [ ] no uncaught project-code exceptions;
- [ ] no unexpected 404s;
- [ ] no repeated warnings indicating broken state;
- [ ] third-party warnings are distinguished from project-owned failures.

## 12. Routing / SEO gate

When applicable:

- [ ] all internal links resolve under actual hosting base path;
- [ ] relative links work on GitHub Pages project paths;
- [ ] clean URL settings match link strategy;
- [ ] title/description/OG metadata exist as specified;
- [ ] sitemap/robots list intended public routes;
- [ ] favicon/theme metadata resolve.

## 13. Deployment gate

Only DUE NOW when release is authorized.

### GitHub Pages

- [ ] Pages source/config is correct;
- [ ] workflow completes;
- [ ] artifact deploy succeeds;
- [ ] production URL loads;
- [ ] project-subpath assets/routes work.

### Vercel

- [ ] correct framework preset;
- [ ] build command/output directory match architecture;
- [ ] deployment succeeds;
- [ ] production route smoke passes.

Do not report deploy PASS based only on config file presence.

## 14. Root-cause remediation policy

When a gate fails:

```text
FAILURE EVIDENCE
↓
EARLIEST RESPONSIBLE OWNER
↓
REPAIR OWNER / INVALIDATE DOWNSTREAM ASSUMPTIONS
↓
RERUN AFFECTED WORK
↓
REVALIDATE
```

Do not weaken tests solely to manufacture a PASS.

If a test contract is stale, prove the new product contract first, update the test to the real contract, and rerun.

## 15. Final QA report

Return:

```text
STATUS: DONE / PARTIAL / BLOCKED

PASS:
- ...

N/A_JUSTIFIED:
- ...

PENDING_FUTURE_PHASE:
- ...

BLOCKED / FAIL:
- ...

EVIDENCE:
- workflow run(s)
- screenshots/artifacts
- test output
- deployment URL(s)

REMAINING RISKS:
- only real unresolved items
```
