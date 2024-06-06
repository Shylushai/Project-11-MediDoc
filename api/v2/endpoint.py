from flask import Blueprint
from api.v2.login import login

endpoint_v2 = Blueprint('login', __name__)
endpoint_v2.register_blueprint(login)
