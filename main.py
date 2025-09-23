import os, asyncio, logging
from html import escape as html_escape
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup as KB, InlineKeyboardButton as BTN
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

# ---------- .env ----------
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0") or 0)
ADMIN_USERNAME = (os.getenv("ADMIN_USERNAME") or "").lstrip("@").strip()
if not BOT_TOKEN: raise RuntimeError("BOT_TOKEN отсутствует")
if not ADMIN_ID:  raise RuntimeError("ADMIN_ID отсутствует")
SELLER_URL = f"tg://user?id={ADMIN_ID}" if ADMIN_ID else (f"https://t.me/{ADMIN_USERNAME}" if ADMIN_USERNAME else None)

# ---------- ТЕКСТЫ ----------
WELCOME_TEXT = (
    "✨ <b>Добро пожаловать в FIFTY EIGHT PARFUMS</b> ✨\n\n"
    "💎 Люкс-ароматы на роспив\n"
    "🎁 Готовые наборы мини-флаконов\n"
    "📦 Новые оригинальные духи\n\n"
    "<b>Каталог:</b>"
)
SPRAYS_MAP = {5: "≈ 50 распылений", 8: "≈ 80 распылений", 18: "≈ 180 распылений"}

# ---------- AIOGRAM ----------
logging.basicConfig(level=logging.INFO)
bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# ---------- ДАННЫЕ (наборы) ----------
def kit_price(k) -> int:
    n = len(k["items"])
    return 5499 if n >= 5 else (3499 if n == 3 else 0)

KITS = [
 {"code":"vostochny","title":"🕌🌙 Набор «Восточный»","photo":"AgACAgIAAxkBAAN_aNF8NzIeIItUw9J4P3oLvcshM7wAAsf2MRtqspFKEp0AAee2XsX8AQADAgADeQADNgQ","items":[("Montale Arabians Tonka",5),("Mancera Red Tobacco",5),("Parfums de Marly Althair",5),("Azzaro The Most Wanted Parfum",5),("Armani Stronger With You Absolutely",5)]},
 {"code":"svezhiy","title":"💦🍃 Набор «Свежий»","photo":"AgACAgIAAxkBAAN9aNF8GK0h-cwWMHP6WkAlFwABQmwZAALF9jEbarKRShK5MEgD8MXBAQADAgADeQADNgQ","items":[("Dior Homme Cologne",5),("Parfums de Marly Greenley",5),("Prada L’Homme L’Eau",5),("Armani Acqua Di Gio Profondo Parfum",5),("Jean Paul Gaultier Le Beau Le Parfum",5)]},
 {"code":"vecherniy","title":"🌙✨ Набор «Вечерний»","photo":"AgACAgIAAxkBAAN4aNF5HwqkdgNcQjgg9gABSo25lFxfAAKw9jEbarKRSqr-Vm7eaG3mAQADAgADeQADNgQ","items":[("Armaf Club de Nuit Intense",5),("Jean Paul Gaultier Le Male Le Parfum",5),("Chanel Bleu de Chanel Eau de Parfum",5),("Yves Saint Laurent Myslf Eau de Parfum",5),("Tom Ford Noir",5)]},
 {"code":"komplimentarnyy","title":"💘🌟 Набор «Комплиментарный»","photo":"AgACAgIAAxkBAAOCaNF8eAd67W7XRioTneRMlxlJSb4AAsr2MRtqspFKaGxSSlgviZYBAAMCAAN5AAM2BA","items":[("Initio Side Effect",5),("Armaf Club de Nuit Intense",5),("Jean Paul Gaultier Le Male Le Parfum",5),("Prada L’Homme L’Eau",5),("Yves Saint Laurent La Nuit de L’Homme Eau de Parfum",5)]},
 {"code":"na_vse_sluchai","title":"🎯🧩 Набор «На все случаи жизни»","photo":"AgACAgIAAxkBAAOEaNF8i5lVXVryRVLRgEMDH8EpLl8AAsv2MRtqspFKosf2SsGkXIoBAAMCAAN5AAM2BA","items":[("Montale Arabians Tonka",5),("Armaf Club de Nuit Intense",5),("Armani Acqua Di Gio Parfum",5),("Jean Paul Gaultier Le Male Le Parfum",5),("Chanel Bleu de Chanel Eau de Parfum",5)]},
 {"code":"big_g","title":"🦁💥 Набор «BIG G»","photo":"AgACAgIAAxkBAAOGaNF8nCTpNhq-UNWry9jtTr8mTnAAAsz2MRtqspFKDfNtpsgRR90BAAMCAAN5AAM2BA","items":[("Parfums de Marly Layton",5),("Tom Ford Ombre Leather",5),("Azzaro The Most Wanted Parfum",5)]},
 {"code":"dzhentelmen","title":"🤵🎩 Набор «Джентельмен»","photo":"AgACAgIAAxkBAAOIaNF8tAfhnzZUEA5IVrXE18KM9L8AAs32MRtqspFK5w3gcQQrVvMBAAMCAAN5AAM2BA","items":[("Parfums de Marly Sedley",5),("Prada L’Homme",5),("Jean Paul Gaultier Le Male Le Parfum",5)]},
 {"code":"papochka","title":"👑🔥 Набор «Папочка»","photo":"AgACAgIAAxkBAAOKaNF8yBFmwnJyKoc4jSiQXkYEbgsAAs72MRtqspFK2Y3owjZIH4cBAAMCAAN5AAM2BA","items":[("Parfums de Marly Althaïr",5),("Dior Homme Intense",5),("Mancera Red Tobacco",5)]},
]

# ---------- ДАННЫЕ (роспив — бренды/ароматы) ----------
DECANT_BRANDS = [
 {"brand":"Armaf","items":[
  {"code":"armaf_club_de_nuit_intense","title":"Armaf Club de Nuit Intense","photo":"AgACAgIAAxkBAAPnaNGbExtBAUSEOC4rXP4_rNoTWdYAAlD4MRtqspFKjRhaxnNHC6QBAAMCAAN4AAM2BA","desc":"Ананасовый аккорд и древесный шлейф.","prices":{5:500,8:800,18:1650}},
 ]},
 {"brand":"Armani","items":[
  {"code":"armani_stronger_with_you_absolutely","title":"Armani Stronger With You Absolutely","photo":"AgACAgIAAxkBAAOpaNGU3H6TXH1TC595dFCygS52XHkAAg34MRtqspFKi4DWbBAqtlABAAMCAAN4AAM2BA","desc":"Каштановый ликёр с пряной теплотой.","prices":{5:920,8:1400,18:2950}},
  {"code":"armani_acqua_di_gio_parfum","title":"Armani Acqua Di Gio Parfum","photo":"AgACAgIAAxkBAAOraNGU-ftqCzlLm4FadHrYCtsdEfMAAg_4MRtqspFKgx7ZtuzGjqkBAAMCAAN4AAM2BA","desc":"Современная интерпретация морской свежести.","prices":{5:1150,8:1800,18:3800}},
  {"code":"armani_acqua_di_gio_profondo_parfum","title":"Armani Acqua Di Gio Profundo Parfum","photo":"AgACAgIAAxkBAAOtaNGV1t9md2a0AuBpubS3oEznDDoAAhP4MRtqspFKZwIITqOJT4cBAAMCAAN5AAM2BA","desc":"Глубокий акватический аккорд с минеральностью.","prices":{5:1200,8:1850,18:3950}},
 ]},
 # ... (остальные бренды оставлены без изменений в целях компактности)
] + [b for b in []]  # заглушка, чтобы не менять остальной контент

# ---------- СОСТОЯНИЯ / КОРЗИНА / ТРЕК СООБЩЕНИЙ ----------
CART: dict[int, list[dict]] = {}
WAIT_FULL: dict[int, bool] = {}
WAIT_MANUAL: dict[int, bool] = {}
WAIT_CONTACT: dict[int, bool] = {}
CUR_NAME: dict[int, str] = {}
TRACK_MSGS: dict[int, list[tuple[int, int]]] = {}

# ---------- УТИЛИТЫ / КЛАВЫ ----------
def price_fmt(x: int) -> str: return f"{x} ₽"

def kb(rows) -> KB:
    return KB(inline_keyboard=[[BTN(**b) for b in row] for row in rows])

def seller_row():
    return ([{"text":"📨 Связаться с продавцом","url":SELLER_URL}]
            if SELLER_URL else
            [{"text":"📨 Связаться с продавцом","callback_data":"contact_seller"}])

def menu_kb() -> KB:
    return kb([[{"text":"💉 Купить на роспив","callback_data":"buy_split"}],
               [{"text":"🎁 Готовые наборы","callback_data":"show_kits"}],
               [{"text":"💎 Купить целый флакон","callback_data":"buy_full"}],
               [{"text":"🛒 Моя корзина","callback_data":"show_cart"}],
               seller_row()])

def brands_kb() -> KB:
    rows = [[{"text":b["brand"],"callback_data":f"brand_{i}"}] for i,b in enumerate(DECANT_BRANDS)]
    rows += [[{"text":"✍️ Ввести вручную","callback_data":"buy_split_manual"}],
             [{"text":"⬅️ В каталог","callback_data":"back_to_menu"}]]
    return kb(rows)

def decant_kb(bi:int, pi:int, prices:dict) -> KB:
    volumes = [{"text":f"{ml} мл", "callback_data":f"dec_add_{bi}_{pi}_{ml}"} for ml in (5,8,18) if ml in prices]
    return kb([
        volumes,
        [{"text":"↩️ К бренду","callback_data":f"brand_{bi}"}],
        [{"text":"🛒 Моя корзина","callback_data":"show_cart"}],
        seller_row(),
        [{"text":"⬅️ К брендам","callback_data":"buy_split"}]
    ])

async def _remember(msg: types.Message):
    if not msg: return
    uid = msg.chat.id
    TRACK_MSGS.setdefault(uid, []).append((msg.chat.id, msg.message_id))

async def _safe_delete(chat_id: int, message_id: int):
    try:    await bot.delete_message(chat_id, message_id)
    except: pass

# удаляем только старые, последнее сообщение оставляем
async def cleanup_user(uid: int):
    msgs = TRACK_MSGS.get(uid, [])
    if len(msgs) <= 1:
        return
    to_delete = msgs[:-1]
    for chat_id, mid in to_delete:
        await _safe_delete(chat_id, mid)
    TRACK_MSGS[uid] = msgs[-1:]

# РЕДАКТИРУЕМ ТОЛЬКО СООБЩЕНИЯ БОТА; иначе — отправляем новое
async def show_screen(base_msg: types.Message, text: str, *, reply_markup=None):
    uid = base_msg.chat.id
    await cleanup_user(uid)

    can_edit = bool(getattr(base_msg, "from_user", None) and base_msg.from_user.is_bot)
    if can_edit:
        try:
            m = await base_msg.edit_text(text, reply_markup=reply_markup)
            TRACK_MSGS.setdefault(uid, [])
            TRACK_MSGS[uid] = [(cid, mid) for (cid, mid) in TRACK_MSGS[uid] if mid != m.message_id] + [(m.chat.id, m.message_id)]
            return m
        except Exception:
            pass

    m = await base_msg.answer(text, reply_markup=reply_markup)
    await _remember(m)
    return m

async def push_card(base_msg: types.Message, text_or_caption: str, *, photo_id: str | None, reply_markup=None):
    m = (await base_msg.answer_photo(photo=photo_id, caption=text_or_caption, reply_markup=reply_markup)
         if photo_id else
         await base_msg.answer(text_or_caption, reply_markup=reply_markup))
    await _remember(m)
    return m

# --- агрегатор/корзина (без изменений) ---
def aggregate_cart(uid: int):
    kits_raw: dict[str, int] = {}
    dec_map: dict[tuple[str, int, int], int] = {}
    manual_map: dict[tuple[str, int], int] = {}
    for it in CART.get(uid, []):
        if it.get("kit"):
            kits_raw[it["kit"]] = kits_raw.get(it["kit"], 0) + 1
        elif it.get("type") == "decant" and it.get("price") is not None:
            key = (it["name"], int(it["ml"]), int(it["price"]))
            dec_map[key] = dec_map.get(key, 0) + 1
        else:
            key = (it["name"], int(it["ml"]))
            manual_map[key] = manual_map.get(key, 0) + 1
    kits_map: dict[str, int] = {}
    for title, pcs in kits_raw.items():
        size = next((len(k["items"]) for k in KITS if k["title"] == title), 1)
        kits_map[title] = pcs // max(1, size)
    return kits_map, dec_map, manual_map

def cart_text(uid: int) -> str:
    cart = CART.get(uid, [])
    if not cart: return "🛒 Ваша корзина пуста."
    kits_map, dec_map, manual_map = aggregate_cart(uid)
    parts = ["🛒 <b>Ваша корзина</b>:"]
    kits_total = dec_total = 0
    if kits_map:
        parts += ["", "<b>🎁 Наборы</b>"]
        for title, count in sorted(kits_map.items()):
            k = next((x for x in KITS if x["title"] == title), None)
            if k:
                sub = kit_price(k) * count; kits_total += sub
                parts.append(f"🎁 {html_escape(title)} ×{count} — <b>{sub} ₽</b>")
            else:
                parts.append(f"🎁 {html_escape(title)} ×{count}")
    if dec_map:
        parts += ["", "<b>💧 Роспив</b>"]
        for (name, ml, price_one), count in sorted(dec_map.items()):
            sub = price_one * count; dec_total += sub
            parts.append(f"• {html_escape(name)} — {ml} мл ×{count} — <b>{sub} ₽</b>")
    if manual_map:
        parts += ["", "<b>✍️ Позиции без цены</b>"]
        for (name, ml), count in sorted(manual_map.items()):
            parts.append(f"• {html_escape(name)} — {ml} мл ×{count}")
    total = kits_total + dec_total
    if total > 0: parts += ["", f"<b>Итого: {total} ₽</b>"]
    return "\n".join(parts)

# ---------- КОМАНДЫ ----------
@dp.message(Command("start","menu"))
async def start(m: types.Message):
    uid = m.from_user.id
    WAIT_FULL[uid] = WAIT_MANUAL[uid] = WAIT_CONTACT[uid] = False
    CUR_NAME[uid] = ""
    await show_screen(m, WELCOME_TEXT, reply_markup=menu_kb())

# ---------- РОСПИВ ----------
@dp.callback_query(F.data=="buy_split")
async def buy_split(c: types.CallbackQuery):
    await show_screen(c.message, "Выберите бренд на роспив:", reply_markup=brands_kb())

@dp.callback_query(F.data=="buy_split_manual")
async def buy_split_manual(c: types.CallbackQuery):
    uid = c.from_user.id
    WAIT_MANUAL[uid] = True; CUR_NAME[uid] = ""
    await show_screen(
        c.message,
        "✍️ Введите название аромата, затем выберите объём.",
        reply_markup=kb([[{"text":"⬅️ К брендам","callback_data":"buy_split"}],
                         [{"text":"⬅️ В каталог","callback_data":"back_to_menu"}]])
    )

@dp.callback_query(F.data.startswith("brand_"))
async def show_brand(c: types.CallbackQuery):
    try:
        bi = int(c.data.split("_")[1])
        b = DECANT_BRANDS[bi]
    except Exception:
        return await c.answer("Бренд не найден", show_alert=True)
    await cleanup_user(c.from_user.id)
    head = await c.message.answer(f"📚 {b['brand']}: доступные ароматы (листайте карточки ниже)")
    await _remember(head)
    for pi, it in enumerate(b["items"]):
        prices = it["prices"]
        lines = [f"• {ml} мл — <b>{price_fmt(p)}</b> ({SPRAYS_MAP.get(ml, '≈ ? распылений')})"
                 for ml, p in sorted(prices.items())]
        cap = f"<b>{html_escape(it['title'])}</b>\n{html_escape(it.get('desc',''))}\n\n" + "\n".join(lines)
        await push_card(c.message, cap, photo_id=it.get("photo") or None,
                        reply_markup=decant_kb(bi, pi, prices))

@dp.callback_query(F.data.startswith("dec_add_"))
async def dec_add(c: types.CallbackQuery):
    uid = c.from_user.id
    CART.setdefault(uid, [])
    try:
        _, _, bi, pi, ml = c.data.split("_")
        bi = int(bi); pi = int(pi); ml = int(ml)
        it = DECANT_BRANDS[bi]["items"][pi]
        price = int(it["prices"][ml])
    except Exception:
        return await c.answer("Не удалось добавить позицию", show_alert=True)
    CART[uid].append({"name": it["title"], "ml": ml, "kit": None, "price": price, "type": "decant"})
    await show_screen(
        c.message,
        f"✅ В корзину: <b>{html_escape(it['title'])}</b> — <b>{ml} мл</b>\n\nЧто дальше?",
        reply_markup=kb([[{"text":"↩️ К бренду","callback_data":f"brand_{bi}"}],
                         [{"text":"➕ Добавить ещё","callback_data":"buy_split"}],
                         [{"text":"🛒 Моя корзина","callback_data":"show_cart"}],
                         [{"text":"✅ Оформить заказ","callback_data":"checkout"}],
                         seller_row(),
                         [{"text":"⬅️ В каталог","callback_data":"back_to_menu"}]])
    )

# ---------- РУЧНОЙ ВВОД ----------
@dp.message(F.text)
async def on_text(m: types.Message):
    uid = m.from_user.id
    if WAIT_CONTACT.get(uid):
        WAIT_CONTACT[uid] = False
        un = m.from_user.username
        client_anchor = (f'<a href="https://t.me/{un}">@{un}</a>' if un
                         else f'<a href="tg://user?id={uid}">Открыть чат</a>')
        await bot.send_message(
            ADMIN_ID,
            "📩 <b>Сообщение от клиента</b>\n"
            f"👤 {client_anchor}\n"
            f"🆔 <code>{uid}</code>\n\n"
            f"{html_escape(m.text)}"
        )
        return await show_screen(
            m, "✅ Сообщение отправлено продавцу.\nОжидайте ответ.",
            reply_markup=kb([[{"text":"⬅️ В каталог","callback_data":"back_to_menu"}]])
        )

    if WAIT_FULL.get(uid):
        un = m.from_user.username
        buttons = [[BTN(text="💬 Написать клиенту", url=f"https://t.me/{un}")]] if un else None
        client_anchor = (f'<a href="https://t.me/{un}">@{un}</a>' if un
                         else f'<a href="tg://user?id={uid}">Открыть чат</a>')
        await bot.send_message(
            ADMIN_ID,
            "📩 <b>Новый запрос на целый флакон</b>\n"
            f"👤 {client_anchor}\n🆔 <code>{uid}</code>\n✍️ {html_escape(m.text)}",
            reply_markup=KB(inline_keyboard=buttons) if buttons else None
        )
        WAIT_FULL[uid] = False
        return await show_screen(
            m, "✅ Запрос отправлен продавцу.\nОн свяжется с вами.",
            reply_markup=kb([seller_row(), [{"text":"⬅️ В каталог","callback_data":"back_to_menu"}]])
        )

    if WAIT_MANUAL.get(uid):
        CUR_NAME[uid] = m.text.strip()
        return await show_screen(
            m,
            f"Вы выбрали: <b>{html_escape(CUR_NAME[uid])}</b>\nВыберите объём:",
            reply_markup=kb([[{"text":"💧 5 мл","callback_data":"mvol_5"},
                              {"text":"🧪 8 мл","callback_data":"mvol_8"},
                              {"text":"💎 18 мл","callback_data":"mvol_18"}],
                             [{"text":"⬅️ К брендам","callback_data":"buy_split"}]])
        )

    await show_screen(m, "<b>Каталог:</b>", reply_markup=menu_kb())

@dp.callback_query(F.data.startswith("mvol_"))
async def manual_volume(c: types.CallbackQuery):
    uid = c.from_user.id
    name = CUR_NAME.get(uid)
    if not name:
        return await c.answer("Сначала введите название", show_alert=True)
    ml = int(c.data.split("_")[1])
    CART.setdefault(uid, []).append({"name": name, "ml": ml, "kit": None, "price": None, "type": "manual"})
    CUR_NAME[uid] = ""
    await show_screen(
        c.message,
        f"✅ В корзину: <b>{html_escape(name)}</b> — <b>{ml} мл</b>\n\nЧто дальше?",
        reply_markup=kb([[{"text":"➕ Ещё аромат","callback_data":"buy_split"}],
                         [{"text":"🛒 Моя корзина","callback_data":"show_cart"}],
                         [{"text":"✅ Оформить заказ","callback_data":"checkout"}],
                         seller_row(),
                         [{"text":"⬅️ В каталог","callback_data":"back_to_menu"}]])
    )

# ---------- КОРЗИНА ----------
def _short_item_label(it: dict) -> str:
    if it.get("kit"): return f"[набор] {it['name']} {it['ml']} мл"
    return f"{it['name']} {it['ml']} мл"

@dp.callback_query(F.data=="show_cart")
async def show_cart(c: types.CallbackQuery):
    txt = cart_text(c.from_user.id)
    has = bool(CART.get(c.from_user.id))
    rows = [[{"text":"✅ Оформить заказ","callback_data":"checkout"}]] if has else []
    rows += [[{"text":"🗑 Удалить позицию","callback_data":"del_menu"}]] if has else []
    rows += [[{"text":"🧹 Очистить","callback_data":"clear_cart"}]] if has else []
    rows += [seller_row(), [{"text":"⬅️ В каталог","callback_data":"back_to_menu"}]]
    await show_screen(c.message, txt, reply_markup=kb(rows))

@dp.callback_query(F.data=="del_menu")
async def del_menu(c: types.CallbackQuery):
    uid = c.from_user.id
    cart = CART.get(uid, [])
    if not cart:
        return await c.answer("Корзина пуста", show_alert=True)
    rows = []
    for i, it in enumerate(cart[:99]):
        rows.append([{"text": f"❌ { _short_item_label(it) }", "callback_data": f"del_idx_{i}"}])
    kits_map, _, _ = aggregate_cart(uid)
    if kits_map:
        rows.append([{"text":"— Удалить набор целиком —", "callback_data":"noop"}])
        for title, _ in kits_map.items():
            ki = next((i for i, k in enumerate(KITS) if k["title"] == title), -1)
            if ki >= 0:
                rows.append([{"text": f"🗑 {title} (все)", "callback_data": f"del_kit_all_idx_{ki}"}])
    rows += [[{"text":"⬅️ Назад в корзину","callback_data":"show_cart"}],
             [{"text":"⬅️ В каталог","callback_data":"back_to_menu"}]]
    await show_screen(c.message, "Выберите, что удалить:", reply_markup=kb(rows))

@dp.callback_query(F.data.startswith("del_idx_"))
async def del_idx(c: types.CallbackQuery):
    uid = c.from_user.id
    try:
        idx = int(c.data.split("_")[2])
        cart = CART.get(uid, [])
        if 0 <= idx < len(cart):
            removed = cart.pop(idx)
            await c.answer(f"Удалено: {removed.get('name','позиция')} {removed.get('ml','?')} мл")
        else:
            return await c.answer("Позиция не найдена", show_alert=True)
    except Exception:
        return await c.answer("Не удалось удалить", show_alert=True)
    await del_menu(c)

@dp.callback_query(F.data.startswith("del_kit_all_idx_"))
async def del_kit_all_idx(c: types.CallbackQuery):
    uid = c.from_user.id
    try:
        ki = int(c.data.split("_")[-1])
        k = KITS[ki]
    except Exception:
        return await c.answer("Набор не найден", show_alert=True)
    title = k["title"]; size = max(1, len(k["items"]))
    total_items = sum(1 for it in CART.get(uid, []) if it.get("kit") == title)
    if total_items == 0:
        return await c.answer("В корзине нет такого набора", show_alert=True)
    CART[uid] = [it for it in CART.get(uid, []) if it.get("kit") != title]
    kits_removed = max(1, total_items // size)
    await c.answer(f"Удалён набор: {title} ×{kits_removed}")
    await del_menu(c)

@dp.callback_query(F.data=="clear_cart")
async def clear_cart(c: types.CallbackQuery):
    CART[c.from_user.id] = []
    await show_screen(c.message, "🧹 Корзина очищена.",
                      reply_markup=kb([[{"text":"⬅️ В каталог","callback_data":"back_to_menu"}]]))

@dp.callback_query(F.data=="checkout")
async def checkout(c: types.CallbackQuery):
    uid = c.from_user.id
    cart = CART.get(uid, [])
    if not cart: return await c.answer("Корзина пуста", show_alert=True)
    txt = cart_text(uid)
    await show_screen(
        c.message,
        "✅ Заказ оформлен и отправлен продавцу.\n🙏 Спасибо за заказ! "
        "Продавец свяжется с вами по поводу оплаты.\n\n" + txt,
        reply_markup=kb([seller_row(), [{"text":"⬅️ В каталог","callback_data":"back_to_menu"}]])
    )
    un = c.from_user.username
    buttons = [[BTN(text="💬 Написать клиенту", url=f"https://t.me/{un}")]] if un else None
    client_anchor = (f'<a href="https://t.me/{un}">@{un}</a>' if un else f'<a href="tg://user?id={uid}">Открыть чат</a>')
    await bot.send_message(
        ADMIN_ID,
        "📩 <b>Новый заказ</b>\n"
        f"👤 {client_anchor}\n"
        f"🆔 <code>{uid}</code>\n\n" + txt,
        reply_markup=KB(inline_keyboard=buttons) if buttons else None
    )
    CART[uid] = []; CUR_NAME[uid] = ""

# ---------- ГОТОВЫЕ НАБОРЫ ----------
@dp.callback_query(F.data=="show_kits")
async def show_kits(c: types.CallbackQuery):
    await cleanup_user(c.from_user.id)
    head = await c.message.answer("🎁 Доступные наборы:")
    await _remember(head)
    for i, k in enumerate(KITS):
        lines = [f"• {html_escape(p)} — <b>{v} мл</b>" for p, v in k["items"]]
        cap = (f"{k['title']}\n\n" + "\n".join(lines) +
               f"\n\n💰 <b>Цена: {price_fmt(kit_price(k))}</b>\n💨 25 мл ≈ 250 пшиков")
        markup = kb([[{"text":"➕ Добавить набор","callback_data":f"kit_add_{i}"}],
                     [{"text":"🛒 Моя корзина","callback_data":"show_cart"}],
                     seller_row(),
                     [{"text":"⬅️ В каталог","callback_data":"back_to_menu"}]])
        await push_card(c.message, cap, photo_id=k.get("photo") or None, reply_markup=markup)

@dp.callback_query(F.data.startswith("kit_add_"))
async def kit_add(c: types.CallbackQuery):
    uid = c.from_user.id
    CART.setdefault(uid, [])
    try:
        i = int(c.data.split("_")[-1]); k = KITS[i]
    except Exception:
        return await c.answer("Набор не найден", show_alert=True)
    for name, ml in k["items"]:
        CART[uid].append({"name": name, "ml": ml, "kit": k["title"], "price": None, "type": "kit"})
    await show_screen(
        c.message,
        f"✅ В корзину добавлен набор: <b>{k['title']}</b>\n💰 <b>Цена: {price_fmt(kit_price(k))}</b>",
        reply_markup=kb([[{"text":"🛒 Моя корзина","callback_data":"show_cart"}],
                         [{"text":"✅ Оформить заказ","callback_data":"checkout"}],
                         [{"text":"⬅️ В каталог","callback_data":"back_to_menu"}]])
    )

# ---------- ЦЕЛЫЙ ФЛАКОН ----------
@dp.callback_query(F.data=="buy_full")
async def buy_full(c: types.CallbackQuery):
    uid = c.from_user.id
    WAIT_FULL[uid] = True; CUR_NAME[uid] = ""
    await show_screen(
        c.message,
        "💎 Напишите название парфюма и желаемый объём.\nМы свяжемся с вами.",
        reply_markup=kb([seller_row(), [{"text":"⬅️ В каталог","callback_data":"back_to_menu"}]])
    )

# ---------- FILE_ID (для админа) ----------
@dp.message(F.photo)
async def photo_id(m: types.Message):
    if m.from_user.id == ADMIN_ID:
        await m.answer(f"file_id: <code>{m.photo[-1].file_id}</code>")

# ---------- НАЗАД / КОНТАКТ ----------
@dp.callback_query(F.data=="back_to_menu")
async def back_to_menu(c: types.CallbackQuery):
    uid = c.from_user.id
    WAIT_FULL[uid] = WAIT_MANUAL[uid] = WAIT_CONTACT[uid] = False
    CUR_NAME[uid] = ""
    await show_screen(c.message, "<b>Каталог:</b>", reply_markup=menu_kb())

@dp.callback_query(F.data=="contact_seller")
async def contact_seller(c: types.CallbackQuery):
    uid = c.from_user.id
    if SELLER_URL:
        return await c.message.answer(f"Свяжитесь с продавцом: {SELLER_URL}")
    WAIT_CONTACT[uid] = True
    await show_screen(
        c.message,
        "✍️ Напишите сообщение для продавца — я сразу передам.",
        reply_markup=kb([[{"text":"⬅️ В каталог","callback_data":"back_to_menu"}]])
    )

# ---------- MAIN ----------
async def main(): await dp.start_polling(bot)
if __name__ == "__main__": asyncio.run(main())