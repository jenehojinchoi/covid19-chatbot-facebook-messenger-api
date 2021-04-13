from api.service.user_service    import UserService
from api.service.message_service import MessageService
from api.models.user_dao         import UserDao
from api.models.message_dao      import MessageDao

class Services:
    pass

def get_services(database):
    user_dao                 = UserDao(database)
    message_dao              = MessageDao(database)
    services                 = Services()
    services.user_service    = UserService(user_dao)
    services.message_service = MessageService(message_dao)

    return services
