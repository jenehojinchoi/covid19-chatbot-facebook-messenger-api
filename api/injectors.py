from flask      import Flask
from flask_cors import CORS

from api.view.views              import create_endpoints
from api.service.user_service    import UserService
from api.service.message_service import MessageService
from api.models.user_dao         import UserDao
from api.models.message_dao      import MessageDao

class Services:
    pass

def create_app(database, facebook_credentials, cache):
    app = Flask(__name__)
    CORS(app)

    user_dao = UserDao(database)
    message_dao = MessageDao(database)

    services = Services()
    services.user_service = UserService(user_dao, cache)
    services.message_service = MessageService(message_dao, cache)

    create_endpoints(app, services, facebook_credentials)

    return app