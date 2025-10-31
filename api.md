# Описание API

Все эндпоинты, описанные ниже, доступны по следующему базовому URL:

`http://localhost:8000/converter/v1`

## Эндпоинты

#### `GET /`
Получение корневого сообщения (проверка доступности сервиса).

**Пример запроса (cURL):**
```bash
curl -X GET "http://localhost:8000/converter/v1/"
```
**Успешный ответ `200 OK`:**
```json
{
  "message": "Welcome to the Currency Converter API!"
}
```

---

#### `GET /today`
Получение списка актуальных курсов валют на сегодня.

**Пример запроса (cURL):**
```bash
curl -X GET "http://localhost:8000/converter/v1/today"
```
**Успешный ответ `200 OK`:**
```json
{
  "date": "2025-10-27",
  "base": "USD",
  "rates": {
    "EUR": 0.95,
    "RUB": 93.50,
    "JPY": 150.40
  }
}
```

---
### Операции обмена

---

#### `POST /exchange_currency`
Создание новой сделки на обмен валюты.

**Пример запроса (cURL):**
```bash
curl -X POST "http://localhost:8000/converter/v1/exchange_currency" \
-H "Content-Type: application/json" \
-d '{
  "source_cur_amount": "100.00",
  "source_cur_abbreviation": "USD",
  "target_cur_abbreviation": "EUR"
}'
```

**Успешный ответ `200 OK`:**
```json
{
  "exchange_uuid": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "status": "pending",
  "source_currency": "USD",
  "target_currency": "EUR",
  "source_amount": "100.00",
  "target_amount_calculated": "95.00",
  "expires_at": "2025-10-27T12:05:00Z"
}
```

---

#### `PATCH /exchange_currency/{exchange_uuid}`
Подтверждение или отмена заявки на обмен.
Используйте `uuid`, полученный при создании заявки.

**Пример запроса на подтверждение (cURL):**
```bash
curl -X PATCH "http://localhost:8000/converter/v1/exchange_currency/a1b2c3d4-e5f6-7890-1234-567890abcdef?action=confirm"
```

**Успешный ответ `200 OK`:**
```json
{
  "exchange_uuid": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "status": "confirmed"
}
```

#### `GET /exchanges`
Получение агрегированных данных об обменах за указанный период.

**Пример запроса (cURL):**
```bash
curl -X 'GET' \
  'http://localhost:8000/converter/v1/exchanges?start_datetime=2025-10-31T08%3A00&end_datetime=2025-10-31T22%3A22&currency_code=VND' \
  -H 'accept: application/json'
 ```

**Успешный ответ `200 OK`:**
```json
[
  {
    "currency_code": "EUR",
    "total_received": "5430.50",
    "total_sent": "5800.00",
    "exchange_count": 42
  }
]
```

---

#### `GET /unfinished_exchanges`
Получение списка всех незавершенных (ожидающих подтверждения) обменов.

**Пример запроса (cURL):**
```bash
curl -X GET "http://localhost:8000/converter/v1/unfinished_exchanges"
```
**Успешный ответ `200 OK`:**
```json
[
  {
    "exchange_uuid": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
    "status": "pending",
    "source_currency": "USD",
    "target_currency": "EUR",
    "source_amount": "100.00"
  }
]
```
---