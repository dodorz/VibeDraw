using VibeDraw.AutoCADWriters.Loading;
using VibeDraw.AutoCADWriters.Models;
using VibeDraw.AutoCADWriters.Sinks;
using VibeDraw.AutoCADWriters.Writers;
using Xunit;

namespace VibeDraw.Tests.Integration.Writers;

public sealed class CanonicalFixtureWriterTests
{
    [Fact]
    public void WritesCanonicalFixtureIntoSingleGenerationScope()
    {
        var fixturePath = Path.GetFullPath(Path.Combine(
            AppContext.BaseDirectory,
            "..", "..", "..", "..", "..", "..", "..",
            "fixtures", "cad-instructions", "canonical-general-arrangement.json"));
        var batch = CadInstructionBatchLoader.LoadFromFile(fixturePath);
        var sink = new FakeAutoCadSink();
        var writer = new AutoCadBatchWriter();

        var result = writer.Write(batch, sink);

        Assert.Equal(batch.Instructions.Count, sink.Entities.Count);
        Assert.Single(sink.GenerationRecords);
        var generation = sink.GenerationRecords[0];
        Assert.Equal(batch.ProjectId, generation.ProjectId);
        Assert.Equal(batch.DrawingId, generation.DrawingId);
        Assert.Equal(batch.Instructions.Count, generation.EntityCount);
        Assert.Equal(
            ["BRIDGE_DECK", "BRIDGE_GIRDER", "BRIDGE_SECTION", "DIM", "TEXT"],
            generation.LayersTouched);
        Assert.Equal(
            ["BRIDGE_DECK", "BRIDGE_GIRDER", "BRIDGE_SECTION", "DIM", "TEXT"],
            result.LayersTouched);
    }

    [Fact]
    public void PropagatesRequiredMetadataToEveryWrittenEntity()
    {
        var batch = new CadInstructionBatch(
            "bridge_001",
            "general_arrangement_001",
            [
                new LineInstruction("line_001", "AXIS", "plan_main", "axis", new Point2D(0, 0), new Point2D(5, 0)),
                new PolylineInstruction("poly_001", "BRIDGE_DECK", "plan_main", "deck", [new Point2D(0, 0), new Point2D(5, 0)], false),
                new TextInstruction("text_001", "TEXT", "elevation_main", "title", new Point2D(0, 2), "TITLE", 2.5),
                new AlignedDimensionInstruction("dim_001", "DIM", "elevation_main", "span_1", new Point2D(0, -1), new Point2D(5, -1), new Point2D(2.5, -2), "5m")
            ]);
        var sink = new FakeAutoCadSink();
        var writer = new AutoCadBatchWriter();

        writer.Write(batch, sink);

        Assert.All(sink.Entities, entity =>
        {
            Assert.Equal("bridge_001", entity.Metadata.ProjectId);
            Assert.Equal("general_arrangement_001", entity.Metadata.DrawingId);
            Assert.False(string.IsNullOrWhiteSpace(entity.Metadata.ViewId));
            Assert.False(string.IsNullOrWhiteSpace(entity.Metadata.SourceComponentId));
            Assert.True(entity.Metadata.IsAiGenerated);
        });
    }

    [Fact]
    public void ReusesLayersAcrossInstructionsInsteadOfDuplicatingThem()
    {
        var batch = new CadInstructionBatch(
            "bridge_001",
            "general_arrangement_001",
            [
                new LineInstruction("line_001", "CENTERLINE", "plan_main", "axis_1", new Point2D(0, 0), new Point2D(5, 0)),
                new LineInstruction("line_002", "CENTERLINE", "plan_main", "axis_2", new Point2D(0, 1), new Point2D(5, 1)),
                new TextInstruction("text_001", "TEXT", "plan_main", "label", new Point2D(0, 2), "Axis", 2)
            ]);
        var sink = new FakeAutoCadSink();
        var writer = new AutoCadBatchWriter();

        writer.Write(batch, sink);

        Assert.Equal(2, sink.Layers.Count);
        Assert.Contains("CENTERLINE", sink.Layers);
        Assert.Contains("TEXT", sink.Layers);
    }
}
