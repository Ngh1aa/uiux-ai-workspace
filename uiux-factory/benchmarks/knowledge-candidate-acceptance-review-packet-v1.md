# A50.8 — Candidate Acceptance Trial · Blind Human Review Packet

Status: **AWAITING INDEPENDENT HUMAN REVIEW**

Review only this packet before opening `knowledge-candidate-acceptance-mapping-v1.json`.

This is procedural blinding, not cryptographic blinding. The paired outputs were authored in a user-directed ChatGPT session and are advisory samples, not runtime/product evidence.

## Rubric

Score each output from `0–2` on:

- `correctness`
- `specificity_actionability`
- `relevance_noise`
- `unsupported_claim_risk`
- `decision_usefulness`

Score meaning:

- `0` — material weakness or harmful regression
- `1` — acceptable / no meaningful advantage
- `2` — materially stronger for the stated task

Then choose `A`, `B`, `TIE`, or `INSUFFICIENT`, write a short rationale, and mark whether there is a **material regression**.

---

## Case 1 — EdTech / LTI integration boundaries

**Task**

Define product and UX decisions for an LMS experience that launches an external learning tool. Keep platform/tool ownership, course context, roles, roster access, assignment/grade exchange and content selection understandable without inventing which LTI services the project actually supports or claiming that LTI mandates a specific UI.

### Output A

1. Model the integration boundary explicitly as learning platform/LMS versus external tool. Treat launch context and user roles as integration context, not as proof that the product grants a particular permission or displays a particular control.
2. When project truth confirms LTI Advantage services, keep their ownership distinct: NRPS can inform names/roles roster context, AGS can inform assignment/line-item/grade exchange expectations, and Deep Linking can inform tool-provided content selection. Do not show those capabilities as available merely because the integration uses LTI 1.3.
3. For each supported integration capability, define which system is authoritative for the state the user sees, what happens when the capability is unavailable or not configured, and which user role is allowed to initiate the action according to project configuration rather than a guessed role model.
4. Keep launch, roster/context access, content selection and grade exchange as separate product concerns. A successful tool launch must not be presented as proof that roster provisioning or grade return is configured successfully.
5. QA the supported service set against project truth and integration configuration. LTI supplies protocol/service semantics; it does not prescribe the page layout, interaction pattern, institutional role taxonomy or security policy of this product.

### Output B

1. Treat the LMS and external learning tool as separate systems and make it clear which side owns the content or action the user is working with.
2. Document the course/class context and user role needed for each integration action rather than assuming every instructor or learner sees the same controls.
3. Separate launching the external tool, choosing content, accessing roster information and sending grades so one successful action is not mistaken for proof that all integration capabilities work.
4. Define empty, unavailable, permission and failure states for integration actions, with recovery guidance that does not blame the user for configuration problems.
5. Validate every displayed capability against the project's actual integration configuration and avoid claiming support for roster, grades or content selection unless the implementation confirms it.

---

## Case 2 — EV / OCPP charging-session truth

**Task**

Define charging-session states and product claims for an EV charging app/dashboard. Keep user-visible progress useful while avoiding the mistake of collapsing charging-station/backend protocol truth into generic loading/payment states or assuming every OCPP 2.1 capability is supported by the deployed system.

### Output A

1. Separate the user journey into connection/authorization, charging progress, interruption or stop, completion and payment/receipt concerns according to the project's actual system model. Do not use a single spinner or payment state as a substitute for charging-system truth.
2. Identify which backend or station observation supports each user-visible state, and mark states unavailable when the project cannot distinguish them reliably instead of inventing precision.
3. Treat smart-charging, bidirectional/V2X or energy-management features as optional capabilities that require explicit implementation evidence before they appear in the UI or marketing copy.
4. Keep charging completion, payment settlement and connector availability as separate concerns so a successful payment does not imply that energy transfer started or completed successfully.
5. QA interrupted, delayed, stopped and completed sessions against the project's real station/backend behavior, with recovery wording that reflects what the system actually knows.

### Output B

1. Use OCPP as charging-station/backend context rather than as a UI state machine. Product states should map to observations the deployed charging system can actually provide, while transaction/protocol semantics remain separate from payment presentation and generic loading feedback.
2. Keep charging-session truth distinct from adjacent concerns: station/connector availability, authorization, energy-transfer progress, transaction interruption/completion and payment/receipt status should not silently prove one another unless project evidence explicitly links them.
3. Treat OCPP 2.1 capabilities such as ISO 15118-20-related support, bidirectional/V2X, DER control and richer smart-charging behavior as conditional product context. Their presence in the standard is not proof that a charger, backend or deployment supports them.
4. For each visible charging state, record the station/backend observation that justifies it and define what the UI says when the observation is delayed, unavailable or contradictory. Prefer an explicit unknown/awaiting-confirmation state over false certainty.
5. QA session interruption, stop/completion, delayed backend updates and capability-gated features against the deployed protocol/backend configuration. OCPP reference knowledge constrains terminology and system boundaries; it does not authorize electrical, certification, billing or interoperability claims.

---

## Review template

```text
EdTech / LTI
Preferred: A / B / TIE / INSUFFICIENT
A: correctness ?, specificity ?, relevance ?, risk ?, usefulness ?
B: correctness ?, specificity ?, relevance ?, risk ?, usefulness ?
Reason:
Material regression: yes/no

EV / OCPP
Preferred: A / B / TIE / INSUFFICIENT
A: correctness ?, specificity ?, relevance ?, risk ?, usefulness ?
B: correctness ?, specificity ?, relevance ?, risk ?, usefulness ?
Reason:
Material regression: yes/no
```

Do not open the mapping file until both cases are scored.
