# AI service

## Переменные окружающей среды

Использует следующие environment variables:
- PORT - порт ии сервиса
- GENERATIVE_MODEL - генеративная модель из реестра ollama
- OLLAMA_URL - адрес олламы

## Заготовленные compose файлы

Запустить ИИ сервис вметсе с олламой для разработки других модулей:
```
docker compose up -f ./ml/compose.yml -d
```

Запустить только олламу для разработки ИИ сервиса:
```
docker compose up -f ./ml/compose.ollama_only.yml -d
```