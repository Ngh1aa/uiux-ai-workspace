# A43.3 — Routing Benchmark

Status: **IMPLEMENTED / FINAL VERIFICATION PENDING**  
Date: **2026-10-02**  
Depends on: A43.1 Flow Selection Engine + A43.2 JIT Context Loader

## 1. Purpose

A43.3 adds a deterministic regression benchmark for the routing system already owned by canonical Flow OS.

The benchmark measures:

```text
natural-language task
→ Task Contract / change surface
→ canonical declarative flow
→ selected stage
→ mandatory skill envelope
→ routed JIT skill envelope
```

It is an evaluation surface only. It does not participate in production routing and cannot modify flows, skills, authority, gates or runtime policy.

Canonical corpus:

```text
benchmarks/routing-v1.json
```

Evaluator:

```text
core/benchmarks/routing_regression.py
```

CLI:

```text
scripts/validate_routing_benchmark.py
```

Tests:

```text
tests/test_routing_benchmark_a43.py
```

## 2. Production path under test

Each benchmark case is evaluated through current production owners:

```text
GoalInterpreter
→ Task Contract
→ A43.1 Brain adapter
→ canonical FlowPlanner
→ canonical ResolvedStage / SkillResolver output
→ A43.2 JIT projection
```

The Brain benchmark does not implement its own classifier, resolver or skill router.

## 3. Corpus coverage

`routing-v1.json` contains 32 representative cases and covers all canonical change surfaces:

```text
MICRO
FOCUSED
PAGE
REDESIGN
PRODUCT
```

Coverage includes:

- atomic visual fixes;
- section/component-cluster work;
- single page/route work;
- whole-site redesign;
- broad product/website builds;
- narrow portfolio changes that must not trigger the broad career flow;
- broad portfolio work that must use `portfolio-career-system`;
- FinTech / payments;
- Lumen-style art/culture;
- CENNEXT-style industrial services;
- travel/tourism;
- mobility/EV;
- EdTech;
- AI software;
- production-learning and real-user-validation lanes;
- English and Vietnamese task wording.

## 4. What a case may assert

Every case requires:

```text
id
goal
expected_surface
expected_flow
```

Optional assertions include:

```text
expected_domain
expected_website_type
stage_id
mandatory_contains
jit_contains
tags
```

Skill assertions are subset assertions, not exact-array snapshots. This prevents harmless ordering/additive changes from becoming false regressions while still protecting essential routing behavior.

## 5. Strict corpus rules

The loader rejects:

- unknown top-level/case fields;
- duplicate IDs;
- unknown change surfaces;
- skill expectations without a `stage_id`;
- corpora with fewer than 20 cases;
- corpora that do not cover all five canonical change surfaces.

The current corpus intentionally exceeds the minimum with 32 cases.

## 6. Read-only guarantee

The benchmark is not another router.

Tests hash every declarative flow file under:

```text
skills_UIUX/flows/*.json
```

before and after a full benchmark run and require byte-identical hashes.

The report also records:

```text
routing_mutation = false
authority_effect = none
```

These values describe the benchmark contract only; they do not grant authority.

## 7. CI integration

The main Factory CI now validates both benchmark families:

```text
python scripts/validate_benchmark_corpus.py
python scripts/validate_routing_benchmark.py
```

This means routing regressions fail CI before merge.

The existing UI/UX product benchmark remains separate because it measures product/evidence coverage rather than Task Contract / Flow OS routing.

## 8. Failure semantics

A routing case fails when any declared expectation differs from production behavior.

Examples:

- task expected `MICRO` but Task Contract returns `PAGE`;
- expected `portfolio-career-system` but canonical planner selects the broad fallback;
- expected financial domain is not inferred;
- required stage is missing;
- expected mandatory/JIT skill is absent.

A failed benchmark reports the actual routing result. It never patches production routing automatically.

Any intentional routing behavior change must update production routing first, then update benchmark expectations with explicit review.

## 9. Acceptance criteria

A43.3 is complete when:

- [x] corpus has at least 30 representative cases;
- [x] all five change surfaces are covered;
- [x] narrow-vs-broad portfolio behavior is represented;
- [x] major current product domains/projects are represented;
- [x] lifecycle-sensitive JIT skill expectations are represented;
- [x] evaluation uses canonical GoalInterpreter/FlowPlanner/ResolvedStage behavior;
- [x] benchmark cannot mutate declarative flow files;
- [x] routing benchmark is executed in main Factory CI;
- [x] failures report actual vs expected routing rather than auto-repairing production policy;
- [ ] final PR head passes UIUX Factory CI and A20 release-candidate regression/dogfood.

## 10. Handoff

After A43.3 is green and merged, A44.1 should begin **Core Design Critics**:

```text
existing VisualCritic adapter
UX / IA Critic
Design System Critic
Accessibility Critic
```

A44.1 must adapt existing visual-critique primitives rather than creating a competing visual QA system. Critics remain advisory and cannot self-pass runtime gates.
