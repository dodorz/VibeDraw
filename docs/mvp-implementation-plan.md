# MVP Implementation Plan

## MVP Goal

Generate editable AutoCAD 2D drawings for a simple prestressed continuous girder
bridge from natural language input, then support model-level iteration and
view-level regeneration.

## MVP Feature Set

- AutoCAD command opens AI side panel.
- User enters bridge description in natural language.
- LLM service returns structured BridgeModel draft.
- UI shows assumptions and editable parameters.
- User confirms generation.
- Plugin generates:
  - elevation view.
  - plan view.
  - typical cross section.
- Generated entities use standard layers and styles.
- Generated entities carry metadata.
- BridgeModel is saved in DWG metadata and sidecar JSON.
- User follow-up prompts produce model patches.
- Affected views can be regenerated.

## Suggested Agent Work Packages

### Agent A: Schema and Domain Model

Owns:

- BridgeIntent schema.
- BridgeModel schema.
- DrawingPlan schema.
- CadInstruction schema.
- Validation rules.
- Example fixtures.

Deliverables:

- JSON schemas or C# DTOs.
- Sample models for 40+70+40 m bridge.
- Unit tests for validation.

### Agent B: LLM Intent Service

Owns:

- Intent parsing endpoint.
- Model patch endpoint.
- Structured output handling.
- Schema validation and error reporting.
- Prompt templates for bridge intent.

Deliverables:

- Local service API.
- Mock LLM mode for tests.
- Example request/response files.

### Agent C: Drawing Planner and Generator

Owns:

- BridgeModel to DrawingPlan.
- DrawingPlan to CadInstruction.
- Deterministic geometry for initial bridge drawings.
- Layer/style template configuration.

Deliverables:

- Elevation generator.
- Plan generator.
- Typical section generator.
- Golden JSON outputs for fixtures.

### Agent D: AutoCAD Plugin Shell

Owns:

- AutoCAD plugin project setup.
- `AIBRIDGE` command.
- WPF PaletteSet.
- HTTP client to local service.
- Parameter confirmation UI.

Deliverables:

- Loadable AutoCAD plugin.
- Basic chat/parameter panel.
- Service connectivity.

### Agent E: AutoCAD Entity Writers

Owns:

- CadInstruction to AutoCAD entity mapping.
- Layers.
- Text styles.
- Dimension styles.
- Transaction handling.

Deliverables:

- Polyline/line/text/dimension writers.
- Generated entity grouping.
- Undo-friendly generation transaction.

### Agent F: Metadata and Regeneration

Owns:

- Per-entity metadata.
- Project-level DWG metadata.
- Sidecar JSON storage.
- View-level deletion and regeneration.

Deliverables:

- Metadata read/write helpers.
- Regenerate current view command.
- Preserve non-AI objects.

## Recommended Build Order

1. Define schemas and sample bridge fixture.
2. Build drawing generator that outputs CadInstruction JSON.
3. Build a minimal AutoCAD writer for lines, polylines, text, and dimensions.
4. Add plugin UI and service calls.
5. Add model storage and view-level regeneration.
6. Replace mocks with real LLM structured outputs.

## MVP Acceptance Criteria

Given this prompt:

```text
Draw a prestressed continuous girder bridge with spans 40+70+40 m and bridge
width 7.5 m.
```

The system should:

- Parse spans and width correctly.
- Present assumptions before generation.
- Generate an elevation view, plan view, and typical section in AutoCAD.
- Use editable AutoCAD entities.
- Save bridge model metadata.
- Regenerate affected views after a follow-up such as:

```text
Change the middle span to 75 m.
```

