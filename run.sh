#!/bin/bash
# Скрипт запуска эмулятора командной оболочки UNIX (Вариант №30)
set -e

SCRIPT_DIR="$(dirname "$0")"
cd "$SCRIPT_DIR"

# Определение команды python3 с поддержкой Tkinter
PYTHON=""
for candidate in /opt/homebrew/bin/python3.14 python3.14 /opt/homebrew/bin/python3 /usr/local/bin/python3.14 /usr/local/bin/python3 python3 python; do
    if command -v "$candidate" &> /dev/null; then
        if "$candidate" -c "import tkinter as tk, sys; sys.exit(0 if tk.TkVersion >= 8.6 else 1)" &> /dev/null; then
            PYTHON="$candidate"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    for candidate in python3.14 python3 /usr/bin/python3 python; do
        if command -v "$candidate" &> /dev/null; then
            PYTHON="$candidate"
            break
        fi
    done
fi

usage() {
    echo "=========================================================="
    echo "  Эмулятор оболочки UNIX (Вариант №30)"
    echo "=========================================================="
    echo "Использование:"
    echo "  ./run.sh                    - запуск десктопного GUI (Tkinter)"
    echo "  ./run.sh --web              - запуск графического GUI в браузере"
    echo "  ./run.sh --cli              - запуск в терминале (консольный REPL)"
    echo "  ./run.sh --vfs <path>       - запуск с виртуальной файловой системой"
    echo "  ./run.sh --vfs <path> --script <path>"
    echo "  ./run.sh test               - запуск всех unit-тестов"
    echo "  ./run.sh all                - запуск всех тестовых сценариев ОС"
    echo "=========================================================="
}

if [ "$1" = "test" ]; then
    echo "=== Запуск unit-тестов ==="
    $PYTHON -m unittest discover -s tests -v
    exit $?
fi

if [ "$1" = "all" ]; then
    echo "=== Запуск всех проверочных скриптов ОС ==="
    for s in scripts/run_*.sh; do
        if [ -f "$s" ]; then
            echo ""
            echo ">>> Запуск сценария: $s"
            bash "$s"
        fi
    done
    echo ""
    echo "=== Все проверочные сценарии выполнены ==="
    exit 0
fi

if [ "$1" = "help" ] || [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    usage
    exit 0
fi

if [ $# -eq 0 ]; then
    $PYTHON main.py --vfs vfs_samples/full.json
else
    $PYTHON main.py "$@"
fi
