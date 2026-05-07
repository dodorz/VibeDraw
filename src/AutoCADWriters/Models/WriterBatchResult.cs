namespace VibeDraw.AutoCADWriters.Models;

public sealed record WriterBatchResult(
    string ProjectId,
    string DrawingId,
    int InstructionsWritten,
    IReadOnlyCollection<string> LayersTouched);
