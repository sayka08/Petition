# Petition - Настройка и запуск приложения

# Склонируй репо
git clone https://github.com/sayka08/Petition.git

# Создай вирутальное окружение 
python -m venv venv

# Активация виртуального окружения на Windows
venv\Scripts\activate 

# Активация виртуального окружения на MacOS/Linux
source venv/bin/activate

# В корне проекта создай файл .env и добавь переменную как в .env_example
# URL будет указывать на твою локальную БД
SQL_DB_URL = "your db_url" # for example sqlite:///./db/name.db

# Создай папку db, в db будет храниться БД 
mkdir db

# Собери docker - образ
docker-compose build

# Запусти контейнер 
docker-compose up






