@echo off
chcp 65001 > nul
title Prompter Baslatiliyor...

echo ========================================================
echo   Windows Ses Takipli ^& Ekran Kaydinda Gizli Prompter
echo ========================================================
echo.

set "PYTHON_EXE="

:: 1. Sistemdeki Codex / AppData Python konumu
if exist "C:\Users\%USERNAME%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" (
    set "PYTHON_EXE=C:\Users\%USERNAME%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
    goto :RUN
)

:: 2. Proje ici Sanal Ortam (.venv)
if exist "%~dp0.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
    goto :RUN
)

:: 3. AppData Local Programs Python
for /d %%i in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
    if exist "%%i\python.exe" (
        set "PYTHON_EXE=%%i\python.exe"
        goto :RUN
    )
)

:: 4. Standart C:\ Python dizinleri
if exist "C:\Python312\python.exe" (
    set "PYTHON_EXE=C:\Python312\python.exe"
    goto :RUN
)
if exist "C:\Python311\python.exe" (
    set "PYTHON_EXE=C:\Python311\python.exe"
    goto :RUN
)
if exist "C:\Python310\python.exe" (
    set "PYTHON_EXE=C:\Python310\python.exe"
    goto :RUN
)
if exist "C:\Program Files\Python312\python.exe" (
    set "PYTHON_EXE=C:\Program Files\Python312\python.exe"
    goto :RUN
)
if exist "C:\Program Files\Python311\python.exe" (
    set "PYTHON_EXE=C:\Program Files\Python311\python.exe"
    goto :RUN
)

:: 5. Sistem PATH uzerindeki gercek python (WindowsApps harici)
for /f "delims=" %%p in ('where python 2^>nul') do (
    echo %%p | findstr /i /v "WindowsApps" >nul
    if not errorlevel 1 (
        if exist "%%p" (
            set "PYTHON_EXE=%%p"
            goto :RUN
        )
    )
)

echo [HATA] Gecerli bir Python kurulumu bulunamadi!
echo Lutfen Python'in kurulu oldugundan emin olun.
pause
exit /b 1

:RUN
echo [BILGI] Python bulundu: "%PYTHON_EXE%"
echo [BILGI] Prompter baslatiliyor...
echo.

"%PYTHON_EXE%" "%~dp0main.py"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [HATA] Prompter calisirken bir sorun olustu.
    pause
)
