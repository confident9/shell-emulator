#!/bin/bash
# Тест 2: Запуск с полной VFS
echo "=== Тест: полная VFS ==="
python3 main.py --vfs vfs_samples/full.json \
    --script scripts/test_commands.sh
echo ""
echo "=== Тест завершён ==="
