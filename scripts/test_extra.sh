# Стартовый скрипт для Этапа 5 (Дополнительные команды)
# Тестирование chmod, touch

# Тест ls перед изменениями
ls

# Тест touch — создание нового файла
touch newfile.txt
ls

# Тест touch — обновление времени
touch motd

# Тест chmod — изменение прав
chmod 755 motd

# Тест chmod на вложенном файле
cd home/user
chmod 600 config.txt
ls

# Тест touch во вложенной директории
touch documents/newdoc.txt
ls documents

# Тест ошибки: chmod несуществующего файла
chmod 777 /no/such/file

# Тест ошибки: touch без аргументов
touch

# Вернуться в корень
cd /
ls

exit
