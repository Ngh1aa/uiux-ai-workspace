# P1.7 — GitHub-Native Production Runner / Transaction Boundary

## Purpose

P1.7 moves UIUX Factory from a governed real subprocess runner to a governed Git/GitHub transaction boundary.

The execution chain is:

```text
WorkExecutionPlan
→ ExecutionDriver
→ GitHubProductionRunner
→ deterministic transaction branch
→ routed segment worker
→ implementation commit / preview / browser QA evidence
→ bounded repair loop
→ pull request handoff
```

P1.7 does **not** replace routing, sequence decomposition, execution-state gates, QA semantics, deployment truth or release authority.

## Canonical ownership

- P1.4 owns multi-intent work decomposition.
- P1.5 owns `pending/runnable/running/passed/failed/blocked` state and artifact gates.
- P1.6 owns concrete runner dispatch, registry/checkpoint and QA-to-repair coordination.
- P1.7 owns only the Git/GitHub target-mutation transaction.

The canonical implementation is `uiux-factory/core/runtime/flow_os/github_transaction.py`.

## Transaction identity and branch isolation

Every production transaction requires an explicit `transaction_id`. The runner derives one deterministic branch:

```text
<branch-prefix>/<transaction-slug>-<sha256-prefix>
```

The configured base branch is never used as a mutation target. The runner rejects a transaction branch that resolves to the base branch and asserts the checked-out branch before every commit/push boundary.

The first transaction operation creates an empty branch-claim commit carrying:

```text
UIUX-Transaction: <transaction-id>
UIUX-Lease-Owner: <lease-owner>
UIUX-Base-SHA: <base-sha>
```

This claim is pushed only to the transaction branch.

## Lease and concurrency fences

P1.7 uses two complementary fences:

1. **Local TTL lease** — an atomic file lease prevents two processes sharing one transaction workspace from mutating concurrently.
2. **Remote branch ownership + CAS** — the latest remote transaction commit must retain the expected transaction/lease provenance, and implementation updates push through `--force-with-lease` using the last observed remote SHA.

If another writer moves or takes over the transaction branch, P1.7 returns `TRANSACTION_LEASE_CONFLICT`. It does not overwrite the branch.

## Segment mutation policy

Audit, design and QA are read-only against target source. Their workers may emit evidence outside the repository checkout, but if they change tracked/untracked target files the runner restores the checkout and returns `UNAUTHORIZED_TARGET_MUTATION`.

Only the implementation segment, including a P1.6 repair rerun, may create a target commit.

Implementation commits carry:

```text
UIUX-Transaction: <transaction-id>
UIUX-Segment: <segment-id>
UIUX-Runner-Mode: normal|repair
UIUX-Lease-Owner: <lease-owner>
UIUX-Base-SHA: <base-sha>
```

The resulting commit is emitted as an `implementation-artifact` with branch, transaction, mode and commit SHA provenance.

## Preview and browser QA

Before the routed QA worker runs, P1.7 may execute one declared `preview_command` inside the transaction checkout.

Its stdout/stderr/return code are persisted as `preview-evidence`.

A preview failure returns `BUILD_FAILED` and prevents PR creation. A QA failure remains a product failure and is returned unchanged to P1.6; P1.6 then resets the correct repair owner and supersedes the stale implementation artifact.

P1.7 does not relabel product QA failures as infrastructure failures.

## Pull request finalization

A PR is created only after:

- an implementation commit exists,
- preview succeeds when configured,
- the routed QA worker passes,
- P1.6 output requirements remain satisfiable.

The GitHub REST client uses **find-or-create** semantics for the deterministic head/base pair. Re-running finalization reuses the existing PR rather than creating a duplicate.

PR provenance is emitted as a `pull-request` evidence artifact with:

- PR number and URL,
- transaction ID,
- head branch,
- base branch,
- latest implementation commit SHA,
- whether the PR was newly created or reused.

P1.7 never merges the PR.

## Cancellation

A transaction has an explicit cancellation marker. It is checked before checkout/claim, after worker execution, and immediately before commit/push boundaries.

A cancelled run returns `TRANSACTION_CANCELLED`, releases its local lease and does not continue to the next mutation boundary.

## Persistence and resume

P1.7 persists `transaction-state.json` under the transaction workspace. It records:

- transaction/base/head identity,
- lease owner,
- base SHA,
- branch claim SHA,
- last observed remote SHA,
- last implementation commit SHA,
- per-segment commit provenance,
- runner invocation count,
- PR number/URL,
- transaction status.

`ProfessionalWebsiteFlow.resolve_github_execution_driver()` also places the P1.6 execution checkpoint in the transaction directory by default. A restart can therefore recover both the workflow state and the Git/GitHub transaction state without inventing completed work.

## Failure classes

P1.7 may produce:

- `TRANSACTION_CANCELLED`
- `TRANSACTION_LEASE_CONFLICT`
- `BRANCH_ISOLATION_FAILED`
- `UNAUTHORIZED_TARGET_MUTATION`
- `BUILD_FAILED`
- `GITHUB_TRANSACTION_FAILED`

Product QA failures such as `PRODUCT_QA_FAILED` pass through unchanged so the P1.6 repair owner remains authoritative.

## Evidence and CI

`.github/workflows/p17-github-production-transaction.yml` validates P1.7 against a real local bare Git origin and a GitHub REST-compatible PR fixture.

The dogfood covers:

- real clone and transaction branch claim,
- base branch immutability,
- implementation commit + push,
- commit trailers/provenance,
- preview evidence,
- QA failure → implementation repair → QA rerun,
- superseded old implementation evidence,
- PR creation and idempotent reuse,
- active lease conflict,
- cancellation before mutation,
- read-only phase mutation rejection,
- remote branch takeover rejection.

The evidence runner writes `github-production-transaction.json` and uploads it from the dedicated P1.7 workflow.

## Safety boundary

P1.7 is a branch-write transaction runner, not a release engine.

A green P1.7 run proves that the governed transaction reached a QA-backed PR handoff under the tested contract. It does not prove deployment, merge authorization, production health or release success. Those claims remain owned by their existing deployment/release evidence gates.
