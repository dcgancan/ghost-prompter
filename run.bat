@echo off
chcp 65001 > nul
title GhostPrompter Baslatiliyor...

set "PYTHON_EXE="

:: 1. Sistemdeki Codex / AppData Python konumu (Sessiz calistirici pythonw.exe oncelikli)
if exist "C:\Users\%USERNAME%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\pythonw.exe" (
    set "PYTHON_EXE=C:\Users\%USERNAME%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\pythonw.exe"
    goto :RUN_SILENT
)
if exist "C:\Users\%USERNAME%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" (
    set "PYTHON_EXE=C:\Users\%USERNAME%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
    goto :RUN_SILENT
)

:: 2. Proje ici Sanal Ortam (.venv)
if exist "%~dp0.venv\Scripts\pythonw.exe" (
    set "PYTHON_EXE=%~dp0.venv\Scripts\pythonw.exe"
    goto :RUN_SILENT
)
if exist "%~dp0.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
    goto :RUN_SILENT
)

:: 3. AppData Local Programs Python
for /d %%i in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
    if exist "%%i\pythonw.exe" (
        set "PYTHON_EXE=%%i\pythonw.exe"
        goto :RUN_SILENT
    )
    if exist "%%i\python.exe" (
        set "PYTHON_EXE=%%i\python.exe"
        goto :RUN_SILENT
    )
)

:: 4. Standart C:\ Python dizinleri
if exist "C:\Python312\pythonw.exe" (
    set "PYTHON_EXE=C:\Python312\pythonw.exe"
    goto :RUN_SILENT
)
if exist "C:\Python311\pythonw.exe" (
    set "PYTHON_EXE=C:\Python311\pythonw.exe"
    goto :RUN_SILENT
)

:: 5. Sistem PATH uzerindeki python
for /f "delims=" %%p in ('where python 2^>nul') do (
    echo %%p | findstr /i /v "WindowsApps" >nul
    if not errorlevel 1 (
        if exist "%%p" (
            set "PYTHON_EXE=%%p"
            goto :RUN_SILENT
        )
    )
)

echo [HATA] Python kurulumu bulunamadi!
pause
exit /b 1

:RUN_SILENT
:: Prompter'ı arka planda bağımsız başlat ve siyah konsol penceresini anında kapat!
start "" "%PYTHON_EXE%" "%~dp0main.py"
exit
