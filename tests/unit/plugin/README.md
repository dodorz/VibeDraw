# Plugin Unit Tests

Run the plugin-shell unit tests with:

```powershell
& 'C:\~\Tools\Scoop\apps\dotnet-SDK-LTS\current\dotnet.exe' test `
  'C:\~\Projects\VibeDraw\tests\unit\plugin\AutoCADPlugin.UnitTests\AutoCADPlugin.UnitTests.csproj'
```

These tests intentionally avoid Autodesk assemblies. They validate:

- command registration and command routing
- canonical prompt loading
- fixture-backed mock service flow
- HTTP service client request shape
- view-model projection of assumptions, questions, and bridge parameters
