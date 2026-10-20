"""GUI-интерфейс эмулятора оболочки UNIX на Tkinter."""

import getpass
import os
import platform
import socket
import subprocess
import sys
import tkinter as tk

from src.emulator import ShellEmulator
from src.vfs import VFS

os.environ["TK_SILENCE_DEPRECATION"] = "1"

STATE_CONTROL_MASK = 0x4
STATE_COMMAND_MASK = 0x8
NAV_KEYS = (
    "Up", "Down", "Left", "Right",
    "Prior", "Next", "Home", "End",
)


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
        path = self.vfs_path
        if not os.path.exists(path):
            base_dir = os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))
            )
            alt = os.path.join(base_dir, path)
            if os.path.exists(alt):
                path = alt
        if path.endswith(".json"):
            self.vfs.load_from_json(path)
        else:
            self.vfs.load_from_directory(path)

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
        self.root.geometry("820x540")
        self.root.minsize(600, 400)
        self.root.configure(bg="#1e1e1e")

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_output_key(self, event):
        """Блокирует редактирование, сохраняя копирование и скроллинг."""
        is_copy = event.keysym.lower() in ("c", "insert")
        is_ctrl = bool(event.state & STATE_CONTROL_MASK)
        is_cmd = (
            sys.platform == "darwin"
            and bool(event.state & STATE_COMMAND_MASK)
        )
        if is_copy and (is_ctrl or is_cmd):
            return None
        if event.keysym in NAV_KEYS:
            return None
        return "break"

    def _on_output_click(self, _event):
        """Переводит фокус в строку ввода команд при клике на вывод."""
        self.root.after(10, self.input_entry.focus_set)

    def _setup_output_widget(self):
        """Создаёт текстовую область вывода терминала."""
        container = tk.Frame(self.root, bg="#1e1e1e")
        container.pack(fill=tk.BOTH, expand=True, padx=8, pady=(8, 0))

        self.scrollbar = tk.Scrollbar(container, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.output = tk.Text(
            container,
            bg="#1e1e1e",
            fg="#00ff66",
            insertbackground="#00ff66",
            selectbackground="#264f78",
            selectforeground="#ffffff",
            font=("Courier", 13),
            wrap=tk.WORD,
            bd=0,
            highlightthickness=0,
            relief=tk.FLAT,
            yscrollcommand=self.scrollbar.set,
        )
        self.output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.output.yview)

        self.output.bind("<Key>", self._on_output_key)
        self.output.bind("<Button-1>", self._on_output_click)

    def _setup_input_widgets(self):
        """Создаёт панель ввода команд с промптом."""
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
            bg="#252526",
            fg="#ffffff",
            insertbackground="#00ff66",
            font=("Courier", 13),
            relief=tk.FLAT,
            bd=3,
            highlightthickness=1,
            highlightbackground="#3c3c3c",
            highlightcolor="#007acc",
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.input_entry.bind("<Return>", self._on_enter)
        self.input_entry.bind("<Up>", self._on_history_up)
        self.input_entry.bind("<Down>", self._on_history_down)
        self.input_entry.focus_set()

    def _setup_widgets(self):
        """Создаёт виджеты интерфейса."""
        self._setup_output_widget()
        self._setup_input_widgets()

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
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)

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
            self.root.after(400, self.root.destroy)
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

    def _activate_window(self):
        """Активирует окно и форсирует отрисовку Cocoa на macOS."""
        try:
            self.root.update_idletasks()
            self.root.lift()
            self.input_entry.focus_set()
        except Exception:
            pass

        if sys.platform == "darwin":
            try:
                pid = os.getpid()
                script = (
                    f'tell application "System Events" to '
                    f'set frontmost of first process whose unix id is '
                    f'{pid} to true'
                )
                subprocess.Popen(
                    ["osascript", "-e", script],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except Exception:
                pass

    def run(self):
        """Запускает главный цикл GUI."""
        self._activate_window()
        self.root.mainloop()
