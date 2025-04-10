# Restaurant Reservation API

REST API сервис для управления бронированием столиков в ресторане. Проект построен с использованием FastAPI, PostgreSQL и Docker.

## Технологический стек

- Python 3.11
- FastAPI
- PostgreSQL
- SQLAlchemy (ORM)
- Alembic (миграции)
- Docker & Docker Compose
- pytest (тестирование)

## Функциональность

- Управление столиками (создание, просмотр, удаление)
- Управление бронированиями (создание, просмотр, удаление)
- Автоматическая проверка конфликтов бронирования
- Автоматические миграции базы данных при запуске
- Тестовое покрытие основного функционала

## Установка и запуск

### Предварительные требования

- Docker
- Docker Compose

### Запуск приложения

1. Клонируйте репозиторий:
```bash
git clone https://github.com/Wiquzix/tzreservation
cd tzreservation
```

2. Запустите приложение с помощью Docker Compose:
```bash
docker-compose up --build
```

API будет доступно по адресу: http://localhost:8000

## API Endpoints

### Столики

- `POST /tables/` - Создать новый столик
- `GET /tables/` - Получить список всех столиков
- `DELETE /tables/{table_id}` - Удалить столик

#### Пример создания столика:
```bash
curl -X POST "http://localhost:8000/tables/" \
     -H "Content-Type: application/json" \
     -d '{"name": "Table 1", "seats": 4, "location": "Main Hall"}'
```

### Бронирования

- `POST /reservations/` - Создать новое бронирование
- `GET /reservations/` - Получить список всех бронирований
- `DELETE /reservations/{reservation_id}` - Удалить бронирование

#### Пример создания бронирования:
```bash
curl -X POST "http://localhost:8000/reservations/" \
     -H "Content-Type: application/json" \
     -d '{
           "customer_name": "John Doe",
           "table_id": 1,
           "reservation_time": "2024-04-10T19:00:00",
           "duration_minutes": 120
         }'
```

## Документация API

После запуска приложения документация доступна по следующим адресам:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Разработка

### Структура проекта
```
.
├── app/
│   ├── core/           # Ядро приложения (БД, конфигурация)
│   ├── models/         # Модели SQLAlchemy
│   ├── schemas/        # Pydantic схемы
│   ├── services/       # Бизнес-логика
│   └── routers/        # Маршруты API
├── tests/              # Тесты
├── alembic/            # Миграции
├── docker-compose.yml  # Docker конфигурация
└── requirements.txt    # Зависимости Python
```

### Запуск тестов

```bash
docker-compose run web pytest
```