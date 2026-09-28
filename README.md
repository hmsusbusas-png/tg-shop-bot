# Khod — Telegram Shop Bot for Board Games

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB) ![aiogram](https://img.shields.io/badge/aiogram-3.x-2CA5E0) ![SQLite](https://img.shields.io/badge/SQLite-stdlib-003B57)

**Khod** («Ход») is a Telegram shop bot for a board game store. Customers browse a catalog of real games, build a cart, and place an order through a step-by-step form — everything is stored in a local SQLite database. No external services, one command to run.

## Features

- 🎲 **Catalog** — 4 categories (Family, Strategy, Party, Kids) and 12 real board games with meaningful descriptions and prices
- 🛒 **Cart** — add games, change quantity with `+/−`, remove items, clear the cart, live total
- 📝 **Checkout** — FSM-based form: name → phone (validated) → address/comment → confirmation
- 📦 **Order history** — `/orders` lists all orders of the current user with items and totals
- 📊 **Admin stats** — `/stats` shows order count, revenue and top-5 games (for the configured `ADMIN_ID`)
- 💾 **SQLite storage** — `shop.db` is created and seeded automatically on first run

## Quick Start

1. Create a bot with [@BotFather](https://t.me/BotFather) and copy the token.
2. Install dependencies (Python **3.10+**, tested on 3.14):

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Put the token into the `BOT_TOKEN` environment variable:

   ```bash
   # Windows (PowerShell)
   $env:BOT_TOKEN = "123456789:AAF..."

   # Linux / macOS
   export BOT_TOKEN="123456789:AAF..."
   ```

4. Run the bot:

   ```bash
   python bot.py
   ```

Without `BOT_TOKEN` the bot prints a clear setup hint and exits.

### Environment variables

| Variable   | Required | Description                                        |
|------------|----------|----------------------------------------------------|
| `BOT_TOKEN`| yes      | Token from @BotFather                              |
| `DB_PATH`  | no       | SQLite file path (default: `shop.db`)              |
| `ADMIN_ID` | no       | Your Telegram numeric id — enables `/stats`        |

## Project Structure

```
tg-shop-bot/
├── bot.py               # entrypoint: token check, Dispatcher, polling
├── config.py            # env-based configuration (BOT_TOKEN, DB_PATH, ADMIN_ID)
├── db.py                # SQLite schema, seed data, query helpers
├── keyboards.py         # inline keyboards and callback-data factories
├── handlers/
│   ├── catalog.py       # /start, categories, product cards
│   ├── cart.py          # cart view, quantity +/-, remove, clear
│   └── checkout.py      # FSM checkout, /orders, /stats, /cancel
├── scripts/
│   └── smoke_test.py    # offline test: imports, db init/seed, dispatcher
├── screenshots/         # bot screenshots (see below)
├── requirements.txt
└── README.md
```

## Screenshots

| Catalog | Product card | Cart |
|---|---|---|
| ![Catalog](screenshots/catalog.png) | ![Product](screenshots/product.png) | ![Cart](screenshots/cart.png) |

| Checkout | Orders | Stats |
|---|---|---|
| ![Checkout](screenshots/checkout.png) | ![Orders](screenshots/orders.png) | ![Stats](screenshots/stats.png) |

## Tech Stack

- Python 3.10+ (tested on 3.14)
- [aiogram 3.x](https://docs.aiogram.dev/) — FSM on `MemoryStorage`, inline keyboards, callback-data factories
- SQLite via stdlib `sqlite3` (no ORM)

## Testing

Offline smoke test (no token needed) — checks imports, database init/seed, order flow and dispatcher assembly:

```bash
python scripts/smoke_test.py
```

---

# Ход — Telegram-бот магазина настольных игр (RU)

Телеграм-бот магазина настольных игр «Ход»: каталог из 4 категорий и 12 реальных настолок, корзина с изменением количества, оформление заказа пошаговой формой (FSM), история заказов `/orders` и админ-статистика `/stats`. Заказы хранятся в SQLite — база `shop.db` создаётся и наполняется автоматически при первом запуске.

## Быстрый старт

1. Создайте бота у [@BotFather](https://t.me/BotFather) и скопируйте токен.
2. Установите зависимости (Python **3.10+**, проверено на 3.14):

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Задайте токен в переменную окружения и запустите:

   ```bash
   # PowerShell
   $env:BOT_TOKEN = "123456789:AAF..."
   python bot.py
   ```

Опционально: `ADMIN_ID` — ваш числовой Telegram id (включает `/stats`), `DB_PATH` — путь к файлу базы.

Без токена бот печатает понятную подсказку по настройке и завершает работу.
