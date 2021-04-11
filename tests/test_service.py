import pytest
import redis
import json
import config

from sqlalchemy                   import create_engine, text
from api.injectors                import create_app
from api.models.message_dao       import MessageDao
from api.models.user_dao          import UserDao
from api.service.message_service  import MessageService, Bot
from api.service.user_service     import UserService

test_db = create_engine(f"{config.TEST_DB_CONNECTION_URL}?charset=utf8")
redis   = redis.Redis('localhost')

facebook_credentials = {
    'FACEBOOK_API_URL'  : config.FACEBOOK_API_URL,
    'VERIFY_TOKEN'      : config.VERIFY_TOKEN,
    'PAGE_ACCESS_TOKEN' : config.PAGE_ACCESS_TOKEN
}

@pytest.fixture
def message_service():
    return MessageService(MessageDao(test_db), redis)

@pytest.fixture
def user_service():
    return UserService(UserDao(test_db), redis)

@pytest.fixture
def bot():
    return Bot(facebook_credentials['PAGE_ACCESS_TOKEN'])

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

def test_auth_args(bot):
    assert bot.auth_args == {'access_token':facebook_credentials['PAGE_ACCESS_TOKEN']}

def test_send_message(bot):
    processed_reply = {'text': 'test reply'}
    assert bot.send_message('5124320487641465', processed_reply)['recipient_id'] == '5124320487641465' 

def test_check_verify_token(message_service):
    assert message_service.check_verify_token('my_secret_token', 'my_secret_token')

def test_get_covid_data(message_service):
    data = message_service.get_covid_data(config.SERVICE_KEY) 
    assert data != None

def test_get_next_state_initial(message_service):
    data = message_service.get_covid_data(config.SERVICE_KEY)
    next_state = message_service.get_next_state(data, 1, 'INITIAL', '안녕')
    assert next_state == 'CASES_OR_POLICY'

def test_get_next_state_cases_or_policy__cases(message_service):
    data = message_service.get_covid_data(config.SERVICE_KEY) 
    next_state = message_service.get_next_state(data, 1, 'CASES_OR_POLICY', '일일 확진자수 확인')
    assert next_state == 'COUNTRY_OR_CITY'

def test_get_next_state_cases_or_policy__policy(message_service):
    data = message_service.get_covid_data(config.SERVICE_KEY) 
    next_state = message_service.get_next_state(data, 1, 'CASES_OR_POLICY', '사회적 거리두기 현황 확인')
    assert next_state == 'POLICY'

def test_get_next_state_choose_cities__city(message_service):
    data = message_service.get_covid_data(config.SERVICE_KEY) 
    next_state = message_service.get_next_state(data, 1, 'CHOOSE_CITIES', '세종')
    assert next_state == 'CITY_CASES'

def test_get_next_state_choose_cities__more_city(message_service):
    data = message_service.get_covid_data(config.SERVICE_KEY) 
    next_state = message_service.get_next_state(data, 1, 'CHOOSE_CITIES', '다른 지역도 확인할래')
    assert next_state == 'CHOOSE_MORE_CITIES'

def test_get_next_state_choose_cities__request_error(message_service):
    data = message_service.get_covid_data(config.SERVICE_KEY) 
    next_state = message_service.get_next_state(data, 1, 'CHOOSE_CITIES', '몰라')
    assert next_state == 'REQUEST_ERROR'

def test_get_next_state_request_error__cases_or_policy(message_service):
    data = message_service.get_covid_data(config.SERVICE_KEY) 
    message_service.save_message(1, '안녕', 'INITIAL', 'CASES_OR_POLICY')
    message_id = message_service.save_message(1, '뭐지', 'CASES_OR_POLICY', 'REQUEST_ERROR')
    next_state = message_service.get_next_state(data, 1, 'REQUEST_ERROR', '뭐지')
    assert next_state == 'CASES_OR_POLICY'

def test_get_next_state_city_cases__initial(message_service):
    data = message_service.get_covid_data(config.SERVICE_KEY) 
    next_state = message_service.get_next_state(data, 1, 'CITY_CASES', '아니, 없어')
    assert next_state == 'INITIAL'

def test_get_current_state(message_service):
    current_state = message_service.get_current_state(1)
    assert current_state == 'INITIAL'

def test_save_message(message_service):
    assert message_service.save_message(1, '안녕', 'INITIAL', 'CASES_OR_POLICY') == 3

def test_save_reply(message_service):
    reply = '안녕하세요, 코로나 알리미 봇입니다.'
    assert message_service.save_reply(1, reply) == 1

def test_save_user(user_service):
    assert user_service.save_user('12345678903') == 3
    
def teardown_function():
    test_db.execute(text("SET FOREIGN_KEY_CHECKS=0"))
    test_db.execute(text("TRUNCATE users"))
    test_db.execute(text("TRUNCATE messages"))
    test_db.execute(text("TRUNCATE replies"))
    test_db.execute(text("SET FOREIGN_KEY_CHECKS=1"))