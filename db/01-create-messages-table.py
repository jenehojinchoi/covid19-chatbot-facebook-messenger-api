"""
Create messages table
"""

from yoyo import step
__depends__ = {'01-create-users-table'}

steps = [
    step("""
        CREATE TABLE messages(
            id INT NOT NULL AUTO_INCREMENT,
            user_id INT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW() ON UPDATE now(),
            text VARCHAR(1000) NULL,
            state VARCHAR(200) DEFAULT 'INITIAL',
            next_state VARCHAR(200) DEFAULT 'CASES_OR_POLICY',
            primary key(id),
            CONSTRAINT messages_user_id_fkey_users_id FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)
]
