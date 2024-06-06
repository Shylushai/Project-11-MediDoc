from flask import Blueprint, request, jsonify

from utils.general import init_db_connection

login = Blueprint('login', __name__, url_prefix='/login')

@login.route('/', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    cn = init_db_connection()
    cursor = cn.cursor()
    cursor.execute('SELECT * FROM Users WHERE username = ?', (username,))
    user = cursor.fetchone()
    cn.close()
    result = {'username': user['username'], 'password': user['password']}
    return result