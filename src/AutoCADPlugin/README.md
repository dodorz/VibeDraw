# AutoCAD Plugin Shell

This package contains the first plugin-shell scaffold for the VibeDraw MVP.

Current scope:

- command registration shape
- panel host abstraction
- prompt submission workflow
- mock or fixture-backed intent service client
- view-model projection of returned bridge intent, assumptions, and questions

Not implemented yet:

- direct Autodesk `IExtensionApplication` integration
- `PaletteSet` construction with real WPF controls
- AutoCAD command attributes and host loading
- generation handoff to a real AutoCAD writer sink

Primary entry points:

- `PluginShell.AutoCadPluginShell`
- `ViewModels.BridgePanelViewModel`
- `Services.FixtureBackedIntentServiceClient`
- `Services.HttpBridgeIntentServiceClient`
