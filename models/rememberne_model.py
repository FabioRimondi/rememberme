from utilities.rememberme_utilities import remember_utilities
from datetime import datetime

# Remember Class is the module to manage everything regarding the database
class Remember:
    def __init__(self, remember_id :str):
        """ 
            user_id (str) : User ID
        """
        self.remember_id    = remember_id
        self.user_id        = self._get_user_id()
        self.content        = self._get_content()
        self.expire_date    = self._get_expire_date()

    @staticmethod
    def return_expiring_remembers(start_date, end_date):
        """Function to retrieve all events to notify

        Args:
            start_date / end_date : Filter for start and end of search.
        """
        remember_list = remember_utilities.return_expiring_remembers(start_date, end_date)
        return remeber_list
    
    def _get_content(self):
        content = remember_utilities.remember_content(self.remember_id)
        return content

    def _get_expire_date(self):
        expire_date = remember_utilities.remember_expire_date(self.remember_id)
        return expire_date

    def _get_user_id(self):
        user_id = remember_utilities.remember_user_id(self.remember_id)
        return user_id

    @staticmethod
    def create(content, expire_date, user):
        # Converting the hour
        expire_date_utc = user.convert_in_utc_from_user_timezone(expire_date)
        
        # Creating the remember
        remember_utilities.create_remember(content, expire_date_utc, user.user_id)
        return 

    def delete(self):
        # Creating the remember
        remember_utilities.delete_remember(self.remember_id)
        return 
            