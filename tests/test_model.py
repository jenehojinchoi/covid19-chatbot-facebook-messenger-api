import pytest
import redis
import json
import config

from sqlalchemy    import create_engine, text
from api.injectors import create_app
from api.models.user_dao  import UserDao
from api.models.message_dao import MessageDao

test_db = create_engine(f"{config.TEST_DB_CONNECTION_URL}?charset=utf8")
redis   = redis.Redis('localhost')

facebook_credentials = {
    'FACEBOOK_API_URL'  : config.FACEBOOK_API_URL,
    'VERIFY_TOKEN'      : config.VERIFY_TOKEN,
    'PAGE_ACCESS_TOKEN' : config.PAGE_ACCESS_TOKEN
}

@pytest.fixture
def user_dao():
    return UserDao(test_db)

@pytest.fixture
def message_dao():
    return MessageDao(test_db)

def setup_function():
    new_users = [
        {
            'facebook_id': '12345678901'
        }, {
            'facebook_id': '12345678902'
        }
    ]
    test_db.execute(text("""
        INSERT INTO users (
            facebook_id
        ) VALUES (
            :facebook_id
        )
    """), new_users)

    test_db.execute(text("""
        INSERT INTO messages (
            user_id,
            text,
            state,
            next_state
        ) VALUES (
            2,
            "안녕",
            "INITIAL",
            "CASES_OR_POLICY"
        )
    """))

    test_db.execute(text("""
        INSERT INTO messages (
            user_id,
            text,
            state,
            next_state
        ) VALUES (
            2,
            "일일 확진자수 확인",
            "CASES_OR_POLICY",
            "COUNTRY_OR_CITY"
        )
    """))

def test_get_user(user_dao):
    user = user_dao.get_user('12345678901')
    assert user == (
        user.id,
        user.facebook_id,
        user.created_at,
        user.updated_at
    )
    
def test_create_user(user_dao):
    new_facebook_id = '12345678903'
    new_user_id = user_dao.create_user(new_facebook_id)
    assert new_user_id == 3

def test_get_state(message_dao):
    state = message_dao.get_state('12345678901')
    assert state == 'INITIAL'

def test_get_previous_state(message_dao):
    state = message_dao.get_state('12345678902')
    assert state == 'INITIAL'

def test_create_message(message_dao):
    message_id = message_dao.create_message(1, '안녕 하세요','INITIAL', 'CASES_OR_POLICY')
    assert message_id == 3

def test_create_reply(message_dao):
    reply_id = message_dao.create_reply(1, '답장입니다')
    assert reply_id == 1

def teardown_function():
    test_db.execute(text("SET FOREIGN_KEY_CHECKS=0"))
    test_db.execute(text("TRUNCATE users"))
    test_db.execute(text("TRUNCATE messages"))
    test_db.execute(text("TRUNCATE replies"))
    test_db.execute(text("SET FOREIGN_KEY_CHECKS=1"))