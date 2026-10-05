#!/bin/bash
# Тест 1: Запуск с минимальной VFS
echo "=== Тест: минимальная VFS ==="
python3 main.py --vfs vfs_samples/minimal.json \
    --script scripts/test_vfs.sh
echo ""
echo "=== Тест завершён ==="
