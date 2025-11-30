# AI service

## Переменные окружающей среды

Использует следующие environment variables:
- PORT - порт ии сервиса
- GENERATIVE_MODEL - генеративная модель из реестра ollama
- OLLAMA_URL - адрес олламы

## Заготовленные compose файлы

### Для разработки других сервисов

Запустить ИИ сервис вметсе с олламой для разработки других модулей:

```
docker compose up -f ./ml/compose.yml -d
```

> В этом же compose.yml можно поменять переменные окружающей среды

### Для разработки ИИ сервиса

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