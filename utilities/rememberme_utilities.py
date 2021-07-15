from database_connections.database_manager import remembers

class remember_utilities:
    @staticmethod
    def return_expiring_remembers(start_date, end_date):
        payload = remembers.find({ "expire_date":{"$gt": start_date, "$lt": end_date}})

        return payload

    @staticmethod
    def remember_content(remember_id):
        remember = remembers.find({ "_id":remember_id})
        return remember[0]['content']

    @staticmethod
    def remember_user_id(remember_id):
        remember = remembers.find({ "_id":remember_id})
        return remember[0]['user_id']

    @staticmethod
    def remember_expire_date(remember_id):
        remember = remembers.find({ "_id":remember_id})
        return remember[0]['expire_date']

    @staticmethod
    def create_remember(content, expire_date_utc, user_id):
        try:
            # Funzione per aggiungere una task.
            remember = {'user_id': user_id, 'content': content, 'expire_date':expire_date_utc}
            remembers.insert_one(remember)
            return True
        except:
            return False 

    @staticmethod
    def delete_remember(remember_id):
        try:
            remembers.delete_one({'_id':remember_id})
            return True
        except:
            return False
