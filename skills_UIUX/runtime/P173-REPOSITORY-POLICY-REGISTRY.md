# P1.7.3 — Repository Policy Registry / Multi-Repo Governance

P1.7.3 moves external side-effect authority out of task/dogfood profiles and into a canonical repository-level registry.

## Authority model

Repository policy is authoritative. Detection is evidence, not permission.

A task may narrow a repository policy, but it may never broaden it. Unknown repositories fail closed with zero remote mutation authority and a zero-deploy-strict preview policy.

The registry owns four independent dimensions:

1. `preview_policy` — `pr-preview-allowed` or `zero-deploy-strict`.
2. `allowed_preview_providers` — providers whose PR-preview side effects are permitted.
3. `mutation_scope` — remote Git/GitHub mutations Factory may perform before owner review.
4. `release_boundary` — merge, production deploy and release authority. These remain owner-controlled for the P1.7.3 canonical targets.

`known_integration_providers` records repository integrations that Factory has evidence for. A known provider does not become authorized merely because it is detected.

## Canonical matrix

| Repository | Preview policy | Known integration | Allowed PR preview provider | Remote mutation scope | Merge / production deploy / release |
| --- | --- | --- | --- | --- | --- |
| `Ngh1aa/Nova` | `pr-preview-allowed` | Vercel | Vercel | branch create/push, PR create/update | denied |
| `Ngh1aa/Lumen` | `zero-deploy-strict` | GitHub Pages | none | none | denied |
| `Ngh1aa/cennext-b2b-prototype` | `pr-preview-allowed` | Vercel | Vercel | branch create/push, PR create/update | denied |
| `Ngh1aa/LuxRoom` | `pr-preview-allowed` | Vercel | Vercel | branch create/push, PR create/update | denied |

## Precedence

1. Resolve canonical policy by repository identity.
2. Apply an optional runtime override only if every requested capability is a subset of canonical authority.
3. Combine registry-known integration evidence with read-only static/PR evidence.
4. Run P1.7.2 external-side-effect assessment.
5. Enforce provider allowlist and mutation scope before transaction construction.
6. Keep release actions outside Factory authority unless a future repository policy explicitly grants them through governance review.

This keeps `assess_external_side_effects()` as the P1.7.2 evaluator. P1.7.3 is an authority layer in front of it rather than a replacement.

## P1.7.1 integration

`AuthenticatedDogfoodProfile` no longer contains `preview_policy`. The authenticated runner resolves repository policy from `profile.repository` before `GitHubTransactionConfig` is constructed. If repository governance does not authorize branch creation, branch push and PR creation, execution stops before remote mutation.

## Live dogfood boundary

The P1.7.3 live lane is read-only. It inspects:

- Nova PR #73 for Vercel evidence;
- CENNEXT PR #8 for Vercel evidence;
- LuxRoom PR #24 for Vercel evidence;
- Lumen's checked-out GitHub Pages workflow as static deployment-integration evidence.

It checks each target `main` SHA before and after evaluation. It contains no production transaction runner, target push, PR creation/update, merge or deployment action.
