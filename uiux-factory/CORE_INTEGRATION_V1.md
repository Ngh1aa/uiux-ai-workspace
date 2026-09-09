# UIUX Factory — Core Integration v1

This step makes the backend integration visible and auditable:

- MetaGPT = real Team / Role / Action runtime.
- skills_UIUX = real SKILL.md execution-policy source.
- UIUX Factory = durable artifacts + event routing.
- Bolt.diy = NEXT step, consuming the event contract produced here.

## What changes

### Real MetaGPT Team

`UIUXMetaTeam` instantiates:

```python
Team(use_mgx=False)
```

Existing specialist Roles are hired lazily into that Team.

The current factory remains deterministic / zero-cost. Single-action Roles
do not need an LLM choice in `_think`, and current deterministic Actions
do not call `_aask`.

### Real skills_UIUX execution context

For every stage, `AdaptiveSkillRouter` chooses only declared real skill paths.

`SkillInstructionCompiler` then:

1. reads the exact local `skills_UIUX/<skill>/SKILL.md`;
2. computes SHA256;
3. copies that exact skill source into run evidence;
4. selects stage-relevant sections;
5. compiles them into the MetaGPT Message content;
6. puts skill path + SHA in Message metadata.

A real run now produces:

```text
runs/<run-id>/
├── events.jsonl
└── skill-context/
    ├── research/
    │   ├── routing.json
    │   ├── skill-context.json
    │   ├── compiled-skills.md
    │   └── sources/
    │       ├── project-context-<sha>.md
    │       └── ...
    ├── ux_ia/
    └── ...
```

This is stronger than merely writing skill names to `skills-used.json`.

### Durable event contract for Bolt.diy

Core Integration v1 writes:

- `team.initialized`
- `skills.resolving`
- `skills.resolved`
- `agent.started`
- `agent.completed`
- `agent.failed`

The next phase will expose this through FastAPI/SSE and render it inside
the Bolt-derived workbench.

## Install

From:

```text
C:\Users\LENOVO\uiux-ai-workspace\uiux-factory
```

run:

```powershell
Expand-Archive `
  "$env:USERPROFILE\Downloads\uiux_factory_core_integration_v1.zip" `
  -DestinationPath "." `
  -Force
```

## Gate 1 — exact real skills only

```powershell
python .\scripts\validate_core_integration.py
```

Required:

```text
[Router Missing] 0
[Code Missing] 0

PASS: every routed/referenced skill exists as a real skills_UIUX SKILL.md file.
```

If Missing > 0: STOP. Never invent a replacement skill.

## Compile

```powershell
python -m py_compile .\core\skills\execution_context.py
python -m py_compile .\core\skills\router.py
python -m py_compile .\core\skills\compiler.py
python -m py_compile .\core\messages\artifact_message.py
python -m py_compile .\core\events\run_event_bus.py
python -m py_compile .\core\team\uiux_team.py
python -m py_compile .\core\team\team_runner.py
python -m py_compile .\scripts\patch_manager_core_integration.py
```

## Gate 2 — prove MetaGPT Team + skills_UIUX together

```powershell
python .\scripts\test_core_integration.py
```

Expected:

```text
[MetaGPT Team] Team
[Result] CORE_INTEGRATION_SMOKE_PASS
[Skill Context] True
[Copied Real Skills] > 0
[Events JSONL] True

PASS
```

## Patch DevelopmentManager

Make sure the Git checkpoint already exists, then:

```powershell
python .\scripts\patch_manager_core_integration.py
python -m py_compile .\core\manager\development_manager.py
```

A backup is created automatically:

```text
core/manager/development_manager.py.before-core-integration-v1
```

The patch replaces simple:

```python
agent = SomeAgent()
result = await agent.run(instruction)
```

with:

```python
result = await self.team_runner.run_role(
    role_class=SomeAgent,
    stage=stage,
    instruction=instruction,
    context=context,
)
```

So every existing specialist Role is now run through the MetaGPT Team +
skills runtime bridge.

## Full run

```powershell
python run.py "Thiết kế website ecommerce hiện đại sang trọng thân thiện màu tím"
```

Then inspect evidence:

```powershell
python .\scripts\inspect_core_integration.py
```

You should see exact `SKILL.md` paths and SHA256 for every integrated stage.

## Important zero-cost limitation

Markdown skills are instruction/policy documents, not executable Python.

Core Integration v1 genuinely:
- selects real skill files;
- reads their exact content;
- copies exact source as evidence;
- compiles relevant content into the MetaGPT Message;
- carries paths/hashes in metadata.

The current deterministic Actions still contain much of the implementation
logic in Python. A later step can deepen structured rule consumption or use
a local/paid model to semantically interpret arbitrary free-form skill text.

This package does NOT falsely claim arbitrary Markdown became executable code.

## Next phase: Bolt.diy workbench

After this passes:

```text
Bolt-derived Workbench
        ↓ POST /runs
FastAPI bridge
        ↓
UIUXTeamRunner / MetaGPT Team
        ↓
runs/<id>/events.jsonl
        ↓ SSE /runs/<id>/events
        ↓
Agent timeline / terminal / files / preview / QA / repair status
```
