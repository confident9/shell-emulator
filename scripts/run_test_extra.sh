#!/bin/bash
# Тест ОС: дополнительные команды (chmod, touch)

set -e

SCRIPT_DIR="$(dirname "$0")"
cd "$SCRIPT_DIR/.."

echo "=========================================================="
echo "  [Тест Команд] Дополнительные команды: chmod, touch"
echo "=========================================================="

python3 main.py --cli --vfs vfs_samples/full.json --script scripts/test_extra.sh

echo ">>> Тестирование дополнительных команд завершено успешно!"
