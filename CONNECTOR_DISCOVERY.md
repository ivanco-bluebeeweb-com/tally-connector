# Tally Connector — Discovery & API Specification

**Vendor:** Tally  
**Catalog URL:** https://tally.so  
**API Base URL:** `https://api.tally.so`  
**Authentication:** API Key (Bearer Token)

## Core Entities & Endpoints
формы (/forms), поля и блоки вопросов, ответы респондентов (/submissions), вебхуки (/webhooks)

## Verified Read Operation
- **Эндпоинт проверки:** `GET /forms`
- **Метод:** GET
- **Ожидаемый ответ:** HTTP 200 OK со структурой метаданных сущности.

## Rate Limits & Pagination
- Стандартная курсорная или offset/limit пагинация вендора.
- Обработка HTTP 429 Too Many Requests с экспоненциальным backoff.
- Защита от тайм-аутов: ограничение на сетевые запросы 15-30 секунд.
