# P1.7.5 — External Integration Discovery / Provider-Native Evidence

P1.7.5 closes the visibility gap left intentionally by P1.7.4. Static repository markers are useful, but deployment integrations may exist entirely outside the Git tree. P1.7.5 adds a second, read-only evidence channel based on GitHub Deployments, deployment statuses, and provider-owned Check Runs on the default branch.

## Goal

For every repository in the canonical repository policy registry, Factory now combines repository-static evidence from P1.7.4 with recent provider-native deployment evidence observable through GitHub.

The combined evidence is evaluated by the same canonical policy drift assessor. External discovery is evidence only; it grants no deployment, merge, release, or mutation authority.

## Provider discovery

P1.7.5 recognizes provider signals from deployment creator metadata, environment/task metadata, payload text, deployment status descriptions/URLs, and Check Run app/name/details metadata.

Current classifier coverage:

- Vercel
- Netlify
- GitHub Pages
- Render
- Railway
- Cloudflare Pages / Workers
- Firebase Hosting

A recent deployment that cannot be attributed becomes explicit `unknown-external` evidence. It is not silently ignored.

## Freshness window

Provider-native evidence is activity evidence, not permanent configuration evidence. By default only deployment activity within the most recent 90 days is eligible. Older deployment history is reported as stale and does not keep a registry provider artificially alive forever.

Repository-static evidence remains non-expiring while the marker exists.

## Fail-closed visibility

P1.7.5 requires both a readable target checkout for static inspection and complete GitHub Deployments/status + default-branch Check Run visibility.

If deployment or Check Run visibility is unavailable or only partially readable, the combined assessment becomes `UNKNOWN_POLICY_DRIFT`. Static configuration is not allowed to hide loss of visibility into the external channel.

For public repositories, the observer may retry the read-only GitHub endpoint without the Factory token when the repository-scoped Actions token cannot read a public target repository. No write fallback exists.

## Registry semantics

Freshness requirements are provider-specific, not a global OR. Nova, CENNEXT and LuxRoom require Vercel through `repository-static` evidence and GitHub Pages through `external-observed` evidence. Lumen requires both Vercel and GitHub Pages through repository-static evidence. External Vercel activity therefore does not substitute for a removed `vercel.json` marker.

This does not broaden preview or release authority. `allowed_preview_providers`, mutation scope, merge authority, production deployment authority, and release authority remain unchanged.

## Canonical dogfood finding

The first real P1.7.5 run exposed registry drift that P1.7.4 could not see: Nova, CENNEXT and LuxRoom all had repeated recent GitHub Pages Deployment records alongside Vercel, while their registry entries declared only Vercel. The registry was updated to record GitHub Pages as a known external integration for those three repositories.

This discovery does **not** authorize GitHub Pages preview mutation. `allowed_preview_providers` remains Vercel-only for Nova, CENNEXT and LuxRoom; GitHub Pages is a known deployment boundary, not a permitted PR-preview provider.

## Continuous monitoring

`.github/workflows/p175-external-integration-discovery.yml` derives its target matrix from the canonical registry, checks out target repositories read-only, reads GitHub Deployments/status and Check Run metadata, emits one JSON artifact per target, runs every six hours plus relevant PR/push/manual events, and manages Factory-only `[P1.7.5 EXTERNAL DRIFT]` issues.

Target repositories are never mutated by this monitor.

## Truth boundary

A P1.7.5 PASS proves that, at scan time, static inspection plus GitHub deployment/status and Check Run visibility completed, recent provider-native evidence is compatible with the registry, no recent unclassified deployment evidence remains, and every registered provider satisfies its own declared freshness channel (`repository-static` or `external-observed`).

It does not prove deployment health, visual correctness, production readiness, release approval, or the absence of an integration that leaves neither repository markers nor GitHub Deployment or provider Check Run evidence.
