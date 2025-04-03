@echo off
set EXE_NAME=치터-로드나인
echo Cleaning up previous build files...

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist main.spec del main.spec

echo Building new executable...

REM pyinstaller --onefile main.py
pyinstaller --onefile --windowed --icon=lordnine.ico --name %EXE_NAME% main.py

echo.
echo.
echo ********************
echo * Build completed! *
echo ********************
echo.
echo.

pause