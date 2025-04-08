@echo off
set EXE_NAME=RUNNER-[도~~오~~ㄴ]
echo Cleaning up previous build files...

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
del /q *.spec

echo Building new executable...

@REM python generate_version_info.py

@REM @REM --onefile 단일파일 / --windowed 콘솔 삭제(--noconsole) / --uac-admin 관리자 권한
@REM pyinstaller --onefile main.py
@REM pyinstaller --clean --onefile --windowed --uac-admin --name %EXE_NAME% main.py
@REM pyinstaller --clean --onefile --windowed --uac-admin --icon=./zzz/icon.ico --name %EXE_NAME% main.py
@REM pyinstaller --clean --onefile --windowed --uac-admin --icon=./lordnine.ico --version-file=version_info.txt --name %EXE_NAME% main.py

@REM DEBUG-Console
@REM --add-data "scripts;scripts" ^
@REM 위의 --add-data는 빌드에 포함
@REM --add-binary "C:\\...\\Lib\\site-packages\\lupa\\lua51.cp312-win_amd64.pyd;lupa" ^
@REM --add-binary "C:\\경로\\lupa\\lua54.dll;lupa" ^
pyinstaller ^
    --clean ^
    --onefile ^
    --uac-admin ^
    --add-binary "C:\\Users\\ZV\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\lupa\\lua51.cp312-win_amd64.pyd;lupa" ^
    --add-binary "C:\\Users\\ZV\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\lupa\\lua52.cp312-win_amd64.pyd;lupa" ^
    --add-binary "C:\\Users\\ZV\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\lupa\\lua53.cp312-win_amd64.pyd;lupa" ^
    --add-binary "C:\\Users\\ZV\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\lupa\\lua54.cp312-win_amd64.pyd;lupa" ^
    --add-binary "C:\\Users\\ZV\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\lupa\\luajit20.cp312-win_amd64.pyd;lupa" ^
    --add-binary "C:\\Users\\ZV\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\lupa\\luajit21.cp312-win_amd64.pyd;lupa" ^
    --name %EXE_NAME%_d ^
    main.py

echo.
echo.
echo ********************
echo * Build completed! *
echo ********************
echo.
echo.

pause