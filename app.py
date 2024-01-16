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
import json

load_dotenv()
SECRET_KEY = os.environ.get("SECRET_KEY")

# user_data = {}


def authenticated_only(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        token = request.cookies.get("token")
        print(token)
        if not token:
            emit("authentication_error", {"error": "Authentication token is missing"})
            return False

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            print("Token decodificado com sucesso", payload)
            user_data = {
                "user_id": payload.get("user_id"),
                "nome": payload.get("nome"),
                "email": payload.get("email"),
            }

            r.set(request.sid, json.dumps(user_data))
            print(request.sid)
            # user_id = payload.get("user_id")
            # user_data[request.sid] = {
            #     "user_id": user_id,
            #     "nome": payload.get("nome"),
            #     "email": payload.get("email"),
            # }
        except jwt.ExpiredSignatureError:
            emit("authentication_error", {"error": "Token expired"})
            return False
        except jwt.InvalidTokenError:
            emit("authentication_error", {"error": "Invalid token"})
            return False

        return f(*args, **kwargs)

    return wrapped


app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"], supports_credentials=True)
app.config["MONGO_URI"] = "mongodb://localhost:27017/click-game-db"
mongo = PyMongo(app)
app.mongo = mongo

r = redis.Redis(host="localhost", port=6379, db=0)
r.flushall()


socketio = SocketIO(app, cors_allowed_origins="*", ping_timeout=10)

app.register_blueprint(user_bp, url_prefix="/api")


################################### socket
rooms = {}
users = {}
last_activity = {}
game_timers = {}


def start_timer(room):
    def timer_finished():
        if room not in rooms or len(rooms[room]) < 2:
            return

        print(f"Timer finished for room {room}")
        start_game(room)

    print(f"Starting timer for room {room}")

    socketio.emit("timer_started", {"room": room, "countdown": 10}, room=room)

    if room in game_timers:
        game_timers[room].cancel()

    game_timers[room] = threading.Timer(10.0, timer_finished)
    game_timers[room].start()


def start_game(room):
    if room not in rooms or len(rooms[room]) < 2:
        return

    def game_finished():
        print(f"Game finished in room {room}")
        game_results = []
        user_ids = set()

        for session_id, user_info in list(users.items()):
            if user_info["room"] == room and user_info["user_id"] not in user_ids:
                game_results.append(
                    {
                        "username": user_info["username"],
                        "user_id": user_info["user_id"],
                        "score": user_info["score"],
                    }
                )
                user_ids.add(user_info["user_id"])
                user_info["score"] = 0
                users[session_id] = user_info

        if game_results:
            app.mongo.db.game_results.insert_one(
                {
                    "room": room,
                    "results": game_results,
                    "finished_at": datetime.utcnow(),
                }
            )

        del rooms[room]

    print(f"Starting game in room {room}")

    socketio.emit("game_started", {"room": room, "countdown": 60}, room=room)

    game_timers[room] = threading.Timer(60.0, lambda: game_finished())
    game_timers[room].start()


@socketio.on("join_game")
def on_join_game(data):
   print("Join game request received", data)
   room = data["room"]
   session_id = request.sid

   if not r.exists(room):
       r.set(room, json.dumps([]))

   user_info = json.loads(r.get(session_id))
   username = user_info["nome"]
   user_id = user_info["user_id"]

   room_users = json.loads(r.get(room))
   if username in room_users:
       emit("join_error", {"msg": "You are already in the room."}, room=room)
       return

   if len(room_users) < 4:
       join_room(room)
       room_users.append(username)
       r.set(room, json.dumps(room_users))
       user_data = {
           "username": username,
           "room": room,
           "user_id": user_id,
           "score": 0,
       }
       r.set(session_id, json.dumps(user_data))
       emit(
           "join_announcement", {"msg": f"{username} has joined the game."}, room=room
       )

       if len(room_users) >= 2:
           start_timer(room)

   else:
       emit("join_error", {"msg": "Sorry, the game room is full."})


@socketio.on("list_rooms")
def on_list_rooms():
    # print("List rooms request received")
    print(users)
    rooms_list = {room: len(members) for room, members in rooms.items()}
    emit("rooms_list", rooms_list)
    # if len(rooms_list) != 0:
    #     print("Users:", users)


@socketio.on("send_message")
def on_send_message(data):
    room = data["room"]
    message = data["message"]
    session_id = request.sid
    # user_info = user_data[session_id]
    user_info = json.loads(r.get(session_id))
    username = user_info["nome"]
    emit("new_message", {"username": username, "msg": message}, room=room)


@socketio.on("connect")
@authenticated_only
def handle_connect():
    print("Client authenticated and connected with ID:", request.sid)
    # user = user_data[request.sid]
    user = json.loads(r.get(request.sid))
    print("User data:", user)
    last_activity[request.sid] = datetime.utcnow()

    existing_session = next(
        (
            session
            for session, data in users.items()
            if data["user_id"] == user["user_id"]
        ),
        None,
    )

    if existing_session:
        users[existing_session] = {
            "username": user["nome"],
            "room": None,
            "user_id": user["user_id"],
        }
    else:
        users[request.sid] = {
            "username": user["nome"],
            "room": None,
            "user_id": user["user_id"],
        }


@socketio.on("leave_game")
def on_leave_game(data):
    room = data["room"]
    session_id = request.sid
    #    user_info = user_data[session_id]
    user_info = json.loads(r.get(session_id))
    username = user_info["nome"]
    leave_room(room)
    if room in rooms and username in rooms[room]:
        rooms[room].remove(username)
        if not rooms[room]:
            del rooms[room]
        emit("leave_announcement", {"msg": f"{username} has left the game."}, room=room)
    if session_id in users:
        del users[session_id]
    if room in rooms and len(rooms[room]) < 2:
        emit(
            "game_start_cancelled",
            {"msg": "Not enough players to start the game."},
            room=room,
        )


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
        # del users[session_id]
        r.delete(session_id)
    print("Client disconnected")


@socketio.on("add_point")
def on_add_point():
    session_id = request.sid

    if session_id in users:
        user_id = users[session_id]["user_id"]
        room = users[session_id]["room"]

        current_score = users[session_id]["score"]

        new_score = current_score + 1

        users[session_id]["score"] = new_score

        print(f"Score updated for user {user_id} in room {room}: {new_score}")
        emit_scores(room)
    else:
        print(f"No user found for session id: {session_id}")


@socketio.on("subtract_point")
def on_subtract_point():
    session_id = request.sid

    if session_id in users:
        user_id = users[session_id]["user_id"]
        room = users[session_id]["room"]

        current_score = users[session_id]["score"]

        new_score = current_score - 1

        users[session_id]["score"] = new_score

        # print(f"Score updated for user {user_id} in room {room}: {new_score}")
        emit_scores(room)
    else:
        print(f"No user found for session id: {session_id}")


def emit_scores(room):
    # print(users)
    filtered_users = {sid: user for sid, user in users.items() if user["room"] == room}
    socketio.emit("update_scores", filtered_users, room=room)


if __name__ == "__main__":
    socketio.run(app, debug=True)
