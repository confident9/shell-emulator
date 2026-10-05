"""Тесты для режимов интерфейса (CLI и Web GUI)."""

import unittest

from src.cli import ShellCLI
from src.web_gui import ShellWebGUI


class TestModes(unittest.TestCase):
    """Тестирование инициализации режимов CLI и Web GUI."""

    def test_cli_init(self):
        """Проверка создания объекта ShellCLI."""
        cli = ShellCLI(vfs_path="vfs_samples/minimal.json")
        self.assertIsNotNone(cli.vfs)
        self.assertIsNotNone(cli.emulator)
        title = cli._get_title()
        self.assertTrue(title.startswith("Эмулятор - ["))

    def test_web_gui_init(self):
        """Проверка создания объекта ShellWebGUI."""
        web = ShellWebGUI(vfs_path="vfs_samples/minimal.json")
        self.assertIsNotNone(web.vfs)
        self.assertIsNotNone(web.emulator)
        title = web._get_title()
        self.assertTrue(title.startswith("Эмулятор - ["))
        self.assertTrue(len(web.initial_items) > 0)


if __name__ == "__main__":
    unittest.main()
