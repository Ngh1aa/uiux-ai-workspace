# Cross-Project Verification — Fix Once, Reuse Safely

This document defines how UIUX Factory prevents a repair discovered in one target project from becoming a project-specific patch that fails on the next project.

## Goal

A bug exposed by Nova, Lumen, CENNEXT, LuxRoom, or a future project should be repaired at the narrowest correct Factory owner and then verified against multiple unlike projects before the repair is promoted as a Factory-level fix.

Passing the project that exposed the bug is necessary but not sufficient.

## Verification levels

Use these states when reporting Factory repairs:

### `PROJECT_FIX_VERIFIED`

The exposing project passes the repaired behavior and its local acceptance evidence.

This proves only that the immediate project is repaired.

### `CROSS_PROJECT_REGRESSION_VERIFIED`

Factory regressions pass and all pinned golden projects pass the same generic dogfood contract.

This proves the repair did not break known stable project snapshots.

### `FACTORY_FIX_VERIFIED`

All of the following pass:

1. Factory unit/regression contract;
2. generic unseen-profile test;
3. pinned golden regression matrix;
4. current-head canary matrix across representative archetypes.

Only this level supports a claim that the Factory repair has been verified as reusable across the currently covered project classes.

It still does not guarantee every future repository shape. New failures must extend the generic contract and representative matrix instead of creating named exceptions in the runner.

## Two real-project lanes

### Golden regression

Golden targets are immutable commit SHAs.

Purpose:

- preserve previously known-good behavior;
- detect regressions introduced by later Factory changes;
- make failures reproducible even when target projects continue evolving.

Current representative set:

- Nova — stateful consumer-fintech/product behavior;
- Lumen — visual/cultural/art-direction experience;
- CENNEXT — B2B/enterprise service workflow;
- LuxRoom — ecommerce catalog/cart/checkout flow.

### Current-head canary

Canaries checkout the target project's current `main` at workflow runtime, bind the actual checked-out SHA, and run the same generic contract.

Purpose:

- catch target-project drift that old golden snapshots cannot expose;
- detect when the Factory's assumptions stop matching current project truth;
- avoid falsely declaring compatibility based only on historical snapshots.

Golden and canary lanes complement each other. Neither replaces the other.

## Generic-runner rule

`RealProjectDogfoodRunner` must remain project-agnostic.

It must not contain branches such as:

```text
if project == "nova": ...
if project == "luxroom": ...
```

Project differences belong in declarative `ProjectDogfoodProfile` data. Routing still belongs to the canonical Goal Interpreter + Flow Resolver.

The test suite must continue proving that the runner accepts a synthetic profile it has never seen before.

## Cross-profile isolation

Each registered profile may declare project-specific isolation markers.

The registry-driven isolation check verifies that one project's profile metadata has not accidentally absorbed another project's concepts. The generic runner itself contains no domain-specific exception list.

When a future project is added:

1. declare its source-truth candidates;
2. declare only evidence paths that really exist and matter;
3. declare its archetype/routing intent/evidence model;
4. add project-specific isolation markers only as data;
5. verify the canonical interpreter chooses the expected change surface from the task wording;
6. never modify generic runner logic merely to make that project pass.

## Fix promotion workflow

When Project A exposes a Factory problem:

```text
Project A exposes failure
        ↓
Classify PRODUCT vs FACTORY ownership
        ↓
Write/extend a generic regression that describes the failure without relying on Project A's name
        ↓
Repair the canonical Factory owner
        ↓
Re-test Project A
        ↓
Run unseen-profile generic contract
        ↓
Run golden matrix
        ↓
Run current-head canary matrix
        ↓
FACTORY_FIX_VERIFIED
```

If Project B fails after Project A passes, do not immediately add a Project B exception. First decide whether:

- the Factory made an invalid universal assumption;
- the profiles are expressing project truth incorrectly;
- the project needs a capability the Factory does not model yet;
- the problem is genuinely project-local.

Repair the earliest responsible generic owner and rerun all downstream gates.

## New-project rule

A newly created project should not require rediscovering already-known Factory bugs.

Before relying on a Factory behavior that previously failed elsewhere:

- the behavior should already have a generic regression;
- the generic runner should not depend on named projects;
- at least one unlike golden project should protect the repaired behavior;
- current-head canaries should remain green.

If the new project reveals a new class of failure, add that class to the reusable contract and representative coverage so the *next* project inherits the repair automatically.

## What this does not mean

Cross-project verification cannot mathematically guarantee compatibility with every future framework, repository topology, domain, or product type.

The guarantee is narrower and truthful:

> A Factory fix is not promoted as reusable merely because the project that exposed it passes. It must survive generic tests plus stable and current real-project representatives, and future failures must strengthen the reusable contract rather than accumulate project-specific patches.
