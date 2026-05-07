using System.Text.Json.Serialization;

namespace VibeDraw.AutoCADPlugin.Contracts;

public sealed record ParseInitialIntentResponse
{
    [JsonPropertyName("intent")]
    public BridgeIntentDto Intent { get; init; } = new();

    [JsonPropertyName("assumptions")]
    public IReadOnlyList<string> Assumptions { get; init; } = [];

    [JsonPropertyName("questions")]
    public IReadOnlyList<string> Questions { get; init; } = [];
}
