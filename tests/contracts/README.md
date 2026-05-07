# Contract Tests

This directory now contains the executable Phase 0 contract validation path for
the frozen JSON schemas in `src/Contracts/`.

## Required Contract Checks

### Positive Cases

- `fixtures/bridge-models/canonical-bridge-intent.json` matches
  `src/Contracts/bridge-intent.schema.json`.
- `fixtures/bridge-models/canonical-bridge-model.json` matches
  `src/Contracts/bridge-model.schema.json`.
- `fixtures/drawing-plans/canonical-general-arrangement.json` matches
  `src/Contracts/drawing-plan.schema.json`.
- `fixtures/cad-instructions/canonical-general-arrangement.json` matches
  `src/Contracts/cad-instruction.schema.json`.
- `tests/contracts/parse-initial-intent.request.valid.json` matches
  `src/Contracts/parse-initial-intent.request.schema.json`.
- `tests/contracts/parse-initial-intent.response.valid.json` matches
  `src/Contracts/parse-initial-intent.response.schema.json`.
- `tests/contracts/patch-model.request.valid.json` matches
  `src/Contracts/patch-model.request.schema.json`.
- `tests/contracts/patch-model.response.valid.json` matches
  `src/Contracts/patch-model.response.schema.json`.

### Negative Cases

- Empty `spans_m` should fail.
- Negative `deck_width_m` should fail.
- Unknown bridge type should fail.
- Unknown section type should fail.
- Unknown instruction `kind` should fail.
- Unsupported patch paths should be flagged by the contract harness.

## Expected Validation Scope

Downstream schema validation code should assert:

- required fields exist
- enum values are stable
- numeric fields that represent dimensions are positive
- batch files do not contain unknown top-level properties

## Running The Tests

Install dependencies once:

```powershell
npm install
```

Run the contract suite:

```powershell
npm run test:contracts
```

## Notes

- JSON Schema handles structure, enums, and numeric bounds.
- Patch path validation is intentionally implemented as a small semantic check in
  the test harness because the current `patch-model.response` schema only
  constrains the shape of a patch, not whether its path stays inside the frozen
  MVP model surface.
