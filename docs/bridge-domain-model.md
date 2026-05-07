# Bridge Domain Model

## Purpose

The bridge domain model is the main abstraction layer. It preserves engineering
intent independently of AutoCAD entities.

The model should describe bridge objects first, not lines and circles.

## Model Layers

```text
BridgeIntent
  Natural-language interpretation. May contain missing or uncertain fields.

BridgeModel
  Confirmed engineering model. Used as the source of truth.

DrawingModel
  Drawing-specific representation: views, layout, scale, annotations, and
  drawing conventions.
```

## Initial BridgeModel Example

```json
{
  "project_id": "bridge_001",
  "bridge": {
    "type": "continuous_girder",
    "material": "prestressed_concrete",
    "spans_m": [40, 70, 40],
    "deck_width_m": 7.5,
    "alignment": {
      "type": "straight",
      "start_station": "K0+000"
    },
    "superstructure": {
      "section_type": "single_box_single_cell",
      "girder_depth_policy": "auto"
    },
    "substructure": {
      "pier_type": "double_column",
      "abutment_type": "gravity"
    },
    "drawings": [
      "general_arrangement",
      "plan",
      "elevation",
      "typical_section"
    ]
  }
}
```

## Initial Domain Objects

- Project.
- Bridge.
- Alignment.
- Station system.
- Span arrangement.
- Girder system.
- Typical cross section.
- Pier.
- Abutment.
- Support line.
- Deck width.
- Barrier/railing.
- Pavement layer.
- Drawing sheet.
- Drawing view.
- Dimension chain.
- Label.

## Defaulting Strategy

LLM-generated defaults must be explicit. The system can fill missing values, but
the user should be able to inspect and edit them.

Example default assumptions:

- Straight bridge.
- Prestressed concrete continuous box girder.
- Single-box single-cell section.
- Equal deck width.
- Default pier and abutment type.
- Default drawing list: plan, elevation, typical section.

## Validation Rules

The deterministic validator should check:

- Span list is non-empty and positive.
- Deck width is positive.
- Units are normalized.
- Required drawing parameters exist before generation.
- View scale and layout are valid.
- Model references are stable.

Later versions can add engineering code checks, but MVP validation should focus
on data completeness and drawing consistency.

