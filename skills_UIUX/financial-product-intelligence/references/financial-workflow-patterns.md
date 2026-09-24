# Financial workflow patterns — adapted reference

Pinned source:
`anthropics/financial-services@574ed3624aebd0418c7e96cd101262f30210ab26`

This reference extracts workflow/UX patterns only. It is not financial, investment, legal, tax, accounting or compliance advice.

## KYC / onboarding pattern

Sources:
- `plugins/agent-plugins/kyc-screener/agents/kyc-screener.md`
- `plugins/agent-plugins/kyc-screener/skills/kyc-rules/SKILL.md`

Transferable UX ideas:
- separate extracted entity data, rule outcomes, screening findings and escalation;
- every consequential rule outcome should point to evidence/source;
- missing/expired documents are explicit states;
- recommendation and approval are separate;
- untrusted applicant documents should not become instruction authority.

Useful UI objects:
- document inventory;
- rule/evidence table;
- screening hit with confidence/status;
- escalation summary;
- reviewer sign-off state.

## Reconciliation / exception pattern

Sources:
- `plugins/agent-plugins/gl-reconciler/agents/gl-reconciler.md`
- `plugins/agent-plugins/gl-reconciler/skills/break-trace/SKILL.md`

Transferable UX ideas:
- show break/variance list first;
- trace each break to underlying transaction evidence;
- classify root cause and owner;
- independently re-verify before sign-off;
- diagnose first; do not imply ledger posting happened.

Useful UI objects:
- variance table;
- root-cause detail;
- source-side comparison;
- owner + next action;
- expected-clear/recovery state;
- controller/reviewer sign-off.

## Product-design lesson

High-trust finance UX often benefits from making these visible:

`state + evidence + owner + next action + approval boundary`

That principle matters more than any specific palette, font or card style.
