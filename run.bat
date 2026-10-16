@echo off
chcp 65001 > nul
cd /d "%~dp0"

python src\cmd_emu.py --vfs "C:\Users\sasha\Documents\vfs-data" --script scripts.txt

pause