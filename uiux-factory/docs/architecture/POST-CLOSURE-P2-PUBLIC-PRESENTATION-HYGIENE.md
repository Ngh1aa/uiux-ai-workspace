# Post-closure P2 — Public presentation hygiene

Status: **PRODUCTIZATION / PRESENTATION HARDENING — NO RUNTIME AUTHORITY CHANGE**  
Date: **2026-10-03**

P2 improves how the public repository and portfolio-validation guidance communicate truth. It does not reopen A50–A55 and does not create a new runtime architecture phase.

## Scope

P2 covers three presentation/hygiene surfaces:

1. evidence-language clarity for fallback usability walkthroughs;
2. separation of historical planning documents from current root truth;
3. a public-facing README architecture/evidence overview.

## Walkthrough terminology

Previous guidance allowed portfolio headlines such as:

```text
Tested with 5 simulated users
5 synthetic-user walkthroughs
```

Although technically labelled simulated/synthetic, that wording could still be read as participant research.

Current default is therefore:

```text
5 scenario-based expert walkthroughs
5 simulated usage scenarios
```

The scenarios are generated evaluation frames, not research participants. They may be used to structure expert walkthroughs, adversarial QA and before/after re-testing, but they cannot provide:

```text
human participant counts
human quotes
observed human task success
human preference evidence
production impact
```

Real-user evidence remains a separate evidence class and must be supported independently.

## Historical-document boundary

The superseded root planning file:

```text
implementation_plan.md
```

is moved to:

```text
docs/history/implementation_plan.md
```

The content remains preserved for traceability with an explicit superseded warning. `docs/history/README.md` states that history files are not current runtime/provider/architecture truth.

Current truth continues to come from source/tests plus:

```text
START-HERE.md
AGENTS.md
docs/CONTRACT-OWNERSHIP.md
uiux-factory/docs/architecture/README.md
uiux-factory/docs/architecture/CURRENT-RUNTIME-MAP.md
```

## Public README boundary

The root README now presents:

- the repository purpose;
- architecture at a glance;
- target-truth-aware routing;
- canonical ownership;
- evidence classes;
- external collaborator and managed CLI paths;
- verification layers;
- protected-main governance;
- intentional holds;
- current licensing truth.

The README must not convert automated regression into claims about human preference, visual excellence, production impact or release approval.

## Repository metadata truth

At the P2 audit point, GitHub repository metadata is still:

```text
description = null
homepage = null
topics = []
license = null
```

The repository connector available to this workflow can read those fields but does not expose a supported repository-metadata write action. P2 therefore does not fabricate a server-side metadata update.

Suggested owner-applied metadata when/if explicitly chosen:

```text
description:
Evidence-first AI-assisted UI/UX design-engineering workspace with target-truth routing, Flow OS, browser QA and governed GitHub workflows.

topics:
ui-ux
product-design
design-engineering
ai-agents
design-systems
playwright
accessibility
product-design-workflow
```

No homepage is suggested automatically because no canonical product/documentation site is declared by repository truth.

No license is selected automatically. The owner must choose licensing terms explicitly before the repository is presented as generally reusable open source.

## Governance boundary

P2 does not modify:

```text
provider default
lifecycle mutation ownership
routing authority
evidence trust authority
gate authority
release authority
Knowledge OS canonical corpus
A55 intentional holds
P0 target-truth routing semantics
P1 GitHub ruleset enforcement
```

P2 is presentation/hygiene only.

## Verification

The PR must pass the protected-main required checks on the exact final head:

```text
foundation
release-candidate
```

Because P2 adds this note under `uiux-factory/**`, A20 is intentionally triggered rather than leaving the required `release-candidate` check unreported on a docs-only PR.
