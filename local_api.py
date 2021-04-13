from flask      import Flask
from flask_cors import CORS

from sqlalchemy    import create_engine
from api.injectors import get_services
import config

from api.view.views import ping

database = create_engine(f"{config.DB_CONNECTION_URL}?charset=utf8")
services = get_services(database)

app = Flask(__name__)
app.add_url_rule('/', 'check_verify_token', check_verify_token, defaults={"services": services})
app.add_url_rule('/', 'facebook_message', facebook_message, defaults={"services": services})

CORS(app)
