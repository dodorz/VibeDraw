# Contract Freeze

## Purpose

This document records the Phase 0 frozen contracts and canonical fixtures for
the first implementation wave.

## Frozen Artifacts

Schemas:

- [BridgeIntent](/C:/~/Projects/VibeDraw/src/Contracts/bridge-intent.schema.json)
- [BridgeModel](/C:/~/Projects/VibeDraw/src/Contracts/bridge-model.schema.json)
- [DrawingPlan](/C:/~/Projects/VibeDraw/src/Contracts/drawing-plan.schema.json)
- [CadInstruction](/C:/~/Projects/VibeDraw/src/Contracts/cad-instruction.schema.json)
- [ParseInitialIntentRequest](/C:/~/Projects/VibeDraw/src/Contracts/parse-initial-intent.request.schema.json)
- [ParseInitialIntentResponse](/C:/~/Projects/VibeDraw/src/Contracts/parse-initial-intent.response.schema.json)
- [PatchModelRequest](/C:/~/Projects/VibeDraw/src/Contracts/patch-model.request.schema.json)
- [PatchModelResponse](/C:/~/Projects/VibeDraw/src/Contracts/patch-model.response.schema.json)

Canonical fixtures:

- [Initial Prompt](/C:/~/Projects/VibeDraw/fixtures/prompts/canonical-initial-prompt.txt)
- [Follow-up Prompt](/C:/~/Projects/VibeDraw/fixtures/prompts/canonical-follow-up-prompt.txt)
- [Canonical BridgeIntent](/C:/~/Projects/VibeDraw/fixtures/bridge-models/canonical-bridge-intent.json)
- [Canonical BridgeModel](/C:/~/Projects/VibeDraw/fixtures/bridge-models/canonical-bridge-model.json)
- [Canonical DrawingPlan](/C:/~/Projects/VibeDraw/fixtures/drawing-plans/canonical-general-arrangement.json)
- [Canonical CadInstruction Batch](/C:/~/Projects/VibeDraw/fixtures/cad-instructions/canonical-general-arrangement.json)

Negative contract fixtures:

- [Invalid BridgeModel Empty Spans](/C:/~/Projects/VibeDraw/tests/contracts/invalid-bridge-model-empty-spans.json)
- [Invalid BridgeModel Negative Width](/C:/~/Projects/VibeDraw/tests/contracts/invalid-bridge-model-negative-width.json)
- [Invalid BridgeModel Unknown Type](/C:/~/Projects/VibeDraw/tests/contracts/invalid-bridge-model-unknown-type.json)
- [Invalid CadInstruction Unknown Kind](/C:/~/Projects/VibeDraw/tests/contracts/invalid-cad-instruction-unknown-kind.json)

## Current Freeze Scope

This freeze intentionally covers only the MVP path:

- bridge type: `continuous_girder`
- material: `prestressed_concrete`
- drawings: `general_arrangement`, `plan`, `elevation`, `typical_section`
- supported instruction kinds:
  - `polyline`
  - `line`
  - `text`
  - `aligned_dimension`

The point of the freeze is not completeness. The point is to give all later
packages one stable backbone for implementation.

## Change Policy

Until the first end-to-end MVP path is proven, changes to the frozen contracts
should be treated as coordinated changes. If a downstream package needs to
widen a schema, it should:

1. explain the mismatch
2. propose the contract change
3. update the canonical fixtures
4. update the negative and positive contract cases

## Next Step

After this contract freeze, the safest next implementation move is:

1. Agent A turns these schema files into validated runtime contracts or DTOs.
2. Agent C generates deterministic `DrawingPlan` and `CadInstruction` output
   from the canonical `BridgeModel`.
3. Agent E proves the fixed instruction batch can render inside AutoCAD.

