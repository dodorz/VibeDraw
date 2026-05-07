# Plugin Manual Smoke Notes

This package does not yet include real Autodesk host integration. Manual smoke
checks are therefore split into two stages.

## Stage 1: Non-host Smoke

Confirm:

1. Unit tests pass for the plugin shell package.
2. The canonical prompt fixture loads from `fixtures/prompts/canonical-initial-prompt.txt`.
3. The fixture-backed intent client can populate assumptions and parameter rows.

## Stage 2: AutoCAD Host Integration Later

Blocked until Autodesk assemblies and an AutoCAD host are available.

Expected future smoke steps:

1. Load the plugin assembly into AutoCAD.
2. Run `AIBRIDGE`.
3. Confirm the bridge panel opens.
4. Submit the canonical prompt through a real panel.
5. Confirm assumptions and parameter rows render.
6. Confirm the next integration layer can hand off generation to the writer path.

## Current Blocking Dependencies

- `AcCoreMgd.dll`
- `AcDbMgd.dll`
- `AcMgd.dll`
- a real `PaletteSet` host surface
- command attributes or `IExtensionApplication` bootstrap wired against Autodesk assemblies
