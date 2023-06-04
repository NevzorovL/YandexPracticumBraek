# импорт библиотек
from aiogram.utils.exceptions import BotBlocked
from aiogram.dispatcher import FSMContext
from aiogram import types, executor
import asyncio
import time

# импорт файлов
from notifications import get_notifications
from keyboards import *
from config import *
from models import *
from utils import *


# -------------------------------------------------------------------------------------------------------- КОМАНДЫ -----


# обработчик команды «START»
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message) -> None:
    # удаляем сообщение «/start», которое прислал нам пользователь
    await message.delete()
    # ищем пользователя в базе данных
    found_user = await find_user(message.from_user.id)
    # если пользователь есть
    if found_user:
        # отвечаем пользователю и выводим клавиатуру «главное меню»
        await message.answer(
            text=main_menu(
                message.from_user.first_name, await get_break_time(message.from_user.id)
            ), parse_mode='HTML', reply_markup=start_keyboard
        )
    # если пользователя нет
    elif not found_user:
        # отвечаем пользователю и выводим клавиатуру «регистрация»
        await message.answer(text=register, parse_mode='HTML', reply_markup=register_keyboard)


# обработчик команды «REG»
@dp.message_handler(commands=['reg'])
async def start_command(message: types.Message) -> None:
    # удаляем сообщение «/start», которое прислал нам пользователь
    await message.delete()
    # отвечаем пользователю и выводим клавиатуру «регистрация»
    await message.answer(text=register, parse_mode='HTML', reply_markup=register_keyboard)


# ------------------------------------------------------------------------------------------------------- КОЛЛБЕКИ -----


# обработчик события «Регистрация»
@dp.callback_query_handler(role_callback.filter())
async def register_callback(callback: types.CallbackQuery, callback_data: dict) -> None:
    # обработчик выбора «DA» на клавиатуре
    if callback_data['action'] == 'da':
        # функция регистрации роли «da» для пользователя
        await register_util(callback, 'da')
    # обработчик выбора «DS» на клавиатуре
    elif callback_data['action'] == 'ds':
        # функция регистрации роли «ds» для пользователя
        await register_util(callback, 'ds')
    # обработчик выбора «Free» на клавиатуре
    elif callback_data['action'] == 'free':
        # функция регистрации роли «free» для пользователя
        await register_util(callback, 'free')


# обработчик кнопок «Запланировать перерыв, отменить перерыв, занятые места, описание»
@dp.callback_query_handler(start_callback.filter())
async def start_callback(callback: types.CallbackQuery, callback_data: dict) -> None:
    # обработчик выбора «Запланировать перерыв» на клавиатуре
    if callback_data['action'] == 'schedule_break':
        # обращаемся к форме, в которую пользователь должен ввести время
        await GetBraceTime.time.set()
        # просим пользователя ввести время
        await callback.message.edit_text(
            text=time_choice, parse_mode='HTML'
        )
        time.sleep(5)
        await callback.message.delete()
    # обработчик выбора «Отменить перерыв» на клавиатуре
    elif callback_data['action'] == 'cancel_break':
        # изменяем текст и клавиатуру внутри сообщения
        await callback.message.edit_text(
            text=await delete_break(callback.from_user.id), parse_mode='HTML', reply_markup=start_keyboard
        )
    # обработчик выбора «Занятые места» на клавиатуре
    elif callback_data['action'] == 'taken_place':
        # изменяем текст и клавиатуру внутри сообщения
        await callback.message.edit_text(
            text=await who_on_break(), parse_mode='HTML', reply_markup=back_keyboard
        )
    # обработчик выбора «Описание» на клавиатуре
    elif callback_data['action'] == 'description':
        # изменяем текст и клавиатуру внутри сообщения
        await callback.message.edit_text(
            text=description, parse_mode='HTML', reply_markup=back_keyboard
        )


# обработчик кнопки «Назад»
@dp.callback_query_handler(back_callback.filter())
async def back_callback(callback: types.CallbackQuery, callback_data: dict) -> None:
    await callback.message.delete()
    # обработчик выбора «Назад» на клавиатуре
    if callback_data['action'] == 'back':
        # изменяем текст и клавиатуру внутри сообщения
        await callback.message.answer(
            text=main_menu(
                callback.from_user.first_name, await get_break_time(callback.from_user.id)
            ), parse_mode='HTML', reply_markup=start_keyboard
        )

# ------------------------------------------------------------------------------------------------------- ФОРМЫ --------


# форма взятия перерыва
@dp.message_handler(state=GetBraceTime.time)
async def get_break(message: types.Message, state: FSMContext):
    # функция перевода формата hh:mm в секунды
    seconds = await seconds_util(message)
    await message.delete()
    # если секунды > 0, то пользователь ввел корректный формат времени
    if seconds != 0:
        # ищем пересечения перерывов пользователей одной группы
        intersect = await find_intersect(message.from_user.id, seconds)
        # если пересечение есть, то нужно выбрать другое время
        if intersect:
            await message.answer(
                text=intersection, parse_mode='HTML', reply_markup=back_keyboard
            )
        # если пересечения нет, то можно выбрать данное время
        elif not intersect:
            # функция вносит перерыв в базу данных и пишет пользователю
            await message.answer(
                text=await take_break(message.from_user.id, seconds, seconds + 3600), parse_mode='HTML', reply_markup=back_keyboard
            )
    # если секунды = 0, то пользователь ввел некорректный формат времени
    elif seconds == 0:
        await message.answer(
            text=time_error, parse_mode='HTML', reply_markup=back_keyboard
        )
    # завершаем обработку формы
    await state.finish()


# --------------------------------------------------------------------------------------------------------- ПОДВАЛ -----


# обрабатывает ошибки при блокировке бота
@dp.errors_handler(exception=BotBlocked)
async def bot_blocked_error(update: types.Update, exception: BotBlocked) -> bool:
    print('Один из пользователей заблокировал бота в момент отправки команды!')
    return True


# запускается при старте бота
async def on_startup(_):
    # подключаем базу данных
    await database()
    #loop = asyncio.get_event_loop()
    asyncio.create_task(get_notifications())
    print('Бот Яндекс.Перерывы — запущен!')


# запускается при выключении бота
async def on_shutdown(_):
    # функция сброса занятых перерывов и меток уведомлений в конце дня
    await delete_all_breaks()
    print('Бот Яндекс.Перерывы — выключен!')


# бот запускается только при запуске данного файла
if __name__ == '__main__':
    executor.start_polling(
        dispatcher=dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown
    )
