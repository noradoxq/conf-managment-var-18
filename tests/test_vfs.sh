#!/usr/bin/env bash
set -eu

cd "$(dirname "$0")/.."

echo "=== Testing minimal VFS ==="
python3 src/cmd_emu.py \
  --vfs "C:\Users\sasha\Documents\vfs-data\data" \
  --script "scripts/startup.txt"

echo
echo "=== Testing VFS with several files ==="
python3 src/cmd_emu.py \
  --vfs "C:\Users\sasha\Documents\vfs-data\notes" \
  --script "scripts/startup.txt"

echo
echo "=== Testing nested VFS ==="
python3 src/cmd_emu.py \
  --vfs "C:\Users\sasha\Documents\vfs-data\nested" \
  --script "scripts/startup.txt"