import sqlite3, telebot
from telebot import types
from newsapi import NewsApiClient

telebot_token = ""
news_api_token = ""
category = {'business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology'}


def new_db():
    connection = sqlite3.connect('bot.db')
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                            (id	INTEGER PRIMARY KEY AUTOINCREMENT, user INTEGER NOT NULL)
                   ''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS categories
                            (id	INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT NOT NULL, user_id INTEGER NOT NULL,
                            FOREIGN KEY(user_id) REFERENCES users(id))
                   ''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS keywords
                            (id	INTEGER PRIMARY KEY AUTOINCREMENT, keyword TEXT NOT NULL, user_id INTEGER NOT NULL,
                            FOREIGN KEY(user_id) REFERENCES users(id))
                   ''')
    connection.commit()
    connection.close()

def add_user(id):
    connection = sqlite3.connect('bot.db')
    cursor = connection.cursor()
    cursor.execute(f'''INSERT INTO users (user) SELECT ('{id}') WHERE NOT EXISTS (SELECT 1 FROM users WHERE user = '{id}')''')
    connection.commit()
    connection.close()

def news_category(id):
    connection = sqlite3.connect('bot.db')
    cursor = connection.cursor()
    categories = cursor.execute(f'''SELECT category FROM categories JOIN users ON users.id = user_id WHERE users.user = {id}''').fetchall()
    set_categories = []
    for x in categories:
        set_categories.insert(-1, x[0])
    connection.commit()
    connection.close()
    return set_categories

def news_q(id):
    connection = sqlite3.connect('bot.db')
    cursor = connection.cursor()
    q = cursor.execute(f'''SELECT keyword FROM keywords JOIN users ON users.id = user_id WHERE users.user = {id}''').fetchall()
    set_q = []
    for x in q:
        set_q.insert(-1, x[0])
    connection.commit()
    connection.close()
    return set_q

def del_category(id, category):
    connection = sqlite3.connect('bot.db')
    cursor = connection.cursor()
    cursor.execute(f'''DELETE FROM categories WHERE category = "{category}" and user_id = (SELECT id FROM users WHERE user = {id})''')
    connection.commit()
    connection.close()

def del_q(id, q):
    connection = sqlite3.connect('bot.db')
    cursor = connection.cursor()
    cursor.execute(f'''DELETE FROM keywords WHERE keyword = "{q}" and user_id = (SELECT id FROM users WHERE user = {id})''')
    connection.commit()
    connection.close()

def add_category(id, category):
    connection = sqlite3.connect('bot.db')
    cursor = connection.cursor()
    cursor.execute(f'''INSERT INTO categories (category, user_id) VALUES ("{category}", (SELECT id FROM users WHERE user = {id}))''')
    connection.commit()
    connection.close()

def add_q(id, q):
    connection = sqlite3.connect('bot.db')
    cursor = connection.cursor()
    cursor.execute(f'''INSERT INTO keywords (keyword, user_id) VALUES ("{q}", (SELECT id FROM users WHERE user = {id}))''')
    connection.commit()
    connection.close()

def news_api_q(q):
    newsapi = NewsApiClient(api_key=news_api_token)
    all_articles = newsapi.get_everything(q=q)
    return all_articles

def news_api_category(category):
    newsapi = NewsApiClient(api_key=news_api_token)
    top_headlines = newsapi.get_top_headlines(category=category)
    return top_headlines

def add_keyboard(keyboard, categories):
    category = {'business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology'}
    s = set(category) & set(categories)
    print(s)
    for x in s:
        print(x)
        keyboard.row(x)
    return keyboard

new_db()

bot = telebot.TeleBot(telebot_token, parse_mode=None)

def main():
    markup = types.ReplyKeyboardMarkup(True)
    key1 = types.KeyboardButton('Подписки по категориям')
    key2 = types.KeyboardButton('Подписки по ключевым словам')
    markup.add(key1)
    markup.add(key2)
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    add_user(user_id)
    user_name = message.from_user.username
    bot.send_message(message.chat.id, 'Привет, ' + str(user_name), reply_markup=main())

flag = False
@bot.message_handler(content_types=['text'])
def cont(message):
    global flag
    if message.text == 'Подписки по категориям':
        keyboard = telebot.types.ReplyKeyboardMarkup(True)
        keyboard.row('Посмотреть подписку')
        keyboard.row('Добавить подписку', 'Удалить подписку')
        bot.send_message(message.chat.id, "Выберите действие", reply_markup=keyboard)

    elif message.text == 'Подписки по ключевым словам':
        keyboard = telebot.types.ReplyKeyboardMarkup(True)
        keyboard.row('Посмотреть подборку')
        keyboard.row('Добавить ключевое слово', 'Удалить ключевое слово')
        bot.send_message(message.chat.id, "Выберите действие", reply_markup=keyboard)

    elif message.text == 'Добавить ключевое слово':
        bot.send_message(message.chat.id, "Введите новое ключевое слово:")
        flag = True

    elif message.text == 'Посмотреть подписку' or message.text == 'Удалить подписку':
        keyboard = telebot.types.ReplyKeyboardMarkup(True)
        for x in news_category(message.from_user.id):
            if message.text.find("Удалить") == 0:
                x = "Удалить " + x
            keyboard.row(x)
        bot.send_message(message.chat.id, "Выберите подписку", reply_markup=keyboard)

    elif message.text == 'Посмотреть подборку' or message.text == 'Удалить ключевое слово':
        keyboard = telebot.types.ReplyKeyboardMarkup(True)
        for x in news_q(message.from_user.id):
            if message.text.find("Удалить") == 0:
                x = "Удалить " + x
            keyboard.row(x)
        bot.send_message(message.chat.id, "Выберите подборку", reply_markup=keyboard)

    elif message.text in category:
        news = news_api_category(message.text)
        if news['totalResults'] == 0:
            bot.send_message(message.chat.id, "Новостей нет", reply_markup=main())
        for x in news["articles"]:
            bot.send_message(message.chat.id, x["title"], reply_markup=main())

    elif message.text in news_q(message.from_user.id):
        news = news_api_q(message.text)
        if news['totalResults'] == 0:
            bot.send_message(message.chat.id, "Новостей нет", reply_markup=main())
        for x in news["articles"]:
            bot.send_message(message.chat.id, x["title"], reply_markup=main())

    elif message.text.find("Удалить") == 0:
        if message.text.split()[1] in news_category(message.from_user.id):
            del_category(message.from_user.id, message.text.split()[1])
        if message.text.split()[1] in news_q(message.from_user.id):
            del_q(message.from_user.id, message.text.split()[1])
        bot.send_message(message.chat.id, "Подписка удалена", reply_markup=main())

    elif message.text == 'Добавить подписку':
        keyboard = telebot.types.ReplyKeyboardMarkup(True)
        for x in category:
            if not x in news_category(message.from_user.id):
                keyboard.row("Добавить " + x)
        bot.send_message(message.chat.id, "Выберите подписку", reply_markup=keyboard)

    elif message.text.find("Добавить") == 0:
        if message.text.split()[1] in category:
            add_category(message.from_user.id, message.text.split()[1])
            bot.send_message(message.chat.id, "Подписка добавлена", reply_markup=main())
    
    elif flag:
        if not message.text in news_q(message.from_user.id):
            add_q(message.from_user.id, message.text)
            bot.send_message(message.chat.id, "Ключевое слово добавлено", reply_markup=main())
        flag = False
    else:
        bot.send_message(message.chat.id, 'Я тебя не понимаю', reply_markup=main())

bot.polling()
