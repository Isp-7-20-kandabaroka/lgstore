import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import aiohttp
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InputFile
import os
import random
import string
import pandas as pd

API_TOKEN = '7480809961:AAG5S-O_6bV8QFkknOYPTkUk91zVag_nL_U'

# Инициализация бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# ID вашего паблика
CHANNEL_ID = -1001801607613
welcome_text = "Дарим за подписку на все соц сети пушечный промокод, который можно использовать при оформлении заказа."
subscribed_users = {}

class PromoCodeStates(StatesGroup):
    DELETE_PROMO_CODE = State()
    ADD_PROMO_CODE = State()

issued_promo_codes = {}

promo_codes = []

# Функция для генерации случайного промокода
def generate_promo_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

# Функция для записи данных в Excel
def save_to_excel(data, file_path="promo_codes.xlsx"):
    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False)

# Обработчик команды /rm
@dp.message_handler(commands=['rm'])
async def change_welcome_text(message: types.Message):
    global welcome_text  # Используем глобальное объявление для изменения переменной
    # Проверяем, принадлежит ли пользователь к списку allowed_users
    allowed_users = [5429082466, 713476634, 832507232, 1036129367]  # Замените на свои ID пользователей
    if message.from_user.id in allowed_users:
        # Получаем новый текст из сообщения пользователя
        new_text = message.text.split('/rm', 1)[-1].strip()
        # Присваиваем новый текст переменной welcome_text
        welcome_text = new_text
        print("Текст приветствия успешно изменен:", welcome_text)  # Отладочный вывод
        await message.answer("Текст приветствия успешно изменен.")
    else:
        await message.answer("У вас нет прав для выполнения этой команды.")

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    global new_text  # Используем глобальную переменную
    # Проверяем подписку пользователя
    subscribed = await is_user_subscribed(user_id)

    if subscribed:
        keyboard = InlineKeyboardMarkup(row_width=1)

        # Кнопки
        subscribe_button = InlineKeyboardButton(text="Наш ТГ 📢", url="https://t.me/legit_check_store")
        get_code_button = InlineKeyboardButton(text="Получить промокод", callback_data="get_code")

        # Новые кнопки ссылки
        youtube_button = InlineKeyboardButton(text="Наш YouTube 📺",
                                              url="https://youtube.com/@Legit_check_store?si=dU7TDbdvNJZEeWVP")
        instagram_button = InlineKeyboardButton(text="Наш Instagram 📸",
                                                url="https://www.instagram.com/legit.check.store?igsh=MWN3ZGs2OTUzYjI1bg%3D%3D&utm_source=qr")
        vk_button = InlineKeyboardButton(text="Наш VK 📘", url="https://vk.com/lcstore_vk")

        # Добавляем кнопки в клавиатуру
        keyboard.add(subscribe_button, youtube_button, instagram_button, vk_button, get_code_button)

        # Путь к файлу с фотографией
        photo_path = "main.jpeg"

        # Отправка фото с клавиатурой
        await message.answer_photo(
            photo=InputFile(os.path.abspath(photo_path)),
            caption=f"С Возвращением в Legit Check Store!🔥 \n- - - - - -\n{welcome_text}\n- - - - - -\nЖми получить промокод",
            reply_markup=keyboard
        )
    else:
        keyboard = InlineKeyboardMarkup(row_width=1)

        # Кнопки
        subscribe_button = InlineKeyboardButton(text="Наш тг 📢", url="https://t.me/legit_check_store")
        # Новые кнопки ссылки
        youtube_button = InlineKeyboardButton(text="Наш YouTube 📺",
                                              url="https://youtube.com/@Legit_check_store?si=dU7TDbdvNJZEeWVP")
        instagram_button = InlineKeyboardButton(text="Наш Instagram 📸",
                                                url="https://www.instagram.com/legit.check.store?igsh=MWN3ZGs2OTUzYjI1bg%3D%3D&utm_source=qr")
        vk_button = InlineKeyboardButton(text="Наш VK 📘", url="https://vk.com/lcstore_vk")

        # Добавляем кнопки в клавиатуру
        keyboard.add(youtube_button, instagram_button, vk_button, subscribe_button)

        # Путь к файлу с фотографией
        photo_path = "main.jpeg"
        # Отправка фото с клавиатурой
        await message.answer_photo(
            photo=InputFile(os.path.abspath(photo_path)),
            caption=f"Приветствуем в Legit Check Store! 🔥\n- - - - - -\n{welcome_text}",
            reply_markup=keyboard
        )
        await message.answer(
            "После подписки на все источники нажми на синюю надпись -> /start"
        )

@dp.callback_query_handler(lambda c: c.data == 'get_code')
async def process_callback_get_code(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user_name = callback_query.from_user.first_name
    if user_id in issued_promo_codes:
        promo_code = issued_promo_codes[user_id]
        await bot.send_message(callback_query.from_user.id, f"Ваш промокод: {promo_code}")
    else:
        promo_code = generate_promo_code()
        issued_promo_codes[user_id] = promo_code
        promo_data = {
            'user_id': user_id,
            'user_name': user_name,
            'promo_code': promo_code
        }
        promo_codes.append(promo_data)
        save_to_excel(promo_codes)
        await bot.send_message(callback_query.from_user.id, f"Поздравляем! Ваш новый промокод: {promo_code}")

@dp.message_handler(commands=['list'])
async def send_promo_list(message: types.Message):
    if message.from_user.id in [5429082466, 713476634, 832507232, 1036129367]:  # Замените на свои ID пользователей
        file_path = "promo_codes.xlsx"
        if os.path.exists(file_path):
            await message.answer_document(InputFile(file_path))
        else:
            await message.answer("Таблица промокодов еще не создана.")
    else:
        await message.answer("У вас нет прав для выполнения этой команды.")

async def is_user_subscribed(user_id):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f'https://api.telegram.org/bot{API_TOKEN}/getChatMember',
            json={'chat_id': CHANNEL_ID, 'user_id': user_id}
        ) as response:
            data = await response.json()
            logging.info(f'getChatMember response: {data}')  # Отладочный вывод
            if response.status == 200:
                status = data['result']['status']
                logging.info(f'User {user_id} status: {status}')
                return status in ['member', 'creator', 'administrator']
            else:
                logging.error(f'Error checking subscription: {data}')
                return False

# Функция для проверки, является ли пользователь администратором или владельцем паблика
async def is_user_admin_or_owner(user_id):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f'https://api.telegram.org/bot{API_TOKEN}/getChatMember',
            json={'chat_id': CHANNEL_ID, 'user_id': user_id}
        ) as response:
            data = await response.json()
            logging.info(f'getChatMember admin/owner response: {data}')  # Отладочный вывод
            if response.status == 200:
                status = data['result']['status']
                logging.info(f'User {user_id} admin status: {status}')
                return status in ['creator', 'administrator']
            else:
                logging.error(f'Error checking admin/owner status: {data}')
                return False

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
