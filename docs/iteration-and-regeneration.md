# Iteration and Regeneration

## Goal

User iteration should happen at the bridge model level, while preserving the
ability to manually edit the generated AutoCAD drawing.

## Iteration Flow

```text
User follow-up prompt
  -> LLM parses model patch
  -> apply patch to BridgeModel
  -> validate model
  -> identify affected drawings/views
  -> generate new CadInstruction[]
  -> replace affected AI-generated objects
  -> preserve unrelated user edits
```

## Patch-Based Updates

Use model patches instead of complete model replacement.

Example:

```json
{
  "op": "replace",
  "path": "/bridge/spans_m/1",
  "value": 75
}
```

Benefits:

- Easier review.
- Easier undo.
- Better audit trail.
- Less accidental loss of user-confirmed data.

## Generated Object Policy

Objects should be classified into at least:

- AI-generated objects.
- User-created objects.
- User-edited generated objects.
- Locked objects.

MVP can start with a simpler policy:

- Delete and regenerate objects with matching `project_id` and `view_id`.
- Preserve all objects without AI metadata.
- Warn before replacing a view.

Later versions can detect edits to generated objects and ask whether to preserve
or regenerate them.

## Regeneration Granularity

Support view-level regeneration first:

- Regenerate elevation view.
- Regenerate plan view.
- Regenerate typical cross section.
- Regenerate all drawings.

Entity-level regeneration can come later.

## Stored State

Store enough state to support future regeneration:

- Current BridgeModel.
- DrawingPlan.
- Generated view IDs.
- Generation version.
- User-confirmed assumptions.
- Last LLM conversation context.

## Undo

AutoCAD transaction handling should allow one generation or regeneration action
to be undone as a single operation where possible.

