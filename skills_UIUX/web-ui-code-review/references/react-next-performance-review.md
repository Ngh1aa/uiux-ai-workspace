# React / Next.js Performance Review — Pinned Synthesis

Source reviewed: `vercel-labs/agent-skills@063bee94c3f4df8453406c830b0a7df0f2860278`, `react-best-practices` (MIT).

Use only after detecting React/Next.js and the relevant framework/version from project source.

## Priority order

### P1 — Eliminate waterfalls

Inspect serial `await` chains, nested fetch timing and API/server work that could start earlier or run independently. Prefer restructuring ownership before adding caching as a bandage.

### P2 — Reduce bundle cost

Look for broad/barrel imports, heavy client-only modules, third-party code loaded before needed, and features that could be dynamically or conditionally loaded.

### P3 — Server-side ownership

Check authentication/authorization of server actions, request-level deduplication, cross-request caching only where safe, excessive RSC serialization, shared mutable module state, and opportunities to parallelize independent server data.

### P4 — Client data behavior

Avoid duplicated fetches/listeners and unnecessary persistent browser storage. Treat client-side state/data libraries as project decisions, not mandatory replacements.

### P5 — Re-render behavior

Check effects that merely derive state, unstable/default object props, subscriptions to more state than needed, components defined inside components, and frequent non-urgent updates that can be deferred.

### P6 — Rendering/hydration

Inspect large lists, static JSX recreated repeatedly, SVG complexity, hydration flicker/mismatch, resource hints and long hidden UI trees. Do not suppress hydration warnings unless mismatch is expected and understood.

### P7 — JavaScript hot paths

Only after higher-impact issues, inspect repeated expensive lookups/iterations, storage reads, DOM mutations and avoidable allocation in actual hot paths.

### P8 — Advanced patterns

Use advanced event/ref/effect patterns only when they solve a demonstrated problem. Do not increase conceptual complexity for theoretical optimization.

## Verification discipline

For every performance finding record:

```text
Observed code path:
Expected user/perf consequence:
Measurement available?: yes/no
Fix:
Verification method:
Framework/version fit:
```

Do not state a user-visible performance improvement from static code review alone. Use build/bundle/lab/field evidence appropriate to the claim and project mode.
