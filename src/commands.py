"""Реализация команд эмулятора оболочки UNIX."""

import calendar
import datetime


def cmd_ls(vfs, args):
    """Команда ls — вывод содержимого директории или имени файла.

    Args:
        vfs: Экземпляр VFS.
        args: Аргументы команды.

    Returns:
        Строка с результатом выполнения.
    """
    target = args[0] if args else "."
    abs_path = vfs.resolve_path(target)
    node = vfs.get_node(abs_path)
    if node is None:
        return f"ls: Нет такого файла или каталога: {target}"
    if not node.is_dir:
        return node.name
    entries = sorted(node.children.keys())
    return "\n".join(entries)


def cmd_cd(vfs, args):
    """Команда cd — смена текущей директории.

    Args:
        vfs: Экземпляр VFS.
        args: Аргументы команды.

    Returns:
        Строка с сообщением об ошибке или пустая строка при успехе.
    """
    if not args or args[0] == "~":
        vfs.cwd = "/"
        return ""
    target = args[0]
    abs_path = vfs.resolve_path(target)
    node = vfs.get_node(abs_path)
    if node is None:
        return f"cd: Нет такого файла или каталога: {target}"
    if not node.is_dir:
        return f"cd: Не является каталогом: {target}"
    vfs.cwd = abs_path
    return ""


def cmd_exit(vfs, args):
    """Команда exit — завершение работы эмулятора.

    Args:
        vfs: Экземпляр VFS.
        args: Аргументы команды.

    Returns:
        Специальный маркер для завершения.
    """
    return "__EXIT__"


def cmd_date(vfs, args):
    """Команда date — вывод текущей даты и времени UNIX.

    Args:
        vfs: Экземпляр VFS.
        args: Аргументы команды.

    Returns:
        Строка с текущей датой и временем.
    """
    now = datetime.datetime.now()
    return now.strftime("%a %b %d %H:%M:%S %Y")


def cmd_cal(vfs, args):
    """Команда cal — вывод календаря.

    Args:
        vfs: Экземпляр VFS.
        args: Аргументы команды.

    Returns:
        Строка с календарём.
    """
    now = datetime.datetime.now()
    if len(args) >= 2:
        return _cal_with_month_year(args)
    if len(args) == 1:
        return _cal_with_year(args[0])
    return calendar.month(now.year, now.month).rstrip()


def _cal_with_month_year(args):
    """Выводит календарь для указанного месяца и года."""
    try:
        month = int(args[0])
        year = int(args[1])
        if month < 1 or month > 12:
            return "cal: неверный номер месяца (должен быть 1-12)"
        return calendar.month(year, month).rstrip()
    except (ValueError, calendar.IllegalMonthError):
        return "cal: неверные аргументы"


def _cal_with_year(arg):
    """Выводит календарь для указанного года."""
    try:
        year = int(arg)
        if year < 1 or year > 9999:
            return "cal: неверный год (должен быть 1-9999)"
        return calendar.calendar(year).rstrip()
    except ValueError:
        return "cal: неверный год"


def cmd_chmod(vfs, args):
    """Команда chmod — изменение прав доступа в памяти.

    Args:
        vfs: Экземпляр VFS.
        args: Аргументы [права, путь].

    Returns:
        Строка с ошибкой или пустая строка при успехе.
    """
    if len(args) < 2:
        return "chmod: недостаточно аргументов"
    permissions = args[0]
    path = args[1]
    abs_path = vfs.resolve_path(path)
    node = vfs.get_node(abs_path)
    if node is None:
        return f"chmod: Нет такого файла или каталога: {path}"
    node.permissions = permissions
    return ""


def cmd_touch(vfs, args):
    """Команда touch — создание файла или обновление времени в памяти.

    Args:
        vfs: Экземпляр VFS.
        args: Аргументы [путь].

    Returns:
        Строка с ошибкой или пустая строка при успехе.
    """
    if not args:
        return "touch: отсутствует операнд"
    path = args[0]
    try:
        vfs.touch(path)
    except FileNotFoundError as e:
        return f"touch: {e}"
    return ""


def cmd_vfs_save(vfs, args):
    """Команда vfs-save — сохранение VFS на диск в исходном формате.

    Args:
        vfs: Экземпляр VFS.
        args: Аргументы [путь_для_сохранения].

    Returns:
        Строка с результатом.
    """
    if not args:
        return "vfs-save: укажите путь для сохранения"
    path = args[0]
    try:
        vfs.save_to_json(path)
    except (IOError, OSError) as e:
        return f"vfs-save: ошибка сохранения: {e}"
    return f"VFS сохранена в {path}"


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit,
    "date": cmd_date,
    "cal": cmd_cal,
    "chmod": cmd_chmod,
    "touch": cmd_touch,
    "vfs-save": cmd_vfs_save,
}
