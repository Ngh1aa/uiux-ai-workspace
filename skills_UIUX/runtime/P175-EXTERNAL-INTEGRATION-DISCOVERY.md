# P1.7.5 — External Integration Discovery / Provider-Native Evidence

P1.7.5 closes the visibility gap left intentionally by P1.7.4. Static repository markers are useful, but deployment integrations may exist entirely outside the Git tree. P1.7.5 adds a second, read-only evidence channel based on GitHub Deployments and deployment statuses.

## Goal

For every repository in the canonical repository policy registry, Factory now combines repository-static evidence from P1.7.4 with recent provider-native deployment evidence observable through GitHub.

The combined evidence is evaluated by the same canonical policy drift assessor. External discovery is evidence only; it grants no deployment, merge, release, or mutation authority.

## Provider discovery

P1.7.5 recognizes provider signals from deployment creator metadata, environment/task metadata, payload text, deployment status descriptions, and deployment/status URLs.

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

P1.7.5 requires both a readable target checkout for static inspection and a complete GitHub Deployments inspection.

If deployment visibility is unavailable or only partially readable, the combined assessment becomes `UNKNOWN_POLICY_DRIFT`. Static configuration is not allowed to hide loss of visibility into the external channel.

For public repositories, the observer may retry the read-only GitHub endpoint without the Factory token when the repository-scoped Actions token cannot read a public target repository. No write fallback exists.

## Registry semantics

Registered providers accept either `repository-static` or `external-observed` freshness evidence. Removal of a static marker is therefore not incorrectly called provider removal when recent provider-native deployment evidence still proves that the integration exists.

This does not broaden preview or release authority. `allowed_preview_providers`, mutation scope, merge authority, production deployment authority, and release authority remain unchanged.

## Continuous monitoring

`.github/workflows/p175-external-integration-discovery.yml` derives its target matrix from the canonical registry, checks out target repositories read-only, reads GitHub Deployments/status metadata, emits one JSON artifact per target, runs every six hours plus relevant PR/push/manual events, and manages Factory-only `[P1.7.5 EXTERNAL DRIFT]` issues.

Target repositories are never mutated by this monitor.

## Truth boundary

A P1.7.5 PASS proves that, at scan time, static inspection and GitHub deployment visibility completed, recent provider-native evidence is compatible with the registry, no recent unclassified deployment evidence remains, and every registered provider has acceptable current static or recent external evidence.

It does not prove deployment health, visual correctness, production readiness, release approval, or the absence of an integration that leaves neither repository markers nor GitHub Deployment evidence.
