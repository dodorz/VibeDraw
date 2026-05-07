# VibeDraw Agent Guide

## Project Context

VibeDraw is being planned as an LLM-assisted CAD drawing product for bridge
engineering.

Current agreed product boundary:

- Target CAD environment: AutoCAD only.
- Product form: AutoCAD plugin.
- Initial scope: 2D bridge engineering drawings.
- Primary workflow: natural language intent -> bridge parameter model -> drawing
  generation -> editable AutoCAD entities -> user iteration and regeneration.
- Deferred scope: progeCAD compatibility, FreeCAD, 3D, BIM, structural
  calculation, detailed reinforcement, and detailed prestressing tendon layout.

## Important Design Documents

Start from:

- `docs/README.md`

Then read the module relevant to your task:

- `docs/product-brief.md`
- `docs/system-architecture.md`
- `docs/bridge-domain-model.md`
- `docs/llm-intent-service.md`
- `docs/drawing-generation-pipeline.md`
- `docs/autocad-plugin-architecture.md`
- `docs/iteration-and-regeneration.md`
- `docs/mvp-implementation-plan.md`

## Core Architecture Decision

Do not design the LLM as a direct AutoCAD drafter.

Use this pipeline:

```text
Natural language intent
  -> structured bridge model
  -> deterministic drawing plan
  -> deterministic CAD instructions
  -> editable AutoCAD entities
  -> user feedback
  -> model-level modification and regeneration
```

The LLM should parse intent, fill assumptions, explain choices, and produce
schema-constrained model patches. Deterministic code should handle geometry,
dimensions, layers, styles, AutoCAD entities, metadata, and regeneration.

## Suggested Work Packages

The MVP implementation plan splits work into these packages:

- Agent A: schemas and bridge domain model.
- Agent B: LLM intent service.
- Agent C: drawing planner and generator.
- Agent D: AutoCAD plugin shell.
- Agent E: AutoCAD entity writers.
- Agent F: metadata and regeneration.

See `docs/mvp-implementation-plan.md` before implementing any package.

## Development Notes

- Keep module boundaries explicit.
- Prefer structured schemas and deterministic transformations over ad hoc text
  parsing.
- Store bridge intent separately from AutoCAD entities.
- Generated AutoCAD entities should carry enough metadata to support view-level
  regeneration.
- Preserve user-created CAD objects during regeneration.
- Do not expand scope into 3D/BIM/FreeCAD unless explicitly requested.

