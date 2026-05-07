# Preview

This package provides a no-AutoCAD MVP preview path for VibeDraw.

It consumes:

- a `BridgeModel` fixture
- the deterministic `DrawingPlan` generator
- the deterministic `CadInstruction` generator

and renders the resulting drawing batch into a lightweight SVG preview.

## Primary entry points

- `build_preview_svg`
- `render_preview_from_bridge_model`
- `python -m src.Preview.cli`

## Scope

This preview path is intended for:

- validating the product core without AutoCAD
- demoing the MVP drawing flow
- regression testing geometry and view output

It is not intended to replace the future AutoCAD host integration.

