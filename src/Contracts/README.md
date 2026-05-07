# Contracts

This directory contains the Phase 0 frozen contracts for VibeDraw.

These files are intentionally language-neutral. They are the shared source of
truth for downstream implementations in:

- `src/LlmService/`
- `src/DrawingPlanner/`
- `src/CadInstructions/`
- `src/AutoCADPlugin/`
- `src/AutoCADWriters/`
- `src/Metadata/`

## Contract Files

- `bridge-intent.schema.json`
- `bridge-model.schema.json`
- `drawing-plan.schema.json`
- `cad-instruction.schema.json`
- `parse-initial-intent.request.schema.json`
- `parse-initial-intent.response.schema.json`
- `patch-model.request.schema.json`
- `patch-model.response.schema.json`

## Notes

- `BridgeIntent` is the parsed user intent. It may be incomplete and may include
  assumptions and questions.
- `BridgeModel` is the normalized engineering source of truth.
- `DrawingPlan` is the deterministic drawing-level organization.
- `CadInstruction` is the deterministic entity instruction protocol consumed by
  AutoCAD-facing code.

All later packages should consume these contracts rather than redefining them in
ad hoc DTOs first.

## Validation

The executable contract suite for these schemas lives in `tests/contracts/`.
Run it with:

```powershell
npm install
npm run test:contracts
```
