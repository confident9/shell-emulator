"""Точка входа эмулятора оболочки UNIX.

Запуск:
    python main.py --vfs path/to/vfs.json [--script path/to/script.sh]
"""

import argparse
import sys

from src.gui import ShellGUI


def parse_args():
    """Разбирает аргументы командной строки.

    Returns:
        Объект с разобранными аргументами.
    """
    parser = argparse.ArgumentParser(
        description="Эмулятор оболочки ОС (GUI)"
    )
    parser.add_argument(
        "--vfs",
        required=False,
        help="Путь к JSON-файлу VFS или директории",
    )
    parser.add_argument(
        "--script",
        required=False,
        help="Путь к стартовому скрипту",
    )
    return parser.parse_args()


def main():
    """Главная функция запуска эмулятора."""
    args = parse_args()
    print("=== Параметры запуска ===")
    print(f"  VFS: {args.vfs or 'не указан'}")
    print(f"  Скрипт: {args.script or 'не указан'}")
    print("========================")
    try:
        gui = ShellGUI(
            vfs_path=args.vfs,
            script_path=args.script,
        )
        gui.run()
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
