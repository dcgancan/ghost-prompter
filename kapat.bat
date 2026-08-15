@echo off
chcp 65001 > nul
title Prompter Kapatiliyor...

echo Prompter kapatiliyor...
taskkill /F /IM python.exe /IM pythonw.exe >nul 2>&1
echo Prompter basariyla kapatildi.
timeout /t 1 >nul
exit /b 0
