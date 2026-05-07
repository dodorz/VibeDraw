# No-AutoCAD MVP

## Purpose

This document defines the MVP that can be built, demoed, and regression-tested
before AutoCAD is installed on the system.

## MVP Shape

```text
prompt
  -> BridgeModel
  -> DrawingPlan
  -> CadInstruction
  -> SVG preview
  -> follow-up prompt
  -> model patch
  -> regenerated SVG preview
```

## What This MVP Validates

- bridge intent can be represented as structured model data
- deterministic view generation works
- drawing output can be previewed without AutoCAD
- canonical fixtures remain stable under regression tests

## Current Implementation Path

The current repository now includes a preview package at:

- [src/Preview](/C:/~/Projects/VibeDraw/src/Preview)

This package renders the frozen canonical bridge path into SVG, using the same
deterministic planning and instruction-generation code that later AutoCAD
integration will consume.

## Why This Matters

This lets the team test the product core before host integration is available.
When AutoCAD is added later, the host layer becomes an additional consumer of
the same `CadInstruction` protocol rather than the only way to see output.

## Suggested Next Steps

1. Add more bridge fixtures beyond the canonical 40+70+40 m case.
2. Add a patch/regeneration preview flow.
3. Add a lightweight web or local preview UI on top of the SVG path.
4. Keep AutoCAD host integration as a separate track.

