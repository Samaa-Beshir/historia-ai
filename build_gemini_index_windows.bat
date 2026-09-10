@echo off
setlocal
cd /d "%~dp0"

if not exist ".env" (
    echo ERROR: The .env file was not found in the project folder.
    echo Add GEMINI_API_KEY to .env, then run this file again.
    pause
    exit /b 1
)

if not exist "backend\.venv\Scripts\python.exe" (
    echo ERROR: The backend Python environment was not found.
    echo Run the backend setup steps from README.md first.
    pause
    exit /b 1
)

set "EMBEDDING_PROVIDER=gemini"
set "EMBEDDING_MODEL_NAME=gemini-embedding-001"
set "EMBEDDING_OUTPUT_DIMENSIONALITY=768"
set "EMBEDDING_DOCUMENT_TASK_TYPE=RETRIEVAL_DOCUMENT"
set "EMBEDDING_QUERY_TASK_TYPE=QUESTION_ANSWERING"
set "EMBEDDING_REQUEST_TIMEOUT_SECONDS=60"
set "EMBEDDING_MAX_RETRIES=6"
set "CHROMA_PERSIST_DIR=%CD%\data\chroma_experiments\gemini_embedding_001"
set "CHROMA_COLLECTION_NAME=historia_gemini_embedding_001"

echo Historia AI - Gemini multilingual index
echo The existing progress will be preserved. Keep this window open.
echo.

pushd backend
.venv\Scripts\python.exe -m app.scripts.ingest --resume --batch-delay-seconds 65
set "INDEX_EXIT_CODE=%ERRORLEVEL%"
popd

echo.
if "%INDEX_EXIT_CODE%"=="0" (
    echo Indexing completed successfully.
) else (
    echo Indexing paused with an error. Run this file again to resume.
)
pause
exit /b %INDEX_EXIT_CODE%
