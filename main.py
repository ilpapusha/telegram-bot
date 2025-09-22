import os, asyncio, logging
from html import escape
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup as KB, InlineKeyboardButton as BTN
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN=os.getenv("BOT_TOKEN"); ADMIN_ID=int(os.getenv("ADMIN_ID","0") or 0)
if not BOT_TOKEN: raise RuntimeError("BOT_TOKEN отсутствует"); 
if not ADMIN_ID:  raise RuntimeError("ADMIN_ID отсутствует")
SELLER_LINK=f"tg://user?id={ADMIN_ID}"

logging.basicConfig(level=logging.INFO)
bot=Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp=Dispatcher()

# ---------- ДАННЫЕ ----------
KITS=[ # цена: 5шт=5499, 3шт=3499
 {"code":"vostochny","title":"🕌🌙 Набор «Восточный»","photo":"AgACAgIAAxkBAAN_aNF8NzIeIItUw9J4P3oLvcshM7wAAsf2MRtqspFKEp0AAee2XsX8AQADAgADeQADNgQ","items":[("Montale Arabians Tonka",5),("Mancera Red Tobacco",5),("Parfums de Marly Althair",5),("Azzaro The Most Wanted Parfum",5),("Armani Stronger With You Absolutely",5)]},
 {"code":"svezhiy","title":"💦🍃 Набор «Свежий»","photo":"AgACAgIAAxkBAAN9aNF8GK0h-cwWMHP6WkAlFwABQmwZAALF9jEbarKRShK5MEgD8MXBAQADAgADeQADNgQ","items":[("Dior Homme Cologne",5),("Parfums de Marly Greenley",5),("Prada L’Homme L’Eau",5),("Armani Acqua Di Gio Profondo Parfum",5),("Jean Paul Gaultier Le Beau Le Parfum",5)]},
 {"code":"vecherniy","title":"🌙✨ Набор «Вечерний»","photo":"AgACAgIAAxkBAAN4aNF5HwqkdgNcQjgg9gABSo25lFxfAAKw9jEbarKRSqr-Vm7eaG3mAQADAgADeQADNgQ","items":[("Armaf Club de Nuit Intense",5),("Jean Paul Gaultier Le Male Le Parfum",5),("Chanel Bleu de Chanel Eau de Parfum",5),("Yves Saint Laurent Myslf Eau de Parfum",5),("Tom Ford Noir",5)]},
 {"code":"komplimentarnyy","title":"💘🌟 Набор «Комплиментарный»","photo":"AgACAgIAAxkBAAOCaNF8eAd67W7XRioTneRMlxlJSb4AAsr2MRtqspFKaGxSSlgviZYBAAMCAAN5AAM2BA","items":[("Initio Side Effect",5),("Armaf Club de Nuit Intense",5),("Jean Paul Gaultier Le Male Le Parfum",5),("Prada L’Homme L’Eau",5),("Yves Saint Laurent La Nuit de L’Homme Eau de Parfum",5)]},
 {"code":"na_vse_sluchai","title":"🎯🧩 Набор «На все случаи жизни»","photo":"AgACAgIAAxkBAAOEaNF8i5lVXVryRVLRgEMDH8EpLl8AAsv2MRtqspFKosf2SsGkXIoBAAMCAAN5AAM2BA","items":[("Montale Arabians Tonka",5),("Armaf Club de Nuit Intense",5),("Armani Acqua Di Gio Parfum",5),("Jean Paul Gaultier Le Male Le Parfum",5),("Chanel Bleu de Chanel Eau de Parfum",5)]},
 {"code":"big_g","title":"🦁💥 Набор «BIG G»","photo":"AgACAgIAAxkBAAOGaNF8nCTpNhq-UNWry9jtTr8mTnAAAsz2MRtqspFKDfNtpsgRR90BAAMCAAN5AAM2BA","items":[("Parfums de Marly Layton",5),("Tom Ford Ombre Leather",5),("Azzaro The Most Wanted Parfum",5)]},
 {"code":"dzhentelmen","title":"🤵🎩 Набор «Джентельмен»","photo":"AgACAgIAAxkBAAOIaNF8tAfhnzZUEA5IVrXE18KM9L8AAs32MRtqspFK5w3gcQQrVvMBAAMCAAN5AAM2BA","items":[("Parfums de Marly Sedley",5),("Prada L’Homme",5),("Jean Paul Gaultier Le Male Le Parfum",5)]},
 {"code":"papochka","title":"👑🔥 Набор «Папочка»","photo":"AgACAgIAAxkBAAOKaNF8yBFmwnJyKoc4jSiQXkYEbgsAAs72MRtqspFK2Y3owjZIH4cBAAMCAAN5AAM2BA","items":[("Parfums de Marly Althaïr",5),("Dior Homme Intense",5),("Mancera Red Tobacco",5)]},
]

DECANT_BRANDS=[ # БРЕНДЫ -> АРОМАТЫ (из твоего списка)
 {"brand":"Armaf","items":[
  {"code":"armaf_club_de_nuit_intense","title":"Armaf Club de Nuit Intense","photo":"AgACAgIAAxkBAAPnaNGbExtBAUSEOC4rXP4_rNoTWdYAAlD4MRtqspFKjRhaxnNHC6QBAAMCAAN4AAM2BA","desc":"Ананасовый аккорд и древесный шлейф.","prices":{5:500,8:800,18:1650}},
 ]},
 {"brand":"Armani","items":[
  {"code":"armani_stronger_with_you_absolutely","title":"Armani Stronger With You Absolutely","photo":"AgACAgIAAxkBAAOpaNGU3H6TXH1TC595dFCygS52XHkAAg34MRtqspFKi4DWbBAqtlABAAMCAAN4AAM2BA","desc":"Каштановый ликёр с пряной теплотой.","prices":{5:920,8:1400,18:2950}},
  {"code":"armani_acqua_di_gio_parfum","title":"Armani Acqua Di Gio Parfum","photo":"AgACAgIAAxkBAAOraNGU-ftqCzlLm4FadHrYCtsdEfMAAg_4MRtqspFKgx7ZtuzGjqkBAAMCAAN4AAM2BA","desc":"Современная интерпретация морской свежести.","prices":{5:1150,8:1800,18:3800}},
  {"code":"armani_acqua_di_gio_profondo_parfum","title":"Armani Acqua Di Gio Profundo Parfum","photo":"AgACAgIAAxkBAAOtaNGV1t9md2a0AuBpubS3oEznDDoAAhP4MRtqspFKZwIITqOJT4cBAAMCAAN5AAM2BA","desc":"Глубокий акватический аккорд с минеральностью.","prices":{5:1200,8:1850,18:3950}},
 ]},
 {"brand":"Azzaro","items":[
  {"code":"azzaro_the_most_wanted_parfum","title":"Azzaro The Most Wanted Parfum","photo":"AgACAgIAAxkBAAOxaNGWHHC7h_Cu4RJO8lFuqwNWehQAAhX4MRtqspFKQDr0zyIyfXkBAAMCAAN4AAM2BA","desc":"Древесно-пряный аккорд с тёплой сладостью.","prices":{5:950,8:1500,18:3200}},
 ]},
 {"brand":"Chanel","items":[
  {"code":"chanel_bleu_de_chanel_eau_de_parfum","title":"Chanel Bleu de Chanel Eau de Parfum","photo":"AgACAgIAAxkBAAOnaNGUvcDyrCSvpowqemnq5qRPNFIAAgz4MRtqspFKL4s-VvjIQ5YBAAMCAAN5AAM2BA","desc":"Древесный аккорд с благородной свежестью.","prices":{5:1700,8:2650,18:5700}},
 ]},
 {"brand":"Creed","items":[
  {"code":"creed_aventus","title":"Creed Aventus","photo":"AgACAgIAAxkBAAOzaNGWNq9LPIrA6RVQuwM2ugL1vs8AAhf4MRtqspFK7kbGl0SFhe4BAAMCAAN5AAM2BA","desc":"Фруктовый акцент и дымный мох.","prices":{5:4600,8:7250,18:15400}},
 ]},
 {"brand":"Dior","items":[
  {"code":"dior_homme_intense","title":"Dior Homme Intense","photo":"AgACAgIAAxkBAAOhaNGUOaHHMiz0T-8HoORdHaOh7OwAAgX4MRtqspFK7Hs0ngAB5qXtAQADAgADeQADNgQ","desc":"Ирис и древесные ноты. Элегантный и глубокий.","prices":{5:1450,8:2200,18:4800}},
  {"code":"dior_sauvage_eau_de_parfum","title":"Dior Sauvage Eau de Parfum","photo":"AgACAgIAAxkBAAOjaNGUcp8OZu0XefSRSWXnFJp6i_gAAgn4MRtqspFKByeurFjEc6kBAAMCAAN5AAM2BA","desc":"Свежий бергамот и амбра. Универсальный и современный.","prices":{5:1350,8:2100,18:4450}},
  {"code":"dior_homme_cologne","title":"Dior Homme Cologne","photo":"AgACAgIAAxkBAAOlaNGUk4pJFyGIe1B8Pwba3PMHn_cAAgr4MRtqspFKVdbdCukOTU4BAAMCAAN5AAM2BA","desc":"Цитрусовая лёгкость с кристальной чистотой.","prices":{5:970,8:1500,18:3100}},
 ]},
 {"brand":"Ex Nihilo","items":[
  {"code":"ex_nihilo_blue_talisman","title":"Ex Nihilo Blue Talisman","photo":"AgACAgIAAxkBAAOvaNGV9kpPv9_UNvB-O-GYgmkclK8AAhT4MRtqspFKqcqnIwMsJKsBAAMCAAN4AAM2BA","desc":"Холодные специи и древесные ноты.","prices":{5:3850,8:6100,18:13000}},
 ]},
 {"brand":"Initio","items":[
  {"code":"initio_side_effect","title":"Initio Side Effect","photo":"AgACAgIAAxkBAAO1aNGWWOSJPBHzzgsrYFr4Ir-DBfYAAhz4MRtqspFKz544k4rORpsBAAMCAAN5AAM2BA","desc":"Табак, ваниль и мягкие специи.","prices":{5:1900,8:3000,18:6400}},
  {"code":"initio_oud_for_greatness","title":"Initio Oud for Greatness","photo":"AgACAgIAAxkBAAO3aNGWhOSanD8p7lDzNWmGPalFJjMAAh_4MRtqspFKBFrAsNrbyYUBAAMCAAN4AAM2BA","desc":"Благородный уд и пряности.","prices":{5:2050,8:3250,18:6900}},
 ]},
 {"brand":"Jean Paul Gaultier","items":[
  {"code":"jean_paul_gaultier_le_beau_le_parfum","title":"Jean Paul Gaultier Le Beau Le Parfum","photo":"AgACAgIAAxkBAAO5aNGWnYhi7syIXUJLnJO9O3rHOfsAAiD4MRtqspFKxEZIzSS9jvQBAAMCAAN5AAM2BA","desc":"Кокос и древесина в изящном балансе.","prices":{5:1550,8:2450,18:5200}},
  {"code":"jean_paul_gaultier_le_male_le_parfum","title":"Jean Paul Gaultier Le Male Le Parfum","photo":"AgACAgIAAxkBAAO7aNGW3ggqX75xvxo7z9L--Sef8dgAAiH4MRtqspFKnVQ7Mp_LWjUBAAMCAAN4AAM2BA","desc":"Ванильный восток и лаванда.","prices":{5:1600,8:2550,18:5450}},
  {"code":"jean_paul_gaultier_le_male_elixir","title":"Jean Paul Gaultier Le Male Elixir","photo":"AgACAgIAAxkBAAO9aNGXOOIUUOGyG4Ww7vVUK2JfvfMAAiL4MRtqspFKSZ-Ir2BLRfwBAAMCAAN5AAM2BA","desc":"Мёд и амбра с тёплым шлейфом.","prices":{5:1650,8:2650,18:5650}},
  {"code":"jean_paul_gaultier_ultra_male","title":"Jean Paul Gaultier Ultra Male","photo":"AgACAgIAAxkBAAO_aNGXWQ3i9xXFcLD8YOrlVRNn_iwAAiP4MRtqspFKdNU0uwq8byABAAMCAAN4AAM2BA","desc":"Сладкие фрукты и лаванда.","prices":{5:1100,8:1750,18:3650}},
 ]},
 {"brand":"Mancera","items":[
  {"code":"mancera_red_tobacco","title":"Mancera Red Tobacco","photo":"AgACAgIAAxkBAAPpaNGbKhgwsl62HLaFU5a3nV7ZnBgAAlH4MRtqspFKwYCTWxqUE_QBAAMCAAN4AAM2BA","desc":"Табак и пряности.","prices":{5:950,8:1500,18:3200}},
 ]},
 {"brand":"Montale","items":[
  {"code":"montale_arabians_tonka","title":"Montale Arabians Tonka","photo":"AgACAgIAAxkBAAPBaNGXfoXnz3HrTmTeD3n1oV-BUUsAAiT4MRtqspFKTVYhFgABjKzYAQADAgADeQADNgQ","desc":"Специи, роза и бобы тонка.","prices":{5:800,8:1250,18:2600}},
 ]},
 {"brand":"Paco Rabanne","items":[
  {"code":"paco_rabanne_1_million_eau_de_toilette","title":"Paco Rabanne 1 Million Eau de Toilette","photo":"AgACAgIAAxkBAAPPaNGZKo9qFHjbZe9BEHKJjO_X2K4AAjT4MRtqspFKS0jO2U5CIBQBAAMCAAN4AAM2BA","desc":"Корица и кожа с лёгкой сладостью.","prices":{5:850,8:1350,18:2850}},
 ]},
 {"brand":"Parfums de Marly","items":[
  {"code":"parfums_de_marly_althair","title":"Parfums de Marly Althair","photo":"AgACAgIAAxkBAAPDaNGXveShSbqU0Lgi-bp1DULwMq0AAif4MRtqspFKY-Y_GsIiixsBAAMCAAN4AAM2BA","desc":"Ваниль с пряным акцентом.","prices":{5:1750,8:2800,18:5900}},
  {"code":"parfums_de_marly_layton","title":"Parfums de Marly Layton","photo":"AgACAgIAAxkBAAPFaNGYMX72EgqMqqliDHcyPx2uwY4AAiv4MRtqspFKC95VEPjk0_QBAAMCAAN4AAM2BA","desc":"Яблоко и специи в элегантной композиции.","prices":{5:2400,8:3800,18:8000}},
  {"code":"parfums_de_marly_greenley","title":"Parfums de Marly Greenley","photo":"AgACAgIAAxkBAAPHaNGYTUtxnCoTOeU_LobuGN-bh4MAAi34MRtqspFKOSjdFCAvQHQBAAMCAAN4AAM2BA","desc":"Цитрусы и зелёные ноты.","prices":{5:1650,8:2650,18:5600}},
  {"code":"parfums_de_marly_sedley","title":"Parfums de Marly Sedley","photo":"AgACAgIAAxkBAAPJaNGYafVy825J-HJ1MLAxl8Ci5ekAAi74MRtqspFKzacNsGh1kDUBAAMCAAN5AAM2BA","desc":"Мятная свежесть и лёгкая древесность.","prices":{5:1700,8:2750,18:5800}},
 ]},
 {"brand":"Prada","items":[
  {"code":"prada_l_homme_l_eau","title":"Prada L’Homme L’Eau","photo":"AgACAgIAAxkBAAPLaNGYl-G46ek4290F0ZocJuARgAADL_gxG2qykUpWzmXr0NnQXQEAAwIAA3gAAzYE","desc":"Чистые и лёгкие свежие ноты.","prices":{5:950,8:1500,18:3150}},
  {"code":"prada_l_homme","title":"Prada L’Homme","photo":"AgACAgIAAxkBAAPNaNGYraCOr0Bef75YCPb6MTovTvgAAjD4MRtqspFKjEnasri_cjEBAAMCAAN4AAM2BA","desc":"Ирис и древесина в чистом звучании.","prices":{5:1000,8:1550,18:3300}},
 ]},
 {"brand":"Stephane Humbert Lucas","items":[
  {"code":"stephane_humbert_lucas_god_of_fire","title":"Stephane Humbert Lucas God of Fire","photo":"AgACAgIAAxkBAAPRaNGZQ0Jyk1yDKAnsDMXud0dAR10AAjX4MRtqspFKqYmKmYtvAAEmAQADAgADeQADNgQ","desc":"Манго и специи.","prices":{5:3000,8:4700,18:9900}},
  {"code":"stephane_humbert_lucas_venom_incarnat","title":"Stephane Humbert Lucas Venom Incarnat","photo":"AgACAgIAAxkBAAPTaNGZiTM8R0QcRrXyPQF44SfaAAE_AAI4-DEbarKRSoeULdG2neISAQADAgADeAADNgQ","desc":"Фрукты с пряным акцентом.","prices":{5:2900,8:4600,18:9700}},
 ]},
 {"brand":"Tom Ford","items":[
  {"code":"tom_ford_tobacco_vanille","title":"Tom Ford Tobacco Vanille","photo":"AgACAgIAAxkBAAPVaNGZqdZ9wIa_kWOl3YSzB_CbtSEAAjn4MRtqspFKR2YgJ0sTrecBAAMCAAN5AAM2BA","desc":"Табак и благородная ваниль.","prices":{5:2600,8:4150,18:8800}},
  {"code":"tom_ford_oud_wood","title":"Tom Ford Oud Wood","photo":"AgACAgIAAxkBAAPXaNGZ7NgE5M8utwhwt2L7ePYL0X0AAjv4MRtqspFKKW6nNfiLp_sBAAMCAAN5AAM2BA","desc":"Уд с древесными оттенками.","prices":{5:2550,8:4050,18:8600}},
  {"code":"tom_ford_noir","title":"Tom Ford Noir","photo":"AgACAgIAAxkBAAPZaNGZ_dZ_F4hTQPWuYGDThJjAYGYAAj74MRtqspFKyHuZuJSd3mMBAAMCAAN5AAM2BA","desc":"Пряный аккорд и амбра.","prices":{5:1200,8:1900,18:4000}},
  {"code":"tom_ford_ombre_leather","title":"Tom Ford Ombre Leather","photo":"AgACAgIAAxkBAAPbaNGaKVVgivqJARh0An2ZOQ6CSIoAAkP4MRtqspFKH5MOU2lhzYUBAAMCAAN5AAM2BA","desc":"Кожа с цветочным акцентом.","prices":{5:1600,8:2550,18:5400}},
 ]},
 {"brand":"Versace","items":[
  {"code":"versace_eros","title":"Versace Eros","photo":"AgACAgIAAxkBAAPjaNGareaGYhud8dNfSGLnI1-hEeQAAk34MRtqspFKyoGp1YVP9PIBAAMCAAN5AAM2BA","desc":"Мята и ваниль.","prices":{5:1050,8:1700,18:3600}},
  {"code":"versace_eros_flame","title":"Versace Eros Flame","photo":"AgACAgIAAxkBAAPlaNGaxXpemL83XYdYfm5zH0yOsJsAAk74MRtqspFKc6UwsNtsMHEBAAMCAAN5AAM2BA","desc":"Цитрусы и специи.","prices":{5:1200,8:1900,18:4000}},
 ]},
 {"brand":"Yves Saint Laurent","items":[
  {"code":"yves_saint_laurent_myslf_eau_de_parfum","title":"Yves Saint Laurent Myslf Eau de Parfum","photo":"AgACAgIAAxkBAAPdaNGaVqW9uhb7d3_wMxaEQ6FW9x4AAkn4MRtqspFK2xM2-EqMP6wBAAMCAAN5AAM2BA","desc":"Свежая современная древесная композиция.","prices":{5:950,8:1500,18:3150}},
  {"code":"yves_saint_laurent_la_nuit_de_l_homme_eau_de_parfum","title":"YSL La Nuit de L'Homme Eau de Parfum","photo":"AgACAgIAAxkBAAPfaNGac8EO1FomBXicg5xDK8SjDAgAAkr4MRtqspFKR-9_tppBbJwBAAMCAAN4AAM2BA","desc":"Кардамон в вечернем звучании.","prices":{5:1150,8:1850,18:3850}},
  {"code":"yves_saint_laurent_y_for_men","title":"Yves Saint Laurent Y For Men","photo":"AgACAgIAAxkBAAPhaNGamA8Hny_Je_9DPrxztXr2sroAAkz4MRtqspFKZFVNwBsfvyIBAAMCAAN5AAM2BA","desc":"Свежая древесная композиция.","prices":{5:1100,8:1750,18:3700}},
 ]},
]

# ---------- СОСТОЯНИЯ/КОРЗИНА ----------
CART:dict[int,list[dict]]={}
WAIT_FULL:dict[int,bool]={}
WAIT_MANUAL:dict[int,bool]={}
CUR_NAME:dict[int,str]={}

# ---------- УТИЛИТЫ/КЛАВЫ ----------
def price_fmt(x:int): return f"{x} ₽"
def kit_price(k): n=len(k["items"]); return 5499 if n>=5 else (3499 if n==3 else 0)
def kb(rows): return KB(inline_keyboard=[[BTN(**b) for b in row] for row in rows])
def menu_kb():
    return kb([[{"text":"💉 Купить на роспив","callback_data":"buy_split"}],
               [{"text":"🎁 Готовые наборы","callback_data":"show_kits"}],
               [{"text":"💎 Купить целый флакон","callback_data":"buy_full"}],
               [{"text":"🛒 Моя корзина","callback_data":"show_cart"}],
               [{"text":"📨 Связаться с продавцом","url":SELLER_LINK}]])
def brands_kb():
    rows=[[{"text":b["brand"],"callback_data":f"brand_{i}"}] for i,b in enumerate(DECANT_BRANDS)]
    rows+= [[{"text":"✍️ Ввести вручную","callback_data":"buy_split_manual"}],
            [{"text":"⬅️ В меню","callback_data":"back_to_menu"}]]
    return kb(rows)
def decant_kb(bi,pi,prices):
    vols=[ml for ml in (5,8,18) if ml in prices]
    first=[{"text":f"{ml} мл — {price_fmt(prices[ml])}","callback_data":f"dec_add_{bi}_{pi}_{ml}"} for ml in vols]
    rows=[first,[{"text":"🛒 Моя корзина","callback_data":"show_cart"}],
          [{"text":"📨 Связаться с продавцом","url":SELLER_LINK}],
          [{"text":"⬅️ К брендам","callback_data":"buy_split"}]]
    return kb(rows)

def cart_sums(uid:int):
    cart=CART.get(uid,[])
    kit_titles=sorted({it.get("kit") for it in cart if it.get("kit")})
    kit_lines,total_k=[],0
    for t in kit_titles:
        k=next((x for x in KITS if x["title"]==t),None)
        if k: p=kit_price(k); total_k+=p; kit_lines.append(f"• {escape(t)} — <b>{price_fmt(p)}</b>")
    dec_lines,total_d=[],0
    for it in cart:
        if it.get("type")=="decant" and it.get("price"):
            dec_lines.append(f"• {escape(it['name'])} — {it['ml']} мл — <b>{price_fmt(int(it['price']))}</b>")
            total_d+=int(it["price"])
    return kit_lines,total_k,dec_lines,total_d

def cart_text(uid:int):
    cart=CART.get(uid,[])
    if not cart: return "🛒 Ваша корзина пуста."
    lines=[f"• {escape(it['name'])} — <b>{it['ml']} мл</b>"
           + (f" <i>(набор: {escape(it['kit'])})</i>" if it.get("kit") else "")
           + (f" — <b>{price_fmt(int(it['price']))}</b>" if it.get("price") else "")
           for it in cart]
    kl,tk,dl,td=cart_sums(uid)
    if kl: lines+=["", "<b>Цены наборов:</b>", *kl]
    if dl: lines+=["", "<b>Позиции на роспив:</b>", *dl]
    if tk+td>0: lines.append(f"\n<b>Итого: {price_fmt(tk+td)}</b>")
    return "🛒 <b>Ваша корзина</b>:\n\n"+"\n".join(lines)

# ---------- КОМАНДЫ ----------
@dp.message(Command("start","menu"))
async def start(m:types.Message):
    uid=m.from_user.id; WAIT_FULL[uid]=WAIT_MANUAL[uid]=False; CUR_NAME[uid]=""
    await m.answer("Добро пожаловать! Выберите действие:", reply_markup=menu_kb())

# ---------- РОСПИВ ----------
@dp.callback_query(F.data=="buy_split")
async def buy_split(c:types.CallbackQuery):
    await c.message.edit_text("Выберите бренд на роспив:", reply_markup=brands_kb())

@dp.callback_query(F.data=="buy_split_manual")
async def buy_split_manual(c:types.CallbackQuery):
    uid=c.from_user.id; WAIT_MANUAL[uid]=True; CUR_NAME[uid]=""
    await c.message.edit_text("✍️ Введите название аромата, затем выберите объём.", 
        reply_markup=kb([[{"text":"⬅️ К брендам","callback_data":"buy_split"}],
                         [{"text":"⬅️ В меню","callback_data":"back_to_menu"}]]))

@dp.callback_query(F.data.startswith("brand_"))
async def show_brand(c:types.CallbackQuery):
    try: bi=int(c.data.split("_")[1]); b=DECANT_BRANDS[bi]
    except: return await c.answer("Бренд не найден", show_alert=True)
    await c.message.edit_text(f"📚 {b['brand']}: доступные ароматы (листайте карточки ниже)")
    for pi,it in enumerate(b["items"]):
        prices=it["prices"]; lines=[f"• {ml} мл — <b>{price_fmt(p)}</b>" for ml,p in sorted(prices.items())]
        cap=f"<b>{escape(it['title'])}</b>\n{escape(it.get('desc',''))}\n\n"+"\n".join(lines)
        if it.get("photo"): 
            await c.message.answer_photo(it["photo"], caption=cap, reply_markup=decant_kb(bi,pi,prices))
        else:
            await c.message.answer(cap, reply_markup=decant_kb(bi,pi,prices))

@dp.callback_query(F.data.startswith("dec_add_"))
async def dec_add(c:types.CallbackQuery):
    uid=c.from_user.id; CART.setdefault(uid,[])
    try: _,bi,pi,ml=c.data.split("_"); bi,pi,ml=int(bi),int(pi),int(ml); it=DECANT_BRANDS[bi]["items"][pi]; price=int(it["prices"][ml])
    except: return await c.answer("Не удалось добавить позицию", show_alert=True)
    CART[uid].append({"name":it["title"],"ml":ml,"kit":None,"price":price,"type":"decant"})
    await c.message.answer(f"✅ В корзину: <b>{escape(it['title'])}</b> — <b>{ml} мл</b> — <b>{price_fmt(price)}</b>\n\nЧто дальше?",
        reply_markup=kb([[{"text":"➕ Добавить ещё","callback_data":"buy_split"}],
                         [{"text":"🛒 Моя корзина","callback_data":"show_cart"}],
                         [{"text":"✅ Оформить заказ","callback_data":"checkout"}],
                         [{"text":"📨 Связаться с продавцом","url":SELLER_LINK}],
                         [{"text":"⬅️ В меню","callback_data":"back_to_menu"}]]))

# ручной ввод названия + выбор объёма (без цены)
@dp.message(F.text)
async def on_text(m:types.Message):
    uid=m.from_user.id
    if WAIT_FULL.get(uid):
        un=m.from_user.username; link=f"https://t.me/{un}" if un else f"tg://user?id={uid}"
        kb=kb=[[{"text":"💬 Написать клиенту","url":link}]]
        await bot.send_message(ADMIN_ID, "📩 <b>Новый запрос на целый флакон</b>\n\n"
            f"👤 @{un or 'без_username'}\n🆔 <code>{uid}</code>\n✍️ {escape(m.text)}", reply_markup=KB(inline_keyboard=[[BTN(text="💬 Написать клиенту", url=link)]]))
        WAIT_FULL[uid]=False
        return await m.answer("✅ Запрос отправлен продавцу.\nℹ️ Он уточнит актуальную цену и свяжется с вами.",
            reply_markup=kb([[{"text":"📨 Связаться с продавцом","url":SELLER_LINK}],
                             [{"text":"⬅️ В меню","callback_data":"back_to_menu"}]]))
    if WAIT_MANUAL.get(uid):
        CUR_NAME[uid]=m.text.strip()
        return await m.answer(f"Вы выбрали: <b>{escape(CUR_NAME[uid])}</b>\nВыберите объём:",
            reply_markup=kb([[{"text":"💧 5 мл","callback_data":"mvol_5"},
                              {"text":"🧪 8 мл","callback_data":"mvol_8"},
                              {"text":"💎 18 мл","callback_data":"mvol_18"}],
                             [{"text":"⬅️ К брендам","callback_data":"buy_split"}]]))
    await m.answer("Выберите действие в меню:", reply_markup=menu_kb())

@dp.callback_query(F.data.startswith("mvol_"))
async def manual_volume(c:types.CallbackQuery):
    uid=c.from_user.id; name=CUR_NAME.get(uid)
    if not name: return await c.answer("Сначала введите название", show_alert=True)
    ml=int(c.data.split("_")[1]); CART.setdefault(uid,[]).append({"name":name,"ml":ml,"kit":None,"price":None,"type":"manual"})
    CUR_NAME[uid]=""
    await c.message.edit_text(f"✅ В корзину: <b>{escape(name)}</b> — <b>{ml} мл</b>\n\nЧто дальше?",
        reply_markup=kb([[{"text":"➕ Ещё аромат","callback_data":"buy_split"}],
                         [{"text":"🛒 Моя корзина","callback_data":"show_cart"}],
                         [{"text":"✅ Оформить заказ","callback_data":"checkout"}],
                         [{"text":"📨 Связаться с продавцом","url":SELLER_LINK}],
                         [{"text":"⬅️ В меню","callback_data":"back_to_menu"}]]))

# ---------- КОРЗИНА ----------
@dp.callback_query(F.data=="show_cart")
async def show_cart(c:types.CallbackQuery):
    txt=cart_text(c.from_user.id)
    has=bool(CART.get(c.from_user.id))
    rows=[[{"text":"✅ Оформить заказ","callback_data":"checkout"}]] if has else []
    rows+=[[{"text":"🧹 Очистить","callback_data":"clear_cart"}]] if has else []
    rows+=[[{"text":"📨 Связаться с продавцом","url":SELLER_LINK}],
           [{"text":"⬅️ В меню","callback_data":"back_to_menu"}]]
    await c.message.edit_text(txt, reply_markup=kb(rows))

@dp.callback_query(F.data=="clear_cart")
async def clear_cart(c:types.CallbackQuery):
    CART[c.from_user.id]=[]
    await c.message.edit_text("🧹 Корзина очищена.", reply_markup=kb([[{"text":"⬅️ В меню","callback_data":"back_to_menu"}]]))

@dp.callback_query(F.data=="checkout")
async def checkout(c:types.CallbackQuery):
    uid=c.from_user.id; cart=CART.get(uid,[])
    if not cart: return await c.answer("Корзина пуста", show_alert=True)
    txt=cart_text(uid)
    await c.message.edit_text("✅ Заказ сформирован и отправлен продавцу.\nℹ️ Он уточнит актуальную цену и свяжется с вами.\n\n"+txt,
        reply_markup=kb([[{"text":"📨 Связаться с продавцом","url":SELLER_LINK}],
                         [{"text":"⬅️ В меню","callback_data":"back_to_menu"}]]))
    un=c.from_user.username; link=f"https://t.me/{un}" if un else f"tg://user?id={uid}"
    await bot.send_message(ADMIN_ID, "📩 <b>Новый заказ</b>\n\n"
        f"👤 @{un or 'без_username'}\n🆔 <code>{uid}</code>\n\n"+txt,
        reply_markup=KB(inline_keyboard=[[BTN(text="💬 Написать клиенту", url=link)]]))
    CART[uid]=[]; CUR_NAME[uid]=""

# ---------- ГОТОВЫЕ НАБОРЫ ----------
@dp.callback_query(F.data=="show_kits")
async def show_kits(c:types.CallbackQuery):
    await c.message.answer("🎁 Доступные наборы:")
    for i,k in enumerate(KITS):
        lines=[f"• {escape(p)} — <b>{v} мл</b>" for p,v in k["items"]]
        cap=f"{k['title']}\n\n"+"\n".join(lines)+f"\n\n💰 <b>Цена: {price_fmt(kit_price(k))}</b>"
        if k.get("photo"):
            await c.message.answer_photo(k["photo"], caption=cap,
                reply_markup=kb([[{"text":"➕ Добавить набор","callback_data":f"kit_add_{i}"}],
                                 [{"text":"🛒 Моя корзина","callback_data":"show_cart"}],
                                 [{"text":"📨 Связаться с продавцом","url":SELLER_LINK}],
                                 [{"text":"⬅️ В меню","callback_data":"back_to_menu"}]]))
        else:
            await c.message.answer(cap, reply_markup=kb([[{"text":"➕ Добавить набор","callback_data":f"kit_add_{i}"}],
                                                         [{"text":"🛒 Моя корзина","callback_data":"show_cart"}],
                                                         [{"text":"📨 Связаться с продавцом","url":SELLER_LINK}],
                                                         [{"text":"⬅️ В меню","callback_data":"back_to_menu"}]]))

@dp.callback_query(F.data.startswith("kit_add_"))
async def kit_add(c:types.CallbackQuery):
    uid=c.from_user.id; CART.setdefault(uid,[])
    try: i=int(c.data.split("_")[-1]); k=KITS[i]
    except: return await c.answer("Набор не найден", show_alert=True)
    for name,ml in k["items"]: CART[uid].append({"name":name,"ml":ml,"kit":k["title"],"price":None,"type":"kit"})
    await c.message.answer(f"✅ В корзину добавлен набор: <b>{k['title']}</b>\n💰 <b>Цена: {price_fmt(kit_price(k))}</b>",
        reply_markup=kb([[{"text":"🛒 Моя корзина","callback_data":"show_cart"}],
                         [{"text":"✅ Оформить заказ","callback_data":"checkout"}],
                         [{"text":"⬅️ В меню","callback_data":"back_to_menu"}]]))

# ---------- ЦЕЛЫЙ ФЛАКОН ----------
@dp.callback_query(F.data=="buy_full")
async def buy_full(c:types.CallbackQuery):
    uid=c.from_user.id; WAIT_FULL[uid]=True; CUR_NAME[uid]=""
    await c.message.edit_text("💎 Напишите название парфюма и желаемый объём.\nℹ️ Продавец уточнит актуальную цену и свяжется с вами.",
        reply_markup=kb([[{"text":"📨 Связаться с продавцом","url":SELLER_LINK}],
                         [{"text":"⬅️ В меню","callback_data":"back_to_menu"}]]))

# ---------- FILE_ID фото (для админа) ----------
@dp.message(F.photo)
async def photo_id(m:types.Message):
    if m.from_user.id==ADMIN_ID:
        await m.answer(f"file_id: <code>{m.photo[-1].file_id}</code>")

# ---------- НАВИГАЦИЯ ----------
@dp.callback_query(F.data=="back_to_menu")
async def back_to_menu(c:types.CallbackQuery):
    uid=c.from_user.id; WAIT_FULL[uid]=WAIT_MANUAL[uid]=False; CUR_NAME[uid]=""
    await c.message.edit_text("Меню:", reply_markup=menu_kb())

# ---------- MAIN ----------
async def main(): await dp.start_polling(bot)
if __name__=="__main__": asyncio.run(main())