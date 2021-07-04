import telebot
from telebot import types

from bot_message_handling import bot_message_handling

import schedule
import threading
import time
import json, os

from remembers_manage import remember_class

from datetime import datetime, timedelta

# You have to insert the "Botfather" token here
bot = telebot.TeleBot(os.environ['rememberme_botfather_token'], parse_mode=None) # You can set parse_mode by default. HTML or MARKDOWN

# Load the language selected.
text_document = json.loads(open('language.json', 'r', encoding="UTF-8").read())[os.environ['rememberme_language']]

# Listening for "Cancel Action" button
@bot.message_handler(func=lambda message: message.text == text_document['cancel_button'] and message.content_type == 'text')
def cancel(message):
    send_welcome(message)

# Listening for "About me" button
@bot.message_handler(func=lambda message: message.text == text_document['about_me_button'] and message.content_type == 'text')
def about_me(message):
    bot.send_message(chat_id=message.chat.id, text=text_document['about_me_message'], parse_mode='Markdown')

# Listening for /start command - Welcome message + show main menu keyboard
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Keyboard
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    itembtn1 = types.KeyboardButton(text_document['new_remember'])              # New "remember"
    itembtn2 = types.KeyboardButton(text_document['remember_list'])             # List of "remember"
    itembtn3 = types.KeyboardButton(text_document['delete_remember'])           # Delete "remember"
    itembtn4 = types.KeyboardButton(text_document['about_me_button'])           # Info about me
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4)
    # Return Welcome message and main menu keyboard
    bot.reply_to(message,text_document['welcome_message'], reply_markup=markup)


# Add new remember me
@bot.message_handler(func=lambda message: message.text == text_document['new_remember'] and message.content_type == 'text')
def new_remember(message):
    bot_message_handling(bot).new_remember(message)

# Listener that return the list of what's saved for the account
@bot.message_handler(func=lambda message: message.text == text_document['remember_list'] and message.content_type == 'text')
def remember_list(message):
    bot_message_handling(bot).get_remember_list(message)

# Delete a element from database
@bot.message_handler(func=lambda message: message.text == text_document['delete_remember'] and message.content_type == 'text')
def remember_delete(message):
    bot_message_handling(bot).remember_delete(message)


def start_bot():
    bot.polling()


############ This part is dedicated to the notification schedule.
def notify_task():
    to_notify = remember_class.return_expiring_remembers(start_date=datetime.now() - timedelta(seconds=1), end_date=datetime.now()+timedelta(minutes=1))
    for notification in to_notify:
        bot.send_message(notification['chat_id'], text_document['notification'].format(notification['remember_name']), parse_mode="Markdown")

def notify_scheduler():
    schedule.every(1).minutes.do(notify_task)                     # Schedule verification every minute
    while True:
        schedule.run_pending()
        time.sleep(1)                                           # To not flood the system.


# Here i start the bot and the notificator.
bot_tg = threading.Thread(target=start_bot)                         
bot_notify_scheduler = threading.Thread(target=notify_scheduler)               
bot_tg.start()
bot_notify_scheduler.start()
