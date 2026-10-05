"""Тесты для виртуальной файловой системы."""

import json
import os
import tempfile
import unittest

from src.vfs import VFS, VFSNode


class TestVFSNode(unittest.TestCase):
    """Тесты узлов VFS."""

    def test_file_node_creation(self):
        """Создание файлового узла."""
        node = VFSNode("test.txt", content=b"hello")
        self.assertEqual(node.name, "test.txt")
        self.assertFalse(node.is_dir)
        self.assertEqual(node.content, b"hello")

    def test_dir_node_creation(self):
        """Создание узла директории."""
        node = VFSNode("dir", is_dir=True)
        self.assertEqual(node.name, "dir")
        self.assertTrue(node.is_dir)
        self.assertEqual(node.children, {})

    def test_serialization(self):
        """Сериализация и десериализация узла."""
        node = VFSNode(
            "test.txt", content=b"hello"
        )
        data = node.to_dict()
        restored = VFSNode.from_dict(data)
        self.assertEqual(restored.name, "test.txt")
        self.assertEqual(restored.content, b"hello")


class TestVFS(unittest.TestCase):
    """Тесты виртуальной файловой системы."""

    def setUp(self):
        """Подготовка тестовой VFS."""
        self.vfs = VFS()
        self._create_test_structure()

    def _create_test_structure(self):
        """Создаёт тестовую структуру файлов."""
        home = VFSNode("home", is_dir=True)
        user = VFSNode("user", is_dir=True)
        doc = VFSNode(
            "doc.txt", content=b"content"
        )
        user.children["doc.txt"] = doc
        home.children["user"] = user
        self.vfs.root.children["home"] = home
        readme = VFSNode(
            "readme.txt", content=b"readme"
        )
        self.vfs.root.children["readme.txt"] = readme

    def test_list_root(self):
        """Вывод содержимого корня."""
        entries = self.vfs.list_dir("/")
        self.assertIn("home", entries)
        self.assertIn("readme.txt", entries)

    def test_change_dir(self):
        """Смена директории."""
        self.vfs.change_dir("home")
        self.assertEqual(self.vfs.cwd, "/home")

    def test_change_dir_nested(self):
        """Смена директории с вложенностью."""
        self.vfs.change_dir("/home/user")
        self.assertEqual(self.vfs.cwd, "/home/user")

    def test_change_dir_dotdot(self):
        """Переход на уровень выше."""
        self.vfs.change_dir("/home/user")
        self.vfs.change_dir("..")
        self.assertEqual(self.vfs.cwd, "/home")

    def test_change_dir_nonexistent(self):
        """Переход в несуществующую директорию."""
        with self.assertRaises(FileNotFoundError):
            self.vfs.change_dir("/nonexistent")

    def test_read_file(self):
        """Чтение содержимого файла."""
        content = self.vfs.read_file("/readme.txt")
        self.assertEqual(content, "readme")

    def test_read_nonexistent(self):
        """Чтение несуществующего файла."""
        with self.assertRaises(FileNotFoundError):
            self.vfs.read_file("/nope.txt")

    def test_touch_new_file(self):
        """Создание нового файла через touch."""
        self.vfs.touch("/newfile.txt")
        node = self.vfs.get_node("/newfile.txt")
        self.assertIsNotNone(node)
        self.assertFalse(node.is_dir)

    def test_chmod(self):
        """Изменение прав доступа."""
        self.vfs.chmod("/readme.txt", "777")
        node = self.vfs.get_node("/readme.txt")
        self.assertEqual(node.permissions, "777")

    def test_remove_file(self):
        """Удаление файла."""
        self.vfs.remove("/readme.txt")
        node = self.vfs.get_node("/readme.txt")
        self.assertIsNone(node)

    def test_remove_nonexistent(self):
        """Удаление несуществующего файла."""
        with self.assertRaises(FileNotFoundError):
            self.vfs.remove("/nope.txt")

    def test_motd(self):
        """Получение motd, если нет — None."""
        self.assertIsNone(self.vfs.get_motd())
        motd_node = VFSNode(
            "motd", content=b"Welcome!"
        )
        self.vfs.root.children["motd"] = motd_node
        self.assertEqual(
            self.vfs.get_motd(), "Welcome!"
        )

    def test_json_roundtrip(self):
        """Загрузка и сохранение JSON VFS."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(
                self.vfs.root.to_dict(), f
            )
            tmp_path = f.name
        try:
            new_vfs = VFS()
            new_vfs.load_from_json(tmp_path)
            entries = new_vfs.list_dir("/")
            self.assertIn("home", entries)
        finally:
            os.unlink(tmp_path)

    def test_resolve_relative_path(self):
        """Разрешение относительного пути."""
        self.vfs.cwd = "/home"
        resolved = self.vfs.resolve_path("user")
        self.assertEqual(resolved, "/home/user")

    def test_resolve_absolute_path(self):
        """Разрешение абсолютного пути."""
        resolved = self.vfs.resolve_path("/home/user")
        self.assertEqual(resolved, "/home/user")


if __name__ == "__main__":
    unittest.main()
