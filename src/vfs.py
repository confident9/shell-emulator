"""Виртуальная файловая система (VFS) для эмулятора."""

import json
import base64
import os
import time


class VFSNode:
    """Узел виртуальной файловой системы."""

    def __init__(self, name, is_dir=False, content=b"",
                 permissions="rwxr-xr-x"):
        """Инициализация узла VFS.

        Args:
            name: Имя файла или директории.
            is_dir: Является ли узел директорией.
            content: Содержимое файла в байтах.
            permissions: Строка прав доступа в формате UNIX.
        """
        self.name = name
        self.is_dir = is_dir
        self.content = content
        self.permissions = permissions
        self.children = {}
        self.mtime = time.time()

    def to_dict(self):
        """Сериализует узел в словарь для JSON.

        Returns:
            Словарь с данными узла.
        """
        result = {
            "name": self.name,
            "is_dir": self.is_dir,
            "permissions": self.permissions,
        }
        if self.is_dir:
            result["children"] = [
                child.to_dict()
                for child in self.children.values()
            ]
        else:
            result["content"] = base64.b64encode(
                self.content
            ).decode("ascii")
        return result

    @classmethod
    def from_dict(cls, data):
        """Создаёт узел из словаря.

        Args:
            data: Словарь с данными узла.

        Returns:
            Экземпляр VFSNode.
        """
        node = cls(
            name=data["name"],
            is_dir=data.get("is_dir", False),
            permissions=data.get("permissions", "rwxr-xr-x"),
        )
        if node.is_dir:
            for child_data in data.get("children", []):
                child = cls.from_dict(child_data)
                node.children[child.name] = child
        else:
            encoded = data.get("content", "")
            node.content = base64.b64decode(encoded)
        return node


class VFS:
    """Виртуальная файловая система на основе JSON."""

    def __init__(self):
        """Инициализация пустой VFS."""
        self.root = VFSNode("/", is_dir=True)
        self.cwd = "/"

    def load_from_json(self, path):
        """Загружает VFS из JSON-файла.

        Args:
            path: Путь к JSON-файлу.

        Raises:
            FileNotFoundError: Если файл не найден.
            json.JSONDecodeError: Если JSON некорректен.
        """
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.root = VFSNode.from_dict(data)
        self.root.name = "/"
        self.cwd = "/"

    def load_from_directory(self, dir_path):
        """Загружает VFS из директории на диске.

        Args:
            dir_path: Путь к директории.

        Raises:
            FileNotFoundError: Если директория не найдена.
        """
        if not os.path.isdir(dir_path):
            raise FileNotFoundError(
                f"Директория не найдена: {dir_path}"
            )
        self.root = self._scan_directory(dir_path, "/")
        self.cwd = "/"

    def _scan_directory(self, real_path, name):
        """Рекурсивно сканирует директорию.

        Args:
            real_path: Реальный путь на диске.
            name: Имя в VFS.

        Returns:
            VFSNode для директории.
        """
        node = VFSNode(name, is_dir=True)
        try:
            entries = sorted(os.listdir(real_path))
        except PermissionError:
            return node
        for entry in entries:
            full = os.path.join(real_path, entry)
            if os.path.isdir(full):
                child = self._scan_directory(full, entry)
                node.children[entry] = child
            elif os.path.isfile(full):
                child = self._read_file_node(full, entry)
                node.children[entry] = child
        return node

    def _read_file_node(self, full_path, name):
        """Читает файл и создаёт узел VFS.

        Args:
            full_path: Полный путь к файлу.
            name: Имя файла в VFS.

        Returns:
            VFSNode для файла.
        """
        try:
            with open(full_path, "rb") as f:
                content = f.read()
        except (PermissionError, IOError):
            content = b""
        return VFSNode(name, is_dir=False, content=content)

    def save_to_json(self, path):
        """Сохраняет VFS в JSON-файл.

        Args:
            path: Путь для сохранения.
        """
        data = self.root.to_dict()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def resolve_path(self, path):
        """Разрешает путь относительно текущей директории.

        Args:
            path: Путь (абсолютный или относительный).

        Returns:
            Нормализованный абсолютный путь.
        """
        if not path.startswith("/"):
            if self.cwd == "/":
                path = "/" + path
            else:
                path = self.cwd + "/" + path
        parts = path.split("/")
        resolved = []
        for part in parts:
            if part == "" or part == ".":
                continue
            elif part == "..":
                if resolved:
                    resolved.pop()
            else:
                resolved.append(part)
        return "/" + "/".join(resolved)

    def get_node(self, path):
        """Получает узел по пути.

        Args:
            path: Путь в VFS.

        Returns:
            VFSNode или None, если узел не найден.
        """
        abs_path = self.resolve_path(path)
        if abs_path == "/":
            return self.root
        parts = abs_path.strip("/").split("/")
        current = self.root
        for part in parts:
            if not current.is_dir:
                return None
            if part not in current.children:
                return None
            current = current.children[part]
        return current

    def get_motd(self):
        """Возвращает содержимое motd из корня VFS.

        Returns:
            Строка с текстом motd или None.
        """
        motd_node = self.root.children.get("motd")
        if motd_node and not motd_node.is_dir:
            return motd_node.content.decode(
                "utf-8", errors="replace"
            )
        return None

    def list_dir(self, path="/"):
        """Возвращает содержимое директории.

        Args:
            path: Путь к директории.

        Returns:
            Список имён файлов и папок.

        Raises:
            FileNotFoundError: Если путь не найден.
            NotADirectoryError: Если путь не является
                директорией.
        """
        node = self.get_node(path)
        if node is None:
            raise FileNotFoundError(
                f"Нет такого файла или каталога: {path}"
            )
        if not node.is_dir:
            raise NotADirectoryError(
                f"Не является каталогом: {path}"
            )
        return sorted(node.children.keys())

    def change_dir(self, path):
        """Меняет текущую директорию.

        Args:
            path: Путь к новой директории.

        Raises:
            FileNotFoundError: Если путь не найден.
            NotADirectoryError: Если путь не является
                директорией.
        """
        abs_path = self.resolve_path(path)
        node = self.get_node(abs_path)
        if node is None:
            raise FileNotFoundError(
                f"Нет такого файла или каталога: {path}"
            )
        if not node.is_dir:
            raise NotADirectoryError(
                f"Не является каталогом: {path}"
            )
        self.cwd = abs_path

    def read_file(self, path):
        """Читает содержимое файла.

        Args:
            path: Путь к файлу.

        Returns:
            Содержимое файла как строка.

        Raises:
            FileNotFoundError: Если файл не найден.
            IsADirectoryError: Если путь — директория.
        """
        node = self.get_node(path)
        if node is None:
            raise FileNotFoundError(
                f"Нет такого файла: {path}"
            )
        if node.is_dir:
            raise IsADirectoryError(
                f"Является каталогом: {path}"
            )
        return node.content.decode("utf-8", errors="replace")

    def touch(self, path):
        """Создаёт пустой файл или обновляет время.

        Args:
            path: Путь к файлу.
        """
        abs_path = self.resolve_path(path)
        node = self.get_node(abs_path)
        if node is not None:
            node.mtime = time.time()
            return
        parent_path = "/".join(
            abs_path.split("/")[:-1]
        ) or "/"
        filename = abs_path.split("/")[-1]
        parent = self.get_node(parent_path)
        if parent is None or not parent.is_dir:
            raise FileNotFoundError(
                f"Нет такого каталога: {parent_path}"
            )
        new_node = VFSNode(filename, is_dir=False)
        parent.children[filename] = new_node

    def chmod(self, path, permissions):
        """Изменяет права доступа к файлу или директории.

        Args:
            path: Путь к файлу или директории.
            permissions: Строка прав доступа.

        Raises:
            FileNotFoundError: Если путь не найден.
        """
        node = self.get_node(path)
        if node is None:
            raise FileNotFoundError(
                f"Нет такого файла или каталога: {path}"
            )
        node.permissions = permissions

    def remove(self, path):
        """Удаляет файл из VFS (только в памяти).

        Args:
            path: Путь к файлу для удаления.

        Raises:
            FileNotFoundError: Если файл не найден.
            IsADirectoryError: Если путь — директория.
        """
        abs_path = self.resolve_path(path)
        if abs_path == "/":
            raise PermissionError(
                "Нельзя удалить корневую директорию"
            )
        parent_path = "/".join(
            abs_path.split("/")[:-1]
        ) or "/"
        filename = abs_path.split("/")[-1]
        parent = self.get_node(parent_path)
        if parent is None:
            raise FileNotFoundError(
                f"Нет такого файла: {path}"
            )
        if filename not in parent.children:
            raise FileNotFoundError(
                f"Нет такого файла: {path}"
            )
        node = parent.children[filename]
        if node.is_dir:
            raise IsADirectoryError(
                f"Является каталогом: {path}"
            )
        del parent.children[filename]
