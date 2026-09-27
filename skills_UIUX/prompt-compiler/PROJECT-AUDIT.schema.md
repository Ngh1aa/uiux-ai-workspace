# Project Audit Schema

Use this schema during Prompt Compile before writing any build specification.

The audit is evidence collection, not design fiction.

## 0. Audit metadata

- **Target repository:** [...]
- **Ref inspected:** [...]
- **Audit date:** [...]
- **Requested goal:** [...]
- **Requested authority:** [spec_only / branch_write / create_pr_only / merge_only / merge_and_deploy]
- **Responsive scope:** [desktop_only / responsive_all / UNKNOWN]
- **Validation lane:** [prototype / evidence-led / production-learning / UNKNOWN]

## 1. Source of truth

| Source | Role | Evidence state | Notes |
|---|---|---|---|
| [...] | requirements / code / design / deploy / tests | VERIFIED / UNKNOWN | [...] |

Record conflicts explicitly. Follow the highest-authority source.

## 2. Repository map

Capture only material surfaces.

```text
repo/
├── ...
```

Identify:

- canonical implementation root;
- generated/vendor directories;
- documentation roots;
- QA/test roots;
- deployment/workflow roots.

## 3. Runtime / stack

- **Frontend:** [...]
- **Backend:** [... / N/A_JUSTIFIED]
- **Languages:** [...]
- **Frameworks:** [...]
- **Build system:** [...]
- **Package manager:** [...]
- **Runtime:** [...]
- **Hosting/deployment:** [...]
- **External services:** [...]

## 4. Entry points and routes

| Route / entry | File / owner | Role | Current state | Evidence |
|---|---|---|---|---|
| [...] | [...] | [...] | working / incomplete / broken / UNKNOWN | VERIFIED / ... |

Include anchor destinations and client-side routing when material.

## 5. Current design system

### Typography

- font families;
- font source;
- type scale;
- special display usage.

### Color/tokens

- exact CSS variables/tokens;
- semantic roles;
- theme behavior.

### Grid/spacing

- container widths;
- major spacing rhythm;
- layout primitives.

### Components

- reusable buttons;
- nav/header/footer;
- cards;
- forms;
- overlays;
- galleries/sliders;
- other repeated patterns.

## 6. DOM / component contracts

Record exact structures whose shape matters.

Example:

```text
main.site-shell
└── section#cinema.cinema-scroll
    └── div.stage
        └── ...
```

Do not list arbitrary DOM detail if it has no effect on preservation or implementation.

## 7. Motion / interaction audit

| Owner | Exact function/selector | Trigger/input | Timing/range | State/output | Preserve level |
|---|---|---|---|---|---|
| [...] | [...] | scroll/click/hover/etc | [...] | [...] | byte / behavior / visual-DNA / can-change |

Capture when applicable:

- named easing/math functions;
- timeline/scroll thresholds;
- CSS variables written by JS;
- slider/carousel normalization;
- cloning strategies;
- state classes;
- focus/keyboard behavior;
- reduced-motion behavior.

## 8. Responsive audit

| Breakpoint / pressure point | Current behavior | Risk | Evidence |
|---|---|---|---|
| [...] | [...] | [...] | VERIFIED / UNKNOWN |

Distinguish explicit media queries from inferred pressure points.

## 9. Media / asset audit

| Asset family | Source | Remote/local | Used by | Constraint | Health |
|---|---|---|---|---|---|
| [...] | [...] | [...] | [...] | crop/URL/name/etc | VERIFIED / UNKNOWN |

Include fonts, hero imagery, icons and externally hosted assets when they materially affect the project.

## 10. Content audit

- existing content that must be preserved;
- placeholder/lorem content;
- missing copy;
- inconsistent labels;
- dead/ambiguous navigation;
- localization/language behavior.

## 11. Accessibility audit

Record only observed/inspectable facts:

- semantic heading structure;
- skip links;
- keyboard/focus behavior;
- alt text;
- reduced motion;
- landmark usage;
- known contrast concerns;
- existing Axe/Lighthouse evidence if available.

Do not claim accessibility compliance from source inspection alone.

## 12. SEO / metadata audit

- title/description;
- OG metadata;
- theme color;
- canonical/robots/sitemap if present;
- favicon;
- structured data when applicable.

## 13. Deployment audit

### GitHub Pages

- workflow path;
- relative/base-path constraints;
- pages source;
- last known deploy state if evidence is available.

### Vercel

- framework preset implications;
- build command;
- output directory;
- `vercel.json`;
- route/clean URL behavior.

### Other

Use only if applicable.

## 14. Current problems / gaps

For each evidence-backed issue:

```text
### [Issue name]
CURRENT: ...
PROBLEM: ...
IMPACT: ...
EVIDENCE STATE: VERIFIED / INFERRED / UNKNOWN
PROPOSED RESOLUTION: ...
```

Do not turn preferences into bugs.

## 15. Immutable / preserve candidates

Classify each candidate:

| Candidate | Preserve level | Why | Evidence |
|---|---|---|---|
| [...] | byte-for-byte / behavior / API-DOM / visual-DNA / content-data | [...] | VERIFIED / user requirement |

## 16. Can-change candidates

List areas where extension/refactor is safe or explicitly requested.

## 17. Unknowns that matter

Only include unknowns that could materially change the spec.

```text
UNKNOWN — [...]
Why it matters: [...]
Can proceed safely? yes/no
Fallback assumption if safe: [...]
```

## 18. Audit verdict

Return:

```text
AUDIT_READY = YES / NO
BLOCKERS = [...]
HIGH-RISK SURFACES = [...]
PRESERVE CONTRACT READY = YES / NO
BUILD-SPEC COMPILATION READY = YES / NO
```
