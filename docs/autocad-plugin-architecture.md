# AutoCAD Plugin Architecture

## Recommended Stack

```text
C# + AutoCAD .NET API + WPF PaletteSet
```

AutoLISP can be useful for small helper scripts, but the main plugin should use
C# for reliable UI, metadata handling, transactions, and service integration.

## Main Modules

```text
CadPlugin
  Commands
  UI
  ServiceClient
  CadRuntime
  DrawingWriters
  BridgeCadAdapter
  MetadataStore
```

## Commands

Initial commands:

- `AIBRIDGE`: open the AI bridge panel.
- `AIBRIDGE_REGEN`: regenerate selected or current generated view.
- `AIBRIDGE_EDIT`: open parameter editor for the current bridge model.
- `AIBRIDGE_EXPORT_MODEL`: export current bridge model to JSON.

## UI

Initial UI panels:

- Chat panel for natural language instructions.
- Parameter panel for structured editing.
- Generation summary panel for assumptions, warnings, and affected views.

The UI should support a confirmation step before generating or regenerating
entities.

## Service Client

The plugin calls the local/backend service for:

- Intent parsing.
- Model patch generation.
- Drawing plan generation.
- CAD instruction generation.

The plugin should not depend on LLM provider details.

## CAD Runtime

Responsibilities:

- Manage AutoCAD transactions.
- Create and reuse layers.
- Create and reuse text styles.
- Create and reuse dimension styles.
- Create and insert blocks.
- Apply lineweight, linetype, and color policy.
- Group generated objects by project/view/version.

## Drawing Writers

Each writer maps one CadInstruction type to AutoCAD .NET API calls:

- LineWriter.
- PolylineWriter.
- ArcWriter.
- CircleWriter.
- TextWriter.
- DimensionWriter.
- HatchWriter.
- BlockReferenceWriter.

Writers should be small and deterministic. They should not know bridge semantics.

## Metadata Store

Every generated object should carry metadata:

```text
project_id
drawing_id
view_id
entity_role
source_component_id
generation_version
is_ai_generated
```

Preferred mechanisms:

- XData for lightweight per-entity metadata.
- XRecord / Named Object Dictionary for project-level model storage.

Also store a sidecar JSON file for full project history and LLM interaction
state.

