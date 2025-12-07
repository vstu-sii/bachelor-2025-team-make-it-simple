# Frontend service

## Структура

frontend\
├─ public\
├─ src\
│&nbsp;&nbsp;&nbsp;&nbsp;├─ api - модуль для работы с бэкендом\
│&nbsp;&nbsp;&nbsp;&nbsp;├─ assets - картинки и файлы, загружаемые из кода\
│&nbsp;&nbsp;&nbsp;&nbsp;├─ components - компоненты, используемые в странциах\
│&nbsp;&nbsp;&nbsp;&nbsp;├─ pages - веб страницы приложения\
│&nbsp;&nbsp;&nbsp;&nbsp;├─ router - эндпоинты\
│&nbsp;&nbsp;&nbsp;&nbsp;├─ stores - работа с браузерным хранилищем\
│&nbsp;&nbsp;&nbsp;&nbsp;├─ App.vue - точка входа в приложение\
│&nbsp;&nbsp;&nbsp;&nbsp;├─ config.js - загрузка переменных окружения при сборке\
│&nbsp;&nbsp;&nbsp;&nbsp;├─ main.js - запуск точки входа в приложение\
│&nbsp;&nbsp;&nbsp;&nbsp;└─ style.css - стиль приложения\
├─ .dockerignore - перечень файлов, не попадающих в контейнер\
├─ .env.example - пример переменных окружения\
├─ .gitignore\
├─ compose.yml - композ файл для запуска сервиса вместе с веб сервером\
├─ Dockerfile - файл упаковки сервиса в контейнер\
├─ ngingx.conf - конфиг веб сервера для контейнера\
├─ package-lock.json - жёсткие зависимости npm пакетов сервиса\
├─ package.json - зависимости npm пакетов сервиса\
└─ vite.config.js - конфиг фреймворка\

## Запуск

### Переменные окружающей среды

Использует следующие environment variables **на этапе сборки**:
- VITE_API_URL - адрес backend сервиса

### Заготовленные compose файлы

> Команды выполняются из папки **frontend**

Запустить фронтенд сервис:

```
docker compose up -d
```

> В этом же compose.yml можно поменять переменные, передаваемые в докерфайл во время сборки

### Разработка

Установить зависимости:
```
npm install
```

Запустить сервер для разработки:
```
npm run dev
```

> Если контейнер не обновляется, к `compose up` можно добавить флаги `--build --force-recreate`