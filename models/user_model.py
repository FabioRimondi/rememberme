import time, pytz
from utilities.user_utilities import user_utilities
from pytz import timezone

class User:
    def __init__(self, user_id):
        self.user_id     = user_id
        self.language    = self._get_language()
        self.timezone    = self._get_timezone()

    @staticmethod
    def exist(user_id):
        return user_utilities.verify_if_user_exist(user_id)

    @staticmethod
    def create(user_id, language, timezone):
        user_utilities.create_user(user_id, language, timezone)
        return 

    def _get_language(self):
        language = user_utilities.user_language(self.user_id)
        return language

    def _get_timezone(self):
        timezone = user_utilities.user_timezone(self.user_id)
        return timezone

    def get_remember_list(self):
        remember_list = user_utilities.get_remember_list(self.user_id)
        return remember_list

    def change_language(self, new_language):
        user_utilities.change_user_language(self.user_id, language)
        return 

    # TODO IMPLEMENT CONVERSION UTC IN USER INTERACTION
    def convert_in_utc_from_user_timezone(self, date):
        """Converting from User hour to UTC hour
         
        """
        user_hour           = timezone(self.timezone).localize(date) # Mezzanotte macchina
        utc_hour            = user_hour.astimezone(timezone("UTC")) # Mezzanotte UTC macchina

        return utc_hour

    def convert_in_user_timezone_from_utc(self, date):
        """Converting from UTC hour to User hour
         
        """

        user_hour = date.replace(tzinfo=pytz.utc).astimezone(timezone(self.timezone))
        return user_hour