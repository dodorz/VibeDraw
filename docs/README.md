# VibeDraw Design Documents

This directory captures the product and architecture decisions for an LLM-assisted
AutoCAD bridge drawing tool.

The current product boundary is intentionally narrow:

- Target domain: bridge engineering.
- Target CAD environment: AutoCAD only.
- Product form: AutoCAD plugin, with an AI side panel.
- Initial drawing scope: 2D CAD drawings.
- Deferred scope: 3D, BIM, FreeCAD, non-AutoCAD compatibility, structural calculation.

## Documents

- [Product Brief](./product-brief.md)
- [System Architecture](./system-architecture.md)
- [Bridge Domain Model](./bridge-domain-model.md)
- [LLM Intent Service](./llm-intent-service.md)
- [Drawing Generation Pipeline](./drawing-generation-pipeline.md)
- [AutoCAD Plugin Architecture](./autocad-plugin-architecture.md)
- [Iteration and Regeneration](./iteration-and-regeneration.md)
- [MVP Implementation Plan](./mvp-implementation-plan.md)
- [Implementation Playbook](./implementation-playbook.md)
- [Agent Task Prompts](./agent-task-prompts.md)
- [Contract Freeze](./contract-freeze.md)
- [No-AutoCAD MVP](./no-autocad-mvp.md)

## Related Repository Areas

- [Project Root README](/C:/~/Projects/VibeDraw/README.md)
- [Agent Guide](/C:/~/Projects/VibeDraw/AGENTS.md)
- [Source Root](/C:/~/Projects/VibeDraw/src)
- [Test Root](/C:/~/Projects/VibeDraw/tests)
- [Fixture Root](/C:/~/Projects/VibeDraw/fixtures)

## Core Thesis

The software should not treat the LLM as a direct CAD drafter. The recommended
architecture is:

```text
Natural language intent
  -> structured bridge model
  -> deterministic drawing plan
  -> deterministic CAD instructions
  -> editable AutoCAD entities
  -> user feedback
  -> model-level modification and regeneration
```

The LLM understands, fills missing intent, explains assumptions, and converts
user feedback into model changes. Geometry, dimensions, layer creation, object
metadata, and AutoCAD entity generation are handled by deterministic code.
