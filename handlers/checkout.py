"""Оформление заказа (FSM), история заказов и админ-статистика."""
import html
import re

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

import config
import db
from keyboards import CartCB, ConfirmCB, back_to_catalog_kb, confirm_kb, format_price

from .cart import cart_total, clear_cart, get_items

router = Router(name="checkout")

PHONE_RE = re.compile(r"^\+?\d[\d\s\-()]{6,18}$")
STATUS_LABELS = {"new": "новый", "done": "выполнен", "cancelled": "отменён"}


async def safe_edit(message: Message, text: str, reply_markup=None) -> None:
    """edit_text, который переживает повторные нажатия и 'message is not modified'."""
    try:
        await message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest:
        # сообщение не изменилось или уже недоступно — просто отвечаем заново
        try:
            await message.answer(text, reply_markup=reply_markup)
        except TelegramBadRequest:
            pass


class CheckoutStates(StatesGroup):
    name = State()
    phone = State()
    address = State()
    confirm = State()


@router.callback_query(CartCB.filter(F.action == "checkout"))
async def start_checkout(cb: CallbackQuery, state: FSMContext) -> None:
    if not get_items(cb.from_user.id):
        await cb.answer("Корзина пуста — сначала добавьте игры 🎲", show_alert=True)
        return
    await state.set_state(CheckoutStates.name)
    await cb.message.answer(
        "📝 <b>Оформление заказа</b>\n\n"
        "Как вас зовут? Укажите имя получателя.\n\n"
        "/cancel — отменить оформление"
    )
    await cb.answer()


@router.message(CheckoutStates.name, F.text)
async def process_name(message: Message, state: FSMContext) -> None:
    name = message.text.strip()
    if not 2 <= len(name) <= 64:
        await message.answer("Имя должно быть от 2 до 64 символов. Попробуйте ещё раз:")
        return
    await state.update_data(name=name)
    await state.set_state(CheckoutStates.phone)
    await message.answer("📞 Введите телефон для связи (например, +7 900 123-45-67):")


@router.message(CheckoutStates.phone, F.text)
async def process_phone(message: Message, state: FSMContext) -> None:
    phone = message.text.strip()
    if not PHONE_RE.fullmatch(phone):
        await message.answer(
            "Не похоже на телефон. Введите номер в формате +7 900 123-45-67:"
        )
        return
    await state.update_data(phone=phone)
    await state.set_state(CheckoutStates.address)
    await message.answer(
        "📍 Введите адрес доставки или пункт выдачи.\n"
        "Можно сразу добавить комментарий для курьера:"
    )


@router.message(CheckoutStates.address, F.text)
async def process_address(message: Message, state: FSMContext) -> None:
    address = message.text.strip()
    if len(address) < 5:
        await message.answer("Адрес слишком короткий. Уточните его:")
        return
    await state.update_data(address=address)
    data = await state.get_data()
    items = get_items(message.from_user.id)
    await state.set_state(CheckoutStates.confirm)
    await message.answer(order_summary(data, items), reply_markup=confirm_kb())


@router.message(StateFilter(CheckoutStates.name, CheckoutStates.phone, CheckoutStates.address))
async def fsm_needs_text(message: Message) -> None:
    """Фолбэк: в форме принимаем только текст (фото/стикеры/голос игнорируем понятно)."""
    await message.answer(
        "Пожалуйста, отправьте ответ обычным текстовым сообщением ✍️\n"
        "(фото, стикеры и голосовые на этом шаге не подходят)."
    )


@router.callback_query(CheckoutStates.confirm, ConfirmCB.filter(F.action == "yes"))
async def confirm_order(cb: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    items = get_items(cb.from_user.id)
    if not items or not data.get("name"):
        await state.clear()
        await safe_edit(
            cb.message,
            "Корзина опустела — заказать не получилось. Соберите её заново 🎲",
            back_to_catalog_kb(),
        )
        await cb.answer()
        return
    name, phone = data["name"], data["phone"]
    order_id = db.create_order(
        user_id=cb.from_user.id,
        username=cb.from_user.username or "",
        customer_name=name,
        phone=phone,
        address=data["address"],
        comment="",
        items=items,
    )
    clear_cart(cb.from_user.id)
    await state.clear()
    await safe_edit(
        cb.message,
        f"✅ <b>Заказ №{order_id} принят!</b>\n\n"
        f"{html.escape(name)}, мы позвоним на {html.escape(phone)} и согласуем доставку.\n"
        "Хорошей игры! 🎲",
        back_to_catalog_kb(),
    )
    await cb.answer()


@router.callback_query(CheckoutStates.confirm, ConfirmCB.filter(F.action == "no"))
async def cancel_order(cb: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await safe_edit(
        cb.message,
        "Оформление отменено. Корзина сохранена — можно вернуться к ней в любой момент.",
        back_to_catalog_kb(),
    )
    await cb.answer()


@router.callback_query(ConfirmCB.filter())
async def stale_confirm(cb: CallbackQuery) -> None:
    """Повторное нажатие Да/Нет после завершения оформления (state уже сброшен)."""
    await cb.answer("Это оформление уже завершено — начните заново из корзины 🛒",
                    show_alert=True)


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Оформление отменено. Введите /start, чтобы вернуться в магазин.")


@router.message(Command("orders"))
async def cmd_orders(message: Message) -> None:
    orders = db.get_user_orders(message.from_user.id)
    if not orders:
        await message.answer(
            "У вас пока нет заказов. Соберите корзину и оформите первый! 🛍"
        )
        return
    lines = ["📦 <b>Ваши заказы</b>", ""]
    for order in orders:
        items = db.get_order_items(order["id"])
        items_str = ", ".join(f"{item['product_title']} × {item['qty']}" for item in items)
        created = order["created_at"].replace("T", " ")
        status = STATUS_LABELS.get(order["status"], order["status"])
        lines.append(
            f"№{order['id']} · {created}\n{items_str}\n"
            f"💰 {format_price(order['total'])} · статус: {status}\n"
        )
    await message.answer("\n".join(lines))


@router.message(Command("stats"))
async def cmd_stats(message: Message) -> None:
    if not config.ADMIN_ID or message.from_user.id != config.ADMIN_ID:
        await message.answer("⛔ Команда доступна только администратору магазина.")
        return
    stats = db.get_stats()
    lines = [
        "📊 <b>Статистика магазина</b>",
        "",
        f"Заказов: {stats['orders']}",
        f"Выручка: {format_price(stats['revenue'])}",
    ]
    if stats["top"]:
        lines.append("")
        lines.append("🏆 Топ игр:")
        lines.extend(
            f"{number}. {row['product_title']} — {row['sold']} шт."
            for number, row in enumerate(stats["top"], 1)
        )
    await message.answer("\n".join(lines))


def order_summary(data: dict, items: list[dict]) -> str:
    lines = ["📋 <b>Проверьте заказ</b>", ""]
    for item in items:
        lines.append(
            f"• {html.escape(item['title'])} × {item['qty']} — {format_price(item['price'] * item['qty'])}"
        )
    lines.append(f"💰 Итого: {format_price(cart_total(items))}")
    lines.extend(
        [
            "",
            f"👤 Имя: {html.escape(data['name'])}",
            f"📞 Телефон: {html.escape(data['phone'])}",
            f"📍 Адрес: {html.escape(data['address'])}",
            "",
            "Всё верно?",
        ]
    )
    return "\n".join(lines)
