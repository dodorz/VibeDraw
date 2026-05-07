# VibeDraw

VibeDraw is an LLM-assisted AutoCAD drawing tool for bridge engineering.

Current scope:

- AutoCAD only.
- AutoCAD plugin form.
- 2D bridge drawings only.
- Natural language intent -> bridge model -> drawing plan -> CAD instructions ->
  editable AutoCAD entities -> targeted regeneration.

## Repository Layout

```text
docs/       design and implementation documents
fixtures/   canonical prompts, models, plans, and instruction fixtures
src/        implementation code by package/layer
tests/      contract, unit, golden, integration, and manual test assets
```

Start with:

- `AGENTS.md`
- `docs/README.md`
- `docs/implementation-playbook.md`
- `docs/agent-task-prompts.md`

Try the no-AutoCAD preview in:

- `preview-app/index.html`

Local LLM service:

- `src/LlmService/README.md`
