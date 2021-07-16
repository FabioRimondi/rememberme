from database_connections.database_manager import users, remembers

class user_utilities:
    @staticmethod
    def verify_if_user_exist(user_id):
        user = users.find({ "user_id":user_id})

        user = [x for x in user]

        # If it doesn't find any user, the array will be len -> 0
        if len(user) == 0:
            return False
        else:
            return True

    @staticmethod
    def create_user(user_id, language, timezone):
        user = {'user_id': user_id, 'language': language, 'timezone':timezone}
        users.insert_one(user)
        return 

    @staticmethod
    def user_language(user_id):
        user = users.find({"user_id":user_id})
        return user[0]['language']

    @staticmethod
    def user_timezone(user_id):
        user = users.find({ "user_id":user_id})
        return user[0]['timezone']

    @staticmethod
    def get_remember_list(user_id):
        remembers_list = [remember for remember in remembers.find({"user_id":user_id})]

        return remembers_list
    
    @staticmethod
    def change_user_language(user_id, language):

        user_query = { "user_id":user_id}
        new_user = users.find({ "user_id":user_id})[0]
        new_user['language'] = language
        
        users.replace_one(user_query, new_user )
        return



