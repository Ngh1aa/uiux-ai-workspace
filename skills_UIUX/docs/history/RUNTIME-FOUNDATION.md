# V5.2 Agent Runtime Foundation (candidate)

`skills_UIUX` remains a skills-first, provider-neutral UI/UX operating system. This foundation adds an executable runtime layer around the existing skills without turning runtime concerns into more `SKILL.md` packages.

## Layer model

```text
knowledge / policy
  SKILL.md
      ↓
context + routing
      ↓
provider-neutral agent harness
      ↓
tool / MCP / integration adapters
      ↓
evidence + evals + trace + checkpoints
```

## Boundary

- Skills own `WHEN / WHY / HOW / GATES`.
- Tools own executable `DO`.
- MCP is an integration protocol, not a design skill.
- Playwright is rendered-browser evidence tooling, not a visual-design skill.
- Figma MCP / Code Connect is a design-to-code context bridge, not project truth.
- Tracing records what happened; it does not make a bad result correct.
- Checkpoints provide local resumability; they are not distributed workflow durability.
- Critical external actions (merge, deploy, destructive mutation, payment, production data) remain human-authorized.

## Candidate capabilities

- context manifest + budget telemetry;
- runtime tool contracts and risk/authority policy;
- provider-neutral single-agent harness;
- role manifests for research / implementation / QA and serial handoff boundaries;
- JSONL tracing with secret-field redaction;
- local atomic checkpoints + resume;
- optional MCP v2 server adapter (`runtime/mcp_server.py`);
- optional Playwright rendered evidence capture;
- Figma MCP / Code Connect mapping contract;
- optional n8n automation boundary;
- runtime validators and eval coverage.

## System reality

| Capability | Reality |
|---|---|
| context manifest | REAL |
| permission gate | REAL |
| trace recorder | REAL |
| local checkpoint/resume | REAL |
| provider-neutral action harness | REAL |
| autonomous LLM reasoning/provider | NOT BUNDLED |
| MCP server | OPTIONAL / requires `mcp>=2` |
| Playwright adapter | OPTIONAL / requires Playwright |
| Figma MCP | EXTERNAL SERVICE / adapter contract only |
| Code Connect mappings | EXTERNAL / project-specific |
| n8n automation | OPTIONAL / external runtime |
| distributed durable execution | NOT CLAIMED |

See `docs/uiux/Agent-Runtime-Foundation-Upgrade.md` for requirements, decisions and verification.
