@echo off
echo 관리자 권한으로 파이썬 스크립트 실행 중...

REM 배치 파일이 있는 경로를 기준으로 상대 경로 계산
set PROJECT_ROOT=%~dp0
cd /d "%PROJECT_ROOT%"

REM 파이썬 파일 경로 지정 (상대 경로로)
set PYTHON_SCRIPT=main.py
REM 또는 프로젝트 구조에 따라 적절히 조정 
REM set PYTHON_SCRIPT=proj\python\main.py

powershell -Command "Start-Process python -ArgumentList '%PYTHON_SCRIPT%' -Verb RunAs -Wait"
@REM pause