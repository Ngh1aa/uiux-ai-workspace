# A8.5 — Section-level JIT Skill Retrieval

A8.5 completes the JIT context line without removing the A8 full-skill activation path.

## Goal

Make every section of every skill already routed to the active specialist run reachable without preloading the entire skill document.

The trust model is:

```text
Flow-routed stage.skills
        ↓
run-scoped section index
        ↓ random capability per section
read_skill_section(capability)
        ↓
bounded advisory knowledge expansion
```

A capability is generated only for a skill already selected by the canonical Flow stage. The provider never receives a library-wide section browser.

## Public index vs private registry

For each specialist run the runtime creates two files under its existing `.uiux-agent-runs/<run_id>/` state directory:

- `skill-section-index.json` — provider-readable, metadata only;
- `skill-section-registry.json` — private runtime registry containing capability mapping, retrieval usage and ledger.

Canonical Safe Read has one narrow exception for the public index. The private registry, checkpoint and trace remain blocked by the existing `.uiux-agent-runs` boundary.

The public index contains:

- routed skill name;
- section id and heading;
- heading level;
- source line range;
- section/chunk character count;
- SHA-256;
- opaque run-scoped capability.

It contains no omitted section body.

## Retrieval tool

`read_skill_section` is a read-only runtime tool. Its single argument is:

```text
capability=<run_id>:<opaque-token>
```

The runtime validates the capability against the private registry, re-reads the source skill through canonical Safe Read, verifies the indexed content/hash still matches, applies retrieval budgets, updates the private ledger, and only then returns the bounded section body.

If the source skill changed after indexing, retrieval fails closed and the specialist stage must restart/replan instead of reading stale knowledge.

## Bounding

Runtime policy owns:

```json
{
  "jit_skill_sections": {
    "enabled": true,
    "max_sections_per_skill": 64,
    "max_section_chars": 12000,
    "max_retrievals_per_stage": 24,
    "max_total_retrieved_chars": 120000,
    "max_index_chars": 60000
  }
}
```

Large source sections are split into bounded parts. Index size, retrieval count and cumulative retrieved characters all fail closed at their limits.

## Evidence boundary

A section read is useful context, not proof that the product is correct.

`evidence_from_tool()` records `read_skill_section` as:

```text
type=skill_section_read
trusted=false
origin=runtime
```

The persisted record intentionally omits the section body. It keeps only bounded provenance such as skill, section id, hash, line range and usage counters.

Therefore a section retrieval cannot satisfy a gate or become release evidence.

## Compatibility

A8.5 does not remove or redefine `activate_skill_context`.

Providers may still activate a whole Flow-routed JIT skill when broad context is useful. A8.5 adds a lower-cost path when only one section is needed.

A8.1 strict JIT policy, A8.2 provenance, A8.3 shared provider-context budget and A8.4 resumable specialist continuity remain unchanged.

## Worktree continuity

Section capabilities belong to the specialist run state stored in the source project. If provider writes create the canonical linked Git worktree, section retrieval resolves back to that exact source project's runtime state using only the canonical `.uiux-worktrees/<source-name>/...` shape. No unbounded filesystem search is used.

## Regression coverage

`uiux-factory/tests/test_jit_skill_sections_a8_5.py` proves:

- only routed skills are indexed;
- exact section/hash retrieval works;
- unknown/cross-run capabilities fail closed;
- retrieval budgets are enforced;
- only the public index crosses Safe Read;
- private registry/checkpoint files remain blocked;
- section reads cannot satisfy gates;
- managed provider requests receive the public index and the section-read tool.
