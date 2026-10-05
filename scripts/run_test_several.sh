#!/bin/bash
# Тест ОС: запуск эмулятора с VFS из нескольких файлов (vfs_samples/several_files.json)

set -e

SCRIPT_DIR="$(dirname "$0")"
cd "$SCRIPT_DIR/.."

echo "=========================================================="
echo "  [Тест VFS] Запуск с несколькими файлами (several_files.json)"
echo "=========================================================="

python3 main.py --cli --vfs vfs_samples/several_files.json --script scripts/test_several.sh

if [ -f "saved_several.json" ]; then
    echo ">>> Файл saved_several.json успешно создан!"
    rm -f saved_several.json
fi

echo ">>> Тест нескольких файлов VFS завершён успешно!"
