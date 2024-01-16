# user_routes.py
from flask import Blueprint, request, current_app
from user.user_controller import register_user, get_user, login_user

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    mongo = current_app.mongo
    return register_user(mongo, data)


@user_bp.route('/user/<user_id>', methods=['GET'])
def get_user_route(user_id):
   mongo = current_app.mongo
   return get_user(mongo, user_id)

@user_bp.route('/login', methods=['POST'])
def login():
    mongo = current_app.mongo
    return login_user(mongo)