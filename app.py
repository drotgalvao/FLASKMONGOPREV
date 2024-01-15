# app.py
from flask import Flask, request
from flask_cors import CORS
from flask_pymongo import PyMongo
from user.user_routes import user_bp
from flask_socketio import SocketIO, join_room, leave_room, emit

from functools import wraps
import jwt
import os
from dotenv import load_dotenv

import redis

load_dotenv()
SECRET_KEY = os.environ.get("SECRET_KEY")

user_data = {}


def authenticated_only(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        token = request.cookies.get("token")
        print(token)
        if not token:
            emit("authentication_error", {"error": "Authentication token is missing"})
            return False  # Reject the connection

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            print("Token decodificado com sucesso", payload)
            user_id = payload.get("user_id")
            print(payload)
            user_data[request.sid] = {
                "user_id": user_id,
                "nome": payload.get("nome"),
                "email": payload.get("email"),
            }
        except jwt.ExpiredSignatureError:
            emit("authentication_error", {"error": "Token expired"})
            return False  # Rejeitar a conexão
        except jwt.InvalidTokenError:
            emit("authentication_error", {"error": "Invalid token"})
            return False  # Rejeitar a conexão

        return f(*args, **kwargs)

    return wrapped


app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"], supports_credentials=True)
app.config["MONGO_URI"] = "mongodb://localhost:27017/click-game-db"
mongo = PyMongo(app)
app.mongo = mongo

r = redis.Redis(host='localhost', port=6379, db=0)
r.set('mykey', 'Hello')

socketio = SocketIO(app, cors_allowed_origins="*")

app.register_blueprint(user_bp, url_prefix="/api")


################################### socket
rooms = {}
users = {}


@socketio.on("join_game")
def on_join_game(data):
    print("Join game request received", data)
    username = data["username"]
    room = data["room"]
    session_id = request.sid

    if room not in rooms:
        rooms[room] = []

    if username in rooms[room]:
        emit("join_error", {"msg": "You are already in the room."}, room=room)
        return

    if len(rooms[room]) < 4:
        join_room(room)
        rooms[room].append(username)
        users[session_id] = {"username": username, "room": room}
        emit(
            "join_announcement", {"msg": f"{username} has joined the game."}, room=room
        )
    else:
        emit("join_error", {"msg": "Sorry, the game room is full."})


@socketio.on("list_rooms")
def on_list_rooms():
    print("List rooms request received")
    rooms_list = {room: len(members) for room, members in rooms.items()}
    emit("rooms_list", rooms_list)
    if len(rooms_list) != 0:
        print("Users:", users)


@socketio.on("send_message")
def on_send_message(data):
    username = data["username"]
    room = data["room"]
    message = data["message"]
    emit("new_message", {"username": username, "msg": message}, room=room)


@socketio.on("connect")
@authenticated_only
def handle_connect():
    print("Client authenticated and connected with ID:", request.sid)
    # Acessar os dados do usuário
    user = user_data[request.sid]
    print("User data:", user)


@socketio.on("leave_game")
def on_leave_game(data):
    username = data["username"]
    room = data["room"]
    session_id = request.sid
    leave_room(room)
    if room in rooms and username in rooms[room]:
        rooms[room].remove(username)
        if not rooms[room]:
            del rooms[room]
        emit("leave_announcement", {"msg": f"{username} has left the game."}, room=room)
    if session_id in users:
        del users[session_id]


@socketio.on("disconnect")
def handle_disconnect():
    session_id = request.sid
    if session_id in users:
        user_info = users[session_id]
        username = user_info["username"]
        room = user_info["room"]
        leave_room(room)
        if room in rooms and username in rooms[room]:
            rooms[room].remove(username)
            if not rooms[room]:
                del rooms[room]
            emit(
                "leave_announcement",
                {"msg": f"{username} has left the game."},
                room=room,
            )
        del users[session_id]
    print("Client disconnected")


def handle_click(user_id):
   clicks = r.incr(user_id)
   r.set(user_id, clicks)

@socketio.on('click')
def handle_click_event(data):
   user_id = data['user_id']
   handle_click(user_id)

def save_game_to_db(game_id, players):
   players_dict = {player['user_id']: player['clicks'] for player in players}
   app.mongo.db.games.insert_one({'_id': game_id, 'players': players_dict})

@socketio.on('end_game')
def handle_end_game_event(data):
   game_id = data['game_id']
   players = data['players']
   save_game_to_db(game_id, players)

if __name__ == "__main__":
    socketio.run(app, debug=True)
