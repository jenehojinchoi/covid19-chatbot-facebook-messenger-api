class UserService:
    def __init__(self, user_dao, redis):	
        self.user_dao = user_dao
        self.redis = redis
    
    def save_user(self, facebook_id):
        return self.user_dao.get_or_create_user(facebook_id)