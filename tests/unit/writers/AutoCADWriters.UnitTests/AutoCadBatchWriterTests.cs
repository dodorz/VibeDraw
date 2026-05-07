using VibeDraw.AutoCADWriters.Models;
using VibeDraw.AutoCADWriters.Sinks;
using VibeDraw.AutoCADWriters.Writers;
using Xunit;

namespace VibeDraw.Tests.Unit.Writers;

public sealed class AutoCadBatchWriterTests
{
    private readonly AutoCadBatchWriter _writer = new();

    [Fact]
    public void WritesLineInstructionIntoFakeSinkWithMetadata()
    {
        var batch = new CadInstructionBatch(
            "project_alpha",
            "drawing_main",
            [
                new LineInstruction("line_001", "CENTERLINE", "plan_main", "bridge_axis", new Point2D(0, 0), new Point2D(10, 0))
            ]);

        var sink = new FakeAutoCadSink();

        var result = _writer.Write(batch, sink);

        var entity = Assert.IsType<FakeLineEntity>(Assert.Single(sink.Entities));
        Assert.Equal(new Point2D(0, 0), entity.From);
        Assert.Equal(new Point2D(10, 0), entity.To);
        Assert.Equal("CENTERLINE", entity.Layer);
        Assert.Equal("project_alpha", entity.Metadata.ProjectId);
        Assert.Equal("drawing_main", entity.Metadata.DrawingId);
        Assert.Equal("plan_main", entity.Metadata.ViewId);
        Assert.Equal("bridge_axis", entity.Metadata.SourceComponentId);
        Assert.True(entity.Metadata.IsAiGenerated);
        Assert.Equal(1, result.InstructionsWritten);
    }

    [Fact]
    public void WritesPolylineInstructionIntoFakeSink()
    {
        var batch = new CadInstructionBatch(
            "project_alpha",
            "drawing_main",
            [
                new PolylineInstruction(
                    "poly_001",
                    "BRIDGE_DECK",
                    "plan_main",
                    "deck_outline",
                    [new Point2D(0, 0), new Point2D(5, 0), new Point2D(5, 2), new Point2D(0, 2)],
                    true)
            ]);

        var sink = new FakeAutoCadSink();

        _writer.Write(batch, sink);

        var entity = Assert.IsType<FakePolylineEntity>(Assert.Single(sink.Entities));
        Assert.True(entity.Closed);
        Assert.Equal(4, entity.Points.Count);
        Assert.Equal("deck_outline", entity.Metadata.SourceComponentId);
    }

    [Fact]
    public void WritesTextInstructionIntoFakeSink()
    {
        var batch = new CadInstructionBatch(
            "project_alpha",
            "drawing_main",
            [
                new TextInstruction(
                    "text_001",
                    "TEXT",
                    "elevation_main",
                    "drawing_title",
                    new Point2D(1, 2),
                    "GENERAL ARRANGEMENT",
                    3.5)
            ]);

        var sink = new FakeAutoCadSink();

        _writer.Write(batch, sink);

        var entity = Assert.IsType<FakeTextEntity>(Assert.Single(sink.Entities));
        Assert.Equal("GENERAL ARRANGEMENT", entity.Text);
        Assert.Equal(3.5, entity.Height);
        Assert.Equal(new Point2D(1, 2), entity.Position);
    }

    [Fact]
    public void WritesAlignedDimensionInstructionIntoFakeSink()
    {
        var batch = new CadInstructionBatch(
            "project_alpha",
            "drawing_main",
            [
                new AlignedDimensionInstruction(
                    "dim_001",
                    "DIM",
                    "elevation_main",
                    "span_1",
                    new Point2D(0, -5),
                    new Point2D(40, -5),
                    new Point2D(20, -12),
                    "40m")
            ]);

        var sink = new FakeAutoCadSink();

        _writer.Write(batch, sink);

        var entity = Assert.IsType<FakeAlignedDimensionEntity>(Assert.Single(sink.Entities));
        Assert.Equal(new Point2D(20, -12), entity.DimensionLinePoint);
        Assert.Equal("40m", entity.Text);
        Assert.Equal("span_1", entity.Metadata.SourceComponentId);
    }
}
