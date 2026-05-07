# Implementation Playbook

## Purpose

This document explains how to execute the A-F work packages in a controlled,
parallel-friendly way, and how to use those packages with multiple agent
sessions.

It is written for two roles:

- A lead agent or human coordinator who assigns work.
- Implementation agents that own a specific package.

The goal is to avoid a common failure mode:

```text
Multiple agents start coding in parallel before shared schemas and interfaces are
stable, and then every package drifts.
```

## When To Use This Document

Use this playbook when:

- The team is ready to move from design documents into implementation.
- Multiple agents will work in parallel.
- A package needs a clear scope, test plan, and completion definition.

Do not use this playbook as a replacement for the architecture docs. It sits on
top of them and turns them into execution steps.

## Required Inputs

Before implementation starts, the following documents should already exist and
be treated as the source of truth:

- `docs/product-brief.md`
- `docs/system-architecture.md`
- `docs/bridge-domain-model.md`
- `docs/llm-intent-service.md`
- `docs/drawing-generation-pipeline.md`
- `docs/autocad-plugin-architecture.md`
- `docs/iteration-and-regeneration.md`
- `docs/mvp-implementation-plan.md`

## Roles

### Lead Agent

Owns:

- Deciding the implementation order.
- Freezing shared contracts.
- Assigning work packages.
- Reviewing integration points.
- Running cross-package acceptance tests.

The lead agent should not let every package freely redefine schemas or service
boundaries.

### Package Agent

Owns:

- One work package.
- The files and tests assigned to that package.
- Local validation for that package.
- Handoff notes for integration.

The package agent should not silently change shared contracts without routing the
change back through the lead agent.

## Execution Model

The best workflow is:

```text
1. Freeze contracts.
2. Implement the packages that depend only on those contracts.
3. Integrate in stages.
4. Run package tests.
5. Run cross-package tests.
```

It is fine to create one agent session per work package, but only after shared
interfaces are frozen enough for parallel work.

## Recommended Order

### Phase 0: Contract Freeze

This is the most important phase. It should be led by the lead agent and treated
as blocking for the rest.

Deliver:

- `BridgeIntent` shape.
- `BridgeModel` shape.
- `DrawingPlan` shape.
- `CadInstruction` shape.
- Service request/response shapes.
- One or more canonical bridge fixtures.
- Initial project directory layout.

Until this phase is stable, avoid parallel package implementation.

### Phase 1: Core Model and Generators

Run:

- Agent A: schemas and validation.
- Agent B: LLM intent service.
- Agent C: drawing planner and generator.

Agent B and Agent C can move in parallel once Agent A has frozen the shared
contracts.

### Phase 2: AutoCAD Integration

Run:

- Agent D: plugin shell.
- Agent E: entity writers.

These can be developed in parallel, but they should use the `CadInstruction`
schema produced by earlier phases without changing it casually.

### Phase 3: Persistence and Regeneration

Run:

- Agent F: metadata and regeneration.

This package depends on the object-writing strategy from D/E, so it should start
after the plugin shell and entity writer path is clear.

### Phase 4: Integration and Acceptance

Run:

- Lead agent integrates all outputs.
- Lead agent runs end-to-end tests.
- Fixes are sent back to the owning package agent if the defect is scoped.

## Package Ownership Model

Each package should be assigned:

- A clear responsibility boundary.
- A primary file or directory ownership area.
- A test ownership area.
- A list of contracts it may consume.
- A list of contracts it must not modify unilaterally.

This reduces integration churn and makes review much easier.

## Suggested Repository Layout

The implementation does not need this exact layout, but using something close to
it will make package ownership easier.

```text
src/
  Contracts/
  Domain/
  LlmService/
  DrawingPlanner/
  CadInstructions/
  AutoCADPlugin/
  AutoCADWriters/
  Metadata/

tests/
  contracts/
  unit/
  golden/
  integration/
  manual/

fixtures/
  bridge-models/
  prompts/
  drawing-plans/
  cad-instructions/
```

## Agent Session Pattern

When creating a session for a package agent, the lead agent should include five
things:

1. The package name and goal.
2. The files/directories the agent owns.
3. The contracts the agent must use as-is.
4. The tests the agent must add or make pass.
5. The completion definition.

### Example Assignment Template

```text
Work Package: Agent C - Drawing Planner and Generator

Goal:
Implement deterministic generation from BridgeModel to DrawingPlan to
CadInstruction for the MVP bridge fixture.

Own:
- src/DrawingPlanner/*
- src/CadInstructions/*
- tests/unit/drawing/*
- tests/golden/drawing/*

Consume without redefining:
- BridgeModel schema
- DrawingPlan schema
- CadInstruction schema

Do not modify without approval:
- Service API contracts
- Plugin UI contracts

Required tests:
- Golden output test for 40+70+40 m bridge
- Coordinate assertions for pier locations
- View ID and layer assignment tests

Done when:
- Plan/elevation/typical section generation works from fixture input
- Tests pass
- Outputs match frozen schema
```

## Work Package Details

### Agent A: Schema and Domain Model

Mission:

- Define the shared data contracts.
- Validate model completeness and consistency.
- Publish canonical fixtures.

Primary outputs:

- Contract DTOs or JSON schemas.
- Validation logic.
- Example fixtures.

Typical owned areas:

- `src/Contracts/`
- `src/Domain/`
- `tests/contracts/`
- `fixtures/bridge-models/`

Tests:

- Valid bridge fixture passes validation.
- Empty span list fails.
- Negative width fails.
- Unknown enum values fail.
- Patch path validation behaves predictably.

Completion definition:

- Other packages can build against stable schemas.
- Fixtures exist for the MVP bridge example.
- Contract tests are green.

### Agent B: LLM Intent Service

Mission:

- Parse initial natural language prompts into structured intent.
- Convert follow-up edits into model patches.
- Return assumptions and missing critical questions separately.

Primary outputs:

- Intent parsing endpoint.
- Model patch endpoint.
- Structured output validation path.
- Mock LLM mode for deterministic tests.

Typical owned areas:

- `src/LlmService/`
- `tests/unit/llm/`
- `tests/integration/llm/`
- `fixtures/prompts/`

Tests:

- Initial prompt parses spans and width correctly.
- Follow-up prompt generates correct patches.
- Assumptions are separated from confirmed fields.
- Invalid LLM output is rejected cleanly.
- Mock mode can run without network access.

Completion definition:

- Service returns schema-valid payloads.
- Prompt fixtures cover the MVP path.
- Failure cases are observable and testable.

### Agent C: Drawing Planner and Generator

Mission:

- Convert BridgeModel into DrawingPlan.
- Convert DrawingPlan into deterministic CadInstruction output.
- Generate the MVP views.

Primary outputs:

- Drawing planner.
- Geometry generator.
- View-specific instruction generators.

Typical owned areas:

- `src/DrawingPlanner/`
- `src/CadInstructions/`
- `tests/unit/drawing/`
- `tests/golden/drawing/`
- `fixtures/drawing-plans/`
- `fixtures/cad-instructions/`

Tests:

- Golden JSON output for the canonical bridge fixture.
- Pier location coordinate checks.
- Deck edge offset checks in plan view.
- Typical section closure checks.
- View IDs, layers, and source component IDs are set.

Completion definition:

- MVP fixture produces elevation, plan, and typical section instructions.
- Outputs are deterministic.
- Golden tests are green.

### Agent D: AutoCAD Plugin Shell

Mission:

- Create the AutoCAD plugin shell and user-facing panel.
- Wire the plugin to the local/backend service.
- Support generation and confirmation workflows.

Primary outputs:

- AutoCAD command registration.
- WPF panel.
- Service client.
- Basic parameter confirmation UI.

Typical owned areas:

- `src/AutoCADPlugin/`
- `tests/unit/plugin/`
- `tests/manual/plugin/`

Tests:

- Plugin loads in AutoCAD.
- `AIBRIDGE` opens the panel.
- Service connectivity can be tested with a mock endpoint.
- Returned assumptions and parameters render in the UI.

Completion definition:

- Plugin shell is loadable.
- User can submit a prompt and inspect returned model data.
- Manual smoke test steps are documented.

### Agent E: AutoCAD Entity Writers

Mission:

- Convert CadInstruction items into AutoCAD entities.
- Apply layers, styles, and transaction handling.
- Attach metadata required for regeneration.

Primary outputs:

- Entity writers.
- Layer/style helpers.
- Generation transaction wrapper.

Typical owned areas:

- `src/AutoCADWriters/`
- `tests/unit/writers/`
- `tests/integration/writers/`
- `tests/manual/writers/`

Tests:

- Polyline, line, text, and dimension writers create expected objects.
- Layers are reused rather than duplicated.
- Metadata is attached to generated entities.
- Generation can be undone in a predictable unit.

Completion definition:

- Fixed CadInstruction fixtures render correctly in AutoCAD.
- Metadata can be read back from generated objects.
- Writer integration tests and smoke tests are documented.

### Agent F: Metadata and Regeneration

Mission:

- Persist model state.
- Track generated objects.
- Replace only affected generated views during regeneration.

Primary outputs:

- DWG metadata store.
- Sidecar project/session store.
- View-level regeneration logic.

Typical owned areas:

- `src/Metadata/`
- `tests/unit/metadata/`
- `tests/integration/regeneration/`
- `tests/manual/regeneration/`

Tests:

- Project metadata can be written and read back.
- Sidecar JSON state can be written and read back.
- Objects can be filtered by `project_id` and `view_id`.
- Regenerating one view does not delete unrelated generated views.
- User-created objects are preserved.

Completion definition:

- View-level regeneration works for the MVP path.
- State is durable enough to reopen and continue.
- Non-AI objects survive regeneration.

## Test Strategy

Each package should include three levels of testing where applicable.

### 1. Contract Tests

Purpose:

- Prove that shared schemas are stable.
- Catch drift between packages early.

Examples:

- DTO or JSON schema validation.
- API request/response shape checks.
- Fixture compatibility checks.

### 2. Deterministic Unit and Golden Tests

Purpose:

- Verify logic that does not require AutoCAD.
- Provide stable regression tests for bridge fixtures.

Examples:

- Geometry calculations.
- Layer assignment rules.
- Patch translation.
- Fixed input to fixed JSON output.

### 3. Integration and Manual AutoCAD Tests

Purpose:

- Validate real plugin behavior inside AutoCAD.
- Confirm metadata, entity creation, and regeneration work in practice.

Examples:

- Plugin loads.
- Command opens panel.
- Generation draws the expected objects.
- Regeneration only replaces the targeted view.

## Canonical Test Fixtures

At minimum, the team should maintain these canonical fixtures:

- Initial prompt:
  `Draw a prestressed continuous girder bridge with spans 40+70+40 m and bridge width 7.5 m.`
- Follow-up prompt:
  `Change the middle span to 75 m.`
- Canonical BridgeModel.
- Canonical DrawingPlan.
- Canonical CadInstruction output for plan/elevation/typical section.

These fixtures are the backbone of regression testing and package integration.

## Definition Of Done By Stage

### Package Done

A package is done when:

- It stays inside its ownership boundary.
- Its tests pass.
- It consumes frozen contracts correctly.
- It documents assumptions and any gaps for integration.

### Integration Done

An integration stage is done when:

- Upstream and downstream contracts line up.
- Canonical fixtures pass through the chain.
- Manual smoke tests for that stage are documented and reproducible.

### MVP Done

The MVP is done when the canonical prompt can travel through the full path:

```text
Prompt
  -> BridgeModel
  -> DrawingPlan
  -> CadInstruction
  -> AutoCAD drawing
  -> model patch
  -> targeted regeneration
```

with editable AutoCAD entities and preserved user-created objects.

## How The Lead Agent Should Use This Playbook

Use this document as an operating manual.

Recommended loop:

1. Read this playbook and the architecture docs.
2. Freeze or update shared contracts.
3. Pick the next phase.
4. Launch one agent session per package in that phase.
5. Give each agent a concrete assignment using the template above.
6. Wait for package completion and review the owned tests.
7. Integrate the outputs.
8. Run canonical fixtures and smoke tests.
9. Send defects back to the owning package agent.

The lead agent should treat this document as the standard for assignment and
acceptance, not as a passive note.

## How A Package Agent Should Use This Playbook

Use this document as a local contract.

Recommended loop:

1. Read the package section.
2. Read the architecture docs for the adjacent layers.
3. Confirm owned files and forbidden boundaries.
4. Implement only the assigned scope.
5. Add or update the required tests.
6. Record any contract mismatch instead of silently redefining it.
7. Hand back results with test status and open issues.

## Practical Session Advice

- Use one session per package when the package has a clean ownership boundary.
- Reuse the same session for follow-up fixes on that package so context stays
  coherent.
- Do not split one small package across many agents unless there is a real file
  boundary.
- Do not run packages in parallel before Phase 0 contract freeze is stable.
- Prefer sending agents canonical fixtures rather than long natural-language
  summaries.

## First Implementation Wave

If the team is starting from scratch, the safest first wave is:

1. Agent A freezes contracts and fixtures.
2. Agent C builds deterministic generation against the fixtures.
3. Agent E proves the fixed CadInstruction set can render in AutoCAD.
4. Agent D adds the plugin shell around the proven generation path.
5. Agent B replaces mock intent parsing with a real LLM-backed path.
6. Agent F adds persistence and regeneration.

This order creates a usable technical spine early, even before the full AI loop
is finished.

