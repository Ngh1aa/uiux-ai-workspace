# Factory Default Website Delivery Policy

The UIUX Factory defaults to `adaptive-prompt-os-v4` for website delivery.

Canonical upstream source:

```text
Ngh1aa/skills_UIUX@e8ed8c9212d20edb2cf4c8c0881fff34add7076e
```

Machine-readable Factory lock:

```text
config/default-website-delivery.json
```

Vendored policy:

```text
../skills_UIUX/policies/adaptive-prompt-os-v4.json
../skills_UIUX/DEFAULT-WEBSITE-DELIVERY-POLICY.md
```

## Factory lane

`DevelopmentManager` is the A→Z substantial-work orchestrator, so its default lane is:

```text
full_prompt_os
```

The task context written into `flow-plan.json` carries:

```json
{
  "delivery": {
    "policy": "adaptive-prompt-os-v4",
    "lane": "full_prompt_os"
  }
}
```

The full substantial lifecycle is:

```text
Prompt 0 — Project Config
→ Prompt 1 — Research / Audit / Design Contract
→ Prompt 2 — Representative-first structural implementation
→ Prompt 3 — Rendered QA + remediation + human visual veto
→ Prompt 4 — Authorized release + production smoke
```

## Lightweight work

Bounded local/component fixes should not invoke the A→Z manager merely to satisfy ceremony. Project/task routing uses the smallest safe skill graph and focused verification, then escalates to the full lane if the root cause becomes structural, shared-owner, cross-route, art-direction, production/high-risk or otherwise material.

## Non-negotiable completion rules

- broad implementation follows passed research/design contract for substantial work;
- multi-page/journey/whole-site work uses a representative rendered gate before broad rollout;
- build success is not visual proof;
- screenshots must be opened and inspected for visual completion;
- visible defects override automated scores;
- substantial visual work requires Creative Director `KEEP / REVISE / REMOVE` judgment;
- system reality remains explicit;
- deployment requires authorization;
- when deployment occurs, deploy success does not replace production smoke or stale-asset/version checks.

Project-specific `.uiux-profile.json`, current user instructions and passed project Design Contracts may refine the policy, but cannot silently weaken truth/evidence/release boundaries.
