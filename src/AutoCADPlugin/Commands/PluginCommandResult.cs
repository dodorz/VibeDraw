namespace VibeDraw.AutoCADPlugin.Commands;

public sealed record PluginCommandResult(bool Succeeded, string Message)
{
    public static PluginCommandResult Success(string message) => new(true, message);

    public static PluginCommandResult NotImplemented(string message) => new(false, message);
}
