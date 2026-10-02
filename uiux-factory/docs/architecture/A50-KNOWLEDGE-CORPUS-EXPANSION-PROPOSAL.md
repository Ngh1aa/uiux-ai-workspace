# A50.6 — Knowledge Corpus Expansion Proposal

Status: **PROPOSAL-ONLY — NO INDEX/RECORD MUTATION**  
Date: **2026-10-02**

## Trigger

A50.6 exists because the completed A50.5R round-two human review crossed the unchanged governance threshold:

```text
expansion_recommendation = CONSIDER_EXPANSION
knowledge_preferred_count = 3/3
baseline_preferred_count = 0
material_regression_count = 0
joint_usefulness_win_count = 3/3
```

That result permits a proposal. It does not permit automatic corpus growth.

Canonical A50.6 governance remains:

```text
index_mutation_allowed = false
record_creation_allowed = false
vector_search_change_allowed = false
current_run_evidence = false
product_evidence = false
authority_effect = none
gate_effect = none
release_effect = none
```

The canonical Knowledge OS index therefore remains exactly three records during A50.6.

## Candidate selection rule

A50.6 intentionally proposes only three new **domain/reference** candidates. It does not populate every empty Knowledge OS category and does not copy methodology from existing skills.

Each candidate must specify:

- proposed record identity;
- official/source provenance and checked date;
- source version/freshness class;
- target domain/stages;
- reusable reference scope;
- methodology explicitly excluded because it remains skill-owned;
- related skill-owner paths;
- duplication and freshness risk;
- expected retrieval value;
- proposal status.

Allowed A50.6 statuses are:

```text
READY_FOR_CONTENT_DRAFT
HOLD_FRESHNESS_REVIEW
REJECT
```

There is deliberately no `ACCEPTED`, `INDEXED`, `ACTIVE` or equivalent state.

## Candidate 1 — EdTech / LTI 1.3

Proposed id:

```text
knowledge.domain.edtech-lti-context-roles-services.v1
```

Domain:

```text
education-edtech
```

Primary source:

```text
https://www.1edtech.org/standards/lti
```

Source check on 2026-10-02 shows 1EdTech describes LTI 1.3 as the current version. The standard defines the learning-platform/remote-tool integration boundary and LTI Advantage services including Assignment and Grade Services, Names and Role Provisioning Services and Deep Linking.

Proposed knowledge scope is limited to protocol/product context:

- platform/LMS versus remote tool boundary;
- institutional/course and role context;
- bounded LTI Advantage service concepts;
- integration terminology useful for product-state and responsibility decisions.

Explicitly excluded as skill-owned:

- education website IA/admissions/content workflow;
- authentication/security implementation procedure;
- generic discovery, UX flow and QA methodology.

Related skill owners:

```text
skills_UIUX/education-website/SKILL.md
skills_UIUX/security-and-privacy/SKILL.md
```

Assessment:

```text
duplication_risk = LOW
freshness = versioned
freshness_risk = LOW
proposal_status = READY_FOR_CONTENT_DRAFT
```

This candidate is ready only for a later content-draft review. It is not accepted into the index by A50.6.

## Candidate 2 — EV charging / OCPP 2.1

Proposed id:

```text
knowledge.domain.ev-charging-ocpp-transaction-semantics.v1
```

Domain:

```text
mobility-ev
```

Primary source:

```text
https://openchargealliance.org/my-oca/ocpp/
```

Source check on 2026-10-02 shows the Open Charge Alliance download surface lists OCPP 2.1 Edition 2 and Errata 2026-06. OCA states Edition 2 incorporates accumulated errata and certification/test material. OCPP 2.1 adds protocol capabilities involving ISO 15118-20, bidirectional charging/V2X, distributed energy resources and expanded smart-charging behavior.

Proposed knowledge scope is limited to charging-domain/protocol semantics that can prevent product work from collapsing real charging-system concepts into generic loading/payment states.

Explicitly excluded as skill-owned:

- generic UI-state inventory and error recovery;
- generic progress/multi-stage workflow methodology;
- electrical engineering, installation or protocol certification procedure.

Related skill owners:

```text
skills_UIUX/state-feedback-and-error-recovery/SKILL.md
skills_UIUX/complex-workflow-and-progress-ux/SKILL.md
```

Assessment:

```text
duplication_risk = LOW
freshness = versioned
freshness_risk = MEDIUM
proposal_status = READY_FOR_CONTENT_DRAFT
```

The medium freshness risk means a later content draft must preserve an explicit source version and re-check current OCA errata before canonicalization.

## Candidate 3 — GenAI / NIST AI 600-1

Proposed id:

```text
knowledge.domain.genai-risk-context-nist-ai-600-1.v1
```

Domain:

```text
ai-software
```

Primary source:

```text
https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence
```

NIST AI 600-1 is a cross-sector Generative AI Profile and companion resource to AI RMF 1.0. It provides reusable risk/context vocabulary and suggested risk-management actions, but it is not a product-design workflow or compliance certificate.

The 2026 freshness check is material: NIST currently states AI RMF 1.0 is being revised. Therefore this candidate is intentionally not ready for drafting/canonicalization.

Explicitly excluded as skill-owned:

- human-AI interaction workflow for capability boundaries, confidence, feedback, correction and human override;
- AI coding-agent implementation guardrails;
- generic trust/transparency UI methodology;
- legal/regulatory compliance advice.

Related skill owners:

```text
skills_UIUX/human-ai-interaction-design/SKILL.md
skills_UIUX/ai-agent-coding-guardrails/SKILL.md
skills_UIUX/trust-credibility-and-transparency/SKILL.md
```

Assessment:

```text
duplication_risk = MEDIUM
freshness = time_sensitive
freshness_risk = HIGH
proposal_status = HOLD_FRESHNESS_REVIEW
```

A later step may reconsider this candidate only after the relevant NIST framework/profile version relationship is re-verified. A50.6 must not convert this HOLD into READY merely to keep all candidates symmetric.

## Executable proposal guard

Canonical proposal artifact:

```text
benchmarks/knowledge-expansion-proposal-v1.json
```

Evaluator:

```text
core/benchmarks/knowledge_expansion_proposal.py
```

Validator:

```text
scripts/validate_knowledge_expansion_proposal.py
```

The evaluator independently re-runs the canonical A50.5R v2 evaluator rather than trusting the proposal's trigger claims.

It also verifies:

- canonical index remains exactly three records;
- proposed record ids are not already indexed;
- candidate domains do not duplicate the three current seed domains;
- sources use HTTPS and carry source version/check provenance;
- related skill-owner paths exist;
- knowledge and excluded methodology scopes are explicit;
- time-sensitive candidates cannot be READY;
- high-risk candidates cannot be READY;
- candidate and top-level authority/gate/evidence/release effects remain none;
- no index/record/vector mutation permission exists.

CI runs this validator before the full pytest suite.

## What A50.6 establishes

A50.6 can establish that:

- human/model-assisted governance justifies evaluating corpus growth;
- three bounded candidates exist with explicit source and ownership review;
- two candidates are reasonable to draft next;
- one candidate is correctly held for freshness rather than forced through;
- the current index has not changed;
- vector search is still unnecessary at this corpus size.

A50.6 does **not** establish that:

- any candidate is already canonical Knowledge OS content;
- source facts are runtime/product evidence;
- a candidate improves user outcomes;
- a drafted record will pass duplication/retrieval/usefulness checks;
- vector retrieval is justified;
- any release gate can pass.

## Next step after proposal verification

If A50.6 merges green, the next implementation should remain bounded:

1. draft **only the READY candidates** (EdTech/LTI and EV/OCPP) as proposed content/metadata on a separate branch;
2. keep GenAI/NIST on HOLD until freshness is re-verified;
3. run source/skill duplication review, deterministic retrieval tests and domain-isolation dogfood before changing `skills_UIUX/knowledge/index.json`;
4. add records to the index only in an explicit accepted implementation PR;
5. keep vector search deferred until corpus breadth or retrieval quality demonstrates a concrete need.
