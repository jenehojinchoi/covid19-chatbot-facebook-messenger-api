import pytest
import redis
import json
import config

from sqlalchemy    import create_engine
from api.injectors import create_app

test_db = create_engine(f"{config.TEST_DB_CONNECTION_URL}?charset=utf8")
redis    = redis.Redis('localhost')

facebook_credentials = {
    'FACEBOOK_API_URL'  : config.FACEBOOK_API_URL,
    'VERIFY_TOKEN'      : config.VERIFY_TOKEN,
    'PAGE_ACCESS_TOKEN' : config.PAGE_ACCESS_TOKEN
}

@pytest.fixture
def api():
    app = create_app(test_db, facebook_credentials, redis)
    app.config['TEST'] = True
    api = app.test_client()

    return api

def test_view_post_success_message(api):
    response = api.post(
        "/",
        data=json.dumps( {'object': 'page', 
        'entry': [{
            'id': '12345678902',
            'messaging': [{'sender': {'id': '12345678901'},
                'recipient': {'id': '12345678902'},
                'message': {
                    'text': '안녕', 
                    'quick_reply': {'payload': '<POSTBACK_PAYLOAD>'}
                    }
                }]
            }]
        }),
        content_type="application/json",
    )
    assert response.status_code == 200

def test_view_post_fail_text_missing(api):
    response = api.post(
        "/",
        data=json.dumps( {'object': 'page', 
        'entry': [{
            'id': '12345678902',
            'messaging': [{'sender': {'id': '12345678901'},
                'recipient': {'id': '12345678902'},
                'message': {
                    'quick_reply': {'payload': '<POSTBACK_PAYLOAD>'}
                    }
                }]
            }]
        }),
        content_type="application/json",
      )

    assert response.status_code == 500 

