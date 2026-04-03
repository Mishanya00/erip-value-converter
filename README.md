# National Bank of the Republic of Belarus value converter 

Сервис обмена валют по курсам Национального Банка Республики Беларусь.

Описание API находится в `api.md`

Для запуска приложения создайте `.env` файл в корне проекта с содержимым:
```dotenv
DB_USER=postgres
DB_PASS=postgres
DB_NAME=converter
DB_HOST_PORT=5432

APP_ENVIRONMENT=LOCAL

EXTERNAL_API_URL=https://api.nbrb.by

TIMEZONE=Europe/Minsk

NATIONAL_CURRENCY=BYN
```

Выполните следующую команду в терминале в корне проекта.
Она соберет образы и запустит все сервис конвертации и базу данных в фоновом режиме (`-d`).
```bash
docker compose up -d --build -d
```

Дополнительные комментарии:

 - Библиотека apscheduler для ежедневных запросов к API
 - Библиотека Babel для правильного округления денежных средств с точностью до минимальной
денежной единицы для каждой валюты
 - Библиотека tenacity для retry-механизма запросов внешнему API.
