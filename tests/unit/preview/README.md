# Preview Test Notes

Run the preview package tests with the bundled Python runtime:

```powershell
& 'C:\Users\dodo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.unit.preview.test_svg_renderer -v
```

Render the canonical SVG preview:

```powershell
& 'C:\Users\dodo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m src.Preview.cli
```

