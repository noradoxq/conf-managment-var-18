@echo off
chcp 65001 > nul

python src\cmd_emu.py --vfs ".\vfs" --script ".\scripts\startup.txt"

pause
