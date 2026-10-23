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

## License notes (10/2026)

- The package is MIT (© 2024 Next Level Builder); keep its `LICENSE` with any redistribution.
- `skills/ui-styling/LICENSE.txt` is the full Apache-2.0 text with a blank copyright line and
  appears derived from Anthropic's canvas-design skill, while its `SKILL.md` says MIT. This
  repository treats `ui-styling` as Apache-2.0, the stricter reading of the two permissive terms.
  The vendored files are left unmodified.
- `skills/ui-styling/canvas-fonts/` holds 29 OFL-1.1 font families. `InstrumentSerif-OFL.txt` was
  missing upstream and was added from https://github.com/Instrument/instrument-serif to satisfy the
  OFL notice requirement.
