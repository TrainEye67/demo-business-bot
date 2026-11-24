import asyncio
import os
from threading import Thread
from flask import Flask
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

app = Flask('')

@app.route('/')
def home():
    return "Demo bot is alive"

def run_flask():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask, daemon=True)
    t.start()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
FOOTER = "\n\n❗Бот пример и не работает❗"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

class DemoOrder(StatesGroup):
    waiting_car = State()
    waiting_time = State()

def main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛠 Услуги и цены", callback_data="prices")],
        [InlineKeyboardButton(text="📝 Оставить заявку", callback_data="order")],
        [InlineKeyboardButton(text="ℹ️ О студии", callback_data="about")]
    ])

def back_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 В главное меню", callback_data="menu")]
    ])

@dp.message(CommandStart())
async def cmd_start(msg: types.Message, state: FSMContext):
    await state.clear()
    text = (
        "👋 Добро пожаловать в детейлинг-центр **«APEX AUTO»**!\n"
        "Выберите нужный раздел в меню ниже:" + FOOTER
    )
    await msg.answer(text, reply_markup=main_kb(), parse_mode="Markdown")

@dp.callback_query(F.data == "menu")
async def cb_menu(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("📋 Главное меню. Выберите действие:" + FOOTER, reply_markup=main_kb())

@dp.callback_query(F.data == "prices")
async def cb_prices(call: types.CallbackQuery):
    text = (
        "💎 **Прайс-лист на услуги:**\n\n"
        "• Комплексная мойка + воск — **2 500 ₽**\n"
        "• Глубокая химчистка салона — **12 000 ₽**\n"
        "• Полировка кузова + керамика — **25 000 ₽**\n"
        "• Оклейка зон риска бронеплёнкой — **35 000 ₽**" + FOOTER
    )
    await call.message.edit_text(text, reply_markup=back_kb(), parse_mode="Markdown")

@dp.callback_query(F.data == "about")
async def cb_about(call: types.CallbackQuery):
    text = (
        "🏢 **О нас:**\n"
        "Работаем ежедневно с 10:00 до 21:00.\n"
        "Гарантия на все виды работ, зона ожидания с кофе и Wi-Fi." + FOOTER
    )
    await call.message.edit_text(text, reply_markup=back_kb(), parse_mode="Markdown")

@dp.callback_query(F.data == "order")
async def cb_order(call: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Химчистка (12 000 ₽)", callback_data="srv_Химчистка")],
        [InlineKeyboardButton(text="Полировка (25 000 ₽)", callback_data="srv_Полировка")],
        [InlineKeyboardButton(text="Бронеплёнка (35 000 ₽)", callback_data="srv_Бронеплёнка")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="menu")]
    ])
    await call.message.edit_text("Выберите интересующую услугу:" + FOOTER, reply_markup=kb)

@dp.callback_query(F.data.startswith("srv_"))
async def cb_service(call: types.CallbackQuery, state: FSMContext):
    service = call.data.split("_", 1)[1]
    await state.update_data(service=service)
    await state.set_state(DemoOrder.waiting_car)
    await call.message.edit_text(f"Выбрано: **{service}**\n\nНапишите марку и модель вашего авто:" + FOOTER, parse_mode="Markdown")

@dp.message(DemoOrder.waiting_car)
async def step_car(msg: types.Message, state: FSMContext):
    await state.update_data(car=msg.text)
    await state.set_state(DemoOrder.waiting_time)
    await msg.answer("Укажите удобный день и время для визита:" + FOOTER)

@dp.message(DemoOrder.waiting_time)
async def step_time(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    text = (
        "✅ **Заявка сформирована (режим демонстрации):**\n\n"
        f"• Услуга: {data.get('service')}\n"
        f"• Автомобиль: {data.get('car')}\n"
        f"• Время: {msg.text}\n\n"
        "В реальном боте эта заявка сразу улетает менеджеру в Telegram." + FOOTER
    )
    await msg.answer(text, reply_markup=back_kb(), parse_mode="Markdown")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    keep_alive()
    asyncio.run(main())
