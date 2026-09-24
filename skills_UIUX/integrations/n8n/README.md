# Optional n8n automation boundary

n8n is an optional external automation surface, not a required runtime dependency.

Use it when a UI/UX workflow is triggered by business-system events outside GitHub, for example:
- a support/CRM signal creates a learning-backlog item;
- an approved deployment emits a verification request;
- a scheduled report gathers non-code operational evidence.

## Contract

n8n may trigger a skills_UIUX run, but it must not silently grant additional authority.

Recommended payload:

```json
{
  "task": "Verify the approved preview deployment",
  "project": "example",
  "requested_agent": "qa",
  "requested_authority": "read_only",
  "evidence_refs": []
}
```

Treat webhook payloads as untrusted input until validated. Never place secrets or personal data into trace attributes merely for convenience.
