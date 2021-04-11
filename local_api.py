import redis

from sqlalchemy    import create_engine

import config
from api.injectors import create_app

database = create_engine(f"{config.DB_CONNECTION_URL}?charset=utf8")
redis    = redis.Redis('localhost')

facebook_credentials = {
    'FACEBOOK_API_URL'  : config.FACEBOOK_API_URL,
    'VERIFY_TOKEN'      : config.VERIFY_TOKEN,
    'PAGE_ACCESS_TOKEN' : config.PAGE_ACCESS_TOKEN
}
app = create_app(database, facebook_credentials, redis)
