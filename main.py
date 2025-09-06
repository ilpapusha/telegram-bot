import os
import asyncio
import logging
from typing import Dict, List, Tuple

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

# ------------------ Настройки и инициализация ------------------
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID_ENV = os.getenv("ADMIN_ID")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN отсутствует в .env")
if not ADMIN_ID_ENV:
    raise RuntimeError("ADMIN_ID отсутствует в .env")

ADMIN_ID = int(ADMIN_ID_ENV)

logging.basicConfig(level=logging.INFO)
bot = Bot(BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

# ------------------ Хранилище состояний (простое, в памяти) ------------------
# Корзина: user_id -> список позиций [(perfume, volume_ml)]
carts: Dict[int, List[Tuple[str, int]]] = {}
# Ввод названия аромата для роспива
waiting_for_perfume: Dict[int, bool] = {}
# Последний введённый аромат (перед выбором объёма): user_id -> perfume
current_perfume: Dict[int, str] = {}
# Ожидание сообщения по «целому флакону»: user_id -> bool
waiting_for_full_bottle: Dict[int, bool] = {}

# ------------------ Вспомогательные клавиатуры ------------------
def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💉 Купить на роспив", callback_data="buy_split")],
        [InlineKeyboardButton(text="💎 Купить целый флакон", callback_data="buy_full")],
        [InlineKeyboardButton(text="🛒 Моя корзина", callback_data="show_cart")]
    ])

def volumes_kb() -> InlineKeyboardMarkup:
    # Объёмы для роспива с нужными эмодзи
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💧 5 мл",  callback_data="volume_5"),
            InlineKeyboardButton(text="🧪 8 мл",  callback_data="volume_8"),
            InlineKeyboardButton(text="💎 18 мл", callback_data="volume_18"),
        ]
    ])

def after_add_item_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить ещё аромат", callback_data="add_more")],
        [InlineKeyboardButton(text="🛒 Моя корзина",          callback_data="show_cart")],
        [InlineKeyboardButton(text="✅ Оформить заказ",       callback_data="checkout")],
        [InlineKeyboardButton(text="⬅️ В меню",               callback_data="back_to_menu")],
    ])

def cart_actions_kb(has_items: bool) -> InlineKeyboardMarkup:
    rows = []
    if has_items:
        rows.append([InlineKeyboardButton(text="✅ Оформить заказ", callback_data="checkout")])
        rows.append([InlineKeyboardButton(text="🧹 Очистить корзину", callback_data="clear_cart")])
    rows.append([InlineKeyboardButton(text="➕ Добавить ещё аромат", callback_data="add_more")])
    rows.append([InlineKeyboardButton(text="⬅️ В меню", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

# ------------------ Хэндлеры ------------------
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    # Сбросим возможные ожидания
    waiting_for_perfume[message.from_user.id] = False
    waiting_for_full_bottle[message.from_user.id] = False
    await message.answer(
        "Добро пожаловать в парфюмерный бот!\nВыберите вариант покупки:",
        reply_markup=main_menu_kb()
    )

# ----------- РОСПИВ: старт -----------
@dp.callback_query(F.data == "buy_split")
async def buy_split(call: types.CallbackQuery):
    uid = call.from_user.id
    # При новом заходе на роспив начинаем свежую корзину, если её не было
    carts.setdefault(uid, [])
    waiting_for_perfume[uid] = True
    waiting_for_full_bottle[uid] = False
    await call.message.edit_text(
        "🧴 Вы выбрали покупку на роспив.\n\n"
        "✍️ <b>Напишите название аромата</b>, который хотите добавить в корзину.\n"
        "После этого я предложу выбрать объём.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛒 Моя корзина", callback_data="show_cart")],
            [InlineKeyboardButton(text="⬅️ В меню", callback_data="back_to_menu")]
        ])
    )

# Когда пользователь вводит название аромата (режим ожидания включён)
@dp.message(F.text)
async def on_text(message: types.Message):
    uid = message.from_user.id

    # Сообщение по «целому флакону»
    if waiting_for_full_bottle.get(uid):
        username = message.from_user.username
        profile_link = f"https://t.me/{username}" if username else f"tg://user?id={uid}"

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💬 Написать клиенту", url=profile_link)]
        ])

        await bot.send_message(
            ADMIN_ID,
            "📩 <b>Новый запрос на целый флакон</b>\n\n"
            f"👤 Пользователь: @{username or 'без_username'}\n"
            f"🆔 ID: <code>{uid}</code>\n"
            f"✍️ Сообщение: {message.html_text}",
            reply_markup=kb
        )
        waiting_for_full_bottle[uid] = False
        await message.answer(
            "✅ Спасибо! Запрос отправлен продавцу.\n"
            "ℹ️ Продавец уточнит <b>актуальную цену</b> выбранного аромата и свяжется с вами."
        )
        return

    # Сообщение — это ввод аромата для роспива
    if waiting_for_perfume.get(uid):
        perfume = message.text.strip()
        if not perfume:
            await message.answer("Пожалуйста, введите название аромата текстом.")
            return

        current_perfume[uid] = perfume
        waiting_for_perfume[uid] = False
        await message.answer(
            f"Вы выбрали аромат: <b>{types.utils.html.quote_html(perfume)}</b>\n\n"
            "Теперь выберите объём 👇",
            reply_markup=volumes_kb()
        )
        return

    # Если пользователь пишет что-то вне контекста — предложим меню
    await message.answer("Выберите действие в меню:", reply_markup=main_menu_kb())

# Выбор объёма (добавление позиции в корзину)
@dp.callback_query(F.data.startswith("volume_"))
async def choose_volume(call: types.CallbackQuery):
    uid = call.from_user.id
    perfume = current_perfume.get(uid)
    if not perfume:
        await call.answer("Сначала введите название аромата.", show_alert=True)
        return

    volume_map = {"volume_5": 5, "volume_8": 8, "volume_18": 18}
    volume = volume_map.get(call.data, 0)
    if not volume:
        await call.answer("Неизвестный объём", show_alert=True)
        return

    carts.setdefault(uid, []).append((perfume, volume))
    # Сброс текущего аромата — чтобы следующий ввод был новым
    current_perfume[uid] = ""

    await call.message.edit_text(
        f"✅ В корзину добавлено: <b>{types.utils.html.quote_html(perfume)}</b> — <b>{volume} мл</b>.\n\n"
        "Что дальше?",
        reply_markup=after_add_item_kb()
    )

@dp.callback_query(F.data == "add_more")
async def add_more(call: types.CallbackQuery):
    uid = call.from_user.id
    waiting_for_perfume[uid] = True
    await call.message.edit_text(
        "✍️ Напишите название <b>следующего</b> аромата для роспива.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛒 Моя корзина", callback_data="show_cart")],
            [InlineKeyboardButton(text="⬅️ В меню", callback_data="back_to_menu")]
        ])
    )

@dp.callback_query(F.data == "show_cart")
async def show_cart(call: types.CallbackQuery):
    uid = call.from_user.id
    cart = carts.get(uid, [])
    if not cart:
        await call.message.edit_text(
            "🛒 Ваша корзина пуста.",
            reply_markup=cart_actions_kb(False)
        )
        return

    lines = [f"• {types.utils.html.quote_html(p)} — <b>{v} мл</b>" for p, v in cart]
    text = "🛒 <b>Ваша корзина</b>:\n\n" + "\n".join(lines)
    await call.message.edit_text(text, reply_markup=cart_actions_kb(True))

@dp.callback_query(F.data == "clear_cart")
async def clear_cart(call: types.CallbackQuery):
    uid = call.from_user.id
    carts[uid] = []
    await call.message.edit_text(
        "🧹 Корзина очищена.",
        reply_markup=cart_actions_kb(False)
    )

@dp.callback_query(F.data == "checkout")
async def checkout(call: types.CallbackQuery):
    uid = call.from_user.id
    cart = carts.get(uid, [])
    if not cart:
        await call.answer("Корзина пуста.", show_alert=True)
        return

    # Сформируем текст корзины
    lines = [f"• {types.utils.html.quote_html(p)} — {v} мл" for p, v in cart]
    cart_text = "\n".join(lines)

    # Сообщение пользователю
    await call.message.edit_text(
        "✅ Заказ сформирован и отправлен продавцу.\n"
        "ℹ️ Продавец уточнит <b>актуальную цену</b> по каждому аромату и свяжется с вами.\n\n"
        "<b>Состав заказа:</b>\n" + cart_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ В меню", callback_data="back_to_menu")]
        ])
    )

    # Сообщение админу с кнопкой «Написать клиенту»
    username = call.from_user.username
    profile_link = f"https://t.me/{username}" if username else f"tg://user?id={uid}"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Написать клиенту", url=profile_link)]
    ])

    await bot.send_message(
        ADMIN_ID,
        "📩 <b>Новый заказ (роспив)</b>\n\n"
        f"👤 Пользователь: @{username or 'без_username'}\n"
        f"🆔 ID: <code>{uid}</code>\n\n"
        f"{cart_text}",
        reply_markup=kb
    )

    # Очистим корзину после оформления
    carts[uid] = []

@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(call: types.CallbackQuery):
    uid = call.from_user.id
    waiting_for_perfume[uid] = False
    waiting_for_full_bottle[uid] = False
    current_perfume[uid] = ""
    await call.message.edit_text("Выберите вариант покупки:", reply_markup=main_menu_kb())

# ----------- ЦЕЛЫЙ ФЛАКОН -----------
@dp.callback_query(F.data == "buy_full")
async def buy_full(call: types.CallbackQuery):
    uid = call.from_user.id
    waiting_for_full_bottle[uid] = True
    waiting_for_perfume[uid] = False
    current_perfume[uid] = ""
    await call.message.edit_text(
        "💎 Вы выбрали покупку целого флакона.\n\n"
        "✍️ <b>Напишите</b>:\n"
        "• Название парфюма\n"
        "• Желаемый объём\n\n"
        "ℹ️ Продавец уточнит <b>актуальную цену</b> выбранного аромата и свяжется с вами.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ В меню", callback_data="back_to_menu")]
        ])
    )

# ------------------ Точка входа ------------------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

