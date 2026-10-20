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
import subprocess
import sys

os.environ["TK_SILENCE_DEPRECATION"] = "1"

MIN_TK_VERSION = 8.6
TK_CHECK_CODE = (
    "import tkinter as tk, sys; sys.exit(0 if tk.TkVersion >= 8.6 else 1)"
)


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


def _is_tkinter_outdated():
    """Проверяет, устарел ли Tkinter (на macOS Tk 8.5 не отрисовывает окна)."""
    try:
        import tkinter as tk
        if sys.platform == "darwin":
            return getattr(tk, "TkVersion", 0) < MIN_TK_VERSION
        return False
    except ImportError:
        return True


def _find_modern_python():
    """Находит в системе Python с поддержкой современной версии Tkinter."""
    candidates = [
        "/opt/homebrew/bin/python3.14",
        "/opt/homebrew/bin/python3",
        "python3.14",
        "/usr/local/bin/python3.14",
        "/usr/local/bin/python3",
        "/usr/bin/python3",
    ]
    for cand in candidates:
        if cand == sys.executable:
            continue
        try:
            check = subprocess.run(
                [cand, "-c", TK_CHECK_CODE],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if check.returncode == 0:
                return cand
        except Exception:
            continue
    return None


def _ensure_gui_python():
    """Перезапускает процесс под Python с поддержкой Tkinter при нужде."""
    if os.environ.get("_SHELL_EMU_REEXEC"):
        return
    if not _is_tkinter_outdated():
        return
    cand = _find_modern_python()
    if cand:
        print(f"[Инфо] Переключение на {cand} для отрисовки GUI...\n")
        env = os.environ.copy()
        env["_SHELL_EMU_REEXEC"] = "1"
        os.execve(cand, [cand] + sys.argv, env)


def _run_gui_with_fallback(args):
    """Запускает GUI Tkinter с резервным переключением на Web GUI и CLI."""
    _ensure_gui_python()
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
