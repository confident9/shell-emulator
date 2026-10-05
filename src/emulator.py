"""Ядро эмулятора оболочки — обработка команд."""

from src.parser import parse_command
from src.commands import COMMANDS


class ShellEmulator:
    """Эмулятор командной оболочки UNIX."""

    def __init__(self, vfs):
        """Инициализация эмулятора.

        Args:
            vfs: Экземпляр VFS для работы с файлами.
        """
        self.vfs = vfs
        self.running = True

    def execute(self, line):
        """Выполняет строку команды.

        Args:
            line: Строка с командой.

        Returns:
            Строка с результатом выполнения.
        """
        try:
            cmd_name, args = parse_command(line)
        except ValueError as e:
            return str(e)
        if cmd_name is None:
            return ""
        if cmd_name not in COMMANDS:
            return f"{cmd_name}: команда не найдена"
        result = COMMANDS[cmd_name](self.vfs, args)
        if result == "__EXIT__":
            self.running = False
            return "Выход из эмулятора."
        return result

    def get_prompt(self):
        """Возвращает строку приглашения к вводу.

        Returns:
            Строка приглашения с текущей директорией.
        """
        cwd_display = self.vfs.cwd
        if cwd_display == "/":
            cwd_display = "/"
        return f"{cwd_display}$ "

    def run_script(self, script_path, output_callback=None):
        """Выполняет стартовый скрипт.

        Останавливается при первой ошибке.
        Поддерживает комментарии (строки, начинающиеся с #).

        Args:
            script_path: Путь к файлу скрипта.
            output_callback: Функция для вывода результатов.

        Raises:
            FileNotFoundError: Если файл скрипта не найден.
        """
        with open(script_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            prompt = self.get_prompt()
            display = f"{prompt}{stripped}"
            if output_callback:
                output_callback(display)
            result = self.execute(stripped)
            if result:
                if output_callback:
                    output_callback(result)
            if not self.running:
                break
            if self._is_error(result):
                msg = (
                    f"Ошибка в скрипте, "
                    f"строка {line_num}: {stripped}"
                )
                if output_callback:
                    output_callback(msg)
                break

    def _is_error(self, result):
        """Проверяет, является ли результат ошибкой.

        Args:
            result: Строка результата команды.

        Returns:
            True если результат содержит ошибку.
        """
        error_markers = [
            "команда не найдена",
            "Нет такого файла",
            "Не является каталогом",
            "недостаточно аргументов",
            "отсутствует операнд",
            "неверные аргументы",
            "ошибка",
            "Ошибка",
        ]
        return any(m in result for m in error_markers)
