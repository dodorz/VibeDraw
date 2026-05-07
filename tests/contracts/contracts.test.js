import test from "node:test";
import assert from "node:assert/strict";
import {
  createAjv,
  loadJson,
  loadSchema,
  validatePatchPaths
} from "./schema-test-helpers.js";

const ajv = createAjv();

function expectValid(schemaName, fixturePath) {
  const schema = loadSchema(schemaName);
  const fixture = loadJson(fixturePath);
  const validate = ajv.getSchema(schema.$id);
  const valid = validate(fixture);

  assert.equal(
    valid,
    true,
    `${fixturePath} should satisfy ${schemaName}: ${ajv.errorsText(validate.errors)}`
  );

  return fixture;
}

function expectInvalid(schemaName, fixturePath, expectedMessageFragment) {
  const schema = loadSchema(schemaName);
  const fixture = loadJson(fixturePath);
  const validate = ajv.getSchema(schema.$id);
  const valid = validate(fixture);

  assert.equal(valid, false, `${fixturePath} should fail ${schemaName}`);

  const errorText = ajv.errorsText(validate.errors, { separator: "\n" });
  assert.match(errorText, expectedMessageFragment);
}

test("canonical positive fixtures satisfy frozen schemas", () => {
  expectValid(
    "bridge-intent.schema.json",
    "fixtures/bridge-models/canonical-bridge-intent.json"
  );
  expectValid(
    "bridge-model.schema.json",
    "fixtures/bridge-models/canonical-bridge-model.json"
  );
  expectValid(
    "drawing-plan.schema.json",
    "fixtures/drawing-plans/canonical-general-arrangement.json"
  );
  expectValid(
    "cad-instruction.schema.json",
    "fixtures/cad-instructions/canonical-general-arrangement.json"
  );
});

test("service request and response fixtures satisfy frozen schemas", () => {
  expectValid(
    "parse-initial-intent.request.schema.json",
    "tests/contracts/parse-initial-intent.request.valid.json"
  );
  expectValid(
    "parse-initial-intent.response.schema.json",
    "tests/contracts/parse-initial-intent.response.valid.json"
  );
  expectValid(
    "patch-model.request.schema.json",
    "tests/contracts/patch-model.request.valid.json"
  );

  const patchResponse = expectValid(
    "patch-model.response.schema.json",
    "tests/contracts/patch-model.response.valid.json"
  );

  assert.deepEqual(validatePatchPaths(patchResponse), []);
});

test("bridge model negatives fail validation as expected", () => {
  expectInvalid(
    "bridge-model.schema.json",
    "tests/contracts/invalid-bridge-model-empty-spans.json",
    /must NOT have fewer than 1 items/
  );
  expectInvalid(
    "bridge-model.schema.json",
    "tests/contracts/invalid-bridge-model-negative-width.json",
    /must be > 0/
  );
  expectInvalid(
    "bridge-model.schema.json",
    "tests/contracts/invalid-bridge-model-unknown-type.json",
    /must be equal to one of the allowed values/
  );
  expectInvalid(
    "bridge-model.schema.json",
    "tests/contracts/invalid-bridge-model-unknown-section-type.json",
    /must be equal to one of the allowed values/
  );
});

test("cad instruction negatives fail validation as expected", () => {
  expectInvalid(
    "cad-instruction.schema.json",
    "tests/contracts/invalid-cad-instruction-unknown-kind.json",
    /must match exactly one schema in oneOf/
  );
});

test("patch paths stay inside the frozen model surface", () => {
  const patchResponse = expectValid(
    "patch-model.response.schema.json",
    "tests/contracts/invalid-patch-model-response-bad-path.json"
  );

  assert.deepEqual(validatePatchPaths(patchResponse), ["/bridge/unsupported_field"]);
});
