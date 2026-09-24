---
name: financial-product-intelligence
description: Provides product/UX intelligence for financial-services interfaces and websites by classifying the financial workflow, actors, trust pressure, decision states, evidence and human-approval boundaries before visual design. Use for fintech, banking, payments, settlement, treasury, ledger/reconciliation, KYC/AML, wealth or investment products; do not use as investment/compliance advice or as a fixed visual style preset.
---

# Financial Product Intelligence

## Purpose

Translate a financial-services brief into product and UX constraints before art direction.

Do **not** reduce finance to "navy + gold", dashboards or generic trust badges.

Start with:

`workflow → actors → decision objects → state/risk → evidence → approval/recovery → visual language`

## Step 1 — Classify the archetype

Use the routed `product_archetype` when available:

- **payments-infrastructure** — settlement, payment rails, treasury, payout, remittance, acquiring, orchestration, ledgers;
- **compliance-operations** — KYC/AML, sanctions/PEP, onboarding, due diligence;
- **financial-operations** — reconciliation, GL/subledger, exception handling, close/fund admin;
- **consumer-banking** — spending, saving, cards, goals, everyday money;
- **investment-wealth** — portfolios, brokerage, advisory, asset/wealth workflows.

If evidence is insufficient, keep the archetype generic rather than guessing.

## Step 2 — Map actors and authority

Identify:

- primary operator/user;
- reviewer/approver;
- counterparty/customer where relevant;
- system/source of record;
- who may recommend;
- who may approve or execute.

A UI that displays a recommendation must not imply the system approved or executed it unless that is verified project truth.

## Step 3 — Model the state machine

Financial UX is often state-heavy. Make important states explicit:

- received / pending / validating;
- matched / unmatched;
- routed / failed / retrying;
- review required / escalated;
- settled / paid / reversed;
- verified / missing evidence.

Use the project's real states when known. Do not invent regulatory or operational states.

## Step 4 — Evidence and traceability

For consequential decisions, expose the evidence needed to understand "why":

- source/reference;
- timestamp;
- transaction/entity identifier;
- rule or reason;
- owner;
- next action;
- recovery/escalation path.

Prefer traceable rows, ledgers, timelines, exception lists and decision summaries when they match the workflow.

## Step 5 — Trust without fake proof

Trust comes from:

- clear process;
- provenance;
- state visibility;
- explicit ownership;
- honest limitations;
- predictable recovery;
- appropriate human sign-off.

Never invent certifications, compliance status, approval rates, uptime, settlement speed, SLA, risk score, testimonials or performance metrics.

## Step 6 — Art-direction implications

Derive visual direction from the archetype and audience rather than from "finance" alone.

Examples:

- institutional infrastructure → precise, restrained, information-dense, state-legible;
- consumer banking → approachable, calm, mobile-native, everyday-language;
- compliance/ops → evidence-first, exception-focused, high legibility;
- investment/wealth → analytical hierarchy with careful uncertainty framing.

These are biases, not fixed palettes/fonts.

## Human-decision boundary

Patterns adapted from Anthropic Financial Services repeatedly separate machine-produced analysis from human approval/sign-off. Preserve that distinction in UI copy, states and interaction whenever project truth requires it.

This skill does not provide investment, legal, tax, accounting or compliance advice.

## Progressive reference

Read [references/financial-workflow-patterns.md](references/financial-workflow-patterns.md) when a finance project needs deeper workflow/state examples.

## Acceptance criteria

- Financial archetype is explicit or truthfully left generic.
- Actors, decision authority and source-of-record are distinguishable.
- Critical states and recovery/escalation paths are visible.
- Claims do not exceed evidence.
- Visual direction follows product/audience/trust needs, not a universal fintech style.
