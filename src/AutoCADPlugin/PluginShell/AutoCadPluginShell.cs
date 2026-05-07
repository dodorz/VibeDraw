using VibeDraw.AutoCADPlugin.Commands;
using VibeDraw.AutoCADPlugin.Host;
using VibeDraw.AutoCADPlugin.ViewModels;

namespace VibeDraw.AutoCADPlugin.PluginShell;

public sealed class AutoCadPluginShell(IPluginPanelHost panelHost, BridgePanelViewModel viewModel)
{
    public IReadOnlyList<string> RegisteredCommands { get; } = PluginCommandNames.All;

    public BridgePanelViewModel ViewModel { get; } = viewModel;

    public PluginCommandResult Execute(string commandName)
    {
        return commandName switch
        {
            PluginCommandNames.AiBridge => OpenBridgePanel(),
            PluginCommandNames.AiBridgeRegenerate => PluginCommandResult.NotImplemented(
                "Regeneration command is reserved for the metadata/regeneration package."),
            PluginCommandNames.AiBridgeEdit => PluginCommandResult.NotImplemented(
                "Structured model editing is reserved for a later plugin-shell iteration."),
            PluginCommandNames.AiBridgeExportModel => PluginCommandResult.NotImplemented(
                "Model export is reserved for a later persistence iteration."),
            _ => throw new ArgumentOutOfRangeException(nameof(commandName), commandName, "Unknown plugin command."),
        };
    }

    private PluginCommandResult OpenBridgePanel()
    {
        panelHost.ShowBridgePanel(ViewModel);
        return PluginCommandResult.Success("Bridge panel opened.");
    }
}
