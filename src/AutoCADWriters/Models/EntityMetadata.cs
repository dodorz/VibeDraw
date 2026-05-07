namespace VibeDraw.AutoCADWriters.Models;

public sealed record EntityMetadata(
    string ProjectId,
    string DrawingId,
    string ViewId,
    string SourceComponentId,
    bool IsAiGenerated);
