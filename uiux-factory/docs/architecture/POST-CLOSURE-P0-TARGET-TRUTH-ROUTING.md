# Post-closure P0 — Target-truth-aware external routing

Status: **PRODUCTIZATION / RELIABILITY HARDENING — NO NEW RUNTIME AUTHORITY**  
Date: **2026-10-03**

This task is not A56 and does not reopen the closed A50–A55 architecture-upgrade sequence. It fixes a post-closure routing weakness discovered while reviewing how external collaborators actually use the workspace.

## Problem

Before this hardening, external task manifests were resolved primarily from natural-language task text:

```text
goal text
→ GoalInterpreter
→ FlowPlanner
```

The GitHub-native runner already checked out the target repository, but that checkout was used mainly for SHA/file snapshot evidence. Structured project truth such as `.uiux-profile.json` or `PROJECT-CONTEXT.md` did not participate in Task Contract routing before Flow resolution.

That meant a short task such as “continue this project” could fall back to generic domain/archetype routing even when the target repository already contained stronger project truth.

## Current pipeline

```text
checked-out target repository
→ TargetTruthProbe

natural-language task
→ GoalInterpreter

TargetTruthProbe + GoalInterpreter
→ truth-aware Task Contract merge
→ explicit caller overrides
→ final contract coherence
→ FlowPlanner
```

The target probe runs before Flow planning.

## Truth sources

The probe is bounded and deterministic. It reads only known routing sources, in priority order:

```text
.uiux-profile.json
PROJECT-CONTEXT.md
PROJECT_CONTEXT.md
package.json + README.md fallback
```

Structured sources are preferred. README/package metadata is fallback inference only and may fill generic stable-identity gaps; it cannot overwrite a specific task-inferred identity.

Declared structured sources remain bounded to the target root. A truth source that resolves outside the target root, including a symlink escape, fails closed.

Malformed declared `.uiux-profile.json` fails closed rather than being silently ignored. Placeholder values such as `UNKNOWN`, `TBD`, `N/A` or template markers do not override task inference.

## Routing fields

Target truth is restricted to:

```text
website_type
domain
product_archetype
validation_lane
mode
risk
features
```

It cannot supply or mutate:

```text
authority
release authorization
provider/model selection
gate results
evidence verdicts
merge/deploy permission
```

Every accepted truth-derived field carries source/provenance and explicit `authority_effect = none`, `evidence_effect = none`, `release_effect = none` metadata.

## Vocabulary normalization

Target projects may use more specific or older vocabulary than the canonical Task Contract. The probe normalizes recognized values before routing.

Example:

```text
consumer_fintech_personal_banking
→ domain = financial-services
→ product_archetype = consumer-banking

interactive_prototype
→ mode = interactive-prototype
```

Unrecognized structured product-archetype values may remain a normalized slug when they do not conflict with canonical domain semantics. Unknown routing values never become authority.

## Precedence and coherence

The declared precedence is:

```text
explicit caller override
> structured target-project truth
> natural-language goal inference
```

The merge is intentionally conservative rather than a blind field overlay:

- structured stable identity (`website_type`, `domain`, `product_archetype`) can override task inference;
- structured lifecycle values (`mode`, `risk`, `validation_lane`) act as project defaults and do not erase a non-default lifecycle request explicitly inferred from the current task;
- target features are additive with task-inferred features;
- README/package fallback only fills generic stable-identity gaps;
- product archetypes remain bound to the final domain and are reset/rejected when their source domain does not survive the merge;
- explicit caller overrides are applied last;
- derived `risk` / `validation_lane` defaults are recomputed when upstream routing truth changes and the current task did not already provide a stronger lifecycle signal.

The final Task Contract records:

```text
target_truth
routing_provenance.precedence
routing_provenance.field_sources
routing_provenance.explicit_override_fields
routing_provenance.derived_fields
routing_provenance.merge_diagnostics
```

## External collaborator surfaces

### GitHub-native runner

`skills_UIUX/scripts/github-external-agent-runner.py` passes its already checked-out `target_root` into manifest compilation. The generated handoff records probe status, truth sources, applied routing fields and precedence.

### Lightweight CLI

`skills_UIUX/scripts/prepare-external-task.py` accepts optional:

```text
--target-root <checked-out-project>
```

When omitted, the manifest truthfully records `target_truth.status = NOT_PROVIDED` and falls back to task inference. It does not pretend that project truth was inspected.

## Authority boundary

Effective authority remains:

```text
min(caller-granted authority, authority requested by current task language)
```

Target-project files do not participate in that calculation. A project file containing `release_authorization`, `merge_and_deploy`, or similar text cannot escalate the external collaborator.

## Regression boundary

P0 must preserve the existing closed architecture program and its five intentional holds. It does not alter:

```text
provider default migration
lifecycle mutation convergence
GenAI/NIST freshness hold
vector/semantic retrieval hold
compatibility-shim removal governance
```

Required verification includes:

```text
UIUX Factory CI
A20 release candidate
Routing Intelligence Contract
A13 Nova real-project dogfood
A14 cross-project isolation
A37 external-agent E2E dogfood
```

P0 is complete only when these routing changes pass the exact final PR head without weakening authority/evidence/release boundaries.
