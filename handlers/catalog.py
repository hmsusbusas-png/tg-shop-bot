"""Каталог: приветствие, категории, список игр, карточка товара."""
from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import db
from keyboards import (
    CategoryCB,
    ProductCB,
    catalog_button,
    categories_kb,
    format_price,
    product_kb,
    products_kb,
)

from .cart import add_item

router = Router(name="catalog")


async def safe_edit(cb: CallbackQuery, text: str, reply_markup=None) -> None:
    """edit_text, который не падает на повторном нажатии той же кнопки."""
    try:
        await cb.message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest:
        pass  # 'message is not modified' или сообщение уже недоступно

WELCOME = (
    "Привет, {name}! 👋\n\n"
    "Добро пожаловать в «Ход» — магазин настольных игр.\n"
    "У нас собраны классические стратегии, лёгкие семейные игры и шумные пати-хиты "
    "для любой компании.\n\n"
    "Жмите «Каталог», выбирайте игры и собирайте корзину — оформление займёт минуту."
)

HOME_TEXT = (
    "🎲 <b>Магазин настольных игр «Ход»</b>\n\n"
    "Стратегии для серьёзных партий, семейные хиты и игры, с которых начинается "
    "любой игровой вечер. Загляните в каталог!"
)

CATEGORIES_TITLE = "🗂 <b>Категории</b>\nВыберите, что ищете:"


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        WELCOME.format(name=message.from_user.first_name),
        reply_markup=catalog_button(),
    )


@router.callback_query(F.data == "start")
async def back_to_start(cb: CallbackQuery) -> None:
    await safe_edit(cb, HOME_TEXT, reply_markup=catalog_button())
    await cb.answer()


@router.callback_query(F.data == "catalog")
async def show_categories(cb: CallbackQuery) -> None:
    await safe_edit(cb, CATEGORIES_TITLE, reply_markup=categories_kb(db.get_categories()))
    await cb.answer()


@router.callback_query(CategoryCB.filter())
async def show_products(cb: CallbackQuery, callback_data: CategoryCB) -> None:
    products = db.get_products_by_category(callback_data.category_id)
    if not products:
        await cb.answer("В этой категории пока пусто", show_alert=True)
        return
    await safe_edit(
        cb,
        f"🎲 <b>{products[0]['category_title']}</b>\nВыберите игру:",
        reply_markup=products_kb(products),
    )
    await cb.answer()


@router.callback_query(ProductCB.filter(F.action == "view"))
async def show_product(cb: CallbackQuery, callback_data: ProductCB) -> None:
    product = db.get_product(callback_data.product_id)
    if not product:
        await cb.answer("Игра не найдена", show_alert=True)
        return
    text = (
        f"🎲 <b>{product['title']}</b>\n"
        f"<i>{product['category_title']}</i>\n\n"
        f"{product['description']}\n\n"
        f"💰 Цена: {format_price(product['price'])}"
    )
    await safe_edit(cb, text, reply_markup=product_kb(product["id"], product["category_id"]))
    await cb.answer()


@router.callback_query(ProductCB.filter(F.action == "add"))
async def add_to_cart(cb: CallbackQuery, callback_data: ProductCB) -> None:
    product = db.get_product(callback_data.product_id)
    if not product:
        await cb.answer("Игра не найдена", show_alert=True)
        return
    add_item(cb.from_user.id, product["id"])
    await cb.answer(f"«{product['title']}» — в корзине 🛒")
