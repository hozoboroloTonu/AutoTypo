@echo off
setlocal enabledelayedexpansion

echo =======================================================
echo     AUTO TYPO - SINGLE FILE PORTABLE BUILD SCRIPT
echo =======================================================
echo.

:: 1. Verify Python
echo [1/5] Verifying Python installation...
py --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    python --version >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Python was not found on your system PATH.
        pause
        exit /b 1
    ) else (
        set PY_CMD=python
    )
) else (
    set PY_CMD=py
)
echo [OK] Using %PY_CMD%

:: 2. Verify / Install Dependencies
echo.
echo [2/5] Checking requirements...
%PY_CMD% -m pip install -r requirements.txt --quiet
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)
echo [OK] Dependencies verified.

:: 3. Clean old build outputs
echo.
echo [3/5] Cleaning previous build artifacts...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
echo [OK] Clean completed.

:: 4. Build single-file application with PyInstaller
echo.
echo [4/5] Compiling single-file standalone Windows executable...
%PY_CMD% -m PyInstaller AutoTypo.spec --noconfirm --clean
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] PyInstaller build failed.
    pause
    exit /b 1
)
echo [OK] Compilation successful.

:: 5. Completion Summary
echo.
echo [5/5] Build Complete!
echo =======================================================
echo Standalone Executable Location:
echo %~dp0dist\AutoTypo.exe
echo =======================================================
echo.
echo You can run the application directly by double-clicking:
echo dist\AutoTypo.exe
echo.
pause
