namespace VibeDraw.AutoCADWriters.Models;

public abstract record FakeAutoCadEntity(
    string InstructionId,
    string Layer,
    EntityMetadata Metadata);

public sealed record FakeLineEntity(
    string InstructionId,
    string Layer,
    EntityMetadata Metadata,
    Point2D From,
    Point2D To)
    : FakeAutoCadEntity(InstructionId, Layer, Metadata);

public sealed record FakePolylineEntity(
    string InstructionId,
    string Layer,
    EntityMetadata Metadata,
    IReadOnlyList<Point2D> Points,
    bool Closed)
    : FakeAutoCadEntity(InstructionId, Layer, Metadata);

public sealed record FakeTextEntity(
    string InstructionId,
    string Layer,
    EntityMetadata Metadata,
    Point2D Position,
    string Text,
    double Height)
    : FakeAutoCadEntity(InstructionId, Layer, Metadata);

public sealed record FakeAlignedDimensionEntity(
    string InstructionId,
    string Layer,
    EntityMetadata Metadata,
    Point2D From,
    Point2D To,
    Point2D DimensionLinePoint,
    string Text)
    : FakeAutoCadEntity(InstructionId, Layer, Metadata);
