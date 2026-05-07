# Writer Test Notes

Run the writer package tests with the local .NET SDK path:

```powershell
& 'C:\~\Tools\Scoop\apps\dotnet-SDK-LTS\current\dotnet.exe' test tests\unit\writers\AutoCADWriters.UnitTests\AutoCADWriters.UnitTests.csproj
& 'C:\~\Tools\Scoop\apps\dotnet-SDK-LTS\current\dotnet.exe' test tests\integration\writers\AutoCADWriters.IntegrationTests\AutoCADWriters.IntegrationTests.csproj
```

If the local machine only has a newer .NET runtime installed, use runtime
roll-forward so `net8.0` tests can still execute:

```powershell
$env:DOTNET_ROLL_FORWARD='Major'
& 'C:\~\Tools\Scoop\apps\dotnet-SDK-LTS\current\dotnet.exe' test tests\unit\writers\AutoCADWriters.UnitTests\AutoCADWriters.UnitTests.csproj
& 'C:\~\Tools\Scoop\apps\dotnet-SDK-LTS\current\dotnet.exe' test tests\integration\writers\AutoCADWriters.IntegrationTests\AutoCADWriters.IntegrationTests.csproj
```

The current tests exercise the deterministic writer abstraction and fake sink.
They do not require AutoCAD assemblies.
