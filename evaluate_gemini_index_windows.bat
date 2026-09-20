@echo off
setlocal
cd /d "%~dp0"

if not exist ".env" (
    echo ERROR: The .env file was not found in the project folder.
    pause
    exit /b 1
)

if not exist "backend\.venv\Scripts\python.exe" (
    echo ERROR: The backend Python environment was not found.
    pause
    exit /b 1
)

set "EMBEDDING_PROVIDER=gemini"
set "EMBEDDING_MODEL_NAME=gemini-embedding-001"
set "EMBEDDING_OUTPUT_DIMENSIONALITY=768"
set "EMBEDDING_DOCUMENT_TASK_TYPE=RETRIEVAL_DOCUMENT"
set "EMBEDDING_QUERY_TASK_TYPE=QUESTION_ANSWERING"
set "EMBEDDING_REQUEST_TIMEOUT_SECONDS=60"
set "EMBEDDING_MAX_RETRIES=8"
set "EMBEDDING_RATE_LIMIT_RETRY_SECONDS=30"
set "CHROMA_PERSIST_DIR=%CD%\data\chroma_experiments\gemini_embedding_001"
set "CHROMA_COLLECTION_NAME=historia_gemini_embedding_001"

echo Historia AI - bilingual Gemini retrieval evaluation
echo Testing Arabic and English retrieval against the completed index.
echo.

pushd backend
.venv\Scripts\python.exe -m app.scripts.evaluate_retrieval --top-k 5 --include-cases > evaluation\bilingual_retrieval_gemini_results.json
set "EVAL_EXIT_CODE=%ERRORLEVEL%"

if "%EVAL_EXIT_CODE%"=="0" (
    echo Evaluation completed successfully.
    echo.
    type evaluation\bilingual_retrieval_gemini_results.json
    echo.
    echo Results saved to backend\evaluation\bilingual_retrieval_gemini_results.json
) else (
    echo Evaluation failed. No index data was changed.
)
popd

echo.
echo Press any key to close this window.
pause >nul
exit /b %EVAL_EXIT_CODE%
