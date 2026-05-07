# Preview App

This is the easiest way to try VibeDraw without AutoCAD.

Open:

- `preview-app/index.html`

The page runs fully client-side when using local parsing.

If you want to use the real local intent service, start:

- `src/LlmService/server.py`

## What it does

- parses a natural-language bridge description into parameters
- applies follow-up patch instructions to the current bridge model
- edits bridge parameters
- regenerates a deterministic drawing preview
- shows the current `BridgeModel`
- shows the current `CadInstruction` batch
- exports SVG and JSON

## Parser modes

- `Local rule parser`
  Runs entirely in the page with no service dependency.
- `LLM service mock`
  Calls the local VibeDraw HTTP service in deterministic mock mode.
- `LLM service via Ollama`
  Calls the local VibeDraw HTTP service, which forwards to your local Ollama
  instance using the selected model name.

## Current limitations

- The local parser is rule-based rather than model-based.
- The service-backed parser depends on the local VibeDraw service being started.
- The Ollama-backed parser depends on Ollama being started and the selected
  model being available.
- It currently focuses on the MVP bridge vocabulary: spans, deck width, section
  type, pier type, abutment type, station, and optional girder depth.

## Suggested prompt style

Try inputs like:

- `画一座40+70+40米跨径、桥宽7.5米的预应力连续梁桥，采用单箱单室，双柱墩，重力式桥台。`
- `Draw a prestressed continuous girder bridge with spans 30+50+30 m, deck width 9.5 m, and manual girder depth 3.2 m.`

Suggested patch prompts:

- `把中跨改成75米。`
- `桥宽改成9米，采用单箱双室。`
- `Change the middle span to 90 m and use solid piers.`
