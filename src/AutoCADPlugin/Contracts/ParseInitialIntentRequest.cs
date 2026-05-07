using System.Text.Json.Serialization;

namespace VibeDraw.AutoCADPlugin.Contracts;

public sealed record ParseInitialIntentRequest
{
    [JsonPropertyName("type")]
    public string Type { get; init; } = "parse_initial_intent";

    [JsonPropertyName("prompt")]
    public string Prompt { get; init; } = string.Empty;
}
