#!/bin/bash
# Скрипт запуска эмулятора оболочки

set -e

SCRIPT_DIR="$(dirname "$0")"

usage() {
    echo "Использование:"
    echo "  ./run.sh                    - запуск без VFS"
    echo "  ./run.sh --vfs <path>       - запуск с VFS"
    echo "  ./run.sh --vfs <path> --script <path>"
    echo "  ./run.sh test               - запуск тестов"
}

if [ "$1" = "test" ]; then
    echo "Запуск тестов..."
    python3 -m unittest discover -s tests -v
    exit $?
fi

if [ "$1" = "help" ] || [ "$1" = "--help" ]; then
    usage
    exit 0
fi

python3 "$SCRIPT_DIR/main.py" "$@"
