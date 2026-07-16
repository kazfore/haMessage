@echo off
REM ============================================================
REM  テスト用 汎用サンプルAPI 起動スクリプト (Windows コマンドプロンプト用)
REM
REM  使い方:
REM    1) このファイルをダブルクリック、または
REM    2) コマンドプロンプトで  run.bat
REM
REM  ポートを変えたい場合は起動前に:
REM    set PORT=9000
REM    run.bat
REM ============================================================

setlocal

REM バッチファイルのあるフォルダへ移動
cd /d "%~dp0"

REM ポート未設定なら 8000 を既定にする
if "%PORT%"=="" set PORT=8000

REM python があるか確認 (py ランチャー優先、なければ python)
where py >nul 2>nul
if %ERRORLEVEL%==0 (
    set "PY=py"
) else (
    where python >nul 2>nul
    if %ERRORLEVEL%==0 (
        set "PY=python"
    ) else (
        echo [エラー] Python が見つかりません。
        echo         https://www.python.org/ からインストールし、
        echo         インストール時に "Add python.exe to PATH" にチェックしてください。
        pause
        exit /b 1
    )
)

echo Python を使用します: %PY%
echo ポート: %PORT%
echo.

%PY% server.py --port %PORT%

endlocal
