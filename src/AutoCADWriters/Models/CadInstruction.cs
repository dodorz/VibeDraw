namespace VibeDraw.AutoCADWriters.Models;

public abstract record CadInstruction(
    string Kind,
    string Id,
    string Layer,
    string ViewId,
    string SourceComponentId);

public sealed record LineInstruction(
    string Id,
    string Layer,
    string ViewId,
    string SourceComponentId,
    Point2D From,
    Point2D To)
    : CadInstruction("line", Id, Layer, ViewId, SourceComponentId);

public sealed record PolylineInstruction(
    string Id,
    string Layer,
    string ViewId,
    string SourceComponentId,
    IReadOnlyList<Point2D> Points,
    bool Closed)
    : CadInstruction("polyline", Id, Layer, ViewId, SourceComponentId);

public sealed record TextInstruction(
    string Id,
    string Layer,
    string ViewId,
    string SourceComponentId,
    Point2D Position,
    string Text,
    double Height)
    : CadInstruction("text", Id, Layer, ViewId, SourceComponentId);

public sealed record AlignedDimensionInstruction(
    string Id,
    string Layer,
    string ViewId,
    string SourceComponentId,
    Point2D From,
    Point2D To,
    Point2D DimensionLinePoint,
    string Text)
    : CadInstruction("aligned_dimension", Id, Layer, ViewId, SourceComponentId);
