using VibeDraw.AutoCADWriters.Models;

namespace VibeDraw.AutoCADWriters.Sinks;

public sealed class FakeAutoCadSink : IAutoCadWriterSink
{
    private readonly HashSet<string> _layers = new(StringComparer.Ordinal);
    private readonly List<FakeAutoCadEntity> _entities = [];
    private readonly List<FakeGenerationRecord> _generationRecords = [];

    public IReadOnlyCollection<string> Layers => _layers;

    public IReadOnlyList<FakeAutoCadEntity> Entities => _entities;

    public IReadOnlyList<FakeGenerationRecord> GenerationRecords => _generationRecords;

    public IAutoCadGenerationScope BeginGeneration(string projectId, string drawingId)
        => new FakeGenerationScope(this, projectId, drawingId);

    private sealed class FakeGenerationScope(FakeAutoCadSink owner, string projectId, string drawingId)
        : IAutoCadGenerationScope
    {
        private readonly HashSet<string> _layersTouched = new(StringComparer.Ordinal);
        private readonly List<FakeAutoCadEntity> _writtenEntities = [];
        private bool _committed;

        public void EnsureLayer(string layerName)
        {
            owner._layers.Add(layerName);
            _layersTouched.Add(layerName);
        }

        public void WriteLine(LineInstruction instruction, EntityMetadata metadata)
            => _writtenEntities.Add(new FakeLineEntity(
                instruction.Id,
                instruction.Layer,
                metadata,
                instruction.From,
                instruction.To));

        public void WritePolyline(PolylineInstruction instruction, EntityMetadata metadata)
            => _writtenEntities.Add(new FakePolylineEntity(
                instruction.Id,
                instruction.Layer,
                metadata,
                instruction.Points,
                instruction.Closed));

        public void WriteText(TextInstruction instruction, EntityMetadata metadata)
            => _writtenEntities.Add(new FakeTextEntity(
                instruction.Id,
                instruction.Layer,
                metadata,
                instruction.Position,
                instruction.Text,
                instruction.Height));

        public void WriteAlignedDimension(AlignedDimensionInstruction instruction, EntityMetadata metadata)
            => _writtenEntities.Add(new FakeAlignedDimensionEntity(
                instruction.Id,
                instruction.Layer,
                metadata,
                instruction.From,
                instruction.To,
                instruction.DimensionLinePoint,
                instruction.Text));

        public void Commit()
        {
            if (_committed)
            {
                throw new InvalidOperationException("Generation scope has already been committed.");
            }

            owner._entities.AddRange(_writtenEntities);
            owner._generationRecords.Add(new FakeGenerationRecord(
                projectId,
                drawingId,
                _writtenEntities.Count,
                _layersTouched.OrderBy(layer => layer, StringComparer.Ordinal).ToArray()));
            _committed = true;
        }

        public void Dispose()
        {
        }
    }
}

public sealed record FakeGenerationRecord(
    string ProjectId,
    string DrawingId,
    int EntityCount,
    IReadOnlyList<string> LayersTouched);
