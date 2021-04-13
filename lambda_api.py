import os
import json
import redis 
from sqlalchemy import create_engine

from api.view.views import ping
from api.injectors  import get_services

database = create_engine(f"http://testdb?charset=utf8")
redis    = redis.Redis('localhost')

facebook_credentials = {
    'FACEBOOK_API_URL'  : os.FACEBOOK_API_URL,
    'VERIFY_TOKEN'      : os.VERIFY_TOKEN,
    'PAGE_ACCESS_TOKEN' : os.PAGE_ACCESS_TOKEN
}
SERVICE_KEY = os.SERVICE_KEY

services = get_services(database, redis, facebook_credentials)

def lambda_handler_get(event, context):
    response = check_verify_token(services, facebook_credentials)

    return {
        "statusCode": 200,
        "body": json.dumps(response),
    }

def lambda_handler_post(event, context):
    response = facebook_message(services, facebook_credentials, SERVICE_KEY)

    return {
        "statusCode": 200,
        "body": json.dumps(response),
    }
