
@echo off
setlocal
chcp 65001 > nul

cd /d "%~dp0.."

echo === Testing minimal VFS ===
python src\cmd_emu.py --vfs "C:\Users\sasha\Documents\vfs-data\data" --script "scripts\startup.txt"
if errorlevel 1 exit /b 1

echo.
echo === Testing VFS with several files ===
python src\cmd_emu.py --vfs "C:\Users\sasha\Documents\vfs-data\notes" --script "scripts\startup.txt"
if errorlevel 1 exit /b 1

echo.
echo === Testing nested VFS ===
python src\cmd_emu.py --vfs "C:\Users\sasha\Documents\vfs-data\nested" --script "scripts\startup.txt"
if errorlevel 1 exit /b 1

pause
endlocal