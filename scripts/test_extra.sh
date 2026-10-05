# Стартовый скрипт для Этапа 5 (Дополнительные команды)
# Тестирование команд chmod и touch, модификации VFS в памяти и обработки ошибок

# Исходное состояние
ls

# 1. Тестирование touch (создание нового файла в текущем каталоге)
touch created_file.txt
ls

# 2. Тестирование touch (обновление времени существующего файла)
touch motd

# 3. Тестирование touch во вложенной директории
touch home/user/documents/new_doc.txt
ls home/user/documents

# 4. Тестирование chmod (изменение прав доступа в памяти)
chmod 755 motd
chmod 600 created_file.txt

# 5. Тестирование chmod для директории
chmod 700 home/user

# 6. Обработка ошибок: touch без аргументов
touch

# 7. Обработка ошибок: touch в несуществующую директорию
touch /not_existing_dir/file.txt

# 8. Обработка ошибок: chmod без аргументов или с недостаточным числом
chmod 777

# 9. Обработка ошибок: chmod для несуществующего пути
chmod 644 /nowhere/file.txt

exit
