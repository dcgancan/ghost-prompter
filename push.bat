@echo off
chcp 65001 > nul
title GhostPrompter - GitHub'a Push

echo ========================================================
echo   GhostPrompter GitHub Push (Muzaffer Ulusoy)
echo ========================================================
echo.

set "GIT_EXE=C:\Program Files\Git\cmd\git.exe"
if not exist "%GIT_EXE%" (
    where git >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set "GIT_EXE=git"
    ) else (
        echo [HATA] Git bulunamadi!
        pause
        exit /b 1
    )
)

echo [BILGI] Degisiklikler ekleniyor ve push ediliyor...
"%GIT_EXE%" add .
"%GIT_EXE%" commit -m "update: GhostPrompter latest updates by Muzaffer Ulusoy" 2>nul
"%GIT_EXE%" branch -M main
"%GIT_EXE%" push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================
    echo   [BASARILI] GhostPrompter GitHub'a basariyla yuklendi!
    echo   Repo: https://github.com/muqo16/ghost-prompter
    echo ========================================================
) else (
    echo.
    echo [BILGI] Eger repo henuz olusturulmadiysa, lutfen once
    echo https://github.com/new adresinden 'ghost-prompter' isimli
    echo public repoyu olusturun ve tekrar deneyin.
)

echo.
pause
