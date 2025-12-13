# Backend service

## Переменные окружающей среды

Использует следующие environment variables:
- От СУБД:
  - POSTGRES_USER - имя пользователя СУБД
  - POSTGRES_PASSWORD - пароль пользователя СУБД
  - POSTGRES_DB - название используемйо БД
  - PGADMIN_DEFAULT_EMAIL - почта для входа в панель управления СУБД
  - PGADMIN_DEFAULT_PASSWORD - пароль для входа в панель управления СУБД
- От backend сервиса:
  - database_url - sqlalchemy engine url к БД
  - app_name *[опц]* - название сервиса
  - debug *[опц]* - дебаг вывод сервиса
  - static_dir *[опц]* - путь к папке со статикой
  - images_dir *[опц]* - путь к папке с картинками
  - cors_origins *[опц]* - доверенные источники запросов. Должен быть в формате '["A", "B", "C"]'

## Заготовленные compose и .env файлы

> Команды выполняются из папки **backend**

### Для разработки других сервисов

Запустить backend сервис вметсе с БД для разработки других модулей:

```
docker compose up -f ./compose.yml -d
```

> В этом же compose.yml можно поменять переменные окружающей среды

> pgadmin доступен по адресу `http://127.0.0.1:15433`

### Для разработки backend сервиса

Пример `.env` файла - `.env.example`

Запустить только БД для разработки backend сервиса:

```
docker compose up -f ./compose.db_only.yml -d
```

> В этом же compose.db_only.yml можно поменять переменные окружающей среды

Создать локальное окружение:
```
python -m venv .venv
```
Активировать его (зависит от системы)

Установить зависимости:
```
pip install -r ./requirements.txt
```

Запустить backend сервис:
```
uvicorn app.main:app
```

### Для теста backend сервиса

```
docker compose -f ./compose.test.yml up --exit-code-from backend --abort-on-container-exit
```

> pgadmin доступен по адресу `http://127.0.0.1:15433`

> Если контейнер не обновляется, к `compose up` можно добавить флаги `--build --force-recreate`