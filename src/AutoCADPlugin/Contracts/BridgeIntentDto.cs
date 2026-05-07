using System.Text.Json.Serialization;

namespace VibeDraw.AutoCADPlugin.Contracts;

public sealed record BridgeIntentDto
{
    [JsonPropertyName("bridge_type")]
    public string BridgeType { get; init; } = string.Empty;

    [JsonPropertyName("material")]
    public string Material { get; init; } = string.Empty;

    [JsonPropertyName("spans_m")]
    public IReadOnlyList<double> SpansM { get; init; } = [];

    [JsonPropertyName("deck_width_m")]
    public double DeckWidthM { get; init; }

    [JsonPropertyName("alignment_type")]
    public string? AlignmentType { get; init; }

    [JsonPropertyName("start_station")]
    public string? StartStation { get; init; }

    [JsonPropertyName("superstructure")]
    public SuperstructureDto? Superstructure { get; init; }

    [JsonPropertyName("substructure")]
    public SubstructureDto? Substructure { get; init; }

    [JsonPropertyName("requested_drawings")]
    public IReadOnlyList<string> RequestedDrawings { get; init; } = [];

    [JsonPropertyName("assumptions")]
    public IReadOnlyList<string> Assumptions { get; init; } = [];

    [JsonPropertyName("questions")]
    public IReadOnlyList<string> Questions { get; init; } = [];
}

public sealed record SuperstructureDto
{
    [JsonPropertyName("section_type")]
    public string? SectionType { get; init; }

    [JsonPropertyName("girder_depth_policy")]
    public string? GirderDepthPolicy { get; init; }

    [JsonPropertyName("girder_depth_m")]
    public double? GirderDepthM { get; init; }
}

public sealed record SubstructureDto
{
    [JsonPropertyName("pier_type")]
    public string? PierType { get; init; }

    [JsonPropertyName("abutment_type")]
    public string? AbutmentType { get; init; }
}
