@echo off
REM ============================================================
REM  本番向けサンプルAPI 起動スクリプト (Windows / waitress 経由)
REM
REM  初回のみ:  pip install -r requirements.txt
REM  起動    :  serve.bat
REM ============================================================

setlocal
cd /d "%~dp0"

if "%HOST%"=="" set HOST=0.0.0.0
if "%PORT%"=="" set PORT=8000

REM waitress があるか確認
python -c "import waitress" 1>nul 2>nul
if not %ERRORLEVEL%==0 (
    echo [情報] 依存ライブラリが未インストールです。インストールします...
    python -m pip install -r requirements.txt
    if not %ERRORLEVEL%==0 (
        echo [エラー] pip install に失敗しました。
        pause
        exit /b 1
    )
)

echo waitress で起動します: http://%HOST%:%PORT%
python -m waitress --host=%HOST% --port=%PORT% app:app

endlocal
