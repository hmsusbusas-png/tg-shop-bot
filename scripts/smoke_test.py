"""Offline smoke test: imports, db init/seed, order flow, dispatcher assembly."""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import bot  # noqa: F401
import db
import keyboards
from handlers import cart, catalog, checkout


def main() -> None:
    products_total = 0
    with tempfile.TemporaryDirectory() as tmp:
        db.init_db(os.path.join(tmp, "test.db"))

        categories = db.get_categories()
        assert len(categories) == 4, f"expected 4 categories, got {len(categories)}"

        products = []
        for category in categories:
            products.extend(db.get_products_by_category(category["id"]))
        products_total = len(products)
        assert 8 <= products_total <= 12, f"unexpected product count: {products_total}"
        assert all(p["description"] and p["price"] > 0 for p in products)

        first = products[0]
        cart.add_item(1, first["id"], 2)
        items = cart.get_items(1)
        assert items and items[0]["qty"] == 2

        order_id = db.create_order(
            user_id=1,
            username="tester",
            customer_name="Тест Тестов",
            phone="+7 900 000-00-00",
            address="Москва, Тверская 1",
            comment="",
            items=items,
        )
        orders = db.get_user_orders(1)
        assert orders and orders[0]["id"] == order_id
        assert db.get_order_items(order_id)[0]["qty"] == 2
        assert db.get_stats()["orders"] == 1

        db.close()

    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(catalog.router, cart.router, checkout.router)
    assert len(dp.sub_routers) == 3, "routers not registered"

    assert keyboards.price_str(2490) == "2 490 ₽"
    print(f"OK: imports, db init, seed ({products_total} products), order flow, dispatcher assembled")


if __name__ == "__main__":
    main()
