# UIUX Factory — Full Pipeline Integration v1

This package closes the gap visible in run `20260909-034756`:

- the run completed through `visual_composition` and `implementation`,
  but those two stages still bypassed `UIUXTeamRunner`;
- no quality-loop stage was called from DevelopmentManager;
- therefore `inspect_core_integration.py` only showed six integrated
  skill stages even though the overall run had eight completed stages.

## What this package changes

### VisualComposer and FrontendEngineer

Both now run through:

```text
DevelopmentManager
  -> UIUXTeamRunner
  -> MetaGPT Team
  -> Role
  -> Action
  <- real skills_UIUX execution context
```

### Quality loop

After implementation, DevelopmentManager runs:

```text
BrowserQA
  -> VisualCritic
  -> PASS

or

BrowserQA
  -> VisualCritic
  -> RepairAgent
  -> BrowserQA regression
  -> VisualCritic
```

All three quality Roles also run through `UIUXTeamRunner`.

Hard stop rules:

- max iterations = 3
- stop if BrowserQA cannot provide critic-ready evidence
- stop if Critic has no actionable repair
- stop if RepairAgent makes no change
- stop as `stagnated` when the same issue fingerprint repeats without
  at least 1 point score improvement
- DevelopmentManager does NOT mark the whole run completed unless
  quality status is `passed`

## Install

From:

```text
C:\Users\LENOVO\uiux-ai-workspace\uiux-factory
```

extract:

```powershell
Expand-Archive `
  "$env:USERPROFILE\Downloads\uiux_factory_full_pipeline_integration_v1.zip" `
  -DestinationPath "." `
  -Force
```

## Patch manager

```powershell
python .\scripts\patch_manager_full_pipeline.py
python -m py_compile .\core\manager\development_manager.py
```

Expected:

```text
[PATCHED] VisualComposer
[PATCHED] FrontendEngineer
[Quality Call] INSERTED
[Quality Method] INSERTED
[Remaining Direct Visual/Frontend] 0
PASS
```

## Validate structure

```powershell
python .\scripts\validate_full_pipeline_integration.py
```

All checks must be True.

## Validate real skills again

```powershell
python .\scripts\validate_core_integration.py
```

Required:

```text
[Router Missing] 0
[Code Missing] 0
PASS
```

## Full run

```powershell
python run.py "Thiết kế website ecommerce hiện đại sang trọng thân thiện màu tím"
```

## Inspect

```powershell
python .\scripts\inspect_full_pipeline.py
```

A clean pass should show integrated stages including:

```text
research
ux_ia
art_direction
design_contract
design_system
implementation_plan
visual_composition
implementation
browser_qa
visual_qa
```

`repair` appears only when VisualCritic actually requests repair.

The run should contain:

```text
runs/<run-id>/
├── run.json
├── events.jsonl
├── quality-loop.json
├── quality-loop/
│   └── iteration-01/
│       ├── browser-report.json
│       ├── visual-critic.json
│       └── repair-result.json   # only when needed
└── skill-context/
    ├── research/
    ├── ux_ia/
    ├── art_direction/
    ├── design_contract/
    ├── design_system/
    ├── implementation_plan/
    ├── visual_composition/
    ├── implementation/
    ├── browser_qa/
    ├── visual_qa/
    └── repair/                  # only when needed
```

## Next phase

Once this full pipeline passes, the next package is the actual Bolt.diy UI
integration:

```text
Bolt-derived Workbench
  -> FastAPI POST /runs
  -> UIUX Factory / MetaGPT Team
  -> events.jsonl
  -> SSE /runs/{id}/events
  -> Agent timeline / skills / files / preview / QA / repair
```
