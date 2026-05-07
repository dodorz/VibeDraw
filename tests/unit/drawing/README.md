# Drawing Package Tests

This package uses Python's built-in `unittest` runner for deterministic drawing
planner and CAD instruction generator checks.

Run the package tests from the repository root:

```powershell
python -m unittest tests.golden.drawing.test_golden_outputs tests.unit.drawing.test_generator -v
```

If `python` is not on `PATH` in the current environment, use the bundled
runtime available in this thread:

```powershell
& 'C:\Users\dodo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.golden.drawing.test_golden_outputs tests.unit.drawing.test_generator -v
```

The golden tests verify that the canonical bridge fixture still produces the
frozen `DrawingPlan` and `CadInstruction` JSON outputs.
