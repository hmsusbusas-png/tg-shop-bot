"""Корзина: просмотр, изменение количества, удаление, очистка."""
from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery

import db
from keyboards import CartCB, cart_kb, price_str

router = Router(name="cart")

# user_id -> {product_id: qty}
_carts: dict[int, dict[int, int]] = {}

EMPTY_CART_TEXT = "🛍 <b>Корзина</b>\n\nПока пусто. Загляните в каталог — там много интересного!"


def add_item(user_id: int, product_id: int, qty: int = 1) -> None:
    items = _carts.setdefault(user_id, {})
    items[product_id] = items.get(product_id, 0) + qty


def change_qty(user_id: int, product_id: int, delta: int) -> None:
    items = _carts.get(user_id)
    if not items or product_id not in items:
        return
    items[product_id] += delta
    if items[product_id] <= 0:
        del items[product_id]


def remove_item(user_id: int, product_id: int) -> None:
    _carts.get(user_id, {}).pop(product_id, None)


def clear_cart(user_id: int) -> None:
    _carts.pop(user_id, None)


def get_items(user_id: int) -> list[dict]:
    items = []
    for product_id, qty in _carts.get(user_id, {}).items():
        product = db.get_product(product_id)
        if product:
            items.append({**dict(product), "qty": qty})
    return items


def total(items: list[dict]) -> int:
    return sum(item["price"] * item["qty"] for item in items)


def cart_text(items: list[dict]) -> str:
    lines = ["🛍 <b>Ваша корзина</b>", ""]
    for number, item in enumerate(items, 1):
        lines.append(
            f"{number}. {item['title']} — {item['qty']} × {price_str(item['price'])} "
            f"= {price_str(item['price'] * item['qty'])}"
        )
    lines.append("")
    lines.append(f"💰 Итого: {price_str(total(items))}")
    return "\n".join(lines)


async def _refresh(cb: CallbackQuery) -> None:
    items = get_items(cb.from_user.id)
    try:
        await cb.message.edit_text(
            cart_text(items) if items else EMPTY_CART_TEXT,
            reply_markup=cart_kb(items),
        )
    except TelegramBadRequest:
        pass


@router.callback_query(F.data == "cart")
async def show_cart(cb: CallbackQuery) -> None:
    await _refresh(cb)
    await cb.answer()


@router.callback_query(CartCB.filter(F.action == "inc"))
async def increase(cb: CallbackQuery, callback_data: CartCB) -> None:
    change_qty(cb.from_user.id, callback_data.product_id, 1)
    await _refresh(cb)
    await cb.answer()


@router.callback_query(CartCB.filter(F.action == "dec"))
async def decrease(cb: CallbackQuery, callback_data: CartCB) -> None:
    change_qty(cb.from_user.id, callback_data.product_id, -1)
    await _refresh(cb)
    await cb.answer()


@router.callback_query(CartCB.filter(F.action == "remove"))
async def remove(cb: CallbackQuery, callback_data: CartCB) -> None:
    remove_item(cb.from_user.id, callback_data.product_id)
    await _refresh(cb)
    await cb.answer("Удалено")


@router.callback_query(CartCB.filter(F.action == "clear"))
async def clear(cb: CallbackQuery) -> None:
    clear_cart(cb.from_user.id)
    await _refresh(cb)
    await cb.answer("Корзина очищена")


@router.callback_query(F.data == "noop")
async def noop(cb: CallbackQuery) -> None:
    await cb.answer()
