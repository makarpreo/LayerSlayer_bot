#main.py
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
from utility import get_user_data

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

# Хранилище данных (можно заменить на БД)
user_data = {}
pending_messages = {}


@bot.message_handler(commands=['start'])
def start_command(message):
    user_data = get_user_data(message.from_user.id)
    show_start_menu(user_data)


def show_start_menu(user_data):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(text='Ассортимент', callback_data='assortment'),
        InlineKeyboardButton(text='Поддержка', callback_data='support'),
        InlineKeyboardButton(text='Вопросы и ответы', callback_data='QA'),
    )
    bot.send_message(chat_id=user_data['chat_id'], text='Главное меню:', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'QA')
def quest_n_answer(call):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text='заглушка'))
    bot.send_message(chat_id=call.from_user.id, text='Выберите вопрос', reply_markup=markup)

if __name__ == '__main__':
    print('бот запущен')
