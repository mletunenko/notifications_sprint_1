# Проектная работа 10 спринта

# Запуск приложения

## Docker-compose

1. Выполнить команды:
```bash
docker compose up -d
```

## Локальный запуск

1. Активировать venv и создать .env по образцу
2. Установить зависимости

```bash
pip install --upgrade pip && pip install -r requirements.txt
```
3. Используйте docker-compose.yml 

Так же поднятие контейнеров с сервисами для локальной работы доступны через 

```bash
dc up -d notifications_pg
```
(dc up --build notifications_pg)
4. Используйте Sentry 

login: mletunenko@gmail.com

pass: 8s.mf#2FRbVVRj7

5. Переменные окружения в конфиге по умолчанию для локального запуска.

6. Запуск приложения

```bash
python src/web_server.py 
```
7. Запуск воркера

```bash
python src/worker.py 
```

# Tests

## Локальный запуск

Запустить командой:

```bash
pytest .
```

## Связанные репозитории

Сервис выдачи контента
- https://github.com/mletunenko/Async_API_sprint_1_team

Сервис административной панели 
- https://github.com/mletunenko/new_admin_panel_sprint_3

Сервис авторизации
- https://github.com/mletunenko/Auth_sprint_1

Сервис аналитики пользовательских действий
- https://github.com/mletunenko/ugc_sprint_1

Сервис хранения пользовательского контента
- https://github.com/mletunenko/ugc_sprint_2

Сервис уведомлений (текущий репозиторий)
- https://github.com/mletunenko/notifications_sprint_1

Сервис профили (Дипломный проект)
- https://github.com/mletunenko/graduate_work