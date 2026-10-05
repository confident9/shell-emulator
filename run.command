#!/bin/bash
# Двойной клик на Mac открывает эмулятор в терминале / окне
cd "$(dirname "$0")"
python3 main.py "$@"
