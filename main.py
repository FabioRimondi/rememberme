# TODO Aggiungere pulsante "cambio lingua"
from user_interactions import *
from models.user_model import User
from models.remember_model import Remember
from datetime import datetime, timedelta
from telebot import types

import schedule, threading, time, json, os
import telebot

# You have to insert the "Botfather" token here
bot = telebot.TeleBot(os.environ['rememberme_botfather_token'], parse_mode=None) # You can set parse_mode by default. HTML or MARKDOWN

# Load the language selected.
text_document = json.loads(open('resources\\language.json', 'r', encoding="UTF-8").read())

# Listening for /start command - Welcome message + show main menu keyboard
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # If who trigger the bot already triggered it, i just show the keyboard, 
    # in case is a new user, i send it to a "welcome page" to get language and timezone
    if User.exist(user_id=message.chat_id):
        utilities_interaction_module(bot, User(message.chat_id)).show_keyboard(message)
    else:
        send_welcome_interaction_module(bot).send_welcome(message)

# Listening for "Cancel Action" button
@bot.message_handler(func=lambda message: message.text == text_document['EN']['cancel_button'] and message.content_type == 'text')
@bot.message_handler(func=lambda message: message.text == text_document['IT']['cancel_button'] and message.content_type == 'text')
def cancel(message):
    # Get the user info
    user = User(message.chat_id)
    # Put back to keyboard
    utilities_interaction_module(bot, user).show_keyboard(message)

# Listening for "About me" button
@bot.message_handler(func=lambda message: message.text == text_document['EN']['about_me_button'] and message.content_type == 'text')
@bot.message_handler(func=lambda message: message.text == text_document['IT']['about_me_button'] and message.content_type == 'text')
def about_me(message):
    # Get the user info
    user = User(message.chat_id)
    # Send Interaction
    about_me_interaction_module(bot, user).about_me(message)


# Add new remember me
@bot.message_handler(func=lambda message: message.text == text_document['EN']['new_remember_button'] and message.content_type == 'text')
@bot.message_handler(func=lambda message: message.text == text_document['IT']['new_remember_button'] and message.content_type == 'text')
def new_remember(message):
    # Get the user info
    user = User(message.chat_id)
    # Send Interaction
    add_remember_interaction_module(bot, user).add_remember(message)

# Listener that return the list of what's saved for the account
@bot.message_handler(func=lambda message: message.text == text_document['EN']['remember_list_button'] and message.content_type == 'text')
@bot.message_handler(func=lambda message: message.text == text_document['IT']['remember_list_button'] and message.content_type == 'text')
def remember_list(message):
    # Get the user info
    user = User(message.chat_id)
    # Send Interaction
    get_remember_list_interaction_module(bot, user).get_remember_list(message)

# Delete a element from database
@bot.message_handler(func=lambda message: message.text == text_document['EN']['delete_remember_button'] and message.content_type == 'text')
@bot.message_handler(func=lambda message: message.text == text_document['IT']['delete_remember_button'] and message.content_type == 'text')
def remember_delete(message):
    # Get the user info
    user = User(message.chat_id)
    # Send Interaction
    remember_delete_interaction_module(bot, user).remember_delete(message)

# Delete a element from database
@bot.message_handler(func=lambda message: message.text == text_document['EN']['change_language_button'] and message.content_type == 'text')
@bot.message_handler(func=lambda message: message.text == text_document['IT']['change_language_button'] and message.content_type == 'text')
def remember_delete(message):
    # Get the user info
    user = User(message.chat_id)
    # Send Interaction
    remember_delete_interaction_module(bot, user).remember_delete(message)


def start_bot():
    bot.polling()


############ This part is dedicated to the notification schedule.
def notify_task():
    to_notify = Remember.return_expiring_remembers(start_date=datetime.now() - timedelta(seconds=1), end_date=datetime.now()+timedelta(minutes=1))

    for notification in to_notify:
        user = User(user_id=notification['user_id'])
        bot.send_message(notification['user_id'], text_document[user.language]['notification'].format(notification['remember_name']), parse_mode="Markdown")

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
