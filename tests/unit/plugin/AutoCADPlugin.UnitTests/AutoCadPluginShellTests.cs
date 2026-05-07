using VibeDraw.AutoCADPlugin.Commands;
using VibeDraw.AutoCADPlugin.Fixtures;
using VibeDraw.AutoCADPlugin.Host;
using VibeDraw.AutoCADPlugin.PluginShell;
using VibeDraw.AutoCADPlugin.Services;
using VibeDraw.AutoCADPlugin.ViewModels;
using Xunit;

namespace VibeDraw.Tests.Unit.Plugin;

public sealed class AutoCadPluginShellTests
{
    [Fact]
    public void ExecuteAiBridgeOpensPanelAndExposesExpectedCommands()
    {
        var panelHost = new FakePanelHost();
        var viewModel = new BridgePanelViewModel(
            new FixtureBackedIntentServiceClient(GetContractsFixturePath("parse-initial-intent.response.valid.json")),
            new FileSystemCanonicalPromptProvider(GetPromptFixturePath()));
        var pluginShell = new AutoCadPluginShell(panelHost, viewModel);

        var result = pluginShell.Execute(PluginCommandNames.AiBridge);

        Assert.True(result.Succeeded);
        Assert.True(panelHost.WasShown);
        Assert.Same(viewModel, panelHost.ViewModel);
        Assert.Equal(
            [
                PluginCommandNames.AiBridge,
                PluginCommandNames.AiBridgeRegenerate,
                PluginCommandNames.AiBridgeEdit,
                PluginCommandNames.AiBridgeExportModel,
            ],
            pluginShell.RegisteredCommands);
    }

    [Fact]
    public void PlaceholderCommandsReturnExplicitNotImplementedResult()
    {
        var panelHost = new FakePanelHost();
        var viewModel = new BridgePanelViewModel(
            new FixtureBackedIntentServiceClient(GetContractsFixturePath("parse-initial-intent.response.valid.json")),
            new FileSystemCanonicalPromptProvider(GetPromptFixturePath()));
        var pluginShell = new AutoCadPluginShell(panelHost, viewModel);

        var result = pluginShell.Execute(PluginCommandNames.AiBridgeRegenerate);

        Assert.False(result.Succeeded);
        Assert.Contains("reserved", result.Message, StringComparison.OrdinalIgnoreCase);
    }

    private static string GetPromptFixturePath()
    {
        return Path.GetFullPath(Path.Combine(
            AppContext.BaseDirectory,
            "..", "..", "..", "..", "..", "..", "..",
            "fixtures", "prompts", "canonical-initial-prompt.txt"));
    }

    private static string GetContractsFixturePath(string fileName)
    {
        return Path.GetFullPath(Path.Combine(
            AppContext.BaseDirectory,
            "..", "..", "..", "..", "..", "..", "..",
            "tests", "contracts", fileName));
    }

    private sealed class FakePanelHost : IPluginPanelHost
    {
        public bool WasShown { get; private set; }

        public BridgePanelViewModel? ViewModel { get; private set; }

        public void ShowBridgePanel(BridgePanelViewModel viewModel)
        {
            WasShown = true;
            ViewModel = viewModel;
        }
    }
}
