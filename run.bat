@echo off
setlocal

set "PY_EXE=C:\Users\%USERNAME%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\pythonw.exe"

if not exist "%PY_EXE%" (
    set "PY_EXE=C:\Users\%USERNAME%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
)

if not exist "%PY_EXE%" (
    if exist "%~dp0.venv\Scripts\pythonw.exe" set "PY_EXE=%~dp0.venv\Scripts\pythonw.exe"
)

if not exist "%PY_EXE%" (
    if exist "C:\Python312\pythonw.exe" set "PY_EXE=C:\Python312\pythonw.exe"
)

if not exist "%PY_EXE%" (
    if exist "C:\Python311\pythonw.exe" set "PY_EXE=C:\Python311\pythonw.exe"
)

if not exist "%PY_EXE%" (
    set "PY_EXE=pythonw.exe"
)

start "" "%PY_EXE%" "%~dp0main.py"
exit /b 0
