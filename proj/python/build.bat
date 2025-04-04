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
@REM @REM --onefile 단일파일 / --windowed 콘솔 삭제 / --uac-admin 관리자 권한

echo.
echo.
echo ********************
echo * Build completed! *
echo ********************
echo.
echo.

pause