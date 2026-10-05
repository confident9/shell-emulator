# Стартовый скрипт для Этапа 4 (Основные команды)
# Тестирование ls, cd, date, cal

# Тест ls в корне
ls

# Тест ls с аргументом
ls home

# Тест ls вложенная директория
ls home/user/documents

# Тест cd
cd home/user
ls

# Тест cd ..
cd ..
ls

# Тест cd /
cd /

# Тест date
date

# Тест cal без аргументов
cal

# Тест cal с годом
cal 2026

# Тест cal с месяцем и годом
cal 10 2026

# Тест ошибки: ls несуществующей директории
ls /nonexistent

# Тест ошибки: cd в файл
cd /etc/hosts

exit
