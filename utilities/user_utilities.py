from database_connections.database_manager import users, remembers

class user_utilities:
    @staticmethod
    def verify_if_user_exist(user_id):
        user = users.find({ "user_id":user_id})

        if user == []:
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
        user = users.find({ "user_id":user_id})
        return user[0]['language']

    @staticmethod
    def user_timezone(user_id):
        user = users.find({ "user_id":user_id})
        return user[0]['timezone']

    @staticmethod
    def get_remember_list(user_id):
        remembers = remembers.find({"user_id":user_id})
        return remembers
    
    @staticmethod
    def change_user_language(user_id, language):
        user = { "user_id":user_id}
        new_language = {"language" : language}
        
        users.replace_one(user, new_language )
        return



