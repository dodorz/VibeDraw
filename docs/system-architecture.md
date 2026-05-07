# System Architecture

## Recommended Shape

```text
AutoCAD Plugin
  - AI chat panel
  - parameter editing panel
  - AutoCAD entity writer
  - object metadata store
  - regeneration commands

Local/Backend Service
  - LLM gateway
  - intent parser
  - bridge model builder
  - rules and defaults engine
  - drawing planner
  - CAD instruction generator
  - project/session store
```

The plugin should handle AutoCAD integration. The backend service should handle
LLM calls, bridge semantics, rule checking, and drawing planning.

## Data Flow

```text
User prompt
  -> LLM intent parser
  -> BridgeIntent
  -> BridgeModelBuilder
  -> BridgeModel
  -> RuleChecker
  -> DrawingPlanner
  -> DrawingPlan
  -> CadInstructionGenerator
  -> CadInstruction[]
  -> AutoCAD plugin writers
  -> AutoCAD entities
```

## Why Not Direct LLM-to-CAD

Directly asking the LLM to generate AutoCAD commands, AutoLISP, DXF, or C# code
is attractive for prototypes but risky for a production tool:

- API hallucinations are difficult to eliminate.
- Small geometry errors are hard to detect from text alone.
- Iteration is hard because the original design intent is lost.
- Regeneration can destroy user edits.
- CAD files become collections of lines instead of bridge objects.

The stable boundary is a structured bridge model and a structured CAD
instruction protocol.

## Deployment Recommendation

Preferred first implementation:

```text
AutoCAD plugin: C# + AutoCAD .NET API + WPF PaletteSet
Local service: C# ASP.NET Core or Python FastAPI
LLM access: service-side gateway
Protocol: JSON over HTTP
Project storage: DWG metadata + sidecar JSON
```

If the team is mostly C#-oriented, prefer an all-C# stack for easier deployment
and shared schemas.

