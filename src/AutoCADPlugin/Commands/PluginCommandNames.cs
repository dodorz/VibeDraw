namespace VibeDraw.AutoCADPlugin.Commands;

public static class PluginCommandNames
{
    public const string AiBridge = "AIBRIDGE";
    public const string AiBridgeRegenerate = "AIBRIDGE_REGEN";
    public const string AiBridgeEdit = "AIBRIDGE_EDIT";
    public const string AiBridgeExportModel = "AIBRIDGE_EXPORT_MODEL";

    public static IReadOnlyList<string> All { get; } =
    [
        AiBridge,
        AiBridgeRegenerate,
        AiBridgeEdit,
        AiBridgeExportModel,
    ];
}
