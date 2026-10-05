"""Реализация команд эмулятора оболочки."""

import calendar
import datetime


def cmd_ls(vfs, args):
    """Команда ls — вывод содержимого директории.

    Args:
        vfs: Экземпляр VFS.
        args: Аргументы команды.

    Returns:
        Строка с результатом выполнения.
    """
    target = args[0] if args else "."
    try:
        entries = vfs.list_dir(
            vfs.resolve_path(target)
        )
    except (FileNotFoundError, NotADirectoryError) as e:
        return f"ls: {e}"
    if not entries:
        return ""
    return "\n".join(entries)


def cmd_cd(vfs, args):
    """Команда cd — смена текущей директории.

    Args:
        vfs: Экземпляр VFS.
        args: Аргументы команды.

    Returns:
        Строка с результатом или пустая строка.
    """
    if not args:
        vfs.cwd = "/"
        return ""
    target = args[0]
    try:
        vfs.change_dir(target)
    except (FileNotFoundError, NotADirectoryError) as e:
        return f"cd: {e}"
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
    """Команда date — вывод текущей даты и времени.

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
    """Выводит календарь для указанного месяца и года.

    Args:
        args: Список из двух аргументов [месяц, год].

    Returns:
        Строка с календарём или сообщение об ошибке.
    """
    try:
        month = int(args[0])
        year = int(args[1])
        return calendar.month(year, month).rstrip()
    except (ValueError, calendar.IllegalMonthError):
        return "cal: неверные аргументы"


def _cal_with_year(arg):
    """Выводит календарь для указанного года.

    Args:
        arg: Строка с номером года.

    Returns:
        Строка с календарём или сообщение об ошибке.
    """
    try:
        year = int(arg)
        return calendar.calendar(year).rstrip()
    except ValueError:
        return "cal: неверный год"


def cmd_chmod(vfs, args):
    """Команда chmod — изменение прав доступа.

    Args:
        vfs: Экземпляр VFS.
        args: Аргументы [права, путь].

    Returns:
        Строка с результатом.
    """
    if len(args) < 2:
        return "chmod: недостаточно аргументов"
    permissions = args[0]
    path = args[1]
    try:
        vfs.chmod(path, permissions)
    except FileNotFoundError as e:
        return f"chmod: {e}"
    return ""


def cmd_touch(vfs, args):
    """Команда touch — создание файла или обновление.

    Args:
        vfs: Экземпляр VFS.
        args: Аргументы [путь].

    Returns:
        Строка с результатом.
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
    """Команда vfs-save — сохранение VFS на диск.

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
