"""GUI-интерфейс эмулятора оболочки UNIX на Tkinter."""

import os
os.environ["TK_SILENCE_DEPRECATION"] = "1"

import getpass
import platform
import socket
import sys
import tkinter as tk
from tkinter import scrolledtext

from src.emulator import ShellEmulator
from src.vfs import VFS


class ShellGUI:
    """Графический интерфейс эмулятора оболочки на Tkinter."""

    def __init__(self, vfs_path=None, script_path=None):
        self.vfs = VFS()
        self.vfs_path = vfs_path
        self.script_path = script_path
        self._load_vfs()
        self.emulator = ShellEmulator(self.vfs)
        self.history = []
        self.history_index = 0
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
        """Формирует заголовок окна."""
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
        self.root.geometry("820x520")
        self.root.minsize(600, 400)
        self.root.configure(bg="#1e1e1e")

        # Принудительный вывод окна на передний план в macOS
        try:
            self.root.lift()
            self.root.attributes("-topmost", True)
            self.root.after_idle(self.root.attributes, "-topmost", False)
            self.root.focus_force()
        except Exception:
            pass

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

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
            padx=8, pady=(8, 0)
        )
        self.output.bind("<Button-1>", lambda e: self.input_entry.focus_set())

        input_frame = tk.Frame(self.root, bg="#1e1e1e")
        input_frame.pack(fill=tk.X, padx=8, pady=8)

        self.prompt_label = tk.Label(
            input_frame,
            text="",
            bg="#1e1e1e",
            fg="#4ec9b0",
            font=("Courier", 13, "bold"),
        )
        self.prompt_label.pack(side=tk.LEFT)

        self.input_entry = tk.Entry(
            input_frame,
            bg="#2d2d2d",
            fg="#ffffff",
            insertbackground="#00ff00",
            font=("Courier", 13),
            relief=tk.FLAT,
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.input_entry.bind("<Return>", self._on_enter)
        self.input_entry.bind("<Up>", self._on_history_up)
        self.input_entry.bind("<Down>", self._on_history_down)
        self.input_entry.focus_set()

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
            self._append_output(f"Скрипт не найден: {self.script_path}")

    def _show_prompt(self):
        """Обновляет отображение приглашения."""
        self.prompt_label.config(text=self.emulator.get_prompt())

    def _append_output(self, text):
        """Добавляет текст в область вывода."""
        self.output.config(state=tk.NORMAL)
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)
        self.output.config(state=tk.DISABLED)

    def _on_enter(self, event):
        """Обработчик нажатия Enter."""
        line = self.input_entry.get()
        self.input_entry.delete(0, tk.END)
        if line.strip():
            self.history.append(line)
            self.history_index = len(self.history)

        prompt = self.emulator.get_prompt()
        self._append_output(f"{prompt}{line}")
        result = self.emulator.execute(line)
        if result:
            self._append_output(result)

        if not self.emulator.running:
            self._append_output("[Выход из эмулятора]")
            self.root.after(600, self.root.destroy)
            return

        self._show_prompt()

    def _on_history_up(self, event):
        """Навигация по истории команд вверх."""
        if self.history and self.history_index > 0:
            self.history_index -= 1
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, self.history[self.history_index])
        return "break"

    def _on_history_down(self, event):
        """Навигация по истории команд вниз."""
        if self.history and self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, self.history[self.history_index])
        else:
            self.history_index = len(self.history)
            self.input_entry.delete(0, tk.END)
        return "break"

    def _on_close(self):
        """Обработчик закрытия окна."""
        self.emulator.running = False
        self.root.destroy()

    def run(self):
        """Запускает главный цикл GUI."""
        self.root.mainloop()
