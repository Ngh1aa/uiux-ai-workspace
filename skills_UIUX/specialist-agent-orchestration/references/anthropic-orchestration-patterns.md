# Anthropic orchestration patterns — adapted reference

Pinned sources:
- `anthropics/claude-code@cbab6f4598e975b382507dab4392f61f42dd1b94`
- `anthropics/claude-cookbooks@c5ff1dc523e28d9b8fbd5c6ecd63204e20b8a0ed`

This file records only the patterns adapted into UIUX Factory. Upstream remains reference material, not project authority.

## From Claude Code

### Agent development
Source: `plugins/plugin-dev/skills/agent-development/SKILL.md`

Useful patterns:
- autonomous agents need specific triggering conditions;
- system prompts should define responsibilities, process, quality standard and output format;
- restrict tools to the minimum needed;
- test whether triggering behavior is correct, not only whether the agent can run.

### Hook development
Source: `plugins/plugin-dev/skills/hook-development/SKILL.md`

Useful patterns:
- validate risky tool use before execution;
- inspect results after execution;
- deterministic checks belong in deterministic hooks/tests;
- context-sensitive policy checks can use a reasoning gate;
- completion standards can be enforced at stop/handoff boundaries.

UIUX adaptation:
- source-of-truth and write safety checks happen before broad edits;
- build/test/render evidence happens after edits;
- merge/release is a gated transition, not an assumption.

## From Claude Cookbooks

Source: `managed_agents/README.md`

Useful patterns:
- do → observe → fix on failing tests;
- issue → fix → PR → CI → review → merge with recovery from CI/review failures;
- specialists should have scoped toolsets;
- independent graders can evaluate an outcome against an actionable rubric;
- human-in-the-loop gates are appropriate for consequential actions;
- prompt/agent versions can be compared and rolled back when evaluation regresses.

## What we intentionally did not import

- Anthropic-specific API/event syntax;
- Claude model-selection fields;
- hosted runtime/session mechanics;
- provider-specific billing/cost controls;
- plugin UI conventions unrelated to UIUX Factory.

Those details remain in upstream and should be consulted only when the target environment actually uses them.
