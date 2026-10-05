#!/bin/bash
# Тест ОС: тестирование основных команд (ls, cd, date, cal)

set -e

SCRIPT_DIR="$(dirname "$0")"
cd "$SCRIPT_DIR/.."

echo "=========================================================="
echo "  [Тест Команд] Основные команды: ls, cd, date, cal"
echo "=========================================================="

python3 main.py --cli --vfs vfs_samples/full.json --script scripts/test_commands.sh

echo ">>> Тестирование основных команд завершено успешно!"
