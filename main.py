"""Точка входа эмулятора командной оболочки UNIX (Вариант №30).

Режимы запуска:
    python3 main.py                             (Графический интерфейс GUI)
    python3 main.py --web                       (Web-GUI в браузере)
    python3 main.py --cli                       (Консольный терминал)
    python3 main.py --vfs vfs_samples/full.json (С виртуальной ФС)
    python3 main.py --vfs ... --script ...      (С VFS и стартовым скриптом)
"""

import argparse
import os
import sys

os.environ["TK_SILENCE_DEPRECATION"] = "1"


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
        help="Режим: gui (десктоп Tkinter), web (в браузере), cli",
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


def _determine_mode(args):
    """Определяет режим работы эмулятора по аргументам CLI."""
    if args.web:
        return "web"
    if args.cli:
        return "cli"
    return args.mode


def _print_launch_params(args, mode):
    """Выводит отладочные параметры запуска эмулятора."""
    print("=== Отладочный вывод параметров запуска ===")
    print(f"  VFS (физический путь): {args.vfs or 'не указан'}")
    print(f"  Стартовый скрипт:     {args.script or 'не указан'}")
    print(f"  Режим интерфейса:     {mode}")
    print("===========================================")


def _run_gui_with_fallback(args):
    """Запускает GUI Tkinter с резервным переключением на Web GUI и CLI."""
    try:
        from src.gui import ShellGUI
        gui = ShellGUI(vfs_path=args.vfs, script_path=args.script)
        gui.run()
    except Exception as err:
        print(
            f"\n[Предупреждение] Ошибка десктопного Tkinter GUI: {err}"
        )
        print("[Инфо] Запуск графического Web GUI в браузере...\n")
        try:
            from src.web_gui import ShellWebGUI
            web_gui = ShellWebGUI(
                vfs_path=args.vfs, script_path=args.script
            )
            web_gui.run()
        except Exception as web_err:
            print(
                f"[Ошибка] Не удалось запустить Web GUI: {web_err}",
                file=sys.stderr,
            )
            print("[Инфо] Переключение в консольный режим CLI...\n")
            from src.cli import ShellCLI
            cli = ShellCLI(vfs_path=args.vfs, script_path=args.script)
            cli.run()


def main():
    """Главная функция запуска эмулятора."""
    args = parse_args()
    mode = _determine_mode(args)
    _print_launch_params(args, mode)

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

    _run_gui_with_fallback(args)


if __name__ == "__main__":
    main()
