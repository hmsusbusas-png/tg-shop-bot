"""SQLite-хранилище: схема, сид-данные и функции-запросы."""
import sqlite3
from datetime import datetime
from typing import Any

from config import DB_PATH

_conn: sqlite3.Connection | None = None

_SCHEMA = """
CREATE TABLE IF NOT EXISTS categories (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS products (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    title       TEXT NOT NULL,
    description TEXT NOT NULL,
    price       INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL,
    username      TEXT NOT NULL DEFAULT '',
    customer_name TEXT NOT NULL,
    phone         TEXT NOT NULL,
    address       TEXT NOT NULL,
    comment       TEXT NOT NULL DEFAULT '',
    total         INTEGER NOT NULL,
    status        TEXT NOT NULL DEFAULT 'new',
    created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS order_items (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id      INTEGER NOT NULL REFERENCES orders(id),
    product_id    INTEGER NOT NULL,
    product_title TEXT NOT NULL,
    price         INTEGER NOT NULL,
    qty           INTEGER NOT NULL
);
"""

SEED_CATEGORIES = ["Семейные", "Стратегии", "Пати-геймы", "Детские"]

SEED_PRODUCTS: dict[str, list[tuple[str, str, int]]] = {
    "Семейные": [
        ("Каркассон",
         "Выкладывайте плитки, прокладывайте дороги и возводите города средневековой Франции. "
         "Простые правила и приятная тактика — идеальная первая семейная стратегия.", 2490),
        ("Диксит",
         "Опишите свою карту так, чтобы угадали только те, кому нужно. "
         "Сюрреалистичные иллюстрации делают каждую партию маленьким приключением.", 3290),
        ("Имаджинариум",
         "Придумывайте ассоциации к странным картинкам и пытайтесь понять ход мысли друзей. "
         "Тёплая атмосферная игра для семейных вечеров.", 2190),
    ],
    "Стратегии": [
        ("Зельеварение",
         "Собирайте ингредиенты и варите эликсиры, обгоняя соперников по славе в гильдии алхимиков. "
         "Карточная стратегия, в которой партии никогда не повторяются.", 3690),
        ("Манчкин",
         "Вали монстров, подставляй друзей и первым доберись до десятого уровня. "
         "Злая и очень весёлая пародия на классические ролевые игры.", 1990),
        ("Колонизаторы",
         "Добывайте ресурсы, стройте дороги и города и торгуйтесь с соперниками. "
         "Легендарная стратегия, с которой у многих начинается любовь к настолкам.", 4290),
    ],
    "Пати-геймы": [
        ("Кодовые имена",
         "Одно меткое слово — и команда угадывает ваши карты, не попав на чужие. "
         "Лучший словесный детектив для двух компаний от двух до восьми человек.", 1790),
        ("Свинтус",
         "Карточная гонка на вылет, где правила меняются на ходу, а штрафные задания заставляют хрюкать. "
         "Гарантированный смех на любой вечеринке.", 990),
        ("Экивоки",
         "Объясняйте слова жестами, рисунком или парой слов, пока не истекло время. "
         "Энергичный хит для больших компаний, который затягивает с первой партии.", 1290),
        ("Уно",
         "Сбрасывайте карты, меняйте цвета и не забудьте крикнуть «Уно!». "
         "Самая известная карточная игра в мире — правила осваиваются за минуту.", 690),
    ],
    "Детские": [
        ("Барабашка",
         "Отвечайте на вопросы жестами, не издавая ни звука, и не перепутайте домового с призраком. "
         "Молниеносная игра на внимание и реакцию.", 1190),
        ("Дженга",
         "Вытаскивайте бруски из деревянной башни и не дайте ей рухнуть. "
         "Просто, напряжённо и весело — подходит и детям, и взрослым.", 1490),
    ],
}


def init_db(path: str = DB_PATH) -> None:
    """Открывает соединение, создаёт схему и наполняет каталог при первом запуске."""
    global _conn
    _conn = sqlite3.connect(path)
    _conn.row_factory = sqlite3.Row
    _conn.executescript(_SCHEMA)
    _seed()
    _conn.commit()


def close() -> None:
    global _conn
    if _conn is not None:
        _conn.close()
        _conn = None


def _seed() -> None:
    if _conn.execute("SELECT 1 FROM products LIMIT 1").fetchone():
        return
    for title in SEED_CATEGORIES:
        category_id = _conn.execute(
            "INSERT INTO categories (title) VALUES (?)", (title,)
        ).lastrowid
        for product_title, description, price in SEED_PRODUCTS[title]:
            _conn.execute(
                "INSERT INTO products (category_id, title, description, price) VALUES (?, ?, ?, ?)",
                (category_id, product_title, description, price),
            )
    _conn.commit()


def get_categories() -> list[sqlite3.Row]:
    return _conn.execute("SELECT * FROM categories ORDER BY id").fetchall()


def get_products_by_category(category_id: int) -> list[sqlite3.Row]:
    return _conn.execute(
        "SELECT p.*, c.title AS category_title "
        "FROM products p JOIN categories c ON c.id = p.category_id "
        "WHERE p.category_id = ? ORDER BY p.id",
        (category_id,),
    ).fetchall()


def get_product(product_id: int) -> sqlite3.Row | None:
    return _conn.execute(
        "SELECT p.*, c.title AS category_title "
        "FROM products p JOIN categories c ON c.id = p.category_id "
        "WHERE p.id = ?",
        (product_id,),
    ).fetchone()


def create_order(
    user_id: int,
    username: str,
    customer_name: str,
    phone: str,
    address: str,
    comment: str,
    items: list[dict[str, Any]],
) -> int:
    """Сохраняет заказ вместе с позициями одной транзакцией, возвращает номер заказа."""
    total = sum(item["price"] * item["qty"] for item in items)
    created_at = datetime.now().isoformat(timespec="seconds")
    order_id = _conn.execute(
        "INSERT INTO orders (user_id, username, customer_name, phone, address, comment, total, status, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, 'new', ?)",
        (user_id, username, customer_name, phone, address, comment, total, created_at),
    ).lastrowid
    _conn.executemany(
        "INSERT INTO order_items (order_id, product_id, product_title, price, qty) VALUES (?, ?, ?, ?, ?)",
        [
            (order_id, item["id"], item["title"], item["price"], item["qty"])
            for item in items
        ],
    )
    _conn.commit()
    return order_id


def get_user_orders(user_id: int, limit: int = 10) -> list[sqlite3.Row]:
    return _conn.execute(
        "SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC LIMIT ?",
        (user_id, limit),
    ).fetchall()


def get_order_items(order_id: int) -> list[sqlite3.Row]:
    return _conn.execute(
        "SELECT * FROM order_items WHERE order_id = ? ORDER BY id", (order_id,)
    ).fetchall()


def get_stats() -> dict[str, Any]:
    totals = _conn.execute(
        "SELECT COUNT(*) AS orders, COALESCE(SUM(total), 0) AS revenue FROM orders"
    ).fetchone()
    top = _conn.execute(
        "SELECT product_title, SUM(qty) AS sold FROM order_items "
        "GROUP BY product_title ORDER BY sold DESC LIMIT 5"
    ).fetchall()
    return {"orders": totals["orders"], "revenue": totals["revenue"], "top": top}
