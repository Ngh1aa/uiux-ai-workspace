# Install profiles

A profile is a named skill bundle that `scripts/install-profile.py` copies into a project's
`.claude/skills/`. Profiles inherit through `extends`, so a leaf profile only lists what it adds.

## Two families, one naming rule

Profiles that look like duplicates (`corporate` and `uiux-corporate`) are **not** duplicates.
They serve different delivery modes and inherit from different roots:

| Prefix | Root | Delivery mode | Use when |
|---|---|---|---|
| none (`corporate`, `education`, `ecommerce`, `redesign`) | `professional-core` | Production website delivery: research, IA, content, build, QA, release | The output ships to real users |
| `uiux-` (`uiux-corporate`, `uiux-saas`, ...) | `prototype-uiux` | Interactive prototype for review, testing or a pitch | The output is evaluated, not shipped |
| `mobile-` (`mobile-app-design`, `mobile-web-preview`) | `mobile-app-design` | Native app design and mobile web preview | The surface is an app or a phone-first preview |

Rule for new profiles: production bundles take a plain domain name, prototype bundles take the
`uiux-` prefix, and every new profile must extend one of the three roots above.

## Inheritance tree

```text
professional-core
├── corporate
├── ecommerce
├── education
└── redesign

prototype-uiux
├── uiux-corporate      ├── uiux-news
├── uiux-ecommerce      ├── uiux-nonprofit
├── uiux-education      ├── uiux-portfolio
├── uiux-government     ├── uiux-real-estate
├── uiux-hospitality    ├── uiux-saas
├── uiux-landing        └── uiux-startup

mobile-app-design
└── mobile-web-preview
```

`scripts/validate-v2.py` checks every `*.json` here (schema, parents, skill names).
