import os
import asyncio
import logging
from typing import Dict, List, Any, Tuple
from html import escape

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties
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

# всегда открываем диалог с тобой по ID
SELLER_LINK = f"tg://user?id={ADMIN_ID}"

logging.basicConfig(level=logging.INFO)
bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# ------------------ Хранилище состояний ------------------
# Корзина: список словарей {"name": str, "ml": int, "kit": Optional[str]}
carts: Dict[int, List[Dict[str, Any]]] = {}
waiting_for_perfume: Dict[int, bool] = {}
current_perfume: Dict[int, str] = {}
waiting_for_full_bottle: Dict[int, bool] = {}

# ------------------ Готовые наборы ------------------
KITS = [
    {
        "code": "vostochny",
        "title": "🕌🌙 Набор «Восточный»",
        "photo": "AgACAgIAAxkBAAN_aNF8NzIeIItUw9J4P3oLvcshM7wAAsf2MRtqspFKEp0AAee2XsX8AQADAgADeQADNgQ",
        "items": [
            ("Montale Arabians Tonka", 5),
            ("Mancera Red Tobacco", 5),
            ("Parfums de Marly Althair", 5),
            ("Azzaro The Most Wanted Parfum", 5),
            ("Armani Stronger With You Absolutely", 5),
        ],
    },
    {
        "code": "svezhiy",
        "title": "💦🍃 Набор «Свежий»",
        "photo": "AgACAgIAAxkBAAN9aNF8GK0h-cwWMHP6WkAlFwABQmwZAALF9jEbarKRShK5MEgD8MXBAQADAgADeQADNgQ",
        "items": [
            ("Dior Homme Cologne", 5),
            ("Parfums de Marly Greenley", 5),
            ("Prada L’Homme L’Eau", 5),
            ("Armani Acqua Di Gio Profondo Parfum", 5),
            ("Jean Paul Gaultier Le Beau Le Parfum", 5),
        ],
    },
    {
        "code": "vecherniy",
        "title": "🌙✨ Набор «Вечерний»",
        "photo": "AgACAgIAAxkBAAN4aNF5HwqkdgNcQjgg9gABSo25lFxfAAKw9jEbarKRSqr-Vm7eaG3mAQADAgADeQADNgQ",
        "items": [
            ("Armaf Club de Nuit Intense", 5),
            ("Jean Paul Gaultier Le Male Le Parfum", 5),
            ("Chanel Bleu de Chanel Eau de Parfum", 5),
            ("Yves Saint Laurent Myslf Eau de Parfum", 5),
            ("Tom Ford Noir", 5),
        ],
    },
    {
        "code": "komplimentarnyy",
        "title": "💘🌟 Набор «Комплиментарный»",
        "photo": "AgACAgIAAxkBAAOCaNF8eAd67W7XRioTneRMlxlJSb4AAsr2MRtqspFKaGxSSlgviZYBAAMCAAN5AAM2BA",
        "items": [
            ("Initio Side Effect", 5),
            ("Armaf Club de Nuit Intense", 5),
            ("Jean Paul Gaultier Le Male Le Parfum", 5),
            ("Prada L’Homme L’Eau", 5),
            ("Yves Saint Laurent La Nuit de L’Homme Eau de Parfum", 5),
        ],
    },
    {
        "code": "na_vse_sluchai",
        "title": "🎯🧩 Набор «На все случаи жизни»",
        "photo": "AgACAgIAAxkBAAOEaNF8i5lVXVryRVLRgEMDH8EpLl8AAsv2MRtqspFKosf2SsGkXIoBAAMCAAN5AAM2BA",
        "items": [
            ("Montale Arabians Tonka", 5),
            ("Armaf Club de Nuit Intense", 5),
            ("Armani Acqua Di Gio Parfum", 5),
            ("Jean Paul Gaultier Le Male Le Parfum", 5),
            ("Chanel Bleu de Chanel Eau de Parfum", 5),
        ],
    },
    {
        "code": "big_g",
        "title": "🦁💥 Набор «BIG G»",
        "photo": "AgACAgIAAxkBAAOGaNF8nCTpNhq-UNWry9jtTr8mTnAAAsz2MRtqspFKDfNtpsgRR90BAAMCAAN5AAM2BA",
        "items": [
            ("Parfums de Marly Layton", 5),
            ("Tom Ford Ombre Leather", 5),
            ("Azzaro The Most Wanted Parfum", 5),
        ],
    },
    {
        "code": "dzhentelmen",
        "title": "🤵🎩 Набор «Джентельмен»",
        "photo": "AgACAgIAAxkBAAOIaNF8tAfhnzZUEA5IVrXE18KM9L8AAs32MRtqspFK5w3gcQQrVvMBAAMCAAN5AAM2BA",
        "items": [
            ("Parfums de Marly Sedley", 5),
            ("Prada L’Homme", 5),
            ("Jean Paul Gaultier Le Male Le Parfum", 5),
        ],
    },
    {
        "code": "papochka",
        "title": "👑🔥 Набор «Папочка»",
        "photo": "AgACAgIAAxkBAAOKaNF8yBFmwnJyKoc4jSiQXkYEbgsAAs72MRtqspFK2Y3owjZIH4cBAAMCAAN5AAM2BA",
        "items": [
            ("Parfums de Marly Althaïr", 5),
            ("Dior Homme Intense", 5),
            ("Mancera Red Tobacco", 5),
        ],
    },
]

# ------------------ Утилиты ------------------
def kit_price(kit: Dict[str, Any]) -> int:
    """Цена набора по количеству позиций: 5 шт → 5499, 3 шт → 3499."""
    n = len(kit.get("items", []))
    if n >= 5:
        return 5499
    if n == 3:
        return 3499
    return 0  # для других размеров пока цена не задана

def format_price(rub: int) -> str:
    return f"{rub} ₽" if rub else "—"

def cart_kits_summary(cart: List[Dict[str, Any]]) -> Tuple[List[str], int]:
    """
    Возвращает:
      - список строк с ценами по каждому набору (уникальные названия),
      - общую сумму по наборам.
    Позиции роспива в сумму не входят (пока).
    """
    # соберём уникальные названия наборов, присутствующих в корзине
    unique_titles = []
    for it in cart:
        title = it.get("kit")
        if title and title not in unique_titles:
            unique_titles.append(title)

    lines = []
    total = 0
    for title in unique_titles:
        k = next((kk for kk in KITS if kk["title"] == title), None)
        if k:
            price = kit_price(k)
            total += price
            lines.append(f"• {escape(title)} — <b>{format_price(price)}</b>")
    return lines, total

# ------------------ Клавиатуры ------------------
def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💉 Купить на роспив", callback_data="buy_split")],
        [InlineKeyboardButton(text="🎁 Готовые наборы", callback_data="show_kits")],
        [InlineKeyboardButton(text="💎 Купить целый флакон", callback_data="buy_full")],
        [InlineKeyboardButton(text="🛒 Моя корзина", callback_data="show_cart")],
        [InlineKeyboardButton(text="📨 Связаться с продавцом", url=SELLER_LINK)],
    ])

def volumes_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💧 5 мл",  callback_data="volume_5"),
            InlineKeyboardButton(text="🧪 8 мл",  callback_data="volume_8"),
            InlineKeyboardButton(text="💎 18 мл", callback_data="volume_18"),
        ],
        [InlineKeyboardButton(text="⬅️ В меню", callback_data="back_to_menu")],
    ])

def after_add_item_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить ещё аромат", callback_data="add_more")],
        [InlineKeyboardButton(text="🛒 Моя корзина",          callback_data="show_cart")],
        [InlineKeyboardButton(text="✅ Оформить заказ",       callback_data="checkout")],
        [InlineKeyboardButton(text="📨 Связаться с продавцом", url=SELLER_LINK)],
        [InlineKeyboardButton(text="⬅️ В меню",               callback_data="back_to_menu")],
    ])

def cart_actions_kb(has_items: bool) -> InlineKeyboardMarkup:
    rows = []
    if has_items:
        rows.append([InlineKeyboardButton(text="✅ Оформить заказ", callback_data="checkout")])
        rows.append([InlineKeyboardButton(text="🧹 Очистить корзину", callback_data="clear_cart")])
    rows.append([InlineKeyboardButton(text="📨 Связаться с продавцом", url=SELLER_LINK)])
    rows.append([InlineKeyboardButton(text="⬅️ В меню", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def kit_card_kb(idx: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить набор в корзину", callback_data=f"kit_add_{idx}")],
        [InlineKeyboardButton(text="🛒 Моя корзина", callback_data="show_cart")],
        [InlineKeyboardButton(text="📨 Связаться с продавцом", url=SELLER_LINK)],
        [InlineKeyboardButton(text="⬅️ В меню", callback_data="back_to_menu")],
    ])

# ------------------ Команды ------------------
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    uid = message.from_user.id
    waiting_for_perfume[uid] = False
    waiting_for_full_bottle[uid] = False
    current_perfume[uid] = ""
    await message.answer("Добро пожаловать в парфюмерный бот!\nВыберите вариант покупки:", reply_markup=main_menu_kb())

@dp.message(Command("menu"))
async def menu_cmd(message: types.Message):
    uid = message.from_user.id
    waiting_for_perfume[uid] = False
    waiting_for_full_bottle[uid] = False
    current_perfume[uid] = ""
    await message.answer("Меню:", reply_markup=main_menu_kb())

# ----------- РОСПИВ -----------
@dp.callback_query(F.data == "buy_split")
async def buy_split(call: types.CallbackQuery):
    uid = call.from_user.id
    carts.setdefault(uid, [])
    waiting_for_perfume[uid] = True
    waiting_for_full_bottle[uid] = False
    current_perfume[uid] = ""
    await call.message.edit_text(
        "🧴 Вы выбрали покупку на роспив.\n\n"
        "✍️ <b>Напишите название аромата</b>, который хотите добавить в корзину.\n"
        "После этого я предложу выбрать объём.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛒 Моя корзина", callback_data="show_cart")],
            [InlineKeyboardButton(text="⬅️ В меню", callback_data="back_to_menu")],
        ])
    )

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
            f"✍️ Сообщение: {escape(message.text)}",
            reply_markup=kb
        )
        waiting_for_full_bottle[uid] = False
        await message.answer(
            "✅ Спасибо! Запрос отправлен продавцу.\n"
            "ℹ️ Продавец уточнит актуальную цену и свяжется с вами.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📨 Связаться с продавцом", url=SELLER_LINK)],
                [InlineKeyboardButton(text="⬅️ В меню", callback_data="back_to_menu")],
            ])
        )
        return

    # Ввод аромата для роспива
    if waiting_for_perfume.get(uid):
        perfume = (message.text or "").strip()
        if not perfume:
            await message.answer("Пожалуйста, введите название аромата текстом.")
            return
        current_perfume[uid] = perfume
        waiting_for_perfume[uid] = False
        await message.answer(
            f"Вы выбрали аромат: <b>{escape(perfume)}</b>\n\nТеперь выберите объём 👇",
            reply_markup=volumes_kb()
        )
        return

    await message.answer("Выберите действие в меню:", reply_markup=main_menu_kb())

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
    carts.setdefault(uid, []).append({"name": perfume, "ml": volume, "kit": None})
    current_perfume[uid] = ""
    await call.message.edit_text(
        f"✅ В корзину добавлено: <b>{escape(perfume)}</b> — <b>{volume} мл</b>.\n\nЧто дальше?",
        reply_markup=after_add_item_kb()
    )

@dp.callback_query(F.data == "add_more")
async def add_more(call: types.CallbackQuery):
    uid = call.from_user.id
    waiting_for_perfume[uid] = True
    current_perfume[uid] = ""
    await call.message.edit_text(
        "✍️ Напишите название <b>следующего</b> аромата для роспива.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛒 Моя корзина", callback_data="show_cart")],
            [InlineKeyboardButton(text="⬅️ В меню", callback_data="back_to_menu")],
        ])
    )

# ----------- КОРЗИНА -----------
@dp.callback_query(F.data == "show_cart")
async def show_cart(call: types.CallbackQuery):
    uid = call.from_user.id
    cart = carts.get(uid, [])
    if not cart:
        await call.message.edit_text("🛒 Ваша корзина пуста.", reply_markup=cart_actions_kb(False))
        return

    # список позиций
    lines = [
        f"• {escape(item['name'])} — <b>{item['ml']} мл</b>"
        + (f" <i>(набор: {escape(item['kit'])})</i>" if item.get("kit") else "")
        for item in cart
    ]

    # цены наборов и итог
    kit_lines, total = cart_kits_summary(cart)
    if kit_lines:
        lines.append("")  # пустая строка
        lines.append("<b>Цены наборов:</b>")
        lines.extend(kit_lines)
        lines.append(f"\n<b>Итого за наборы: {format_price(total)}</b>")

    text = "🛒 <b>Ваша корзина</b>:\n\n" + "\n".join(lines)
    await call.message.edit_text(text, reply_markup=cart_actions_kb(True))

@dp.callback_query(F.data == "clear_cart")
async def clear_cart(call: types.CallbackQuery):
    carts[call.from_user.id] = []
    await call.message.edit_text("🧹 Корзина очищена.", reply_markup=cart_actions_kb(False))

@dp.callback_query(F.data == "checkout")
async def checkout(call: types.CallbackQuery):
    uid = call.from_user.id
    cart = carts.get(uid, [])
    if not cart:
        await call.answer("Корзина пуста.", show_alert=True)
        return

    # позиции
    lines = [
        f"• {escape(item['name'])} — {item['ml']} мл"
        + (f" (набор: {escape(item['kit'])})" if item.get("kit") else "")
        for item in cart
    ]

    # цены наборов и итог
    kit_lines, total = cart_kits_summary(cart)
    if kit_lines:
        lines.append("")
        lines.append("Цены наборов:")
        lines.extend(kit_lines)
        lines.append(f"\n<b>Итого за наборы: {format_price(total)}</b>")

    cart_text = "\n".join(lines)
    total_items = len(cart)

    # пользователю
    await call.message.edit_text(
        "✅ Заказ сформирован и отправлен продавцу.\n"
        "ℹ️ Продавец уточнит актуальную цену и свяжется с вами.\n\n"
        "<b>Состав заказа:</b>\n" + cart_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📨 Связаться с продавцом", url=SELLER_LINK)],
            [InlineKeyboardButton(text="⬅️ В меню", callback_data="back_to_menu")],
        ])
    )

    # админу
    username = call.from_user.username
    profile_link = f"https://t.me/{username}" if username else f"tg://user?id={uid}"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Написать клиенту", url=profile_link)]
    ])
    await bot.send_message(
        ADMIN_ID,
        "📩 <b>Новый заказ</b>\n\n"
        f"👤 Пользователь: @{username or 'без_username'}\n"
        f"🆔 ID: <code>{uid}</code>\n"
        f"🧾 Позиции: <b>{total_items}</b>\n\n"
        f"{cart_text}",
        reply_markup=kb
    )

    carts[uid] = []
    current_perfume[uid] = ""

# ----------- ГОТОВЫЕ НАБОРЫ (сразу все карточки с ценой) -----------
@dp.callback_query(F.data == "show_kits")
async def show_kits(call: types.CallbackQuery):
    await call.message.answer("🎁 Доступные наборы (листай вверх/вниз):")
    for idx, kit in enumerate(KITS):
        lines = [f"• {escape(p)} — <b>{v} мл</b>" for p, v in kit["items"]]
        price_line = f"\n💰 <b>Цена: {format_price(kit_price(kit))}</b>"
        caption = f"{kit['title']}\n\n" + "\n".join(lines) + price_line
        if kit.get("photo"):
            await call.message.answer_photo(
                photo=kit["photo"],
                caption=caption,
                parse_mode="HTML",
                reply_markup=kit_card_kb(idx)
            )
        else:
            await call.message.answer(
                caption, parse_mode="HTML", reply_markup=kit_card_kb(idx)
            )

@dp.callback_query(F.data.startswith("kit_add_"))
async def kit_add(call: types.CallbackQuery):
    uid = call.from_user.id
    carts.setdefault(uid, [])
    try:
        idx = int(call.data.split("_")[-1])
        kit = KITS[idx]
    except Exception:
        await call.answer("Набор не найден", show_alert=True)
        return

    for perfume, vol in kit["items"]:
        carts[uid].append({"name": perfume, "ml": vol, "kit": kit["title"]})

    added_list = "\n".join([f"• {escape(p)} — <b>{v} мл</b>" for p, v in kit["items"]])
    await call.message.answer(
        f"✅ В корзину добавлен набор:\n<b>{kit['title']}</b>\n\n{added_list}\n\n"
        f"💰 <b>Цена набора: {format_price(kit_price(kit))}</b>\n\nЧто дальше?",
        reply_markup=after_add_item_kb()
    )

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
        "ℹ️ Продавец уточнит актуальную цену и свяжется с вами.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📨 Связаться с продавцом", url=SELLER_LINK)],
            [InlineKeyboardButton(text="⬅️ В меню", callback_data="back_to_menu")],
        ])
    )

# ----------- ВЫДАЧА file_id фото (только для админа) -----------
@dp.message(F.photo)
async def admin_photo_id_echo(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    fid = message.photo[-1].file_id
    await message.answer(f"file_id: <code>{fid}</code>")

@dp.message(F.media_group_id)
async def admin_album_ids(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    if message.photo:
        fid = message.photo[-1].file_id
        await message.answer(f"(album) file_id: <code>{fid}</code>")

# ------------------ Точка входа ------------------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())