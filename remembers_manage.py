from database_manager import remembers

from datetime import datetime

# Remember Class is the module to manage everything regarding the database
class remember_class:
    def __init__(self, chat_id :str):
        """ 
            chat_id (str) : Chat ID
        """
        self.chat_id = chat_id

    @staticmethod
    def return_expiring_remembers(start_date, end_date):
        """Function to retrieve all events to notify

        Args:
            start_date / end_date : Filter for start and end of search.
        """

        payload = remembers.find({ "expire_date":{"$gt": start_date, "$lt": end_date}})
        return payload

    def add(self, remember_name :str, expire_date :object):
        """Add a simple remember data

        Args:
            remember_name (str): Content of remember
            expire_date (datetime): When to notify
        """
        try:
            # Funzione per aggiungere una task.
            remember = {'chat_id': self.chat_id, 'remember_name': remember_name, 'expire_date':expire_date}
            remembers.insert_one(remember)
            return True
        except:
            return False 

    def return_list(self) ->list:
        """Return a simple list of remembers 

        Returns:
            list: List of remembers
        """
        payload = remembers.find({"chat_id":self.chat_id,  "expire_date":{"$gt": datetime.now()}}).sort("expire_date", 1)
        return payload

    @staticmethod
    def delete(remember_id):
        """Delete a element in MongoDB

        Args:
            task_id (str): ID in MongoDB of remember
        """
        try:
            remembers.delete_one({'_id':remember_id})
            return True
        except:
            return False

            