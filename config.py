from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher


# -------------------------------------------------------------------------------------------------- Инициализация -----


# токен бота
TOKEN_API = '5640315326:AAFwunY8aFUofrM3DI4W0UxAlpv89HpvmPQ'


# машина состояний
storage = MemoryStorage()


# инициализация бота
bot = Bot(token=TOKEN_API)
dp = Dispatcher(bot=bot, storage=storage)