#!/bin/bash
# Тест 3: Запуск с дополнительными командами
echo "=== Тест: дополнительные команды ==="
python3 main.py --vfs vfs_samples/full.json \
    --script scripts/test_extra.sh
echo ""
echo "=== Тест завершён ==="
