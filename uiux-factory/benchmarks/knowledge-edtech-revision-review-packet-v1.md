# A50.9A — EdTech Draft Revision · Blind Human Review Packet

Status: **AWAITING INDEPENDENT HUMAN REVIEW**

Review this packet before opening `knowledge-edtech-revision-mapping-v1.json`.

This is procedural blinding, not cryptographic blinding. The paired outputs are advisory samples authored in a user-directed ChatGPT session; they are not runtime, user-validation or product evidence.

## Task

Define product and UX decisions for an LMS experience that launches an external learning tool. Make service ownership, concrete states and recovery behavior useful to the design team without inventing which LTI services, roles or retry actions the project actually supports.

## Output A

1. Treat the LMS and external learning tool as separate systems and make it clear which side owns the content or action the user is working with.
2. Document the course/class context and user role needed for each integration action rather than assuming every instructor or learner sees the same controls.
3. Separate launching the external tool, choosing content, accessing roster information and sending grades so one successful action is not mistaken for proof that all integration capabilities work.
4. Define empty, unavailable, permission and failure states for integration actions, with recovery guidance that does not blame the user for configuration problems.
5. Validate every displayed capability against the project's actual integration configuration and avoid claiming support for roster, grades or content selection unless the implementation confirms it.

## Output B

1. Model launch, NRPS roster/context access, Deep Linking content selection and AGS grade exchange as separate capability tracks. A successful LTI launch proves only launch success; it must not imply that roster, content selection or grade return are configured.
2. Use concrete states only when project truth can distinguish them: launch can be ready/launched/unavailable/failed; roster can be available/unavailable/role-limited/error; content selection can be available/unavailable/cancelled/failed/selected; grade exchange can be available/unavailable/pending/succeeded/failed.
3. Attach each visible state to an authoritative integration observation and required configured service. For example, roster_available requires confirmed NRPS availability for the current context/role, content_selected requires a usable Deep Linking result, and grade_send_succeeded requires a project-backed AGS exchange result rather than a local grade value.
4. For recovery, distinguish not configured, role/context limited, temporary failure and unknown when the implementation can tell them apart. Preserve LMS/course context, use the configured admin/support path for configuration-owned failures, and show retry/resubmit only when the implementation supports repeating that operation safely.
5. Keep LTI semantics as a truth boundary rather than a UI prescription: do not infer AGS, NRPS or Deep Linking support from LTI 1.3 alone, do not blame the user for configuration-owned failure, and prefer an explicit unknown/unconfirmed state over false success.

## Rubric

Score each output from `0–2` on:

- `correctness`
- `specificity_actionability`
- `relevance_noise`
- `unsupported_claim_risk`
- `decision_usefulness`

Then choose `A`, `B`, `TIE`, or `INSUFFICIENT`, explain briefly, and mark material regression `yes/no`.

```text
EdTech / LTI revision
Preferred: A / B / TIE / INSUFFICIENT
A: correctness ?, specificity ?, relevance ?, risk ?, usefulness ?
B: correctness ?, specificity ?, relevance ?, risk ?, usefulness ?
Reason:
Material regression: yes/no
```

Do not open the mapping file until the case is scored.
