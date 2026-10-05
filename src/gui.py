"""GUI-интерфейс эмулятора оболочки UNIX."""

import getpass
import platform
import socket
import tkinter as tk
from tkinter import scrolledtext

from src.emulator import ShellEmulator
from src.vfs import VFS


class ShellGUI:
    """Графический интерфейс эмулятора оболочки."""

    def __init__(self, vfs_path=None, script_path=None):
        """Инициализация GUI.

        Args:
            vfs_path: Путь к JSON-файлу VFS.
            script_path: Путь к стартовому скрипту.
        """
        self.vfs = VFS()
        self.vfs_path = vfs_path
        self.script_path = script_path
        self._load_vfs()
        self.emulator = ShellEmulator(self.vfs)
        self._setup_window()
        self._setup_widgets()
        self._show_motd()
        self._run_startup_script()
        self._show_prompt()

    def _load_vfs(self):
        """Загружает VFS из указанного источника."""
        if self.vfs_path is None:
            return
        if self.vfs_path.endswith(".json"):
            self.vfs.load_from_json(self.vfs_path)
        else:
            self.vfs.load_from_directory(self.vfs_path)

    def _get_title(self):
        """Формирует заголовок окна.

        Returns:
            Строка заголовка с username@hostname.
        """
        try:
            username = getpass.getuser()
        except Exception:
            username = "user"
        try:
            hostname = socket.gethostname()
        except Exception:
            hostname = "localhost"
        return f"Эмулятор - [{username}@{hostname}]"

    def _setup_window(self):
        """Настраивает главное окно приложения."""
        self.root = tk.Tk()
        self.root.title(self._get_title())
        self.root.geometry("800x500")
        self.root.configure(bg="#1e1e1e")

    def _setup_widgets(self):
        """Создаёт виджеты интерфейса."""
        self.output = scrolledtext.ScrolledText(
            self.root,
            bg="#1e1e1e",
            fg="#00ff00",
            insertbackground="#00ff00",
            font=("Courier", 13),
            wrap=tk.WORD,
            state=tk.DISABLED,
        )
        self.output.pack(
            fill=tk.BOTH, expand=True,
            padx=5, pady=(5, 0)
        )
        input_frame = tk.Frame(
            self.root, bg="#1e1e1e"
        )
        input_frame.pack(
            fill=tk.X, padx=5, pady=5
        )
        self.prompt_label = tk.Label(
            input_frame,
            text="",
            bg="#1e1e1e",
            fg="#00ff00",
            font=("Courier", 13),
        )
        self.prompt_label.pack(side=tk.LEFT)
        self.input_entry = tk.Entry(
            input_frame,
            bg="#2d2d2d",
            fg="#00ff00",
            insertbackground="#00ff00",
            font=("Courier", 13),
            relief=tk.FLAT,
        )
        self.input_entry.pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )
        self.input_entry.bind(
            "<Return>", self._on_enter
        )
        self.input_entry.focus()

    def _show_motd(self):
        """Отображает сообщение motd при старте."""
        motd = self.vfs.get_motd()
        if motd:
            self._append_output(motd)

    def _run_startup_script(self):
        """Выполняет стартовый скрипт, если указан."""
        if self.script_path is None:
            return
        try:
            self.emulator.run_script(
                self.script_path,
                output_callback=self._append_output
            )
        except FileNotFoundError:
            self._append_output(
                f"Скрипт не найден: {self.script_path}"
            )

    def _show_prompt(self):
        """Обновляет отображение приглашения."""
        self.prompt_label.config(
            text=self.emulator.get_prompt()
        )

    def _append_output(self, text):
        """Добавляет текст в область вывода.

        Args:
            text: Текст для добавления.
        """
        self.output.config(state=tk.NORMAL)
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)
        self.output.config(state=tk.DISABLED)

    def _on_enter(self, event):
        """Обработчик нажатия Enter.

        Args:
            event: Событие клавиатуры.
        """
        line = self.input_entry.get()
        self.input_entry.delete(0, tk.END)
        prompt = self.emulator.get_prompt()
        self._append_output(f"{prompt}{line}")
        result = self.emulator.execute(line)
        if result:
            self._append_output(result)
        if not self.emulator.running:
            self.root.after(500, self.root.destroy)
            return
        self._show_prompt()

    def run(self):
        """Запускает главный цикл GUI."""
        self.root.mainloop()
