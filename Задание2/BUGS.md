# BUGS.md - Найденные дефекты

## Баг-001 (Критическая)
**Краткое описание:** POST /api/1/item возвращает `{"status": "..."}` вместо объекта объявления

**Шаги воспроизведения:**
В Postman при проверке API вручную нужно в строку POST запроса ввести:
```json
POST https://qa-internship.avito.com/api/1/item
```
Затем открыть Body → raw → JSON и ввести: 
```json
{"sellerID": 500000, "name": "Test", "price": 100, "statistics": {"likes":1,"viewCount":1,"contacts":1}}
```

**Фактический результат:**
```json
{"status": "Сохранили объявление - 0af4ae69-e81e-45a6-ac77-33251688f9a6"}
```

**Ожидаемый результат** (Postman-коллекция):
```json
{"id": "...", "sellerId": 500000, "name": "Test", "price": 100, "statistics": {...}, "createdAt": "..."}
```

**Серьёзность:** Критическая, тк пользователи не могут получить данные объявления сразу после создания; UUID приходится извлекать парсингом строки

**Host:** https://qa-internship.avito.com

---

## Баг-002 (Высокая)
**Краткое описание:** POST /api/1/item отклоняет валидные значения price=0 и нулевую статистику с кодом 400

**Шаги воспроизведения:**
```json
POST https://qa-internship.avito.com/api/1/item
Body: {"sellerID": 500000, "name": "Free item", "price": 0, "statistics": {"likes":0,"viewCount":0,"contacts":0}}
```

**Фактический результат:** 
```json
HTTP 400
{
    "result": {
        "message": "поле price обязательно",
        "messages": {}
    },
    "status": "400"
}
```

**Ожидаемый результат:** HTTP 200 - нулевая цена и нулевая статистика являются допустимыми бизнес-значениями (бесплатное объявление без просмотров)

**Серьёзность:** Высокая, тк пользователь не может установить нулевую цену и получает ошибку

**Host:** https://qa-internship.avito.com

---

## Баг-003 (Низкая)
**Краткое описание:** POST /api/1/item отклоняет name длиной 255 символов, граница не задокументирована

**Шаги воспроизведения:**
```json
POST https://qa-internship.avito.com/api/1/item
{"sellerID": 500000, "name": "AAA...AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaAAAAAAAAAAAA (очень большое имя)", "price": 100, "statistics": {...}}
```

**Фактический результат:** 
```json
HTTP 400 Bad Request
{"result": {"message": "", "messages": {}},"status": "не передан объект - объявление"}
```

**Ожидаемый результат:** HTTP 200, либо явно задокументированное ограничение на длину name с соответствующим сообщением об ошибке

**Серьёзность:** Низкая

**Host:** https://qa-internship.avito.com

---

## Баг-004 (Критическая)
**Краткое описание:** Сервер периодически не отвечает в течение 10+ секунд (ReadTimeout)

**Шаги воспроизведения:**
1. POST `https://qa-internship.avito.com/api/1/item` с валидными данными, напимер:
```json
{
  "sellerID": 500123,
  "name": "Test item",
  "price": 1000,
  "statistics": {
    "likes": 5,
    "viewCount": 20,
    "contacts": 2
  }
}
```
2. Дождаться ответа

**Фактический результат:**
Запрос POST `/api/1/item` периодически не отвечает более 10 секунд, возникает ReadTimeout
```py
requests.exceptions.ReadTimeout:HTTPSConnectionPool(host='qa-internship.avito.com', port=443):Read timed out. (read timeout=10)
```

**Ожидаемый результат:** Ответ в течение 2000 мс

**Серьёзность:** Высокая - нефункциональный дефект производительности, сервис иногда работает нестабильно 

**Host:** https://qa-internship.avito.com

## Баг-005 (Средняя)
**Краткое описание:** API ответа POST /api/1/item не возвращает созданные данные объявления, из-за чего невозможно проверить соответствие данных при последующем GET.

**Шаги воспроизведения:**
1. Отправить запрос POST https://qa-internship.avito.com/api/1/item
```json
{
  "sellerID": 123456,
  "name": "Test item",
  "price": 1000,
  "statistics": {
    "likes": 1,
    "viewCount": 10,
    "contacts": 2
  }
} 
```
2. Получить ответ сервера

**Фактический результат^**
API возвращает только строку статуса:
```json
{"status": "Сохранили объявление - 0af4ae69-e81e-45a6-ac77-33251688f9a6"}
```

В ответе отсутствуют поля созданного объявления:
- name
- price
- sellerID
- statistics

**Ожидаемый результат:**
API должен возвращать данные созданного объекта.

Пример ожидаемого ответа:
```json
{
  "id": "0af4ae69-e81e-45a6-ac77-33251688f9a6",
  "sellerID": 123456,
  "name": "Test item",
  "price": 1000,
  "statistics": {
    "likes": 1,
    "viewCount": 10,
    "contacts": 2
  }
}
```
**Серьезность:** операция создания работает, но невозможно проверить корректность данных без дополнительного GET