from utilities.rememberme_utilities import remember_utilities
from datetime import datetime

from bson.objectid import ObjectId

# Remember Class is the module to manage everything regarding the database
class Remember:
    def __init__(self, remember_id :str):
        """ 
            remember_id (str) : Remember ID
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
        return remember_list
    
    def _get_content(self):
        content = remember_utilities.remember_content(ObjectId(self.remember_id))
        return content

    def _get_expire_date(self):
        expire_date = remember_utilities.remember_expire_date(ObjectId(self.remember_id))
        return expire_date

    def _get_user_id(self):
        user_id = remember_utilities.remember_user_id(ObjectId(self.remember_id))
        return user_id

    @staticmethod
    def create(content, expire_date, user):

        # Creating the remember
        remember_utilities.create_remember(content, expire_date, user.user_id)
        return 

    def delete(self):
        # Creating the remember
        remember_utilities.delete_remember(self.remember_id)
        return 
    
    def edit_expiredate(self, new_expire):
        remember_utilities.update_remember_expiredate(remember_id=ObjectId(self.remember_id), new_expire=new_expire)
        return
            