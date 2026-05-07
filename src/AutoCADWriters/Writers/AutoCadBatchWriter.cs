using VibeDraw.AutoCADWriters.Models;
using VibeDraw.AutoCADWriters.Sinks;

namespace VibeDraw.AutoCADWriters.Writers;

public sealed class AutoCadBatchWriter
{
    public WriterBatchResult Write(CadInstructionBatch batch, IAutoCadWriterSink sink)
    {
        ArgumentNullException.ThrowIfNull(batch);
        ArgumentNullException.ThrowIfNull(sink);

        var layersTouched = new HashSet<string>(StringComparer.Ordinal);

        using var scope = sink.BeginGeneration(batch.ProjectId, batch.DrawingId);
        foreach (var instruction in batch.Instructions)
        {
            scope.EnsureLayer(instruction.Layer);
            layersTouched.Add(instruction.Layer);

            var metadata = new EntityMetadata(
                batch.ProjectId,
                batch.DrawingId,
                instruction.ViewId,
                instruction.SourceComponentId,
                true);

            switch (instruction)
            {
                case LineInstruction line:
                    scope.WriteLine(line, metadata);
                    break;
                case PolylineInstruction polyline:
                    scope.WritePolyline(polyline, metadata);
                    break;
                case TextInstruction text:
                    scope.WriteText(text, metadata);
                    break;
                case AlignedDimensionInstruction alignedDimension:
                    scope.WriteAlignedDimension(alignedDimension, metadata);
                    break;
                default:
                    throw new InvalidOperationException(
                        $"Writer does not support instruction type '{instruction.GetType().Name}'.");
            }
        }

        scope.Commit();

        return new WriterBatchResult(
            batch.ProjectId,
            batch.DrawingId,
            batch.Instructions.Count,
            layersTouched.OrderBy(layer => layer, StringComparer.Ordinal).ToArray());
    }
}
