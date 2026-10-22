# Governance

How this design system changes without breaking the products that use it. The general method
lives in the skill `skills_UIUX/design-system-governance-and-adoption/SKILL.md`; this page is
the concrete policy for this repository.

## Versioning

The version is in `CHANGELOG.md` and follows semantic versioning applied to the **public
surface**: token paths, CSS class names, state attributes and documented behavior.

| Change | Version bump | Examples |
|---|---|---|
| Remove or rename a token path or class | major | `text.muted` renamed to `text.secondary` |
| Change a contract in `component-contracts.md` | major | Badge loses its icon slot |
| Change a semantic token's value | minor | `action.primary.bg` moves from jade 700 to 800 |
| Add a token, class, variant or component | minor | New `.ds-switch` |
| Fix a bug that restores the documented contract | patch | Focus ring missing on select |

Changing a value is minor, not patch, because consumers may have screenshots or visual tests
tied to it.

## Deprecation

1. Mark the token with `"$deprecated": "Use {new.path}. Removal in the next major."` (DTCG
   2025.10). `validate.py` warns on every reference to a deprecated token.
2. Keep the old path as an alias of the new one for at least one minor release.
3. Remove only in a major release, listed under **Removed** in the changelog with the
   replacement.

## Contribution: new component, variant or local composition?

Answer in order; stop at the first yes.

1. Can the need be met by composing existing components with layout primitives
   (`.ds-stack`, `.ds-cluster`, `.ds-split`)? Then it is a **local composition**; do not add to
   the system.
2. Is it an existing component with a different emphasis, size or tone that at least two
   products need? Then it is a **variant**.
3. Does it have its own anatomy, states and accessibility contract, and do at least two products
   need it? Then it is a **new component**: write the contract first, then tokens, then CSS.

A proposal includes: the problem, screenshots of the current workaround, the contract draft and
the contrast pairs it needs.

## Definition of done for a system change

- [ ] `python3 design-system/scripts/build.py` run; `generated/` committed.
- [ ] `python3 design-system/scripts/validate.py` passes (format, layering, parity, contrast, CSS lint).
- [ ] `python3 -m pytest design-system/tests` passes.
- [ ] New foreground/background pairs added to `contrast-pairs.json`.
- [ ] Contract updated in `docs/component-contracts.md`.
- [ ] Example and docs gallery render the change in light and dark; capture script passes.
- [ ] `CHANGELOG.md` entry with the correct version bump.

## Health signals to review each release

Count, do not guess: number of local overrides of `--ds-*` variables in consuming products,
components with open accessibility issues, deprecated tokens still referenced, and contrast
pairs that pass only by a margin under 0.3 (fragile to future palette tweaks;
`validate.py --report` lists ratios).
