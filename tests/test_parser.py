"""Тесты для парсера команд."""

import unittest

from src.parser import parse_command


class TestParser(unittest.TestCase):
    """Тесты парсера командной строки."""

    def test_empty_input(self):
        """Пустая строка возвращает (None, [])."""
        cmd, args = parse_command("")
        self.assertIsNone(cmd)
        self.assertEqual(args, [])

    def test_whitespace_input(self):
        """Строка из пробелов возвращает (None, [])."""
        cmd, args = parse_command("   ")
        self.assertIsNone(cmd)
        self.assertEqual(args, [])

    def test_simple_command(self):
        """Простая команда без аргументов."""
        cmd, args = parse_command("ls")
        self.assertEqual(cmd, "ls")
        self.assertEqual(args, [])

    def test_command_with_args(self):
        """Команда с несколькими аргументами."""
        cmd, args = parse_command("ls -la /home")
        self.assertEqual(cmd, "ls")
        self.assertEqual(args, ["-la", "/home"])

    def test_quoted_args(self):
        """Аргументы в кавычках."""
        cmd, args = parse_command('echo "hello world"')
        self.assertEqual(cmd, "echo")
        self.assertEqual(args, ["hello world"])

    def test_single_quoted_args(self):
        """Аргументы в одинарных кавычках."""
        cmd, args = parse_command("echo 'hello world'")
        self.assertEqual(cmd, "echo")
        self.assertEqual(args, ["hello world"])

    def test_mixed_quotes(self):
        """Смешанные кавычки в аргументах."""
        cmd, args = parse_command(
            'echo "hello" \'world\''
        )
        self.assertEqual(cmd, "echo")
        self.assertEqual(args, ["hello", "world"])

    def test_unclosed_quotes(self):
        """Незакрытые кавычки вызывают ошибку."""
        with self.assertRaises(ValueError):
            parse_command('echo "unclosed')


if __name__ == "__main__":
    unittest.main()
