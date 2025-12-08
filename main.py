# main.py
import telebot
from telebot.types import (
    InlineKeyboardMarkup, InlineKeyboardButton
)
import logging
import time
import threading
from datetime import datetime
import traceback
import config
from admin import user_data
from config import admin_id
from db import *

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Инициализация бота с настройками
bot = telebot.TeleBot(
    token=config.token_main,
    parse_mode='HTML',  # Режим парсинга HTML
    threaded=True,  # Многопоточность
    num_threads=5  # Количество потоков
)
db = DatabaseManager(DB_CONFIG)

# Хранилище данных (можно заменить на БД)
user_sessions = {}
pending_messages = {}

def get_user_data(user_id):
    """Получает или создает данные пользователя"""
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            'chat_id': user_id
        }
    return user_sessions[user_id]

@bot.message_handler(commands=['start'])
def start_command(message):
    user_data = get_user_data(message.from_user.id)
    print(user_data)
    show_start_menu(user_data)


def show_start_menu(user_data):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(text='Ассортимент', callback_data='ass_or_tea_meant'),
        InlineKeyboardButton(text='Поддержка', callback_data='support'),
        InlineKeyboardButton(text='Вопросы и ответы', callback_data='QA'),
    )
    bot.send_message(chat_id=user_data['chat_id'], text='Главное меню:', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'QA')
def quest_n_answer(call):
    bot.answer_callback_query(call.id)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text='заглушка'))
    bot.send_message(chat_id=call.from_user.id, text='Выберите вопрос', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'ass_or_tea_meant')
def ass_or_tea_meant(call):
    bot.answer_callback_query(call.id)
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(text='Вязаные изделя', callback_data='goods:knitted_toys'),
        InlineKeyboardButton(text='3D печать', callback_data='goods:3d_printed'),
        InlineKeyboardButton(text='Другое', callback_data='goods:other'),
    )
    bot.send_message(chat_id=call.from_user.id, text='Выберите категорию', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('goods:'))
def show_goods(call):
    bot.answer_callback_query(call.id)
    good_type = call.data.split(':')[1]

    goods = db.select_actvie_ids_and_titles(good_type)
    markup = InlineKeyboardMarkup(row_width=1)
    for id, title in goods:
        markup.add(InlineKeyboardButton(text=title, callback_data=f'select_good:{id}'))
    bot.send_message(chat_id=call.from_user.id, text='Выберите товар', reply_markup=markup)



@bot.callback_query_handler(func=lambda call: call.data.startswith('select_good:'))
def select_good(call):
    bot.answer_callback_query(call.id)
    id = call.data.split(':')[1]
    print(db.show_good_by_id(id))
    id, title, text, price, photo, type, count = db.show_good_by_id(id)[0]
    text = f'{title}\n\n{text}\n{price}'
    markup = InlineKeyboardMarkup(InlineKeyboardButton(text='Заказать', callback_data=f'purchase:{id}'))
    bot.send_photo(chat_id=call.from_user.id, photo=open(photo, 'rb'), caption=text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('purchase:'))
def purchase_start(call):
    bot.answer_callback_query(call.id)
    id = call.data.split(':')[1]
    bot.send_message(chat_id=call.from_user.id, text='Введите данные: ФИО, номер телефона, email')
    bot.register_next_step_handler(call.message, purchase_1, id)

def purchase_1(message, id):
    user_data = get_user_data(message.from_user.id)
    user_data['bio'] = message.text
    id, title, text, price, photo, type, count = db.show_good_by_id(id)[0]
    text = f'{title}\n\n{text[:30]}...\n{price}\n\n{message.text}'
    markup = InlineKeyboardMarkup(InlineKeyboardButton(text='Подтвердить заявку', callback_data=f'confirm:{id}'))
    bot.send_photo(chat_id=message.from_user.id, photo=open(photo, 'rb'), caption=text, reply_markup=markup)
    user_data['order'] = text


@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm:'))
def confirm_purchase(call):
    user_data = get_user_data(call.from_user.id)
    bot.answer_callback_query(call.id)
    id = call.data.split(':')[1]
    text = user_data['order']
    text += f'\n{call.from_user.username}'
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("✅ Принять", callback_data=f'accepted:{id}'),
        InlineKeyboardButton("❌ Отклонить", callback_data=f'declined:{id}'),
        row_width=2)
    bot.send_message(chat_id=admin_id, text=text)


@bot.callback_query_handler(func=lambda call: call.data.startswith('accepted:'))
def accpeted(call):


if __name__ == '__main__':
    print('бот запущен')
    bot.infinity_polling()
