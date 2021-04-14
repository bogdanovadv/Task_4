import sqlite3, telebot
from telebot import types
from newsapi import NewsApiClient

telebot_token = "1794433387:AAGsLnL2AYlbBOoI5SFTuqqzU5ltMQ99P2U"
news_api_token = "51f3bc1ce6384971b2e00b29d92c5e98"


def new_db():
    connection = sqlite3.connect('bot.db')
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                            (id	INTEGER PRIMARY KEY AUTOINCREMENT, user INTEGER NOT NULL,
                                PRIMARY KEY(id))
                   ''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS categories
                            (id	INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT NOT NULL, user_id INTEGER NOT NULL,
                            PRIMARY KEY(id),
                            FOREIGN KEY(user_id) REFERENCES users(id))
                   ''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS keywords
                            (id	INTEGER PRIMARY KEY AUTOINCREMENT, keyword TEXT NOT NULL, user_id INTEGER NOT NULL,
                            PRIMARY KEY(id),
                            FOREIGN KEY(user_id) REFERENCES users("id"))
                   ''')
    connection.commit()
    connection.close()

def add_user(id):
    connection = sqlite3.connect('bot.db')
    cursor = connection.cursor()
    cursor.execute(f'''INSERT INTO users (user) SELECT ('{id}') WHERE NOT EXISTS (SELECT 1 FROM users WHERE user = '{id}')''')
    connection.commit()
    connection.close()

new_db()

bot = telebot.TeleBot(telebot_token, parse_mode=None)

def main():
    markup = types.ReplyKeyboardMarkup(True)
    key1 = types.KeyboardButton('Посмотреть новости')
    key2 = types.KeyboardButton('Управление подписками')
    key3 = types.KeyboardButton('Жуть')
    markup.add(key1)
    markup.add(key2)
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    add_user(user_id)
    user_name = message.from_user.username
    bot.send_message(message.chat.id, 'Привет, ' + str(user_name), reply_markup=main())

@bot.message_handler(content_types=['text'])
def cont(message):
    if message.text == 'Посмотреть новости':
        bot.send_message(message.chat.id, 'Типа смотрю новости', reply_markup=main())
    elif message.text == 'Управление подписками':
        bot.send_message(message.chat.id, 'Типа управляю подписками', reply_markup=main())
    else:
        bot.send_message(message.chat.id, 'Я тебя не понимаю', reply_markup=main())
bot.polling()



def news_user(id):
    connection = sqlite3.connect('bot.db')
    cursor = connection.cursor()
    cursor.execute(f'''SELECT category FROM categories WHERE JOIN users ON users.id = users.id WHERE users.id = {id}''')
    connection.commit()
    connection.close()

def news_api(q, category):
    newsapi = NewsApiClient(api_key=news_api_token)

    # через запятую 'bbc-news,the-verge'
    category = 'business, entertainment, general, health, science, sports, technology'
    q = 'bitcoin'
    top_headlines = newsapi.get_top_headlines(q=q,
                                             category=category,
                                             sortBy='relevancy',
                                             pageSize=10,
                                             page=1)

    sources = newsapi.get_sources()
    return sources