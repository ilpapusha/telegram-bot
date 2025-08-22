import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import Router
from dotenv import load_dotenv

# Загружаем токен и ID админа из .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

# Состояния для FSM
class OrderStates(StatesGroup):
    waiting_for_screenshot = State()

# Кнопки
main_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🛒 Купить")]],
    resize_keyboard=True
)

cancel_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌ Отмена")]],
    resize_keyboard=True
)

contact_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📞 Связаться с продавцом")]],
    resize_keyboard=True
)

# Старт
@router.message(F.text == "/start")
async def start_cmd(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Привет! 👋\nЗдесь можно купить товар.\nНажми кнопку ниже:",
        reply_markup=main_kb
    )

# Нажали "Купить"
@router.message(F.text == "🛒 Купить")
async def buy_cmd(message: types.Message, state: FSMContext):
    await state.set_state(OrderStates.waiting_for_screenshot)
    await message.answer(
        "Переведи деньги на карту:\n\n"
        "💳 1234 5678 9012 3456\n\n"
        "После оплаты отправь сюда скриншот чека.",
        reply_markup=cancel_kb
    )

# Пользователь отправляет скриншот
@router.message(OrderStates.waiting_for_screenshot, F.photo)
async def handle_screenshot(message: types.Message, state: FSMContext):
    user_link = f"tg://user?id={message.from_user.id}"
    caption = (
        f"🆕 Новый платёж!\n\n"
        f"👤 Покупатель: {message.from_user.full_name}\n"
        f"🔗 [Ссылка на Telegram]({user_link})"
    )
    # Пересылаем админу фото
    await bot.send_photo(
        chat_id=ADMIN_ID,
        photo=message.photo[-1].file_id,
        caption=caption,
        parse_mode="Markdown"
    )

    await message.answer(
        "Спасибо! ✅ Мы проверим оплату и скоро свяжемся с тобой.",
        reply_markup=contact_kb
    )
    await state.clear()

# Обработка кнопки "Связаться с продавцом"
@router.message(F.text == "📞 Связаться с продавцом")
async def contact_seller(message: types.Message):
    await message.answer(
        "Ты можешь написать продавцу напрямую: "
        f"[Перейти в чат](tg://user?id={ADMIN_ID})",
        parse_mode="Markdown"
    )

# Отмена
@router.message(F.text == "❌ Отмена")
async def cancel_cmd(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Отменено. Возвращаюсь в главное меню.", reply_markup=main_kb)

# Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
