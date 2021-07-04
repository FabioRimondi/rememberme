# Module explanation: 
#   - Here are the core communication with the user. 
#
#
from telebot import types

import json, os
from datetime import datetime 
from remembers_manage import remember_class

# Load the language selected.
text_document = json.loads(open('language.json', 'r', encoding="UTF-8").read())[os.environ['rememberme_language']]


class bot_message_handling:
    def __init__(self, bot) -> None:
        self.bot = bot

    @staticmethod
    # Return main menu
    def show_keyboard(bot, message):
        # Keyboard
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        itembtn1 = types.KeyboardButton(text_document['new_remember'])              # New "remember"
        itembtn2 = types.KeyboardButton(text_document['remember_list'])             # List of "remember"
        itembtn3 = types.KeyboardButton(text_document['delete_remember'])           # Delete "remember"
        itembtn4 = types.KeyboardButton(text_document['about_me_button'])           # Info about me
        markup.add(itembtn1, itembtn2, itembtn3, itembtn4)
        # Return Main menu message and main menu keyboard
        bot.send_message(message.from_user.id, text_document['main_menu'], reply_markup=markup)


    def new_remember(self, message):
        """Function with series of action to do for creating a new thing to remember
        """

        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        itembtn = types.KeyboardButton(text_document['cancel_button'])
        markup.add(itembtn)
        
        self.bot.reply_to(message, text_document['question_what_to_remember'], reply_markup=markup)
        self.bot.register_next_step_handler(message, self._new_remember_select_date_expiring)

    # Choosing expiring date
    def _new_remember_select_date_expiring(self, message, remember_content = None):
        if message.text == text_document['cancel_button']:
            self.show_keyboard(message)
            return
        # This verify exist because i can come back to this function after the function "new_remember_verify_date" validated a wrong date.
        # I need this because i have to save the value of what i have to remember.
        if remember_content == None:
            remember_content = message.text 
            self.bot.reply_to(message, text_document['question_when_remember_date'])
        else:
            remember_content = remember_content

        
        self.bot.register_next_step_handler(message, self._new_remember_verify_date, remember_content=remember_content)

    # Check date entry
    def _new_remember_verify_date(self, message, remember_content):
        if message.text == text_document['cancel_button']:
            self.show_keyboard(message)
            return
        expiring_date_selected = message.text # Day for notification
        try:
            datetime.strptime(expiring_date_selected, '%d/%m/%Y')
            self._new_remember_select_hour_expiring(message, remember_content=remember_content, expiring_date_selected=expiring_date_selected)
        except:
            self.bot.reply_to(message, text_document['warning_date_format_wrong'])
            self._new_remember_select_date_expiring(message,  remember_content=remember_content)    

    # Choosing expiring hour
    def _new_remember_select_hour_expiring(self, message, remember_content, expiring_date_selected, error=False):
        if message.text == text_document['cancel_button']:
            self.show_keyboard(message)
            return
        if error:
            self.bot.reply_to(message, text_document['warning_hour_format_wrong'])
        else:
            self.bot.reply_to(message, text_document['question_when_remember_hour'])
        self.bot.register_next_step_handler(message, self._new_remember_verifyHour, remember_content=remember_content, expiring_date_selected=expiring_date_selected)

    # Check hour entry
    def _new_remember_verifyHour(self, message, remember_content, expiring_date_selected):
        if message.text == text_document['cancel_button']:
            self.show_keyboard(message)
            return
        expiring_hour_selected = message.text # Ora notifica
        try:
            # If everything is verified, i can add the new thing to remember in my database
            datetime.strptime(expiring_hour_selected, '%H:%M')
            remember_expire = datetime.strptime(expiring_date_selected + ' ' + expiring_hour_selected, '%d/%m/%Y %H:%M')
            self._add_remember(message=message, chat_id = message.chat.id, content = remember_content, expire = remember_expire)
        except:
            self._new_remember_select_hour_expiring(message,  remember_content=remember_content, expiring_date_selected=expiring_date_selected, error=True)    

    # Here will be called the function of the database to add the remember thing. After the User will be prompted with a confirmation message
    def _add_remember(self, message, chat_id, content, expire):
        remember_class(chat_id=chat_id).add(remember_name=content, expire_date=expire)
        self.bot.send_message(chat_id=chat_id, text=text_document['add_remember_confirmation'].format(str(content), datetime.strftime(expire, "%d/%m/%Y "),  datetime.strftime(expire, "%H:%M")), parse_mode='Markdown')
        bot_message_handling.show_keyboard(self.bot, message)

    # Get the list of thing to remember
    def get_remember_list(self, message):
        remember_list = remember_class(chat_id=message.chat.id).return_list()

        # In case the list is empty, it mean the user don't have any remember still pending
        if remember_list == []:
            self.bot.reply_to(message, text_document['no_things_to_rememeber'], parse_mode='Markdown')
        else:
            payload_reply = text_document['show_list_title']
            for remember in remember_list:
                payload_reply += text_document['list_element'].format(remember['remember_name'], datetime.strftime(remember['expire_date'], "%d/%m/%Y "), datetime.strftime(remember['expire_date'], "%H:%M"))

            self.bot.reply_to(message, payload_reply, parse_mode='Markdown')

    # Delete a element to remember
    def remember_delete(self, message):
        # Keyboard
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)

        remember_list = remember_class(chat_id=message.chat.id).return_list()

        temp_list = [] 
        index = 0
        for remember in remember_list:
            index += 1
            markup.add(str(index) + "- " + remember['remember_name'])
            temp_list.append({'index': index, 'obj_id': remember['_id']})

        self.bot.reply_to(message, text_document['what_to_delete'], reply_markup=markup)
        self.bot.register_next_step_handler(message, self._verify_remember_delete, temp_list=temp_list)

    # Check if the user is sure to delete the element
    def _verify_remember_delete(self, message, temp_list):
        # To help the bot to not confuse itself with flood messages.
        try:
            selected_index = int(str(message.text).split('-')[0]) - 1 # In "remember delete" to being more user friendly, i've hadded +1 to the index showed.
            selected_name = str(message.text).split('-')[1]
            selected_id = temp_list[selected_index]['obj_id']
        except:
            bot_message_handling.show_keyboard(self.bot, message)
            return

        # Keyboard
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        yes = types.KeyboardButton(text_document['yes'])
        no = types.KeyboardButton(text_document['no'])

        markup.add(yes, no)

        self.bot.reply_to(message, text_document['delete_confirmation'].format(selected_name), reply_markup=markup, parse_mode='Markdown')
        self.bot.register_next_step_handler(message, self._remember_delete_confirm, selected_id = selected_id)

        
    def _remember_delete_confirm(self, message, selected_id):
        if message.text == text_document['yes']:
            remember_class.delete(remember_id=selected_id)
            self.bot.send_message(chat_id=message.chat.id, text=text_document['done'], parse_mode='Markdown')
        else:
            self.bot.send_message(chat_id=message.chat.id, text=text_document['cancelled'], parse_mode='Markdown')

        bot_message_handling.show_keyboard(self.bot, message)