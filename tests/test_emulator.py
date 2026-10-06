"""Тесты для ядра эмулятора."""

import unittest

from src.emulator import ShellEmulator
from src.vfs import VFS, VFSNode


class TestEmulator(unittest.TestCase):
    """Тесты ядра эмулятора."""

    def set_up(self):
        """Подготовка эмулятора для тестов."""
        self.vfs = VFS()
        home = VFSNode("home", is_dir=True)
        self.vfs.root.children["home"] = home
        self.emulator = ShellEmulator(self.vfs)

    def test_execute_ls(self):
        """Выполнение команды ls."""
        result = self.emulator.execute("ls")
        self.assertIn("home", result)

    def test_execute_unknown(self):
        """Выполнение неизвестной команды."""
        result = self.emulator.execute("foo")
        self.assertIn("команда не найдена", result)

    def test_execute_empty(self):
        """Выполнение пустой строки."""
        result = self.emulator.execute("")
        self.assertEqual(result, "")

    def test_execute_exit(self):
        """Выполнение exit завершает работу."""
        self.emulator.execute("exit")
        self.assertFalse(self.emulator.running)

    def test_prompt(self):
        """Приглашение содержит текущий каталог."""
        prompt = self.emulator.get_prompt()
        self.assertIn("/", prompt)
        self.assertIn("$", prompt)

    def test_prompt_after_cd(self):
        """Приглашение обновляется после cd."""
        self.emulator.execute("cd home")
        prompt = self.emulator.get_prompt()
        self.assertIn("home", prompt)

    def test_quoted_args(self):
        """Парсер корректно обрабатывает кавычки."""
        result = self.emulator.execute(
            'ls "home"'
        )
        self.assertNotIn("Ошибка", result)


setattr(TestEmulator, "setUp", TestEmulator.set_up)


if __name__ == "__main__":
    unittest.main()
