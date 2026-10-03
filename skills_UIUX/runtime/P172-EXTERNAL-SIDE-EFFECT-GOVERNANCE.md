# P1.7.2 — External Side-Effect / Preview Governance

P1.7.2 closes a boundary discovered by the authenticated P1.7.1 LuxRoom dogfood: a transaction runner can avoid calling any deploy command while a connected platform such as Vercel still creates a PR preview automatically.

## Canonical owner

Runtime policy lives in:

- `uiux-factory/core/runtime/flow_os/external_side_effects.py`

P1.7 remains the owner of Git/GitHub mutation. P1.7.2 is a preflight/postflight governance layer around that mutation boundary; it does not choose product flows, execute implementation work, merge PRs, or deploy releases.

## Policies

### `pr-preview-allowed`

Remote transaction mutation may proceed. Known or observed PR preview integrations must be recorded as evidence. `PREVIEW_EXPECTED`, `PREVIEW_OBSERVED`, and `UNKNOWN_EXTERNAL_SIDE_EFFECT` are distinct states; preview is never reported as production deployment.

### `zero-deploy-strict`

Fail closed before any remote mutation that could activate an external integration.

- configured or observed integration → `BLOCKED_EXTERNAL_SIDE_EFFECT`
- incomplete integration visibility → `UNKNOWN_EXTERNAL_SIDE_EFFECT` and blocked
- completed inspection with no detected integration → `NONE_DETECTED`

P1.7.2 never disables Vercel, Netlify, GitHub Pages, or another provider automatically.

## Evidence sources

Repository-visible signals:

- `vercel.json` / `.vercel/project.json`
- `netlify.toml`
- GitHub Pages workflow markers such as `actions/deploy-pages`

Live GitHub signals:

- `vercel[bot]` PR comments
- `netlify[bot]` PR comments
- GitHub Actions comments explicitly reporting a Pages deployment

Absence of one static config file is not proof that an external GitHub App integration is absent.

## P1.7.1 integration

The authenticated LuxRoom profile is explicitly `pr-preview-allowed`. Before constructing the GitHub transaction it performs read-only recent-PR inspection. This means side-effect policy is evaluated before the P1.7 transaction can claim/push a remote branch.

The authenticated report now separates:

- `external_side_effect_preflight`
- `external_side_effect_postflight`
- `production_deployment = OUT_OF_SCOPE`

## Real dogfood

P1.7.2 uses existing LuxRoom PR #24 as immutable evidence instead of creating another target branch:

- `pr-preview-allowed` must resolve to `PREVIEW_OBSERVED` with Vercel evidence
- `zero-deploy-strict` must resolve to `BLOCKED_EXTERNAL_SIDE_EFFECT`
- LuxRoom `main` SHA must be unchanged before/after inspection
- target mutation, merge, and deployment by the dogfood workflow are forbidden

The live lane is intentionally read-only and uses `UIUX_TARGET_REPO_TOKEN` only to read repository/PR evidence.

## Boundary

P1.7.2 proves governance of known/observable external side effects. It does not claim that every external system is discoverable from GitHub. Under `zero-deploy-strict`, incomplete visibility is itself a blocking condition rather than evidence of safety.
