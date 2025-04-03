@echo off
set EXE_NAME=로드나인치터
echo Cleaning up previous build files...

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist main.spec del main.spec

echo Building new executable...

REM pyinstaller --onefile main.py
REM pyinstaller --onefile --windowed --icon=myicon.ico --name MyApp main.py
pyinstaller --onefile --windowed --name %EXE_NAME% main.py

echo.
echo.
echo ********************
echo * Build completed! *
echo ********************
echo.
echo.

pause