@echo off
setlocal
cd /d "%~dp0"

if not exist "backend\.venv\Scripts\python.exe" (
    echo ERROR: The backend Python environment was not found.
    pause
    exit /b 1
)

echo Historia AI - package the completed Gemini index
echo The existing deployed index archive will not be changed.
echo.

pushd backend
.venv\Scripts\python.exe -m app.scripts.package_gemini_index
set "PACKAGE_EXIT_CODE=%ERRORLEVEL%"
popd

echo.
if "%PACKAGE_EXIT_CODE%"=="0" (
    echo Packaging completed successfully.
) else (
    echo Packaging failed. The completed index was not changed.
)
echo Press any key to close this window.
pause >nul
exit /b %PACKAGE_EXIT_CODE%
