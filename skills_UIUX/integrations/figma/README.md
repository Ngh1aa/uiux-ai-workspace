# Figma MCP / Code Connect integration boundary

Figma design context is an external input, not automatically the canonical project truth.

As of the 2026-09-06 review of Figma's official developer documentation:
- Figma recommends its hosted Remote MCP server for most supported clients;
- the MCP server can provide frames/components/variables/layout context and write native Figma content when authorized;
- Code Connect enriches MCP context with real code-component mappings and implementation snippets;
- final production code is still the agent/codebase responsibility, not the Figma MCP server's output.

## skills_UIUX routing

```text
project truth/source
→ reference-analysis-and-design-to-code
→ Figma MCP design context when available
→ Code Connect/component map when available
→ reuse existing code component
→ implementation
→ rendered verification
```

## Component mapping evidence

Projects may maintain a mapping artifact using the shape in `integrations/figma/component-map.example.json`.

This artifact is only local evidence. It is not a replacement for Figma's official Code Connect mapping state.

## Safety

- Do not copy a Figma component into a parallel code component when a mapped owner already exists.
- Do not let Figma/MCP context silently override current code, project tokens or approved Design Contract.
- Figma write operations are external writes and require authority appropriate to the requested action.
- Verify current Figma plan/client support before making availability claims.
