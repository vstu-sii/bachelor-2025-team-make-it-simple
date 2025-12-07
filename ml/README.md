# AI service

## Структура

ml\
├─ api\
│&nbsp;&nbsp;&nbsp;&nbsp;├─ vector_db - работа с векторной БД\
│&nbsp;&nbsp;&nbsp;&nbsp;├─ routes.py - эндпоинты ллм сервера\
│&nbsp;&nbsp;&nbsp;&nbsp;└─ server.py - ллм веб сервер\
├─ evaluation - оценка моделей\
│&nbsp;&nbsp;&nbsp;&nbsp;├─ evaluator.py - модуль для оценки моделей\
│&nbsp;&nbsp;&nbsp;&nbsp;└─ metrics.py - сборщик метрик моделей\
├─ utils\
│&nbsp;&nbsp;&nbsp;&nbsp;├─ env.py - модуль для переменными окружения\
│&nbsp;&nbsp;&nbsp;&nbsp;└─ ollama.py - модуль для работы с ollama (функции, которые есть в api олламы, но нет в библиотеке)\
├─ .dockerignore - перечень файлов, не попадающих в контейнер\
├─ .gitignore\
├─ compose.ollama_only.yml - композ файл для запуска олламы для разработки сервиса\
├─ compose.yml - композ файл для запуска сервиса\
├─ Dockerfile - файл упаковки сервиса в контейнер\
└─ requirements.txt - зависимости pip пакетов сервиса\

## Запуск

### Переменные окружающей среды

Использует следующие environment variables:
- PORT - порт ии сервиса
- GENERATIVE_MODEL - генеративная модель из реестра ollama
- OLLAMA_URL - адрес олламы

### Заготовленные compose файлы

#### Для разработки других сервисов

Запустить ИИ сервис вметсе с олламой для разработки других модулей:

```
docker compose up -f ./ml/compose.yml -d
```

> В этом же compose.yml можно поменять переменные окружающей среды

#### Для разработки ИИ сервиса

Запустить только олламу для разработки ИИ сервиса:

```
docker compose up -f ./ml/compose.ollama_only.yml -d
```

> В этом же compose.ollama_only.yml можно поменять переменные окружающей среды

Создать локальное окружение:
```
python -m venv .venv
```
Активировать его (зависит от системы)

Установить зависимости:
```
pip install -r ./ml/requirements.txt
```

Запустить ИИ сервис:
```
python ./ml/api/server.py
```

> Если контейнер не обновляется, к `compose up` можно добавить флаги `--build --force-recreate`