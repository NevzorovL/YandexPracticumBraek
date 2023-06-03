# импорт библиотек
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# импорт файлов
from callbackdata import *


# ------------------------------------------------------------------------------------------------------- КЛАВИАТУРЫ ---


# клавиатура главного меню
start_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    # добавляем две кнопки вверх
    [InlineKeyboardButton(text='Запланировать перерыв',
                          callback_data=start_callback.new('schedule_break')),
     InlineKeyboardButton(text='Отменить перерыв',
                          callback_data=start_callback.new('cancel_break'))],
    # добавляем две кнопки вниз
    [InlineKeyboardButton(text='Занятые места',
                          callback_data=start_callback.new('taken_place')),
     InlineKeyboardButton(text='Описание',
                          callback_data=start_callback.new('description'))]
])


# клавиатура регистрации
register_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    # добавляем три кнопки вряд
    [InlineKeyboardButton(text='DA',
                          callback_data=role_callback.new('da')),
    InlineKeyboardButton(text='DS',
                         callback_data=role_callback.new('ds')),
    InlineKeyboardButton(text='Free',
                         callback_data=role_callback.new('free'))]
])


# клавиатура с кнопкой «Назад»
back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    # добавляем кнопку
    [InlineKeyboardButton(text='Назад',
                          callback_data=back_callback.new('back'))]
])
