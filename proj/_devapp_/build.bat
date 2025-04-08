@echo off

set EXE_NAME=RUNNER-[도~~오~~ㄴ]
@REM set PUBLISH_NAME=%EXE_NAME%
set PUBLISH_NAME=%EXE_NAME%_d

@REM set USE_CONSOLE=false
set USE_CONSOLE=true

echo Cleaning up previous build files...

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
@REM del /q *.spec

echo Building new executable...

@REM python generate_version_info.py

pyinstaller build.spec
@REM echo.
echo ✅ 빌드 완료

echo.
echo.
xcopy scripts dist\scripts\ /E /I /Y
echo ✅✅ scripts 폴더 복사 완료

echo.
echo.
echo ********************
echo * Tasks completed! *
echo ********************
echo.
echo.

pause