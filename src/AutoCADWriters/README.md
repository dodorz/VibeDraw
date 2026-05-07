# AutoCAD Writers

This package implements the first writer-layer scaffold for the frozen
`CadInstruction` protocol.

Current status:

- Real: deterministic instruction loading, instruction dispatch, layer reuse,
  metadata propagation, and generation transaction grouping.
- Real: tests against the canonical instruction fixture.
- Scaffold only: actual AutoCAD .NET entity creation. The current environment
  does not include AutoCAD assemblies or a running AutoCAD host, so this
  package uses a fake sink that mirrors the writer concerns without taking a
  dependency on AutoCAD yet.

Primary entry points:

- `CadInstructionBatchLoader`: load a frozen batch from JSON.
- `AutoCadBatchWriter`: write a batch into a sink.
- `FakeAutoCadSink`: deterministic sink for integration and regression tests.
