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
from datetime import datetime

import redis
import threading
import time

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

r = redis.Redis(host="localhost", port=6379, db=0)
r.set("mykey", "Hello")

socketio = SocketIO(app, cors_allowed_origins="*", ping_timeout=10)

app.register_blueprint(user_bp, url_prefix="/api")


################################### socket
rooms = {}
users = {}
last_activity = {}
game_timers = {}



def start_timer(room):
    def timer_finished():
        print(f"Timer finished for room {room}")
        start_game(room)

    print(f"Starting timer for room {room}")

    socketio.emit("timer_started", {"room": room, "countdown": 10}, room=room)

    game_timers[room] = threading.Timer(10.0, timer_finished)
    game_timers[room].start()

def start_game(room):
    def game_finished():
        print(f"Game finished in room {room}")


    print(f"Starting game in room {room}")

    socketio.emit("game_started", {"room": room, "countdown": 60}, room=room)

    game_timers[room] = threading.Timer(60.0, game_finished)
    game_timers[room].start()





@socketio.on("join_game")
def on_join_game(data):
   print("Join game request received", data)
   room = data["room"]
   session_id = request.sid

   if room not in rooms:
       rooms[room] = []

   user_info = user_data[session_id]
   username = user_info["nome"]
   user_id = user_info["user_id"]

   if username in rooms[room]:
       emit("join_error", {"msg": "You are already in the room."}, room=room)
       return

   if len(rooms[room]) < 4:
       join_room(room)
       rooms[room].append(username)
       users[session_id] = {"username": username, "room": room, "user_id": user_id}
       emit(
           "join_announcement", {"msg": f"{username} has joined the game."}, room=room
       )

       if len(rooms[room]) >= 2:
           start_timer(room)

       r.hset(user_id, 'score', 0)

   else:
       emit("join_error", {"msg": "Sorry, the game room is full."})


@socketio.on("list_rooms")
def on_list_rooms():
    # print("List rooms request received")
    rooms_list = {room: len(members) for room, members in rooms.items()}
    emit("rooms_list", rooms_list)
    # if len(rooms_list) != 0:
    #     print("Users:", users)


@socketio.on("send_message")
def on_send_message(data):
    room = data["room"]
    message = data["message"]
    session_id = request.sid
    user_info = user_data[session_id]
    username = user_info["nome"]
    emit("new_message", {"username": username, "msg": message}, room=room)


@socketio.on("connect")
@authenticated_only
def handle_connect():
   print("Client authenticated and connected with ID:", request.sid)
   user = user_data[request.sid]
   print("User data:", user)
   last_activity[request.sid] = datetime.utcnow()

   existing_session = next((session for session, data in users.items() if data['user_id'] == user['user_id']), None)

   if existing_session:
       users[existing_session] = {"username": user['nome'], "room": None, "user_id": user['user_id']}
   else:
       users[request.sid] = {"username": user['nome'], "room": None, "user_id": user['user_id']}


@socketio.on("leave_game")
def on_leave_game(data):
    room = data["room"]
    session_id = request.sid
    user_info = user_data[session_id]
    username = user_info["nome"]
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
        username = user_info["nome"]
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


@socketio.on('add_point')
def on_add_point():
 session_id = request.sid

 if session_id in users:
     user_id = users[session_id]['user_id']
     room = users[session_id]['room']

     current_score = int(r.hget(f'{room}_score', user_id) or 0)

     new_score = current_score + 1

     r.hset(f'{room}_score', user_id, new_score)


     print(f"Score updated for user {user_id} in room {room}: {new_score}")
     show_scores()
 else:
     print(f"No user found for session id: {session_id}")


@socketio.on('subtract_point')
def on_subtract_point():
  session_id = request.sid

  if session_id in users:
      user_id = users[session_id]['user_id']
      room = users[session_id]['room']

      current_score = int(r.hget(f'{room}_score', user_id) or 0)

      new_score = current_score - 1

      r.hset(f'{room}_score', user_id, new_score)

      print(f"Score updated for user {user_id} in room {room}: {new_score}")
      show_scores()
  else:
      print(f"No user found for session id: {session_id}")


@socketio.on('show_scores')
def show_scores():
   for room in rooms.values():
       for user_id in room:
           score = int(r.hget(f'{room}_score', user_id) or 0)
           emit('user_score', {'user_id': user_id, 'score': score}, room=room)


if __name__ == "__main__":
    socketio.run(app, debug=True)
