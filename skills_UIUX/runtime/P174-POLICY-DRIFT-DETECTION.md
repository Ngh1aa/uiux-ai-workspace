# P1.7.4 — Policy Drift Detection / Registry Freshness

P1.7.4 turns repository policy freshness into a continuously checked governance contract instead of a manual dogfood step.

## Goal

For every repository registered in `repository_policy_registry.py`, Factory compares the repository's **current, repository-visible integration footprint** against the canonical `known_integration_providers` set.

The monitor is read-only against target repositories. It never creates target branches, pushes commits, creates or updates target pull requests, merges, deploys, or releases.

## Canonical statuses

- `IN_SYNC` — detected providers match the registry and every registered provider satisfies its freshness evidence rule.
- `DRIFT_ADDED_PROVIDER` — the repository now contains integration evidence for a provider missing from the registry.
- `DRIFT_REMOVED_PROVIDER` — the registry still declares a provider whose required current evidence is absent.
- `DRIFT_ADDED_AND_REMOVED_PROVIDER` — both changes happened in one scan.
- `UNKNOWN_POLICY_DRIFT` — the repository checkout/inspection is incomplete; this is not treated as safe.
- `UNKNOWN_UNVERIFIABLE_PROVIDER` — a registered provider lacks a freshness rule.

## Evidence boundary

P1.7.4 deliberately does **not** use registry declarations as detected evidence. Otherwise a provider removed from a repository could never be detected as removed.

P1.7.4 inspects only the `repository-static` evidence channel:

- Vercel: `vercel.json` or `.vercel/project.json`
- Netlify: `netlify.toml`
- GitHub Pages: Pages deployment workflow markers
- Render: `render.yaml` / `render.yml`
- Railway: `railway.json` / `railway.toml`
- Cloudflare: Wrangler config
- Firebase Hosting: `firebase.json` containing a hosting block

A provider whose canonical freshness rule is provider-native-only is outside P1.7.4's removal scope. P1.7.4 must not report that provider as removed merely because it does not inspect the external channel; P1.7.5 owns that evidence.

The detector can discover providers that are not yet allowed. Discovery is evidence, not authority.

## Registry-derived monitoring

The scheduled workflow builds its target matrix directly from `registered_repository_policies()` rather than maintaining a second hard-coded repo list. Registering another repository therefore automatically adds it to freshness monitoring.

## Schedule and alerts

`.github/workflows/p174-policy-drift-detection.yml` runs:

- on relevant Factory pull requests,
- on relevant pushes to `main`,
- every six hours,
- on manual `workflow_dispatch`.

When a scheduled/main/manual run detects drift, the workflow opens or updates a `[P1.7.4 DRIFT] <repository>` issue **inside `uiux-ai-workspace` only**. When the repository returns to sync, that alert is closed automatically.

## Safety boundary

A P1.7.4 PASS proves only that current repository-visible integration evidence matches the canonical registry footprint at scan time.

It does not prove:

- deployment health,
- preview visual correctness,
- production readiness,
- release approval,
- that an externally configured provider with no repository-visible marker does or does not exist.

If a future provider cannot be verified from repository-static evidence, its policy must declare an appropriate evidence channel before Factory can consider the registry fresh.
