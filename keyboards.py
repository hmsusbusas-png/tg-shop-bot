"""Inline-клавиатуры и фабрики callback-данных."""
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class CategoryCB(CallbackData, prefix="cat"):
    category_id: int


class ProductCB(CallbackData, prefix="prd"):
    action: str  # view | add
    product_id: int
    category_id: int = 0


class CartCB(CallbackData, prefix="crt"):
    action: str  # inc | dec | remove | clear | checkout
    product_id: int = 0


class ConfirmCB(CallbackData, prefix="cfm"):
    action: str  # yes | no


def format_price(value: int) -> str:
    return f"{value:,}".replace(",", " ") + " ₽"


def catalog_button() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="🎲 Каталог", callback_data="catalog")]]
    )


def back_to_catalog_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="🎲 В каталог", callback_data="catalog")]]
    )


def categories_kb(categories) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for category in categories:
        builder.button(
            text=category["title"],
            callback_data=CategoryCB(category_id=category["id"]).pack(),
        )
    builder.button(text="🏠 Главное меню", callback_data="start")
    builder.adjust(2)
    return builder.as_markup()


def products_kb(products) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for product in products:
        builder.button(
            text=f"{product['title']} · {format_price(product['price'])}",
            callback_data=ProductCB(
                action="view", product_id=product["id"], category_id=product["category_id"]
            ).pack(),
        )
    builder.button(text="◀️ Категории", callback_data="catalog")
    builder.button(text="🏠 Главное меню", callback_data="start")
    builder.adjust(1)
    return builder.as_markup()


def product_kb(product_id: int, category_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🛒 В корзину",
        callback_data=ProductCB(action="add", product_id=product_id, category_id=category_id).pack(),
    )
    builder.button(text="🛍 Корзина", callback_data="cart")
    builder.button(text="◀️ Назад", callback_data=CategoryCB(category_id=category_id).pack())
    builder.adjust(1)
    return builder.as_markup()


def cart_kb(items) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for item in items:
        builder.button(text="➖", callback_data=CartCB(action="dec", product_id=item["id"]).pack())
        builder.button(text=str(item["qty"]), callback_data="noop")
        builder.button(text="➕", callback_data=CartCB(action="inc", product_id=item["id"]).pack())
        builder.button(text="🗑", callback_data=CartCB(action="remove", product_id=item["id"]).pack())
        builder.button(
            text=item["title"],
            callback_data=ProductCB(
                action="view", product_id=item["id"], category_id=item["category_id"]
            ).pack(),
        )
    if items:
        builder.button(text="✅ Оформить заказ", callback_data=CartCB(action="checkout").pack())
        builder.button(text="🧹 Очистить", callback_data=CartCB(action="clear").pack())
    builder.button(text="◀️ В каталог", callback_data="catalog")
    builder.adjust(5, 2, 1)
    return builder.as_markup()


def confirm_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить", callback_data=ConfirmCB(action="yes").pack())
    builder.button(text="❌ Отменить", callback_data=ConfirmCB(action="no").pack())
    builder.adjust(2)
    return builder.as_markup()
