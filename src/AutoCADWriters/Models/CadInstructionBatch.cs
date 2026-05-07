namespace VibeDraw.AutoCADWriters.Models;

public sealed record CadInstructionBatch(
    string ProjectId,
    string DrawingId,
    IReadOnlyList<CadInstruction> Instructions);
