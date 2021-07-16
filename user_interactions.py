# Module explanation: 
#   - Here are the core communication with the user. 
#
#
from telebot import types
import json, os, requests, time
from pytz import timezone
from datetime import datetime 
from models.user_model import User
from models.rememberme_model import Remember


# Load the language selected.
text_document = json.loads(open('resources\\language.json', 'r', encoding="UTF-8").read())

class utilities_interaction_module:
    def __init__(self, bot, user):
        self.bot        = bot
        self.user       = user
        self.language   = user.language
    
    # Return main menu
    def show_keyboard(self, message):
        # Keyboard
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
        itembtn1 = types.KeyboardButton(text_document[self.language]['new_remember_button'])              # New "remember"
        itembtn2 = types.KeyboardButton(text_document[self.language]['remember_list_button'])             # List of "remember"
        itembtn3 = types.KeyboardButton(text_document[self.language]['delete_remember_button'])           # Delete "remember"
        itembtn4 = types.KeyboardButton(text_document[self.language]['about_me_button'])                  # Info about me
        itembtn5 = types.KeyboardButton(text_document[self.language]['change_language_button'])           # Change language
        markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5)
        # Return Main menu message and main menu keyboard
        self.bot.send_message(message.from_user.id, text_document[self.language]['main_menu'], reply_markup=markup)

class send_welcome_interaction_module:
    def __init__(self, bot):
        self.bot        = bot

    def send_welcome(self, message):
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
        itembtn_ita = types.KeyboardButton(text_document["it"]['language_name'])
        itembtn_en = types.KeyboardButton(text_document["en"]['language_name'])
        markup.add(itembtn_ita, itembtn_en)
        
        # Try to load the language of the telegram client, if it doesn't appear will trow a error to the user
        try:
            welcome_message = str(text_document[message.from_user.language_code]['welcome']) + "\n\n\n" + str(text_document["en"]['welcome'])
        except:
            welcome_message = str(text_document["en"]['welcome']) +  str(text_document["en"]["language_missing_message"].format(str(message.from_user.language_code)))

        self.bot.reply_to(message, welcome_message, reply_markup=markup)
        self.bot.register_next_step_handler(message, self._get_language_and_ask_living_city)
    
    def _get_language_and_ask_living_city(self, message):
        if message.text != text_document["it"]['language_name'] and message.text != text_document["en"]['language_name']:
            self.send_welcome(message)
        else:
            self.language = str(message.text).split('-')[0]

        # If here, the language is get
        self.bot.reply_to(message, text_document[self.language]['bot_description'], reply_markup=None, parse_mode="Markdown")
        self.bot.reply_to(message, text_document[self.language]['privacy_warning'], reply_markup=None, parse_mode="Markdown")
        self.bot.reply_to(message, text_document[self.language]['asking_location'], reply_markup=None, parse_mode="Markdown")
        self.bot.register_next_step_handler(message, self._try_guess_the_time)

    def _try_guess_the_time(self, message):
        # Here i ask a list of places with that name and hope to catch it by choosing the first. 
        # I'll verify giving the user the time i think is in that city, if he config i get the Timezone
        city = requests.get("http://nominatim.openstreetmap.org/search.php?q={}&format=jsonv2".format(message.text))
        
        # In this case i didn't find anything, prbly the the user inserted the place in a wrong way
        if city.json() == []:
            # TODO User Fabio per contatti problemi
            self.bot.reply_to(message, text_document[self.language]['city_not_found'], parse_mode="Markdown")
            self.bot.register_next_step_handler(message, self._try_guess_the_time)
            return
        
        timezone_response = requests.get("https://timezonefinder.michelfe.it/api/2_{}_{}".format(city.json()[0]['lon'], city.json()[0]['lat']))
        self.timezone = timezone_response.json()["tz_name"]

        now_utc             = timezone("UTC").localize(datetime.now()) # Mezzanotte macchina
        user_hour           = now_utc.astimezone(timezone(self.timezone)) # Mezzanotte UTC macchina

        # Keyboard
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
        yes = types.KeyboardButton(text_document[self.language]['yes'])
        no = types.KeyboardButton(text_document[self.language]['no'])

        markup.add(yes, no)

        self.bot.reply_to(message, text_document[self.language]['ask_timezone_confirm'].format(user_hour), reply_markup=markup, parse_mode="Markdown")
        self.bot.register_next_step_handler(message, self._check_if_timezone_correct)
    
    def _check_if_timezone_correct(self, message):
        if message.text == text_document[self.language]['yes']:
            User.create(message.chat.id, self.language, self.timezone)
            self.bot.send_message(chat_id=message.chat.id, text=text_document[self.language]['timezone_correct'], parse_mode='Markdown')
            
            utilities_interaction_module(self.bot, self.user).show_keyboard(message)
        else:
            self.bot.send_message(chat_id=message.chat.id, text=text_document[self.language]['timezone_incorrect'], parse_mode='Markdown')
            self.bot.register_next_step_handler(message, self._try_guess_the_time)

class change_language_interaction_module:
    def __init__(self, bot, user):
        self.bot        = bot
        self.user       = user
        self.language   = user.language

    def change_language(self, message):
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
        itembtn_ita = types.KeyboardButton(text_document["it"]['language_name'])
        itembtn_en = types.KeyboardButton(text_document["en"]['language_name'])
        markup.add(itembtn_ita, itembtn_en)

        self.bot.send_message(chat_id=message.chat.id, text=text_document[self.language]['change_language_question'], reply_markup=markup, parse_mode='Markdown')
        self.bot.register_next_step_handler(message, self._language_choosed)
        
    def _language_choosed(self, message):
        if message.text != text_document["it"]['language_name'] and message.text != text_document["en"]['language_name']:
            utilities_interaction_module(self.bot, self.user).show_keyboard(message)
        else:
            self.language = str(message.text).split('-')[0]
            self.user.change_language(self.language)
            utilities_interaction_module(self.bot, self.user).show_keyboard(message)
        return

class about_this_bot_interaction_module:
    def __init__(self, bot, user):
        self.bot        = bot
        self.user       = user
        self.language   = user.language

    def about_this_bot(message):
        self.bot.send_message(chat_id=message.chat.id, text=text_document[self.language]['about_this_bot_message'], parse_mode='Markdown')

class add_remember_interaction_module:
    def __init__(self, bot, user):
        self.bot        = bot
        self.user       = user
        self.language   = user.language

    def add_remember(self, message):
        """Function with series of action to do for creating a new thing to remember
        """

        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        itembtn = types.KeyboardButton(text_document[self.language]['cancel_button'])
        markup.add(itembtn)
        
        self.bot.reply_to(message, text_document[self.language]['question_what_to_remember'], reply_markup=markup)
        self.bot.register_next_step_handler(message, self._new_remember_select_date_expiring)

    # Choosing expiring date
    def _new_remember_select_date_expiring(self, message, remember_content = None):
        
        if message.text == text_document[self.language]['cancel_button']:
            utilities_interaction_module(self.bot, self.user).show_keyboard(message)
            return
        
        # This verify exist because i can come back to this function after the function "new_remember_verify_date" validated a wrong date.
        # I need this because i have to save the value of what i have to remember.
        if remember_content == None:
            remember_content = message.text 
            self.bot.reply_to(message, text_document[self.language]['question_when_remember_date'])
        else:
            remember_content = remember_content

        
        self.bot.register_next_step_handler(message, self._new_remember_verify_date, remember_content=remember_content)

    # Check date entry
    def _new_remember_verify_date(self, message, remember_content):
        if message.text == text_document[self.language]['cancel_button']:
            utilities_interaction_module(self.bot, self.user).show_keyboard(message)
            return

        expiring_date_selected = message.text # Day for notification
        try:
            datetime.strptime(expiring_date_selected, '%d/%m/%Y')
            self._new_remember_select_hour_expiring(message, remember_content=remember_content, expiring_date_selected=expiring_date_selected)
        
        except:
            self.bot.reply_to(message, text_document[self.language]['warning_date_format_wrong'])
            self._new_remember_select_date_expiring(message,  remember_content=remember_content)    

    # Choosing expiring hour
    def _new_remember_select_hour_expiring(self, message, remember_content, expiring_date_selected, error=False):
        if message.text == text_document[self.language]['cancel_button']:
            utilities_interaction_module(self.bot, self.user).show_keyboard(message)
            return

        if error:
            self.bot.reply_to(message, text_document[self.language]['warning_hour_format_wrong'])
        else:
            self.bot.reply_to(message, text_document[self.language]['question_when_remember_hour'])
        
        self.bot.register_next_step_handler(message, self._new_remember_verifyHour, remember_content=remember_content, expiring_date_selected=expiring_date_selected)

    # Check hour entry
    def _new_remember_verifyHour(self, message, remember_content, expiring_date_selected):
        if message.text == text_document[self.language]['cancel_button']:
            utilities_interaction_module(self.bot, self.user).show_keyboard(message)
            return
            
        expiring_hour_selected = message.text # Ora notifica
        try:
            # If everything is verified, i can add the new thing to remember in my database
            datetime.strptime(expiring_hour_selected, '%H:%M')
            remember_expire = datetime.strptime(expiring_date_selected + ' ' + expiring_hour_selected, '%d/%m/%Y %H:%M')
            remember_expire_in_utc = self.user.convert_in_utc_from_user_timezone(remember_expire)
            self._add_remember(message=message, chat_id = message.chat.id, content = remember_content, expire = remember_expire_in_utc)
        except:
            self._new_remember_select_hour_expiring(message,  remember_content=remember_content, expiring_date_selected=expiring_date_selected, error=True)    

    # Here will be called the function of the database to add the remember thing. After the User will be prompted with a confirmation message
    def _add_remember(self, message, chat_id, content, expire):

        Remember.create(content=content, expire_date=expire, user=self.user)

        expire_as_user_time_zone = self.user.convert_in_user_timezone_from_utc(expire)
        
        self.bot.send_message(chat_id=chat_id, text=text_document[self.language]['add_remember_confirmation'].format(str(content), datetime.strftime(expire_as_user_time_zone, "%d/%m/%Y "),  datetime.strftime(expire_as_user_time_zone, "%H:%M")), parse_mode='Markdown')
        utilities_interaction_module(self.bot, self.user).show_keyboard(message)

class get_remember_list_interaction_module:
    def __init__(self, bot, user):
        self.bot        = bot
        self.user       = user
        self.language   = user.language
        
    # Get the list of thing to remember
    def get_remember_list(self, message):
        remember_list = self.user.get_remember_list()

        # In case the list is empty, it mean the user don't have any remember still pending
        if len(remember_list) == 0:
            self.bot.reply_to(message, text_document[self.language]['no_things_to_remember'], parse_mode='Markdown')
            utilities_interaction_module(self.bot, self.user).show_keyboard(message)
        else:
            payload_reply = text_document[self.language]['show_list_title']
            for remember in remember_list:
                expire_as_user_time_zone = self.user.convert_in_user_timezone_from_utc(remember['expire_date'])
                payload_reply += text_document[self.language]['list_element'].format(remember['content'], datetime.strftime(expire_as_user_time_zone, "%d/%m/%Y "), datetime.strftime(expire_as_user_time_zone, "%H:%M"))

            self.bot.reply_to(message, payload_reply, parse_mode='Markdown')
            utilities_interaction_module(self.bot, self.user).show_keyboard(message)

class remember_delete_interaction_module:
    def __init__(self, bot, user):
        self.bot        = bot
        self.user       = user
        self.language   = user.language

    # Delete a element to remember
    def remember_delete(self, message):
        # Keyboard
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)

        remember_list = self.user.get_remember_list()

        temp_list = [] 
        index = 0
        for remember in remember_list:
            index += 1
            markup.add(str(index) + "- " + remember['content'])
            temp_list.append({'index': index, 'obj_id': remember['_id']})

        self.bot.reply_to(message, text_document[self.language]['what_to_delete'], reply_markup=markup)
        self.bot.register_next_step_handler(message, self._verify_remember_delete, temp_list=temp_list)

    # Check if the user is sure to delete the element
    def _verify_remember_delete(self, message, temp_list):
        # To help the bot to not confuse itself with flood messages.
        try:
            selected_index = int(str(message.text).split('-')[0]) - 1 # In "remember delete" to being more user friendly, i've hadded +1 to the index showed.
            selected_name = str(message.text).split('-')[1]
            selected_id = temp_list[selected_index]['obj_id']
        except:
            utilities_interaction_module(self.bot, self.user).show_keyboard(message)
            return

        # Keyboard
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
        yes = types.KeyboardButton(text_document[self.language]['yes'])
        no = types.KeyboardButton(text_document[self.language]['no'])

        markup.add(yes, no)

        self.bot.reply_to(message, text_document[self.language]['delete_confirmation'].format(selected_name), reply_markup=markup, parse_mode='Markdown')
        self.bot.register_next_step_handler(message, self._remember_delete_confirm, selected_id = selected_id)

        
    def _remember_delete_confirm(self, message, selected_id):
        if message.text == text_document[self.language]['yes']:
            Remember(remember_id=selected_id).delete()
            self.bot.send_message(chat_id=message.chat.id, text=text_document[self.language]['done'], parse_mode='Markdown')
        else:
            self.bot.send_message(chat_id=message.chat.id, text=text_document[self.language]['cancelled'], parse_mode='Markdown')

        utilities_interaction_module(self.bot, self.user).show_keyboard(message)
