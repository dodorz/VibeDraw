# Writer Manual Smoke Test

This package currently validates the writer layer without a real AutoCAD host.

## What is covered now

- Loading the frozen `CadInstruction` batch from JSON.
- Mapping `line`, `polyline`, `text`, and `aligned_dimension` instructions into
  deterministic writer operations.
- Reusing layers through the sink abstraction.
- Attaching writer-level metadata:
  - `project_id`
  - `drawing_id`
  - `view_id`
  - `source_component_id`
  - `is_ai_generated`
- Grouping one batch write into one generation scope.

## What remains blocked on AutoCAD

- Referencing `AcDbMgd.dll` and related AutoCAD .NET assemblies.
- Opening a real AutoCAD transaction and committing entities to a DWG.
- Writing metadata into XData or extension dictionaries.
- Verifying actual undo behavior inside AutoCAD.

## Planned future smoke test once AutoCAD integration exists

1. Load the plugin shell into AutoCAD.
2. Run the writer path with the canonical instruction fixture.
3. Confirm that line, polyline, text, and aligned dimension entities appear on
   the expected layers.
4. Inspect generated objects for metadata.
5. Undo once and confirm the whole batch is removed as one operation.
