@echo off
set EXE_NAME=RUNNER-로드나인
echo Cleaning up previous build files...

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist main.spec del main.spec

echo Building new executable...

@REM pyinstaller --onefile main.py
pyinstaller --clean --onefile --windowed --uac-admin --name %EXE_NAME% main.py
@REM pyinstaller --clean --onefile --windowed --uac-admin --icon=lordnine.ico --name %EXE_NAME% main.py

echo.
echo.
echo ********************
echo * Build completed! *
echo ********************
echo.
echo.

pause