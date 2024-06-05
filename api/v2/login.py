from flask import Blueprint, request, jsonify

login = Blueprint('login', __name__, url_prefix='/login')

@login.route('/', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    result = {'username': username, 'password': password}
    return result