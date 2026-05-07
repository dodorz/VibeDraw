# LLM Intent Service

## Role

The LLM service converts user language into structured bridge model operations.
It should not directly generate AutoCAD entities or executable CAD code.

## Responsibilities

- Parse initial bridge intent.
- Extract bridge type, spans, width, material, and requested drawings.
- Fill non-critical defaults.
- Identify missing critical parameters.
- Convert follow-up instructions into model patches.
- Explain assumptions to the user.
- Produce structured output that matches a schema.

## Non-Responsibilities

The LLM should not be trusted to perform:

- Final geometry calculations.
- Dimension closure.
- AutoCAD entity creation.
- Layer/style creation.
- File writing.
- Deterministic regeneration.
- Engineering compliance validation.

## Request Types

### Parse Initial Intent

Input:

```json
{
  "type": "parse_initial_intent",
  "prompt": "Draw a 40+70+40 m span, 7.5 m wide prestressed continuous girder bridge."
}
```

Output:

```json
{
  "intent": {
    "bridge_type": "continuous_girder",
    "material": "prestressed_concrete",
    "spans_m": [40, 70, 40],
    "deck_width_m": 7.5
  },
  "assumptions": [
    "Alignment is straight.",
    "Section type is single-box single-cell.",
    "Generate plan, elevation, and typical cross section."
  ],
  "questions": []
}
```

### Patch Existing Model

Input:

```json
{
  "type": "patch_model",
  "current_model": {},
  "prompt": "Change the middle span to 75 m and use a single-box double-cell section."
}
```

Output:

```json
{
  "patches": [
    {
      "op": "replace",
      "path": "/bridge/spans_m/1",
      "value": 75
    },
    {
      "op": "replace",
      "path": "/bridge/superstructure/section_type",
      "value": "single_box_double_cell"
    }
  ],
  "affected_views": [
    "plan",
    "elevation",
    "typical_section"
  ]
}
```

## Implementation Notes

- Use strict JSON schema outputs.
- Keep a small domain vocabulary for bridge types and drawing types.
- Return assumptions separately from confirmed user inputs.
- Prefer model patches over full-model rewrites for iteration.
- Log prompts, parsed outputs, schema errors, and user confirmations.

