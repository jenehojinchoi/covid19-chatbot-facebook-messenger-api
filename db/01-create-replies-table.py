# database code와 api code는 분리해주세요!


"""
Create replies table
"""

from yoyo import step
__depends__ = {'01-create-messages-table'}

steps = [
    step("""
        CREATE TABLE replies(
            id INT NOT NULL AUTO_INCREMENT,
            text VARCHAR(1000) NOT NULL,
            message_id INT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW() ON UPDATE now(),
            primary key(id),
            CONSTRAINT replies_message_id_fkey_message_id FOREIGN KEY (message_id) REFERENCES messages(id)
        );
    """)
]
