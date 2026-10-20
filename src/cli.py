"""Консольный REPL-интерфейс эмулятора оболочки."""

import getpass
import os
import socket
import sys

from src.emulator import ShellEmulator
from src.vfs import VFS


class ShellCLI:
    """Консольный интерфейс эмулятора оболочки UNIX."""

    def __init__(self, vfs_path=None, script_path=None):
        self.vfs = VFS()
        self.vfs_path = vfs_path
        self.script_path = script_path
        self._load_vfs()
        self.emulator = ShellEmulator(self.vfs)

    def _load_vfs(self):
        """Загружает VFS из JSON или директории."""
        if self.vfs_path is None:
            return
        path = self.vfs_path
        if not os.path.exists(path):
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            alt = os.path.join(base_dir, path)
            if os.path.exists(alt):
                path = alt
        if path.endswith(".json"):
            self.vfs.load_from_json(path)
        else:
            self.vfs.load_from_directory(path)

    def _get_title(self):
        """Формирует заголовок оболочки."""
        try:
            username = getpass.getuser()
        except Exception:
            username = "user"
        try:
            hostname = socket.gethostname()
        except Exception:
            hostname = "localhost"
        return f"Эмулятор - [{username}@{hostname}]"

    def run(self):
        """Запускает консольный интерактивный цикл REPL."""
        print(f"=== {self._get_title()} ===")
        motd = self.vfs.get_motd()
        if motd:
            print(motd)

        if self.script_path:
            try:
                self.emulator.run_script(
                    self.script_path,
                    output_callback=print
                )
            except FileNotFoundError:
                print(f"Скрипт не найден: {self.script_path}", file=sys.stderr)

        while self.emulator.running:
            try:
                line = input(self.emulator.get_prompt())
            except (EOFError, KeyboardInterrupt):
                print("\nВыход из эмулятора.")
                break

            result = self.emulator.execute(line)
            if result:
                print(result)
