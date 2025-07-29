FastAPI-приложение, реализующее чат-интерфейс с памятью, векторным поиском по базе знаний и интеграцией с OpenAI GPT-4o.
Проект использует PostgreSQL с расширением pgvector для хранения эмбеддингов, Redis для хранения истории чатов, а также OpenAI API для генерации ответов и векторных представлений текста.

---

## Функциональные возможности

* Обработка входящих сообщений и генерация ответов с учетом истории
* Поиск релевантных знаний по эмбеддингам (векторный поиск)
* Хранение и очистка истории чатов в Redis
* Импорт знаний из CSV-файла
* Поддержка Docker и изолированного окружения

---

## Технологический стек

* Python 3.11+
* FastAPI
* PostgreSQL + pgvector
* Redis 7
* SQLAlchemy (async)
* Alembic
* OpenAI GPT-4o
* Docker / Docker Compose
* Poetry

---

## Установка и запуск

```bash
git clone https://github.com/kilebles/mastercert_api.git
cd mastercert_api
cp .env.example .env
docker-compose up --build
```


## Формат `.env`

```env
OPENAI_API_KEY=...
SYSTEM_PROMPT=...
POSTGRES_DB=...
POSTGRES_USER=...
POSTGRES_PASSWORD=...
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
REDIS_HOST=redis
REDIS_PORT=6379
```

---

## Эндпоинты

### `GET /`

Проверка доступности API.

**Ответ:**

```json
{
  "message": "API is running"
}
```

### `POST /ask`

Отправка вопроса и получение ответа от модели.

**Тело запроса:**

```json
{
  "message": "Как получить сертификат?",
  "chat_id": "user-123"
}
```

**Ответ:**

```json
{
  "response": "Чтобы получить сертификат, необходимо..."
}
```

### `POST /clear`

Очистка истории чата.

**Тело запроса:**

```json
{
  "chat_id": "user-123"
}
```

**Ответ:**

```json
{
  "status": "ok"
}
```

---

## Импорт базы знаний

Файл `data.csv` должен содержать столбцы: `question`, `answer`

```bash
docker-compose exec stroy_api poetry run python app/utils/import_csv.py
```

---

## Работа с миграциями

Создать миграцию:

```bash
docker-compose exec stroy_api alembic revision --autogenerate -m "init"
```

Применить миграции:

```bash
docker-compose exec stroy_api alembic upgrade head
```

---

## Структура проекта

```
.
├── docker-compose.yaml
├── Dockerfile
├── .env
├── data.csv
├── alembic/
│   └── versions/
├── app/
│   ├── main.py
│   ├── core/
│   ├── database/
│   ├── routers/
│   ├── services/
│   └── utils/
```
