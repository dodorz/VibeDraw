# LLM Service Test Notes

Run the local service unit tests with the bundled Python runtime:

```powershell
& 'C:\Users\dodo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.unit.llm.test_parsing -v
```

Run the service locally:

```powershell
& 'C:\Users\dodo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m src.LlmService.server
```

