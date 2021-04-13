"""
Create user table
"""

from yoyo import step
__depends__ = {}

steps = [
    step("""
        CREATE TABLE users(
            id INT NOT NULL AUTO_INCREMENT,
            facebook_id VARCHAR(50) NULL,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW() ON UPDATE now(),
            primary key(id)
        );
    """)
]
