@echo off
echo Building omni-translator executable...
echo.

REM Install build essential package
uv add pyinstaller pillow

REM Clean previous builds
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

REM Build the executable
echo Building executable...
uv run pyinstaller omni-translator.spec

if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo Build completed successfully!
echo Executable location: dist\omni-translator.exe
echo.
pause
