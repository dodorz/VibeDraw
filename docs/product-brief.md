# Product Brief

## Goal

Build an LLM-assisted CAD drawing tool for bridge engineering. The long-term
interaction should be high-level and intent-oriented, for example:

```text
Draw a prestressed continuous girder bridge with spans 40+70+40 m and bridge
width 7.5 m.
```

The product should generate editable 2D AutoCAD drawings and support iterative
modification by the user.

## Initial Product Boundary

In scope:

- AutoCAD plugin.
- 2D bridge drawings.
- Natural language input.
- Structured bridge parameter model.
- General arrangement drawings.
- Plan view, elevation view, and typical cross section.
- AutoCAD-native editable entities.
- Local regeneration of AI-generated drawing regions.

Out of scope for the first version:

- progeCAD and other AutoCAD-compatible products.
- FreeCAD integration.
- 3D modeling.
- BIM/IFC.
- Detailed reinforcement drawings.
- Detailed prestressing tendon layout.
- Structural calculation and code compliance.

## Target Workflow

```text
1. User opens AutoCAD and runs the plugin command.
2. User describes a bridge in natural language.
3. The system parses intent and produces a parameter draft.
4. The system lists assumptions and missing critical parameters.
5. User confirms or edits the parameters.
6. The plugin generates editable AutoCAD entities.
7. User gives follow-up instructions.
8. The system updates the bridge model and regenerates affected views.
9. User continues editing the DWG in normal AutoCAD workflows.
```

## Product Principle

The product should feel like:

```text
AI turns bridge design intent into editable, iterative, engineering-style
AutoCAD drawings.
```

It should not feel like:

```text
AI draws a pile of disconnected lines.
```

