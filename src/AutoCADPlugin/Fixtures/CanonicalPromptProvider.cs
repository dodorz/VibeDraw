namespace VibeDraw.AutoCADPlugin.Fixtures;

public interface ICanonicalPromptProvider
{
    string LoadCanonicalPrompt();
}

public sealed class FileSystemCanonicalPromptProvider(string promptPath) : ICanonicalPromptProvider
{
    public string PromptPath { get; } = promptPath;

    public string LoadCanonicalPrompt()
    {
        return File.ReadAllText(PromptPath).Trim();
    }
}
