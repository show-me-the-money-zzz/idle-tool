@echo off
setlocal enabledelayedexpansion

set DEV=./_devapp_
set DEST=./ZZZ/KKUSOGE

set PATH_CORE=core
set PATH_SCRIPTS=scripts
set PATH_UI=ui
set PATH_ZZZ=zzz
set PATH_DOT_VSCODE=.vscode

set FILE_BUILDER=build.bat
set FILE_BUILD_SPEC=build.spec
set FILE_MAIN=main.py
set FILE_REQUIREMENTS=requirements.txt
set FILE_RUN_ADMIN=run_as_admin.bat

echo 템플릿 생성을 시작합니다...
echo.

REM DEST 폴더가 없으면 생성
if not exist "%DEST%" (
    echo DEST 폴더가 없습니다. 생성합니다: %DEST%
    mkdir "%DEST%"
) else (
    echo DEST 폴더가 이미 존재합니다: %DEST%
)

echo.
echo 계속 진행 하려면 아무키나 누르세요..
pause

REM 심볼릭 링크 생성 전에 기존 항목 삭제
echo.
echo 기존 링크 및 파일 정리 중...

REM 기존 심볼릭 링크 삭제
if exist "%DEST%\%PATH_CORE%" (
    echo 기존 %PATH_CORE% 심볼릭 링크 삭제 중...
    rmdir "%DEST%\%PATH_CORE%"
)

if exist "%DEST%\%PATH_SCRIPTS%" (
    echo 기존 %PATH_SCRIPTS% 심볼릭 링크 삭제 중...
    rmdir "%DEST%\%PATH_SCRIPTS%"
)

if exist "%DEST%\%PATH_UI%" (
    echo 기존 %PATH_UI% 심볼릭 링크 삭제 중...
    rmdir "%DEST%\%PATH_UI%"
)

REM 기존 파일 삭제
if exist "%DEST%\%PATH_ZZZ%" (
    echo 기존 %PATH_ZZZ% 폴더 삭제 중...
    rmdir /s /q "%DEST%\%PATH_ZZZ%"
)

if exist "%DEST%\%PATH_DOT_VSCODE%" (
    echo 기존 %PATH_DOT_VSCODE% 폴더 삭제 중...
    rmdir /s /q "%DEST%\%PATH_DOT_VSCODE%"
)

if exist "%DEST%\%FILE_BUILDER%" (
    echo 기존 %FILE_BUILDER% 파일 삭제 중...
    del "%DEST%\%FILE_BUILDER%"
)

if exist "%DEST%\%FILE_BUILD_SPEC%" (
    echo 기존 %FILE_BUILD_SPEC% 파일 삭제 중...
    del "%DEST%\%FILE_BUILD_SPEC%"
)

if exist "%DEST%\%FILE_MAIN%" (
    echo 기존 %FILE_MAIN% 파일 삭제 중...
    del "%DEST%\%FILE_MAIN%"
)

if exist "%DEST%\%FILE_REQUIREMENTS%" (
    echo 기존 %FILE_REQUIREMENTS% 파일 삭제 중...
    del "%DEST%\%FILE_REQUIREMENTS%"
)

if exist "%DEST%\%FILE_RUN_ADMIN%" (
    echo 기존 %FILE_RUN_ADMIN% 파일 삭제 중...
    del "%DEST%\%FILE_RUN_ADMIN%"
)

echo.
echo 심볼릭 링크 생성 중...

REM 심볼릭 링크 생성
echo %PATH_CORE% 폴더의 심볼릭 링크 생성...
if exist "%DEV%\%PATH_CORE%" (
    mklink /d "%DEST%\%PATH_CORE%" "%CD%\%DEV%\%PATH_CORE%"
) else (
    echo 경고: 소스 폴더가 존재하지 않습니다 - %DEV%\%PATH_CORE%
)

echo %PATH_SCRIPTS% 폴더의 심볼릭 링크 생성...
if exist "%DEV%\%PATH_SCRIPTS%" (
    mklink /d "%DEST%\%PATH_SCRIPTS%" "%CD%\%DEV%\%PATH_SCRIPTS%"
) else (
    echo 경고: 소스 폴더가 존재하지 않습니다 - %DEV%\%PATH_SCRIPTS%
)

echo %PATH_UI% 폴더의 심볼릭 링크 생성...
if exist "%DEV%\%PATH_UI%" (
    mklink /d "%DEST%\%PATH_UI%" "%CD%\%DEV%\%PATH_UI%"
) else (
    echo 경고: 소스 폴더가 존재하지 않습니다 - %DEV%\%PATH_UI%
)

echo.
echo 파일 및 폴더 복사 중...

REM 폴더 복사
if exist "%DEV%\%PATH_ZZZ%" (
    echo %PATH_ZZZ% 폴더 복사...
    xcopy "%DEV%\%PATH_ZZZ%" "%DEST%\%PATH_ZZZ%\" /E /I /Y
) else (
    echo 경고: 소스 폴더가 존재하지 않습니다 - %DEV%\%PATH_ZZZ%
)

if exist "%DEV%\%PATH_DOT_VSCODE%" (
    echo %PATH_DOT_VSCODE% 폴더 복사...
    xcopy "%DEV%\%PATH_DOT_VSCODE%" "%DEST%\%PATH_DOT_VSCODE%\" /E /I /Y
) else (
    echo 경고: 소스 폴더가 존재하지 않습니다 - %DEV%\%PATH_DOT_VSCODE%
)

REM 파일 복사
if exist "%DEV%\%FILE_BUILDER%" (
    echo %FILE_BUILDER% 파일 복사...
    copy "%DEV%\%FILE_BUILDER%" "%DEST%\%FILE_BUILDER%" /Y
) else (
    echo 경고: 소스 파일이 존재하지 않습니다 - %DEV%\%FILE_BUILDER%
)

if exist "%DEV%\%FILE_BUILD_SPEC%" (
    echo %FILE_BUILD_SPEC% 파일 복사...
    copy "%DEV%\%FILE_BUILD_SPEC%" "%DEST%\%FILE_BUILD_SPEC%" /Y
) else (
    echo 경고: 소스 파일이 존재하지 않습니다 - %DEV%\%FILE_BUILD_SPEC%
)

if exist "%DEV%\%FILE_MAIN%" (
    echo %FILE_MAIN% 파일 복사...
    copy "%DEV%\%FILE_MAIN%" "%DEST%\%FILE_MAIN%" /Y
) else (
    echo 경고: 소스 파일이 존재하지 않습니다 - %DEV%\%FILE_MAIN%
)

if exist "%DEV%\%FILE_REQUIREMENTS%" (
    echo %FILE_REQUIREMENTS% 파일 복사...
    copy "%DEV%\%FILE_REQUIREMENTS%" "%DEST%\%FILE_REQUIREMENTS%" /Y
) else (
    echo 경고: 소스 파일이 존재하지 않습니다 - %DEV%\%FILE_REQUIREMENTS%
)

if exist "%DEV%\%FILE_RUN_ADMIN%" (
    echo %FILE_RUN_ADMIN% 파일 복사...
    copy "%DEV%\%FILE_RUN_ADMIN%" "%DEST%\%FILE_RUN_ADMIN%" /Y
) else (
    echo 경고: 소스 파일이 존재하지 않습니다 - %DEV%\%FILE_RUN_ADMIN%
)

echo.
echo 템플릿 생성 완료!
echo.
echo 생성된 템플릿 경로: %DEST%
echo.

pause