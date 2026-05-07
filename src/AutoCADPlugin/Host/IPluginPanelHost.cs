using VibeDraw.AutoCADPlugin.ViewModels;

namespace VibeDraw.AutoCADPlugin.Host;

public interface IPluginPanelHost
{
    void ShowBridgePanel(BridgePanelViewModel viewModel);
}
