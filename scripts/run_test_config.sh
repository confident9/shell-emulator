#!/bin/bash
# Тест 4: Проверка параметров командной строки
echo "=== Тест: без параметров ==="
python3 main.py
echo ""

echo "=== Тест: только VFS ==="
python3 main.py --vfs vfs_samples/minimal.json
echo ""

echo "=== Тест: VFS + скрипт ==="
python3 main.py --vfs vfs_samples/full.json \
    --script scripts/test_commands.sh
echo ""
echo "=== Все тесты завершены ==="
