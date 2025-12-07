# admin.py
import telebot
# from pyexpat.errors import messages
# from telebot.apihelper import send_message
from telebot.types import (
    InlineKeyboardMarkup, InlineKeyboardButton
)
import logging
# import time
# import threading
# from datetime import datetime
# import traceback
import config
import os
from utility import get_user_data, add_qa, load_qa_dict, delete_qa
import json

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
    token=config.token_admin,
    parse_mode='HTML',  # Режим парсинга HTML
    threaded=True,  # Многопоточность
    num_threads=5  # Количество потоков
)

# Хранилище данных (можно заменить на БД)
user_data = {}
pending_messages = {}
good_data = {}


@bot.message_handler(commands=['start'])
def start_command(message):
    user_data = get_user_data(message.from_user.id)
    return show_start_menu(user_data)
    # bot.register_next_step_handler(message, show_start_menu, user_data)


def show_start_menu(user_data):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(text='Редактировать наличие товаров', callback_data='good_manage'),
        InlineKeyboardButton(text='Редактировать вопросы-ответы', callback_data='qa_manage'),
    )
    bot.send_message(chat_id=user_data['chat_id'], text='Главное меню:', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'qa_manage')
def qa_manage(call):
    bot.answer_callback_query(call.id)
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(text='Добавить вопрос', callback_data='qa_add'),
        InlineKeyboardButton(text='Удалить вопрос', callback_data='qa_delete'),
    )
    bot.send_message(chat_id=call.from_user.id, text='Что делать?', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'qa_add')
def qa_add(call):
    bot.answer_callback_query(call.id)
    bot.send_message(chat_id=call.from_user.id, text='Введи вопрос')
    bot.register_next_step_handler(call.message, qa_add_1)


def qa_add_1(message):
    question = message.text
    bot.send_message(chat_id=message.from_user.id, text='Введи ответ')
    bot.register_next_step_handler(message, qa_add_2, question)


def qa_add_2(message, question):
    answer = message.text
    add_qa(question, answer)
    bot.send_message(chat_id=message.from_user.id, text=f'Добавлен вопрос:\n\n{question}\n\n{answer}')
    return show_start_menu(get_user_data(message.from_user.id))


@bot.callback_query_handler(func=lambda call: call.data == 'qa_delete')
def qa_delete(call):
    bot.answer_callback_query(call.id)
    data = load_qa_dict()
    markup = InlineKeyboardMarkup(row_width=1)
    for q, a in data.items():
        markup.add(InlineKeyboardButton(text=q, callback_data=f'qa_delete_1:{q}'))

    bot.send_message(chat_id=call.from_user.id, text='Выбери вопрос который хочешь удалить', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('qa_delete_1:'))
def qa_delete_1(call):
    bot.answer_callback_query(call.id)
    question = call.data.split(':')[1]
    bot.send_message(chat_id=call.from_user.id, text=f'Введи <code>Подтвердить</code> чтобы удалить вопрос')
    bot.register_next_step_handler(call.message, qa_delete_2, question)


def qa_delete_2(message, question):
    if message.text == 'Подтвердить':
        delete_qa(question)
        bot.send_message(chat_id=message.from_user.id, text=f'Удален вопрос: {question}')
        return show_start_menu(get_user_data(message.from_user.id))
    else:
        bot.send_message(chat_id=message.from_user.id, text=f'Отмена удаления')
        return show_start_menu(get_user_data(message.from_user.id))  # qa_manage


@bot.callback_query_handler(func=lambda call: call.data == 'good_manage')
def good_manage(call):
    bot.answer_callback_query(call.id)
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(text='Добавить товар', callback_data='good_add'),
        InlineKeyboardButton(text='Удалить товар', callback_data='good_delete'),
    )
    bot.send_message(chat_id=call.from_user.id, text='Что делать', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'good_add')
def good_add(call):
    bot.answer_callback_query(call.id)
    bot.send_message(chat_id=call.from_user.id, text='Введи заголовок')
    bot.register_next_step_handler(call.message, good_add_1)


def good_add_1(message):
    good_data['title'] = message.text
    bot.send_message(chat_id=message.from_user.id, text='Введи описание')
    bot.register_next_step_handler(message, good_add_2)


def good_add_2(message):
    good_data['text'] = message.text
    bot.send_message(chat_id=message.from_user.id, text='Введи стоимость')
    bot.register_next_step_handler(message, good_add_3)


def good_add_3(message):
    good_data['price'] = message.text
    bot.send_message(chat_id=message.from_user.id, text='Добавь фото')
    bot.register_next_step_handler(message, good_add_photo)


def good_add_photo(message):
    # Получаем информацию о фото (последнее фото - самое большое качество)
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    # Определяем путь к папке media относительно текущего файла
    # Получаем директорию текущего файла (admin.py)
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Папка media находится в той же директории
    media_folder = os.path.join(current_dir, 'media')

    # Создаем безопасное имя файла
    file_id = message.photo[-1].file_id
    safe_filename = file_id.replace('/', '_').replace('\\', '_') + '.jpg'

    # Формируем полный путь
    src = os.path.join(media_folder, safe_filename)

    # Сохраняем файл
    with open(src, 'wb') as new_file:
        new_file.write(downloaded_file)

    # Сохраняем путь к файлу
    good_data['photo'] = src
    bot.reply_to(message, "Фото добавлено")
    # text = good_data['title'] + '\n' + good_data['text'] + '\n'  + good_data['price']
    # bot.send_photo(chat_id=message.chat.id, photo=open(src, 'rb'), caption=text)


def good_set_type(message):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(text='Вязанные изделия', callback_data='good_set_type:0'),
        InlineKeyboardButton(text='3D печать', callback_data='good_set_type:1'),
        InlineKeyboardButton(text='Другое', callback_data='good_set_type:2'),
    )
    bot.send_message(chat_id=message.chat.id, text='Выбери тип товара', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('good_set_type:'))
def good_set_type_2(call):
    bot.answer_callback_query(call.id)
    type = call.data.split(':')[1]
    text = good_data['title'] + '\n' + good_data['text'] + '\n'  + good_data['price'] + '\n' + type
    bot.send_photo(chat_id=call.chat.id, photo=open(good_data['photo'], 'rb'), caption=text)

if __name__ == '__main__':
    print('бот запущен')
    bot.infinity_polling()
