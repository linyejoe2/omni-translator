#!/bin/bash

echo "Building omni-translator executable..."
echo

REM Install build essential package
uv add pyinstaller pillow

# Clean previous builds
if [ -d "build" ]; then
    rm -rf build
fi
if [ -d "dist" ]; then
    rm -rf dist
fi

# Build the executable
echo "Building executable..."
uv run pyinstaller omni-translator.spec

if [ $? -ne 0 ]; then
    echo "Build failed!"
    exit 1
fi

echo
echo "Build completed successfully!"
echo "Executable location: dist/omni-translator"
echo