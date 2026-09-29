# Ход — Telegram-бот магазина настольных игр

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB) ![aiogram](https://img.shields.io/badge/aiogram-3.x-2CA5E0) ![SQLite](https://img.shields.io/badge/SQLite-stdlib-003B57)

«Ход» — Telegram-бот магазина настольных игр: покупатель листает каталог, собирает корзину и оформляет заказ пошаговой формой. Заказы хранятся в локальной базе SQLite, корзина и состояние формы живут в памяти. Внешних сервисов нет, запускается одной командой.

## Возможности

- каталог из 4 категорий и 12 реальных настолок с осмысленными описаниями и ценами
- корзина с изменением количества кнопками +/− — сумма пересчитывается на месте, без перезапросов; позиции можно убирать, корзину очищать целиком
- оформление заказа FSM-формой: имя → телефон (с валидацией) → адрес/комментарий → подтверждение
- история заказов: `/orders` показывает последние 10 заказов пользователя с составом и суммами
- админ-статистика `/stats`: число заказов, выручка и топ-5 игр (для заданного `ADMIN_ID`)
- база `shop.db` создаётся и наполняется товарами автоматически при первом запуске
- без `BOT_TOKEN` бот печатает понятную подсказку по настройке и завершает работу

## Быстрый старт

1. Создайте бота у [@BotFather](https://t.me/BotFather) и скопируйте токен.
2. Склонируйте репозиторий и установите зависимости (Python 3.10+, проверено на 3.14):

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Задайте токен в переменную окружения:

   ```bash
   # PowerShell
   $env:BOT_TOKEN = "123456789:AAF..."

   # Linux / macOS
   export BOT_TOKEN="123456789:AAF..."
   ```

4. Запустите бота:

   ```bash
   python bot.py
   ```

При первом запуске создаётся и наполняется база `shop.db`. Без токена бот выведет подсказку по настройке и завершится.

### Переменные окружения

| Переменная  | Нужна | Описание                                            |
|-------------|-------|-----------------------------------------------------|
| `BOT_TOKEN` | да    | токен от @BotFather                                 |
| `DB_PATH`   | нет   | путь к файлу SQLite (по умолчанию `shop.db`)        |
| `ADMIN_ID`  | нет   | ваш числовой Telegram id — включает `/stats`        |

## Проверка

Офлайн-смоук-тест (токен не нужен): импорты, инициализация и наполнение базы, сценарий заказа, сборка диспетчера.

```bash
python scripts/smoke_test.py
```

## Честно об ограничениях

- корзина и FSM-форма живут в памяти (`dict` + `MemoryStorage` aiogram) и сбрасываются при перезапуске бота; в базе остаются только оформленные заказы
- `/orders` показывает последние 10 заказов пользователя
- скриншотов в репозитории пока нет — запустите бота и посмотрите вживую

## Структура

```
tg-shop-bot/
├── bot.py               # входная точка: проверка токена, Dispatcher, polling
├── config.py            # конфиг из переменных окружения (BOT_TOKEN, DB_PATH, ADMIN_ID)
├── db.py                # схема SQLite, сид-данные, хелперы запросов
├── keyboards.py         # inline-клавиатуры и фабрики callback-data
├── handlers/
│   ├── __init__.py       # сборка роутеров
│   ├── catalog.py       # /start, категории, карточки товаров
│   ├── cart.py          # корзина: просмотр, количество ±, удаление, очистка
│   └── checkout.py      # FSM-оформление, /orders, /stats, /cancel
├── scripts/
│   └── smoke_test.py    # офлайн-тест: импорты, база, диспетчер
├── requirements.txt
└── README.md
```

## Стек

Python 3.10+, aiogram 3.x (FSM на MemoryStorage, inline-клавиатуры, callback-data), SQLite через stdlib `sqlite3` без ORM.

---

## EN

Khod is a Telegram shop bot for a board game store: customers browse a catalog of 12 games, build a cart and place an order through an FSM checkout form. Orders live in a local SQLite database; the cart and form state are in-memory. Set `BOT_TOKEN` and run `python bot.py`. Python 3.10+, aiogram 3.x — details in the Russian section above.
