from sqlalchemy import text

class MessageDao:							
    def __init__(self, db):	
        self.db = db
        
    def get_state(self, sender_id):
        state = self.db.execute(text("""
            SELECT *
            FROM messages
            WHERE user_id = :sender_id
            ORDER BY created_at DESC
            LIMIT 1
        """), sender_id=sender_id).fetchone()
        # print('=======================')
        # print(state)
        if not state:
            return 'INITIAL'

        return state.state

    def get_previous_state(self, sender_id):
        return self.db.execute(text("""
            SELECT state
            FROM messages
            WHERE user_id = :sender_id
            ORDER BY created_at DESC
            LIMIT 1
        """), sender_id=sender_id).fetchone()[0]

    def create_message(self, sender_id, message, state, next_state):
        data = {'text': message, 'user_id' : sender_id, 'state': state, 'next_state': next_state}
        return self.db.execute(text("""
            INSERT INTO messages (
                text,
                user_id,
                state,
                next_state)
            VALUES (
                :text, 
                :user_id, 
                :state,
                :next_state)
            """), data).lastrowid
        
    def create_reply(self, message_id, reply):
        # messages = self.db.execute(text("""
        #     SELECT id
        #     FROM messages
        #     ORDER BY created_at DESC
        # """)).fetchall()
        # print('============================================')
        # print(messages)
        data = {'text': reply.replace('\n', ''), 'message_id' : message_id}
        return self.db.execute(text('INSERT INTO replies (text, message_id) VALUES (:text, :message_id)'), data).lastrowid
