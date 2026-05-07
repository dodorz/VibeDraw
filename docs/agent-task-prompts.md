# Agent Task Prompts

## Purpose

This document contains copy-ready task prompts for launching implementation
agents for work packages A-F.

These prompts are intended to be used by the lead agent or human coordinator
after reading:

- `docs/implementation-playbook.md`
- `docs/mvp-implementation-plan.md`

They assume the project remains inside the current product boundary:

- AutoCAD only.
- AutoCAD plugin form.
- 2D bridge drawings only.
- No 3D/BIM/FreeCAD scope.

## How To Use

1. Complete Phase 0 contract freeze first.
2. Pick the package you want to assign.
3. Copy the matching prompt below into a new agent session.
4. Adjust directory names if the repository layout changes.
5. Keep the ownership boundary intact unless the lead agent explicitly widens it.

These prompts are intentionally specific. The less the implementation agent has
to infer, the less integration churn we will create.

## Common Coordinator Prefix

Use this prefix before any package-specific prompt if you want consistency:

```text
You are implementing one bounded work package for VibeDraw.

Read these project documents first:
- docs/README.md
- docs/implementation-playbook.md
- docs/mvp-implementation-plan.md
- AGENTS.md

Follow the package boundary exactly.
Do not silently redefine shared contracts.
If you find a contract mismatch, report it explicitly.
Add or update tests for your package.
At the end, report:
- what you changed
- what tests you ran
- any open issues or contract mismatches
```

## Phase 0 Prompt

Use this before parallel implementation starts.

```text
Work Package: Phase 0 - Contract Freeze

Goal:
Freeze the shared contracts and canonical fixtures that all later packages will
consume.

Read first:
- docs/product-brief.md
- docs/system-architecture.md
- docs/bridge-domain-model.md
- docs/llm-intent-service.md
- docs/drawing-generation-pipeline.md
- docs/implementation-playbook.md
- AGENTS.md

Own:
- shared contract definitions
- canonical fixtures
- validation rules
- directory skeleton if missing

Deliver:
- BridgeIntent contract
- BridgeModel contract
- DrawingPlan contract
- CadInstruction contract
- service API request/response shapes
- canonical bridge fixture for 40+70+40 m, 7.5 m bridge
- validation tests

Constraints:
- Do not implement AutoCAD-specific UI or entity-writing behavior here.
- Do not leave shared contracts implicit in prose; encode them in files.
- Prefer deterministic sample fixtures that downstream packages can consume.

Done when:
- downstream packages can build against the frozen contracts
- validation tests exist and pass
- canonical fixtures exist and are documented
```

## Agent A Prompt

```text
Work Package: Agent A - Schema and Domain Model

Goal:
Implement the shared schema/domain layer for VibeDraw so downstream packages can
build against stable contracts.

Read first:
- docs/bridge-domain-model.md
- docs/system-architecture.md
- docs/mvp-implementation-plan.md
- docs/implementation-playbook.md
- AGENTS.md

Primary responsibilities:
- define BridgeIntent schema
- define BridgeModel schema
- define DrawingPlan schema
- define CadInstruction schema
- implement validation rules
- publish canonical fixtures

Suggested ownership:
- src/Contracts/
- src/Domain/
- tests/contracts/
- fixtures/bridge-models/
- fixtures/drawing-plans/
- fixtures/cad-instructions/

You may consume:
- project architecture docs

Do not modify without explicit need:
- plugin UI behavior
- AutoCAD writer behavior
- LLM prompt strategy beyond schema needs

Required tests:
- valid 40+70+40 m bridge fixture passes
- empty span list fails
- negative deck width fails
- unknown enum values fail
- patch path validation is predictable

Deliverables:
- schema/DTO definitions
- validation logic
- canonical fixtures
- contract tests

Done when:
- other packages can compile against your contracts
- fixtures are stable and documented
- tests pass
```

## Agent B Prompt

```text
Work Package: Agent B - LLM Intent Service

Goal:
Implement the LLM-facing intent service that parses initial bridge prompts and
follow-up edit prompts into schema-valid structured outputs.

Read first:
- docs/llm-intent-service.md
- docs/bridge-domain-model.md
- docs/system-architecture.md
- docs/implementation-playbook.md
- AGENTS.md

Consume as fixed inputs:
- BridgeIntent schema
- BridgeModel schema
- service request/response contracts

Primary responsibilities:
- parse initial natural-language bridge intent
- generate explicit assumptions and questions
- translate follow-up edits into model patches
- validate LLM outputs against schema
- provide a mock LLM mode for deterministic tests

Suggested ownership:
- src/LlmService/
- tests/unit/llm/
- tests/integration/llm/
- fixtures/prompts/

Do not modify without explicit approval:
- shared schema definitions
- AutoCAD plugin UI contracts
- CadInstruction format

Required tests:
- canonical prompt extracts spans and width correctly
- follow-up prompt changes middle span to 75 m correctly
- assumptions are returned separately from confirmed values
- malformed LLM output fails clearly
- mock mode works without network access

Deliverables:
- parsing endpoint or service
- patch-generation endpoint or service
- schema validation and error handling
- prompt fixtures and tests

Done when:
- outputs are schema-valid
- mock mode covers the MVP path
- tests pass
```

## Agent C Prompt

```text
Work Package: Agent C - Drawing Planner and Generator

Goal:
Implement deterministic generation from BridgeModel to DrawingPlan to
CadInstruction for the MVP bridge example.

Read first:
- docs/drawing-generation-pipeline.md
- docs/bridge-domain-model.md
- docs/system-architecture.md
- docs/implementation-playbook.md
- AGENTS.md

Consume as fixed inputs:
- BridgeModel schema
- DrawingPlan schema
- CadInstruction schema
- canonical bridge fixture

Primary responsibilities:
- convert BridgeModel into DrawingPlan
- convert DrawingPlan into deterministic CadInstruction output
- generate elevation view
- generate plan view
- generate typical section view

Suggested ownership:
- src/DrawingPlanner/
- src/CadInstructions/
- tests/unit/drawing/
- tests/golden/drawing/
- fixtures/drawing-plans/
- fixtures/cad-instructions/

Do not modify without explicit approval:
- shared schemas
- AutoCAD plugin shell behavior
- metadata persistence rules

Required tests:
- golden output test for canonical bridge fixture
- pier location coordinate checks
- deck edge offset checks in plan view
- typical section closure checks
- layer/view/source_component_id presence checks

Deliverables:
- deterministic drawing planner
- deterministic instruction generators
- golden fixtures and tests

Done when:
- canonical bridge fixture produces elevation, plan, and typical section output
- output is stable between runs
- tests pass
```

## Agent D Prompt

```text
Work Package: Agent D - AutoCAD Plugin Shell

Goal:
Implement the AutoCAD plugin shell, user-facing panel, and service connectivity
for the MVP workflow.

Read first:
- docs/autocad-plugin-architecture.md
- docs/system-architecture.md
- docs/implementation-playbook.md
- docs/mvp-implementation-plan.md
- AGENTS.md

Consume as fixed inputs:
- service request/response contracts
- BridgeModel-related UI data
- CadInstruction pipeline outputs from upstream packages

Primary responsibilities:
- register AutoCAD commands
- create the WPF PaletteSet or equivalent plugin panel
- wire service calls for prompt submission and response display
- show assumptions and editable returned parameters

Suggested ownership:
- src/AutoCADPlugin/
- tests/unit/plugin/
- tests/manual/plugin/

Do not modify without explicit approval:
- shared schemas
- drawing generator logic
- metadata storage contracts unless coordinated

Required tests:
- plugin loads in AutoCAD
- AIBRIDGE opens the panel
- mock service connectivity works
- returned assumptions and parameters render correctly

Deliverables:
- loadable plugin shell
- prompt submission flow
- parameter/assumption display
- smoke test notes

Done when:
- user can open the panel and submit the canonical prompt
- returned model data is visible in the UI
- tests and smoke checks are documented
```

## Agent E Prompt

```text
Work Package: Agent E - AutoCAD Entity Writers

Goal:
Implement CadInstruction-to-AutoCAD entity writing for the MVP drawing types.

Read first:
- docs/autocad-plugin-architecture.md
- docs/drawing-generation-pipeline.md
- docs/iteration-and-regeneration.md
- docs/implementation-playbook.md
- AGENTS.md

Consume as fixed inputs:
- CadInstruction schema
- layer/style conventions
- canonical CadInstruction fixtures

Primary responsibilities:
- map line/polyline/text/dimension instructions to AutoCAD entities
- create or reuse layers and styles
- wrap generation in predictable transactions
- attach metadata required for regeneration

Suggested ownership:
- src/AutoCADWriters/
- tests/unit/writers/
- tests/integration/writers/
- tests/manual/writers/

Do not modify without explicit approval:
- shared schemas
- plugin shell UI
- LLM parsing behavior

Required tests:
- line/polyline/text/dimension writers create expected objects
- layers are reused instead of duplicated
- generated entities contain required metadata
- generation can be undone in a predictable unit

Deliverables:
- entity writers
- layer/style helpers
- integration tests or smoke tests against fixture instructions

Done when:
- canonical CadInstruction fixtures render correctly in AutoCAD
- metadata can be read back
- tests and smoke steps are documented
```

## Agent F Prompt

```text
Work Package: Agent F - Metadata and Regeneration

Goal:
Implement project state persistence and view-level regeneration while preserving
user-created AutoCAD objects.

Read first:
- docs/iteration-and-regeneration.md
- docs/autocad-plugin-architecture.md
- docs/system-architecture.md
- docs/implementation-playbook.md
- AGENTS.md

Consume as fixed inputs:
- BridgeModel persistence requirements
- entity metadata requirements
- project_id/view_id conventions

Primary responsibilities:
- persist project/model state
- persist and recover generated object metadata
- identify affected generated views
- replace only targeted AI-generated objects during regeneration
- preserve non-AI objects

Suggested ownership:
- src/Metadata/
- tests/unit/metadata/
- tests/integration/regeneration/
- tests/manual/regeneration/

Do not modify without explicit approval:
- shared schemas
- core drawing generation logic
- plugin UI behavior except where needed for regeneration wiring

Required tests:
- project metadata round-trip works
- sidecar JSON round-trip works
- filtering by project_id and view_id works
- regenerating one view preserves unrelated generated views
- user-created objects are preserved

Deliverables:
- DWG metadata helpers
- sidecar persistence helpers
- view-level regeneration flow
- integration and smoke tests

Done when:
- canonical bridge can be reopened and regenerated by view
- user-created objects survive regeneration
- tests pass
```

## Integration Prompt

Use this after several package agents have completed their work.

```text
Task: Integration and Acceptance

Goal:
Integrate the completed package outputs and verify the MVP end-to-end flow from
prompt to AutoCAD drawing to targeted regeneration.

Read first:
- docs/implementation-playbook.md
- docs/mvp-implementation-plan.md
- docs/README.md
- AGENTS.md

Use these completed outputs:
- schemas and fixtures
- LLM intent service or mock path
- drawing planner/generator
- AutoCAD plugin shell
- AutoCAD entity writers
- metadata and regeneration logic

Primary responsibilities:
- verify package boundaries still align
- run canonical fixtures through the full chain
- document integration defects by owning package
- fix only clearly scoped integration glue in your owned area

Required checks:
- canonical prompt creates the canonical BridgeModel
- canonical BridgeModel creates DrawingPlan and CadInstruction outputs
- AutoCAD plugin can render the generated output
- follow-up prompt to change middle span to 75 m regenerates affected views
- user-created objects survive regeneration

Done when:
- the MVP acceptance path is demonstrated end-to-end
- failures are either fixed or assigned back to the correct package owner
- acceptance status is documented
```

## Lightweight Prompt Variant

If you want a shorter task prompt after the team already knows the project well,
use this form:

```text
Take ownership of Work Package [A-F] from docs/implementation-playbook.md and
docs/agent-task-prompts.md.

Read the relevant package docs first.
Stay inside the package boundary.
Do not redefine shared contracts silently.
Implement the package, add the required tests, and report:
- changed files
- tests run
- open issues
```

