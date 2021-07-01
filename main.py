import telebot
from telebot import types

import schedule
import threading
import time
import os
import json

from datetime import datetime, timedelta
from remembers_manage import remember_class

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
    itembtn1 = types.KeyboardButton(text_document['new_remember'])           # New "remember"
    itembtn2 = types.KeyboardButton(text_document['remember_list'])            # List of "remember"
    itembtn3 = types.KeyboardButton(text_document['delete_remember'])        # Delete "remember"
    itembtn4 = types.KeyboardButton(text_document['about_me_button'])  # Info about me
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4)
    # Return Welcome message and main menu keyboard
    bot.reply_to(message,text_document['welcome_message'], reply_markup=markup)

# Return main menu
def show_keyboard(message):
    # Keyboard
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    itembtn1 = types.KeyboardButton(text_document['new_remember'])           # New "remember"
    itembtn2 = types.KeyboardButton(text_document['remember_list'])            # List of "remember"
    itembtn3 = types.KeyboardButton(text_document['delete_remember'])        # Delete "remember"
    itembtn4 = types.KeyboardButton(text_document['about_me_button'])  # Info about me
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4)
    # Return Main menu message and main menu keyboard
    bot.send_message(message.from_user.id, text_document['main_menu'], reply_markup=markup)


# Add new remember me
@bot.message_handler(func=lambda message: message.text == text_document['new_remember'] and message.content_type == 'text')
def new_remember(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    itembtn = types.KeyboardButton(text_document['cancel_button'])
    markup.add(itembtn)
    
    bot.reply_to(message, text_document['question_what_to_remember'], reply_markup=markup)
    bot.register_next_step_handler(message, new_remember_select_date_expiring)

# Choosing expiring date
def new_remember_select_date_expiring(message, remember_content = None):
    if message.text == text_document['cancel_button']:
        show_keyboard(message)
        return
    # This verify exist because i can come back to this function after the function "new_remember_verify_date" validated a wrong date.
    # I need this because i have to save the value of what i have to remember.
    if remember_content == None:
        remember_content = message.text 
        bot.reply_to(message, text_document['question_when_remember_date'])
    else:
        remember_content = remember_content

    
    bot.register_next_step_handler(message, new_remember_verify_date, remember_content=remember_content)


# Check date entry
def new_remember_verify_date(message, remember_content):
    if message.text == text_document['cancel_button']:
        show_keyboard(message)
        return
    expiring_date_selected = message.text # Day for notification
    try:
        datetime.strptime(expiring_date_selected, '%d/%m/%Y')
        new_remember_select_hour_expiring(message, remember_content=remember_content, expiring_date_selected=expiring_date_selected)
    except:
        bot.reply_to(message, text_document['warning_date_format_wrong'])
        new_remember_select_date_expiring(message,  remember_content=remember_content)    

# Choosing expiring hour
def new_remember_select_hour_expiring(message, remember_content, expiring_date_selected, error=False):
    if message.text == text_document['cancel_button']:
        show_keyboard(message)
        return
    if error:
        bot.reply_to(message, text_document['warning_hour_format_wrong'])
    else:
        bot.reply_to(message, text_document['question_when_remember_hour'])
    bot.register_next_step_handler(message, new_remember_verifyHour, remember_content=remember_content, expiring_date_selected=expiring_date_selected)

# Check hour entry
def new_remember_verifyHour(message, remember_content, expiring_date_selected):
    if message.text == text_document['cancel_button']:
        show_keyboard(message)
        return
    expiring_hour_selected = message.text # Ora notifica
    try:
        # If everything is verified, i can add the new thing to remember in my database
        datetime.strptime(expiring_hour_selected, '%H:%M')
        remember_expire = datetime.strptime(expiring_date_selected + ' ' + expiring_hour_selected, '%d/%m/%Y %H:%M')
        add_remember(message=message, chat_id = message.chat.id, content = remember_content, expire = remember_expire)
    except:
        new_remember_select_hour_expiring(message,  remember_content=remember_content, expiring_date_selected=expiring_date_selected, error=True)    

# Function that communicate with my database for adding data
def add_remember(message, chat_id, content, expire):
    remember_class(chat_id=chat_id).add(remember_name=content, expire_date=expire)
    bot.send_message(chat_id=chat_id, text=text_document['add_remember_confirmation'].format(str(content), datetime.strftime(expire, "%d/%m/%Y "),  datetime.strftime(expire, "%H:%M")), parse_mode='Markdown')
    show_keyboard(message)


# Listener that return the list of what's saved for the account
@bot.message_handler(func=lambda message: message.text == text_document['remember_list'] and message.content_type == 'text')
def remember_list(message):
    remember_list = remember_class(chat_id=message.chat.id).return_list()
    payload_reply = text_document['show_list_title']
    for remember in remember_list:
        payload_reply += text_document['list_element'].format(remember['remember_name'], datetime.strftime(remember['expire_date'], "%d/%m/%Y "), datetime.strftime(remember['expire_date'], "%H:%M"))

    bot.reply_to(message, payload_reply, parse_mode='Markdown')

# Delete a element from database
@bot.message_handler(func=lambda message: message.text == text_document['delete_remember'] and message.content_type == 'text')
def remember_delete(message):
    # Keyboard
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)

    remember_list = remember_class(chat_id=message.chat.id).return_list()

    temp_list = [] 
    index = 0
    for remember in remember_list:
        index += 1
        markup.add(str(index) + "- " + remember['remember_name'])
        temp_list.append({'index': index, 'obj_id': remember['_id']})

    bot.reply_to(message, text_document['what_to_delete'], reply_markup=markup)
    bot.register_next_step_handler(message, verify_remember_delete, temp_list=temp_list)

# Check if the user is sure to delete the element
def verify_remember_delete(message, temp_list):
    # To help the bot to not confuse itself with flood messages.
    try:
        selected_index = int(str(message.text).split('-')[0]) - 1 # In "remember delete" to being more user friendly, i've hadded +1 to the index showed.
        selected_name = str(message.text).split('-')[1]
        selected_id = temp_list[selected_index]['obj_id']
    except:
        show_keyboard(message)
        return

    

    # Keyboard
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    yes = types.KeyboardButton(text_document['yes'])
    no = types.KeyboardButton(text_document['no'])

    markup.add(yes, no)

    bot.reply_to(message, text_document['delete_confirmation'].format(selected_name), reply_markup=markup, parse_mode='Markdown')
    bot.register_next_step_handler(message, remember_delete_confirm, selected_id = selected_id)
    
def remember_delete_confirm(message, selected_id):
    if message.text == text_document['yes']:
        remember_class.delete(remember_id=selected_id)
        bot.send_message(chat_id=message.chat.id, text=text_document['done'], parse_mode='Markdown')
    else:
        bot.send_message(chat_id=message.chat.id, text=text_document['cancelled'], parse_mode='Markdown')

    show_keyboard(message)


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
