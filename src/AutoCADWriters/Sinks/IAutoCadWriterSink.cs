using VibeDraw.AutoCADWriters.Models;

namespace VibeDraw.AutoCADWriters.Sinks;

public interface IAutoCadWriterSink
{
    IAutoCadGenerationScope BeginGeneration(string projectId, string drawingId);
}

public interface IAutoCadGenerationScope : IDisposable
{
    void EnsureLayer(string layerName);

    void WriteLine(LineInstruction instruction, EntityMetadata metadata);

    void WritePolyline(PolylineInstruction instruction, EntityMetadata metadata);

    void WriteText(TextInstruction instruction, EntityMetadata metadata);

    void WriteAlignedDimension(AlignedDimensionInstruction instruction, EntityMetadata metadata);

    void Commit();
}
