
# Документация проекта: `bachelor-2025-team-make-it-simple`

> Этот репозиторий содержит код и инфраструктуру для проекта по предмету "Системы искусственного интеллекта", по теме "Формирование персональной траектории обучения".  
> Всё работает через Docker + GitHub Actions + Prometheus/Grafana для мониторинга.

---

## 1. Запуск локального (dev) окружения

### Предварительные требования

Убедитесь, что у вас установлено:

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (или Docker Engine + Compose на Linux)
- Git
- (Опционально) VS Code или другой редактор

---

### Запуск через Docker Compose

```bash
# Клонируйте репозиторий
git clone https://github.com/ваш-юзернейм/bachelor-2025-team-make-it-simple.git
cd bachelor-2025-team-make-it-simple

# Запустите всё сразу
docker compose -f docker-compose.dev.yml up --build
```

> Если файл называется `docker-compose.dev.yml` — используйте именно его.  
> Если нет — замените на `docker-compose.yml`.

---

### Что запускается?

- **Ollama** → `http://localhost:11434` — API для работы с LLM.
- **Prometheus** → `http://localhost:9090` — сбор метрик.
- **Grafana** → `http://localhost:3000` — визуализация метрик (логин: `admin`, пароль: `grafana`).

---

### Как работать с кодом

- Изменения в `lab1.py`, `src/`, `tests/` автоматически применяются при перезапуске контейнера.
- Для быстрой пересборки:
  ```bash
  docker compose -f docker-compose.dev.yml down && docker compose -f docker-compose.dev.yml up --build
  ```
- Чтобы войти в контейнер:
  ```bash
  docker exec -it <имя_контейнера> bash
  ```

---

## 2. Troubleshooting Guide (Что делать, если что-то не работает)

### Проблема: `Port 9090 is already in use`

**Решение:**

```bash
# Найти процесс, занимающий порт
lsof -i :9090

# Убить процесс (например, PID=1234)
kill -9 1234

# Или просто остановить все контейнеры
docker compose -f docker-compose.dev.yml down
```

---

### Проблема: `npm ci` падает с ошибкой

**Возможные причины:**

- Нет файла `package-lock.json`
- Неверная версия Node.js

**Решение:**

```bash
# Убедитесь, что у вас правильная версия Node.js
node -v  # должна быть 18.x, 20.x или 22.x

# Пересоздайте lock-файл
rm -rf node_modules package-lock.json
npm install
```

---

### Проблема: Grafana не видит Prometheus

**Проверьте:**

1. Открыт ли `http://localhost:9090`.
2. Правильно ли настроен источник данных в Grafana.
3. В `./grafana/datasources.yml` должен быть URL `http://prometheus:9090` (имя сервиса, а не `localhost`).

---

### Проблема: Ollama не запускается или не отвечает

**Решение:**

- Убедитесь, что папка `.ollama_data` создана и доступна.
- Попробуйте запустить Ollama вручную и проверить логи:
  ```bash
  docker logs ollama
  ```
- Если используется GPU, раскомментируйте секцию `deploy` в `docker-compose.yml`.

---

### Проблема: GitHub Actions падает

**Проверьте:**

- Синтаксис YAML в `.github/workflows/`.
- Установлены ли нужные версии Node.js в workflow.
- Правильно ли указаны команды `npm install`, `npm test`.

---

## 3. Архитектура инфраструктуры

> *На основе предоставленного изображения.*

Система состоит из следующих компонентов:

- **Frontend (React/Vue)** — веб-интерфейс для взаимодействия с пользователем.
- **Backend (Node.js/Python)** — API-сервер, обрабатывает запросы, взаимодействует с LLM.
- **Ollama** — локальный движок для запуска LLM.
- **Langfuse** — для трассировки, логирования и оценки вызовов LLM.
- **Prometheus** — сбор метрик производительности и состояния сервисов.
- **Grafana** — визуализация метрик из Prometheus.
- **Docker Compose** — orchestrator для запуска всех сервисов локально.
- **GitHub Actions** — CI/CD для автоматизации сборки, тестирования и деплоя.

---

## 4. Cheat Sheet для команды

### Docker Compose

| Команда | Описание |
|--------|----------|
| `docker compose up` | Запустить все сервисы |
| `docker compose up --build` | Пересобрать и запустить |
| `docker compose down` | Остановить и удалить контейнеры |
| `docker compose logs <service>` | Посмотреть логи сервиса |

### Git

| Команда | Описание |
|--------|----------|
| `git checkout -b feat/название-фичи` | Создать новую ветку |
| `git add . && git commit -m "feat: add new feature"` | Закоммитить изменения |
| `git push origin feat/название-фичи` | Запушить ветку на GitHub |
| `git fetch && git rebase origin/main` | Обновить ветку с `main` |

### Типы коммитов

| Тип | Описание |
|-----|----------|
| `feat` | Новая фича |
| `fix` | Исправление бага |
| `docs` | Изменения в документации |
| `style` | Форматирование, стили |
| `refactor` | Рефакторинг |
| `test` | Изменения в тестах |
| `chore` | Прочие изменения |

### Ссылки

| Сервис | URL |
|--------|-----|
| Ollama API | `http://localhost:11434` |
| Prometheus | `http://localhost:9090` |
| Grafana | `http://localhost:3000` (admin/grafana) |
| Langfuse | `http://localhost:3001` (если используется) |

### GitHub Actions

- `.github/workflows/` — папка с workflow-файлами.
- Пример workflow для Node.js:
  ```yaml
  name: Node.js CI
  on: [push]
  jobs:
    build:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - name: Use Node.js
          uses: actions/setup-node@v4
          with:
            node-version: '20.x'
        - run: npm ci
        - run: npm run build --if-present
        - run: npm test
  ```
