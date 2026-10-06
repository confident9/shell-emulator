"""Тесты для команд эмулятора."""

import unittest

from src.commands import (
    cmd_ls, cmd_cd, cmd_exit,
    cmd_date, cmd_cal, cmd_chmod,
    cmd_touch,
)
from src.vfs import VFS, VFSNode


class TestCommands(unittest.TestCase):
    """Тесты команд эмулятора."""

    def set_up(self):
        """Подготовка VFS для тестов."""
        self.vfs = VFS()
        home = VFSNode("home", is_dir=True)
        user = VFSNode("user", is_dir=True)
        doc = VFSNode(
            "doc.txt", content=b"hello"
        )
        user.children["doc.txt"] = doc
        home.children["user"] = user
        self.vfs.root.children["home"] = home

    setUp = set_up

    def test_ls_root(self):
        """Команда ls в корне."""
        result = cmd_ls(self.vfs, [])
        self.assertIn("home", result)

    def test_ls_subdir(self):
        """Команда ls в подкаталоге."""
        result = cmd_ls(self.vfs, ["home"])
        self.assertIn("user", result)

    def test_ls_nonexistent(self):
        """ls несуществующей директории."""
        result = cmd_ls(self.vfs, ["/nope"])
        self.assertIn("Нет такого", result)

    def test_cd_home(self):
        """Команда cd в home."""
        result = cmd_cd(self.vfs, ["home"])
        self.assertEqual(result, "")
        self.assertEqual(self.vfs.cwd, "/home")

    def test_cd_no_args(self):
        """cd без аргументов — в корень."""
        self.vfs.cwd = "/home"
        result = cmd_cd(self.vfs, [])
        self.assertEqual(result, "")
        self.assertEqual(self.vfs.cwd, "/")

    def test_cd_nonexistent(self):
        """cd в несуществующую директорию."""
        result = cmd_cd(self.vfs, ["/nope"])
        self.assertIn("Нет такого", result)

    def test_exit(self):
        """Команда exit возвращает маркер."""
        result = cmd_exit(self.vfs, [])
        self.assertEqual(result, "__EXIT__")

    def test_date(self):
        """Команда date возвращает строку."""
        result = cmd_date(self.vfs, [])
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

    def test_cal_no_args(self):
        """Команда cal без аргументов."""
        result = cmd_cal(self.vfs, [])
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

    def test_cal_with_year(self):
        """Команда cal с указанием года."""
        result = cmd_cal(self.vfs, ["2026"])
        self.assertIn("2026", result)

    def test_cal_with_month_year(self):
        """Команда cal с месяцем и годом."""
        result = cmd_cal(self.vfs, ["1", "2026"])
        self.assertIn("January", result)

    def test_chmod(self):
        """Команда chmod изменяет права."""
        cmd_chmod(
            self.vfs, ["755", "home/user/doc.txt"]
        )
        node = self.vfs.get_node(
            "/home/user/doc.txt"
        )
        self.assertEqual(node.permissions, "755")

    def test_chmod_no_args(self):
        """chmod без аргументов — ошибка."""
        result = cmd_chmod(self.vfs, [])
        self.assertIn("недостаточно", result)

    def test_touch_new(self):
        """touch создаёт новый файл."""
        cmd_touch(self.vfs, ["new.txt"])
        node = self.vfs.get_node("/new.txt")
        self.assertIsNotNone(node)

    def test_touch_no_args(self):
        """touch без аргументов — ошибка."""
        result = cmd_touch(self.vfs, [])
        self.assertIn("отсутствует", result)


if __name__ == "__main__":
    unittest.main()
