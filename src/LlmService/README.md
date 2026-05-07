# LLM Service

This package provides the first local HTTP intent service for VibeDraw.

## Endpoints

- `GET /health`
- `POST /intent/parse-initial`
- `POST /intent/patch-model`

## Query Parameters

- `mode=mock|ollama`
- `model=<ollama-model-name>` when `mode=ollama`

## Run

Use the bundled Python runtime:

```powershell
& 'C:\Users\dodo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m src.LlmService.server
```

## Examples

Mock parse:

```powershell
Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8011/intent/parse-initial?mode=mock' -ContentType 'application/json' -Body '{"type":"parse_initial_intent","prompt":"画一座40+70+40米跨径、桥宽7.5米的预应力连续梁桥。"}'
```

Ollama parse:

```powershell
Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8011/intent/parse-initial?mode=ollama&model=llama3.1:8b' -ContentType 'application/json' -Body '{"type":"parse_initial_intent","prompt":"画一座40+70+40米跨径、桥宽7.5米的预应力连续梁桥。"}'
```

## Notes

- `mock` mode is deterministic and useful for tests.
- `ollama` mode uses the local Ollama HTTP API at `http://127.0.0.1:11434`.
- The Ollama response is normalized through the same MVP assumptions used by the
  mock parser, so incomplete JSON still lands on the frozen contract surface.

