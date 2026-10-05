"""Парсер командной строки для эмулятора оболочки."""

import shlex


def parse_command(line):
    """Разбирает строку команды на имя и аргументы.

    Корректно обрабатывает аргументы в кавычках.

    Args:
        line: Строка команды для разбора.

    Returns:
        Кортеж (имя_команды, список_аргументов) или
        (None, []) если строка пустая.
    """
    stripped = line.strip()
    if not stripped:
        return None, []
    try:
        tokens = shlex.split(stripped)
    except ValueError as e:
        raise ValueError(
            f"Ошибка разбора команды: {e}"
        ) from e
    if not tokens:
        return None, []
    return tokens[0], tokens[1:]
