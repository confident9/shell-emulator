# Эмулятор оболочки ОС (Вариант №30)

Эмулятор командной оболочки UNIX-подобной ОС с графическим интерфейсом (GUI).

## Общее описание

Приложение эмулирует работу командной строки UNIX-подобной операционной
системы. Реализовано в форме графического интерфейса с использованием
`tkinter`. Поддерживает виртуальную файловую систему (VFS) на основе
JSON-файлов с кодированием двоичных данных в base64.

## Структура проекта

```
shell-emulator/
├── main.py                  # Точка входа
├── run.sh                   # Скрипт запуска
├── README.md                # Документация
├── .gitignore               # Игнорируемые файлы
├── src/                     # Исходный код
│   ├── __init__.py
│   ├── parser.py            # Парсер команд
│   ├── vfs.py               # Виртуальная ФС
│   ├── commands.py          # Реализация команд
│   ├── emulator.py          # Ядро эмулятора
│   └── gui.py               # GUI-интерфейс
├── tests/                   # Тесты
│   ├── __init__.py
│   ├── test_parser.py
│   ├── test_vfs.py
│   ├── test_commands.py
│   └── test_emulator.py
├── scripts/                 # Скрипты тестирования
│   ├── test_vfs.sh          # Стартовый скрипт (VFS)
│   ├── test_commands.sh     # Стартовый скрипт (команды)
│   ├── test_extra.sh        # Стартовый скрипт (chmod, touch)
│   ├── run_test_minimal.sh  # Тест с минимальной VFS
│   ├── run_test_full.sh     # Тест с полной VFS
│   ├── run_test_extra.sh    # Тест доп. команд
│   └── run_test_config.sh   # Тест конфигурации
└── vfs_samples/             # Образцы VFS
    ├── minimal.json         # Минимальная VFS
    ├── several_files.json   # VFS с несколькими файлами
    └── full.json            # Полная VFS (3+ уровня)
```

## Функции и настройки

### Поддерживаемые команды

| Команда   | Описание                                |
|-----------|-----------------------------------------|
| `ls`      | Вывод содержимого директории            |
| `cd`      | Смена текущей директории                |
| `exit`    | Завершение работы эмулятора             |
| `date`    | Вывод текущей даты и времени            |
| `cal`     | Вывод календаря (месяц/год)             |
| `chmod`   | Изменение прав доступа (в памяти)       |
| `touch`   | Создание файла / обновление времени     |
| `vfs-save`| Сохранение состояния VFS на диск        |

### Параметры командной строки

- `--vfs <путь>` — путь к JSON-файлу VFS или директории
- `--script <путь>` — путь к стартовому скрипту

### Стартовые скрипты

Скрипты содержат команды эмулятора (по одной на строку).
Комментарии начинаются с символа `#`.
Выполнение останавливается при первой ошибке.

### Виртуальная файловая система (VFS)

VFS хранится в формате JSON. Двоичные данные файлов кодируются в
base64. Все модификации (touch, chmod) выполняются только в памяти.
Для сохранения состояния VFS на диск используется команда `vfs-save`.

При старте эмулятора выводится содержимое файла `motd` из корня VFS
(если он существует).

## Сборка и запуск

### Требования

- Python 3.7+
- tkinter (обычно входит в стандартную поставку Python)
- pytest (для запуска тестов)

### Запуск эмулятора

```bash
# Без VFS (пустая файловая система)
python3 main.py

# С VFS
python3 main.py --vfs vfs_samples/full.json

# С VFS и стартовым скриптом
python3 main.py --vfs vfs_samples/full.json --script scripts/test_commands.sh
```

Или через скрипт запуска:

```bash
chmod +x run.sh
./run.sh --vfs vfs_samples/full.json
```

### Запуск тестов

```bash
# Через run.sh
./run.sh test

# Или напрямую
python3 -m pytest tests/ -v
```

### Скрипты тестирования ОС

```bash
chmod +x scripts/*.sh
bash scripts/run_test_minimal.sh
bash scripts/run_test_full.sh
bash scripts/run_test_extra.sh
bash scripts/run_test_config.sh
```

## Примеры использования

### Интерактивный режим

```
/$ ls
bin  etc  home  motd  tmp
/$ cd home/user
/home/user$ ls
config.txt  documents
/home/user$ cd documents
/home/user/documents$ ls
data.csv  report.txt
/home/user/documents$ cd /
/$ date
Mon Oct 05 22:00:00 2026
/$ cal
    October 2026
Mo Tu We Th Fr Sa Su
          1  2  3  4
 5  6  7  8  9 10 11
...
/$ touch newfile.txt
/$ chmod 755 newfile.txt
/$ exit
```

### Стартовый скрипт

```bash
# Пример скрипта (scripts/test_vfs.sh)
ls
cd home
ls
cd ..
date
exit
```
