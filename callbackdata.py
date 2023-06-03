# импорт библиотек
from aiogram.utils.callback_data import CallbackData


# --- 1 Уровень Блоков ---------------------------------------------------------------------------------- КЛАВИАТУРЫ ---


# обработчик регистрации
role_callback = CallbackData('register', 'action')

# обработчик главного меню
start_callback = CallbackData('start', 'action')

# обработчик кнопки «Назад»
back_callback = CallbackData('back', 'action')
