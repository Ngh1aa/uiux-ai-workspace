# UI UX Pro Max vendored source

- Upstream: `nextlevelbuilder/ui-ux-pro-max-skill`
- Pinned commit: `314307f156aeab0c6b567bbaa1ce4e7aabd5a636`
- Imported: `2026-09-06`
- License: MIT (see `LICENSE`)
- Policy: upstream files in `skills/` and `engine/` are vendored verbatim. Local behavior belongs outside the vendor directory.

## Included

- all upstream `.claude/skills/*` packages;
- full `src/ui-ux-pro-max` engine, including databases, stack guidance, templates, search and validation scripts;
- upstream MIT license.

## Update rule

Do not float on upstream `main`. Review a new immutable commit, inspect license/provenance/data/search changes, update this lock, run target validators + vendor smoke, and record migration impact before promotion.
