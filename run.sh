#!/bin/bash
# Скрипт запуска эмулятора командной оболочки UNIX (Вариант №30)
set -e

SCRIPT_DIR="$(dirname "$0")"
cd "$SCRIPT_DIR"

# Определение команды python3
PYTHON="python3"
if ! command -v python3 &> /dev/null; then
    if command -v python &> /dev/null; then
        PYTHON="python"
    else
        echo "Ошибка: Python 3 не установлен в вашей системе."
        exit 1
    fi
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

$PYTHON main.py "$@"
