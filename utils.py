from keyboards import start_keyboard
from models import add_user
from messages import register_successfully


# --- УТИЛИТЫ ----------------------------------------------------------------------------------------------------------


# функция регистрации пользователя, если ранее он не был зарегистрирован
async def register_util(callback, role):
    # добавляем пользователя в базу данных
    await add_user(callback.from_user.id, callback.from_user.first_name, role)
    # отвечаем пользователю и выводим клавиатуру «главное меню»
    await callback.message.edit_text(
        text=register_successfully, parse_mode='HTML', reply_markup=start_keyboard
    )


# функция перевода часов формата hh:mm в секунды
async def seconds_util(message):
    try:
        return sum(x * int(t) for x, t in zip([3600, 60, 1], message.text.split(":")))
    except:
        return 0
