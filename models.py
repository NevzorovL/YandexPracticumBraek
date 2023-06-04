# импорт библиотек
from aiogram.dispatcher.filters.state import State, StatesGroup
import sqlite3 as sq

# импорт файлов
from messages import *


# --- БАЗА ДАННЫХ ------------------------------------------------------------------------------------------------------


# функция создания базы данных
async def database():
    """
    Поля базы данных «database.db»:
    id:VARCHAR — уникальный код пользователя из телеграмм,
    name:TEXT — имя пользователя,
    role:TEXT — роль пользователя,
    break_from:INTEGER — время начала перерыва,
    break_to:INTEGER — время конца перерыва
    """
    global db, cur
    db = sq.connect('database.db')
    cur = db.cursor()
    # если ранее база не была создана, то создаем ее
    cur.execute(
        'CREATE TABLE IF NOT EXISTS '
        'users(id VARCHAR PRIMARY KEY, name TEXT, role TEXT, break_from INTEGER, break_to INTEGER, notification INTEGER)'
    )
    db.commit()


# функция поиска пользователя в базе данных
async def find_user(user_id):
    # ищем пользователя по его уникальному id
    user = cur.execute(
        "SELECT id FROM users WHERE id = '{id}'".format(
            id=user_id)
    ).fetchone()
    # если пользователь существует, отвечаем и выводим клавиатуру «главное меню»
    if user:
        return True
    # если пользователь не существует, отвечаем и выводим клавиатуру «регистрация»
    elif not user:
        return False
    # обработчик ошибок для админа
    else:
        print('Возникала ошибка на стадии поиска пользователя!')


# функция добавления пользователя в базу данных
async def add_user(user_id, name, role, break_from=0, break_to=0, notification=0):
    # ищем пользователя по его уникальному id
    user = cur.execute(
        "SELECT id FROM users WHERE id = '{id}'".format(
            id=user_id)
    ).fetchone()
    # если пользователя нет в базе, заносим данные о нем
    if not user:
        cur.execute(
            "INSERT INTO users VALUES('{id}', '{name}', '{role}', '{break_from}', '{break_to}', '{notification}')".format(
                id=user_id, name=name, role=role, break_from=break_from, break_to=break_to, notification=notification)
        )
        db.commit()
    # обработчик ошибок для админа
    else:
        print('Возникала ошибка на стадии добавления пользователя!')


# функция проверки пересечения времени в одной группе
async def find_intersect(user_id, break_from):
    # ищем роль пользователя по его уникальному id
    user_role = cur.execute(
        "SELECT role FROM users WHERE id = '{id}'".format(
            id=user_id)
    ).fetchone()
    # ищем все перерывы для роли пользователя
    users_break = cur.execute(
        "SELECT break_from FROM users WHERE role = '{role}'".format(
            role=user_role[0])
    ).fetchall()
    # просчитываем пересечения множеств
    for values in users_break:
        # если длинна списка > 0, то пересечение обнаружено
        if len(list(set(range(values[0], values[0] + 3600)) & set(range(break_from, break_from + 3600)))) > 0:
            return True
    # если длинна списка < 0, то пересечение не обнаружено
    return False


# функция взятия перерыва пользователем
async def take_break(user_id, break_from, break_to):
    # ищем, брал ли пользователь перерыв ранее
    user_break = cur.execute(
        "SELECT break_from FROM users WHERE id = '{id}'".format(
            id=user_id)
    ).fetchone()
    # если пользователь не брал перерыв ранее
    if user_break == (0,):
        cur.execute(
            "UPDATE users SET break_from = {break_from}, break_to = {break_to} WHERE id = '{id}'".format(
                id=user_id, break_from=break_from, break_to=break_to)
        )
        db.commit()
        # возвращаем сообщение
        return break_successfully
    # если пользователь брал перерыв ранее
    elif user_break != (0,):
        # возвращаем сообщение
        return break_earlier
    # обработчик ошибок для админа
    else:
        print('Возникала ошибка на стадии взятия перерыва!')


# функция удаления перерыва пользователем
async def delete_break(user_id):
    # ищем, брал ли пользователь перерыв ранее
    user_break = cur.execute(
        "SELECT break_from FROM users WHERE id = '{id}'".format(
            id=user_id)
    ).fetchone()
    # если пользователь не брал перерыв ранее
    if user_break != (0,):
        cur.execute(
            "UPDATE users SET break_from = 0, break_to = 0, notification = 0 WHERE id = '{id}'".format(
            id=user_id)
        )
        db.commit()
        # возвращаем сообщение
        return break_cancellation
    # если пользователь брал перерыв ранее
    elif user_break == (0,):
        # возвращаем сообщение
        return break_cancellation_error
    # обработчик ошибок для админа
    else:
        print('Возникала ошибка на стадии удаления перерыва!')


# функция перевода секунд в формат hh:mm
def hours_util(seconds):
    # ищем секунды
    seconds = seconds % (24 * 3600)
    # ищем часы
    hours = seconds // 3600
    # ищем минуты
    minutes = (seconds % 3600) // 60
    # если минут > 0, то выводим hh:mm
    if minutes > 0:
        return f'{hours}:{minutes}'
    # если минуты = 0, то выводим hh:00, иначе получилось бы hh:0
    else:
        return f'{hours}:00'


# функция вывода времени перерыва пользователя
async def get_break_time(user_id):
    users_break = cur.execute(
        "SELECT break_from FROM users WHERE id = '{id}'".format(
            id=user_id)
    ).fetchone()
    return users_break[0]


# функция вывода информации о пользователях, находящихся на перерыве
async def who_on_break():
    # выбираем всех пользователей
    user_break = cur.execute(
        "SELECT name, role, break_from, break_to FROM users ORDER BY role"
    ).fetchall()
    # создаем заготовку сообщения
    message = ''
    da_line = 0
    ds_line = 0
    free_line = 0
    # перебираем всех пользователей
    for value in user_break:
        # если пользователь взял перерыв, то вносим его в список
        if value[2] > 0:
            if value[1] == 'da':
                if da_line == 0:
                    message = message + f'\n\n<b>Data Analytics</b>\n------------------------------\n'
                    da_line = da_line + 1
                message = message + f'{value[0]}: {hours_util(value[2])}-{hours_util(value[3])}\n'
            elif value[1] == 'ds':
                if ds_line == 0:
                    message = message + f'\n\n<b>Data Scientists</b>\n------------------------------\n'
                    ds_line = ds_line + 1
                message = message + f'{value[0]}: {hours_util(value[2])}-{hours_util(value[3])}\n'
            elif value[1] == 'free':
                if free_line == 0:
                    message = message + f'\n\n<b>Free Guys</b>\n------------------------------\n'
                    free_line = free_line + 1
                message = message + f'{value[0]}: {hours_util(value[2])}-{hours_util(value[3])}\n'
            else:
                print('Возникла ошибка на стадии создания списка пользователей на перерыве!')
    return message


# функция сброса занятых перерывов в конце дня
async def delete_all_breaks():
    cur.execute(
        "UPDATE users SET break_from = 0, break_to = 0, notification = 0"
    )
    db.commit()


# функция вывода id, времени и меток перерывов о всех пользователях для работы уведомлений
async def get_information_about_users():
    information = cur.execute(
        "SELECT id, break_from, notification FROM users WHERE break_from > 0"
    ).fetchall()

    return information


# метка о пришедшем уведомлении
async def notification_received(user_id):
    cur.execute(
        "UPDATE users SET notification = 1 WHERE id = '{id}'".format(
            id=user_id
        )
    )
    db.commit()


# --------------------------------------------------------------------------------------------------------- ФОРМЫ ------

# форма для ввода пользователем времени перерыва
class GetBraceTime(StatesGroup):
    time = State()
