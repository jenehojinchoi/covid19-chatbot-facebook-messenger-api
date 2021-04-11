from sqlalchemy import text

class UserDao:							
    def __init__(self, db):	
        self.db = db

    def get_user(self, facebook_id):
        user = self.db.execute(text("""
            SELECT 
                *
            FROM users
            WHERE facebook_id = :facebook_id
        """), {'facebook_id' : facebook_id}).fetchone()
        return user

    def create_user(self, facebook_id):
        return self.db.execute(text("""
            INSERT INTO users (
                facebook_id
            ) VALUES (
                :facebook_id
            )
        """), {"facebook_id" : facebook_id}).lastrowid

    def get_or_create_user(self, facebook_id):
        user = self.get_user(facebook_id)

        if not user:
            return self.create_user(facebook_id)
        return user.id
