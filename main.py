import logging
import random
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import aiohttp
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InputFile
import os

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
# Словарь для отслеживания промокодов, выданных пользователям
issued_promo_codes = {}

promo_codes = []

# Функция для проверки подписки и администраторства пользователя в паблике
async def check_membership(user_id):
    subscribed = await is_user_subscribed(user_id)
    admin_or_owner = await is_user_admin_or_owner(user_id)
    return subscribed or admin_or_owner
# Обработчик команды /start

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
            keyboard.add( youtube_button, instagram_button, vk_button, subscribe_button)

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





async def is_user_subscribed(user_id):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f'https://api.telegram.org/bot{API_TOKEN}/getChatMember',
            json={'chat_id': CHANNEL_ID, 'user_id': user_id}
        ) as response:
            data = await response.json()
            if response.status == 200:
                return data['result']['status'] == 'member'
            else:
                return False

# Функция для проверки, является ли пользователь администратором или владельцем паблика
async def is_user_admin_or_owner(user_id):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f'https://api.telegram.org/bot{API_TOKEN}/getChatMember',
            json={'chat_id': CHANNEL_ID, 'user_id': user_id}
        ) as response:
            data = await response.json()
            if response.status == 200:
                status = data['result']['status']
                return status in ['creator', 'administrator']
            else:
                return False

@dp.message_handler(commands=['code'])
async def code(message: types.Message):
    # Проверяем, является ли пользователь разрешенным для доступа к этой функции
    allowed_users = [5429082466, 713476634,832507232]  # Замените на свои ID пользователей
    user_id = message.from_user.id
    if user_id in allowed_users:
        # Показываем список доступных промокодов и кнопки для добавления и удаления промокодов
        if promo_codes:
            promo_codes_list = "\n".join([f"{index + 1}. {code}" for index, code in enumerate(promo_codes)])
            await message.answer(
                f"Список доступных промокодов:\n{promo_codes_list}\n\nЧто вы хотите сделать?",
                reply_markup=InlineKeyboardMarkup().row(
                    InlineKeyboardButton("Добавить промокод", callback_data="add_code"),
                    InlineKeyboardButton("Удалить промокод", callback_data="delete_code")
                )
            )
        else:
            await message.answer("Список доступных промокодов пуст.\n\nЧто вы хотите сделать?",
                                 reply_markup=InlineKeyboardMarkup().row(
                                     InlineKeyboardButton("Добавить промокод", callback_data="add_code")
                                 ))
    else:
        # Если пользователь не является разрешенным, отправляем ему сообщение об ошибке доступа
        await message.answer("Извините, у вас нет доступа к этой функции.")



def add_promo_code(code):
    promo_codes.append(code)

# Обработчик нажатия кнопки "Получить промокод"
@dp.callback_query_handler(lambda c: c.data == 'get_code')
async def get_code(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user_name = callback_query.from_user.first_name
    if promo_codes:
        # Проверяем, был ли уже выдан промокод пользователю
        if user_id in issued_promo_codes:
            # Если промокод уже выдан, отправляем тот же самый промокод
            await callback_query.message.answer(f"Твой промокод: {issued_promo_codes[user_id]}")
        else:
            # Если пользователь еще не получал промокод, выдаем ему рандомный промокод из списка и запоминаем его
            random_promo_code = random.choice(promo_codes)
            issued_promo_codes[user_id] = random_promo_code
            await callback_query.message.answer(f"Твой промокод: {random_promo_code}")
    else:
        # Если список promo_codes пуст, сообщаем об этом пользователю
        await callback_query.message.answer("Промокодов в данный момент нет.")



# Обработчик добавления бота в паблик
@dp.message_handler(content_types=['new_chat_members'])
async def on_new_chat_members(message: types.Message):
    for user in message.new_chat_members:
        if user.id == bot.id:  # Проверяем, что добавленный участник - это наш бот
            # Добавляем бота в список подписанных пользователей
            subscribed_users[message.chat.id] = True
            logging.info(f"Бот был добавлен в паблик {message.chat.title}")



# Обработчик нажатия кнопки "Удалить промокод"
@dp.callback_query_handler(lambda c: c.data == 'delete_code')
async def delete_code(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите индексы промокодов, которые нужно удалить (через пробел или запятую):")
    await PromoCodeStates.DELETE_PROMO_CODE.set()

# Обработчик текстового сообщения после запроса на удаление промокода
@dp.message_handler(state=PromoCodeStates.DELETE_PROMO_CODE)
async def process_delete_promo_code(message: types.Message, state: FSMContext):
    # Получаем текст сообщения и разделяем его на индексы
    indexes_str = message.text
    indexes = []
    try:
        # Пытаемся преобразовать индексы в числа
        indexes = [int(index.strip()) for index in indexes_str.replace(',', ' ').split()]
    except ValueError:
        # Если введены некорректные значения, отправляем сообщение об ошибке
        await message.answer("Некорректный ввод. Пожалуйста, введите индексы числами, разделенными пробелом или запятой.")
        return

    # Проверяем, все ли введенные индексы существуют в списке промокодов
    if any(index < 1 or index > len(promo_codes) for index in indexes):
        await message.answer("Некорректные индексы. Пожалуйста, выберите индексы из списка.")
        return

    # Удаляем промокоды по указанным индексам
    deleted_promo_codes = [promo_codes.pop(index - 1) for index in sorted(indexes, reverse=True)]
    await state.finish()

    # Формируем сообщение об успешном удалении
    deleted_promo_codes_str = '\n'.join(deleted_promo_codes)
    await message.answer(f"Промокоды успешно удалены:\n{deleted_promo_codes_str}")
# Обработчик нажатия кнопки "Добавить промокод"
@dp.callback_query_handler(lambda c: c.data == 'add_code')
async def add_code(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите новый промокод:")
    await PromoCodeStates.ADD_PROMO_CODE.set()

# Обработчик текстового сообщения после запроса на добавление промокода
@dp.message_handler(state=PromoCodeStates.ADD_PROMO_CODE)
async def process_add_promo_code(message: types.Message, state: FSMContext):
    new_code = message.text
    add_promo_code(new_code)
    await state.finish()
    await message.answer("Новый промокод успешно добавлен!")

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
