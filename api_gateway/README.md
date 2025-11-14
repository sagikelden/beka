
Otets Platform — Документация по микросервисам
1. Auth Service
Описание:
Микросервис для аутентификации и управления пользователями. Использует JWT-токены для авторизации.
Эндпоинты:
/register (POST)
Регистрация нового пользователя.
Параметры: username, password
Ответ:
{
  "id": "user_id",
  "username": "example"
}
/login (POST)
Вход пользователя, возвращает JWT.
Параметры: username, password
Ответ:
{
  "access_token": "jwt_token",
  "token_type": "bearer"
}
/health/db (GET)
Проверка соединения с базой данных MongoDB.
Ответ:
{
  "status": "ok"
}
Переменные окружения:
Имя	Описание	Пример
MONGO_URI	Строка подключения к MongoDB Atlas	mongodb+srv://user:pass@cluster0.mongodb.net/dbname
DB_NAME	Название базы данных	otets_db
JWT_SECRET	Секрет для подписи JWT	random_secret_key

2. Media Service
(уже описан выше)

3. Gateway Service
Описание:
API-шлюз для объединения всех сервисов. Перенаправляет запросы на Auth, Media и другие сервисы.
Эндпоинты:
/auth/... → проксирует запросы на Auth Service
/media/... → проксирует запросы на Media Service
Переменные окружения:
Имя	Описание	Пример
AUTH_URL	URL Auth Service	http://auth:8000
MEDIA_URL	URL Media Service	http://media:8000

4. Live Service
Описание:
Сервис для работы с живым контентом, стримами или другими медиа-данными.
Эндпоинты:
/live/start — запуск трансляции
/live/stop — остановка трансляции
/live/status — проверка статуса
Переменные окружения:
Имя	Описание	Пример
LIVE_PORT	Порт для стриминга	9000

5. Запуск сервисов локально через Docker Compose
docker-compose up --build
Все сервисы запускаются в отдельных контейнерах
Auth подключается к MongoDB
Media хранит файлы в указанной директории
Gateway маршрутизирует запросы к нужному сервису

6. Структура проекта
otets_platform_scaffold/
├── auth_service/
│   ├── app/
│   ├── Dockerfile
│   └── requirements.txt
├── media_service/
│   ├── app/
│   ├── Dockerfile
│   └── requirements.txt
├── gateway_service/
│   ├── app/
│   ├── Dockerfile
│   └── requirements.txt
├── live_service/
│   ├── app/
│   ├── Dockerfile
│   └── requirements.txt
└── docker-compose.yml

