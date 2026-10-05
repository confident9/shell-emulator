# Стартовый скрипт для Этапа 4 (Основные команды)
# Тестирование команд ls, cd, date, cal и обработки ошибок

# 1. Тестирование команды ls
ls
ls home
ls home/user/documents
ls home/user/documents/report.txt

# 2. Тестирование команды cd
cd home/user
ls
cd documents
ls
cd ..
ls
cd /etc
ls
cd /
ls

# 3. Тестирование команды date
date

# 4. Тестирование команды cal
cal
cal 2026
cal 10 2026

# 5. Примеры обработки ошибок
ls /not_found_directory
cd /etc/hosts
cal invalid_year
cal 15 2026

exit
