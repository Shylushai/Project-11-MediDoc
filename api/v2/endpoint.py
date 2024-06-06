from flask import Blueprint
import api.v2.login

endpoint_v2 = Blueprint('v2', __name__)
endpoint_v2.register_blueprint(api.v2.login.bp)
