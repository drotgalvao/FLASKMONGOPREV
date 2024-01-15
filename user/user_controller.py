# user\user_controller.py
from dotenv import load_dotenv
import os
from user.user_model import User
import bcrypt
from bson import ObjectId
from flask import jsonify, request, make_response
import datetime
import jwt

load_dotenv()
SECRET_KEY = os.environ.get('SECRET_KEY')

def register_user(mongo, data):
    nome = data.get('nome')
    email = data.get('email')
    password = data.get('password')
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    if mongo.db.users.find_one({'email': email}):
        return {'error': 'Email already exists'}, 400
    else:
        user = User(nome, email, hashed_password)
        mongo.db.users.insert_one(user.__dict__)
        return {'message': 'User registered successfully'}, 201
   
def get_user(mongo, user_id):
    user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    if user:
        user['_id'] = str(user['_id'])
        return jsonify(user), 200
    else:
        return {'error': 'User not found'}, 404
    

def login_user(mongo):
    email = request.json.get('email')
    password = request.json.get('password')
    user = mongo.db.users.find_one({'email': email})

    if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        payload = {
            'user_id': str(user['_id']),
            'email': user['email'],
            'nome': user['nome'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        response = make_response(jsonify({'token': token}), 200)

        response.set_cookie('token', token, httponly=False, secure=True, samesite='None')
        return response
    else:
        return jsonify({'error': 'Invalid credentials'}), 401