@echo off
setlocal

set "ROOT=%~dp0"
cd /d "%ROOT%"

set "PYTHON_EXE=C:\~\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
set "SERVICE_URL=http://127.0.0.1:8011/health"
set "OLLAMA_TAGS_URL=http://127.0.0.1:11434/api/tags"
set "PREVIEW_PAGE=%ROOT%preview-app\index.html"

echo VibeDraw preview launcher
echo.

if not exist "%PYTHON_EXE%" (
  echo Bundled Python runtime was not found:
  echo   %PYTHON_EXE%
  echo.
  echo Start the service manually after fixing the runtime path.
  exit /b 1
)

curl -s "%SERVICE_URL%" >nul 2>nul
if %errorlevel% equ 0 (
  echo LLM service is already running at http://127.0.0.1:8011/
) else (
  echo Starting VibeDraw LLM service...
  start "VibeDraw LLM Service" /min "%PYTHON_EXE%" -m src.LlmService.server
  timeout /t 2 /nobreak >nul
  curl -s "%SERVICE_URL%" >nul 2>nul
  if %errorlevel% neq 0 (
    echo Failed to confirm the LLM service is running.
    echo Try launching it manually from:
    echo   %ROOT%
    echo.
    echo Command:
    echo   "%PYTHON_EXE%" -m src.LlmService.server
    exit /b 1
  )
  echo LLM service started at http://127.0.0.1:8011/
)

echo.
curl -s "%OLLAMA_TAGS_URL%" >nul 2>nul
if %errorlevel% equ 0 (
  echo Ollama is reachable at http://127.0.0.1:11434/
) else (
  echo Ollama is not reachable right now.
  echo If you want "LLM service via Ollama" mode, start Ollama first.
)

echo.
echo Next steps:
echo   1. The preview page will open automatically.
echo   2. In the page, choose:
echo        Parser Mode = LLM service mock
echo      or
echo        Parser Mode = LLM service via Ollama
echo   3. Use model name: glm-4.7:cloud
echo.
echo Service info:
echo   http://127.0.0.1:8011/
echo.
if exist "%PREVIEW_PAGE%" (
  start "" "%PREVIEW_PAGE%"
) else (
  echo Preview page was not found:
  echo   %PREVIEW_PAGE%
  echo.
)

pause
