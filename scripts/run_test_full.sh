#!/bin/bash
# Тест ОС: запуск эмулятора с полной VFS (не менее 3 уровней вложенности)

set -e

SCRIPT_DIR="$(dirname "$0")"
cd "$SCRIPT_DIR/.."

echo "=========================================================="
echo "  [Тест VFS] Запуск с полной VFS (full.json, 3+ уровня)"
echo "=========================================================="

python3 main.py --cli --vfs vfs_samples/full.json --script scripts/test_vfs.sh

if [ -f "saved_full.json" ]; then
    echo ">>> Файл saved_full.json успешно создан!"
    rm -f saved_full.json
fi

echo ">>> Тест полной VFS завершён успешно!"
