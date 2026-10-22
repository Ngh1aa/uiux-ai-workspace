# A10 — Vision Creative Director

A10 adds an executable multi-screen visual-review layer on top of trusted BrowserQA screenshots while preserving the A7 rule that model interpretation is advisory rather than authority.

## Pipeline

```text
trusted browser_render records
        ↓
A7 screenshot path/hash/signature revalidation
        ↓
multi-screen Vision Creative Director
        ↓
KEEP / REVISE / REMOVE guidance
        ↓
earliest_owner routing hints
```

The analyzer receives local screenshot paths plus route/viewport/hash metadata. Image bytes are never copied into runtime JSON artifacts.

## Output vocabulary

The automated review deliberately borrows the human creative-review vocabulary without reusing the authoritative `CreativeDirective` contract:

```text
overall_direction
keep[]
revise[]
remove[]
notes[]
```

Every KEEP/REVISE/REMOVE item must cite one or more exact screenshot `evidence_refs` supplied by the runtime. Invented refs fail closed.

A `revise` item contains:

```text
priority: P0 | P1 | P2
route
section
earliest_owner
problem
instruction
success_criteria
confidence
evidence_refs[]
```

Allowed earliest owners match the existing creative-review stage vocabulary, but the field is a routing hint only. It does not mutate the Flow.

## Human CreativeDirective remains authoritative

A10 never constructs `core.contracts.creative_review_schema.CreativeDirective`.

That contract accepts authoritative human/external reviewer input and includes `status=approved|revise`. Automated vision output is intentionally separate and has no `approved`, `pass`, `gate`, `merge`, `release`, `deploy`, `authority` or `decision` field. Such keys are rejected recursively.

This prevents a vision model from accidentally entering the authoritative reviewer path.

## Analyzer configuration

The runtime provides an operator-configured command adapter. No provider is silently selected.

Configuration uses:

```text
UIUX_VISION_CREATIVE_COMMAND_JSON
UIUX_VISION_CREATIVE_ANALYZER_NAME
UIUX_VISION_CREATIVE_MODEL
UIUX_VISION_CREATIVE_COST_CLASS
```

`UIUX_VISION_CREATIVE_COMMAND_JSON` is a JSON argv array and is executed with `shell=false`. Input is one JSON document on stdin and output must be one bounded JSON object matching the A10 contract.

No command configured means:

```text
status=NOT_RUN
```

The runtime still validates all screenshot evidence but manufactures no aesthetic PASS or approval.

External analyzers require `vision_creative_director.allow_external=true`. The repository default remains `false`, preserving the no-hidden-paid-provider rule.

## CLI

From the repository root:

```bash
python -B skills_UIUX/scripts/vision-creative-review.py \
  --artifacts-dir artifacts/browser-pack
```

Relative artifact paths are resolved below `uiux-factory/qa`. The CLI first collects trusted `browser_render` records through the canonical Playwright adapter, then runs A10.

## Coverage

A10 reports screenshot, route and viewport counts plus whether the configured recommended viewport coverage was met. Coverage metadata is descriptive; it does not convert an automated review into a gate.

## Trust boundary

Every result carries:

```text
advisory_only=true
trusted=false
authority_effect=none
gate_effect=none
merge_effect=none
release_effect=none
```

The screenshot file/hash remains trusted runtime evidence. Creative interpretation remains model-authored guidance.

## Regression coverage

`uiux-factory/tests/test_vision_creative_director_a10.py` proves:

- zero-cost/no-analyzer mode validates evidence without manufacturing a verdict;
- multi-screen viewport coverage is reported;
- valid KEEP/REVISE/REMOVE output is grounded in exact evidence refs;
- invented evidence refs fail closed;
- approval/pass-style authority keys are rejected;
- external analyzers require explicit policy opt-in;
- screenshot hash mismatches fail closed;
- command analyzers are never enabled implicitly.
