#!/bin/bash
# Тест ОС: запуск эмулятора с минимальной VFS (vfs_samples/minimal.json)

set -e

SCRIPT_DIR="$(dirname "$0")"
cd "$SCRIPT_DIR/.."

echo "=========================================================="
echo "  [Тест VFS] Запуск с минимальной VFS (minimal.json)"
echo "=========================================================="

python3 main.py --cli --vfs vfs_samples/minimal.json --script scripts/test_minimal.sh

# Проверяем, что vfs-save создал файл
if [ -f "saved_minimal.json" ]; then
    echo ">>> Файл saved_minimal.json успешно создан!"
    rm -f saved_minimal.json
fi

echo ">>> Тест минимальной VFS завершён успешно!"
