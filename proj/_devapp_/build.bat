@echo off

@REM grinder | miner
set EXE_NAME=DiaMiner-[ZZXX]
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


@REM 아이콘 복사용 디렉토리 생성 및 복사
@REM 해당 앱의 윈도우 아이콘은 실시간으로 불러오기 때문에 동봉시켜야 함
if not exist dist\zzz (
    mkdir dist\zzz
)
copy /Y zzz\icon.ico dist\zzz\
echo ✅✅✅ 아이콘 복사 완료

echo.
echo.
echo.
echo ********************
echo * Tasks completed! *
echo ********************
echo.
echo.

pause