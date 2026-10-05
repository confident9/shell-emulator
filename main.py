#!/usr/bin/env python3
"""Точка входа эмулятора командной оболочки UNIX (Вариант №30).

Режимы запуска:
    python3 main.py                             # Графический интерфейс (GUI)
    python3 main.py --web                       # Web-GUI в браузере
    python3 main.py --cli                       # Консольный терминал
    python3 main.py --vfs vfs_samples/full.json # С виртуальной файловой системой
    python3 main.py --vfs ... --script ...      # С VFS и стартовым скриптом
"""

import os
os.environ["TK_SILENCE_DEPRECATION"] = "1"

import argparse
import sys


def parse_args():
    """Разбирает аргументы командной строки."""
    parser = argparse.ArgumentParser(
        description="Эмулятор командной оболочки ОС UNIX (Вариант №30)"
    )
    parser.add_argument(
        "--vfs", "-v",
        required=False,
        help="Путь к физическому расположению JSON-файла VFS",
    )
    parser.add_argument(
        "--script", "-s",
        required=False,
        help="Путь к стартовому скрипту эмулятора",
    )
    parser.add_argument(
        "--mode", "-m",
        choices=["gui", "web", "cli"],
        default="gui",
        help="Режим интерфейса: gui (десктоп Tkinter), web (в браузере), cli (терминал)",
    )
    parser.add_argument(
        "--web",
        action="store_true",
        help="Запустить GUI в браузере (быстрый ключ для --mode web)",
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Запустить в терминале (быстрый ключ для --mode cli)",
    )
    return parser.parse_args()


def main():
    """Главная функция запуска эмулятора."""
    args = parse_args()

    # Определение режима работы
    mode = args.mode
    if args.web:
        mode = "web"
    elif args.cli:
        mode = "cli"

    # Отладочный вывод параметров запуска (Требование Этапа 2)
    print("=== Отладочный вывод параметров запуска ===")
    print(f"  VFS (физический путь): {args.vfs or 'не указан'}")
    print(f"  Стартовый скрипт:     {args.script or 'не указан'}")
    print(f"  Режим интерфейса:     {mode}")
    print("===========================================")

    if mode == "cli":
        from src.cli import ShellCLI
        cli = ShellCLI(vfs_path=args.vfs, script_path=args.script)
        cli.run()
        return

    if mode == "web":
        from src.web_gui import ShellWebGUI
        web_gui = ShellWebGUI(vfs_path=args.vfs, script_path=args.script)
        web_gui.run()
        return

    # По умолчанию: режим GUI (десктопный Tkinter)
    try:
        from src.gui import ShellGUI
        gui = ShellGUI(vfs_path=args.vfs, script_path=args.script)
        gui.run()
    except Exception as e:
        print(f"\n[Предупреждение] Не удалось запустить десктопный Tkinter GUI: {e}")
        print("[Инфо] Автоматически запускаем графический Web GUI в вашем браузере...\n")
        try:
            from src.web_gui import ShellWebGUI
            web_gui = ShellWebGUI(vfs_path=args.vfs, script_path=args.script)
            web_gui.run()
        except Exception as web_err:
            print(f"[Ошибка] Не удалось запустить Web GUI: {web_err}", file=sys.stderr)
            print("[Инфо] Переключение в консольный режим CLI...\n")
            from src.cli import ShellCLI
            cli = ShellCLI(vfs_path=args.vfs, script_path=args.script)
            cli.run()


if __name__ == "__main__":
    main()
