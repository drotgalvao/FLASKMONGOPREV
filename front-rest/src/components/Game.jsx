import React, { useState, useEffect, useRef } from "react";
import io from "socket.io-client";
import Cookies from "js-cookie";
import "./Game.css";

function Game() {
  const [username, setUsername] = useState("");
  const [room, setRoom] = useState("");
  const [message, setMessage] = useState("");
  const [roomsList, setRoomsList] = useState({});
  const [inRoom, setInRoom] = useState(false);
  const [blueSquarePosition, setBlueSquarePosition] = useState({ x: 0, y: 0 });
  const [clicks, setClicks] = useState(0);
  const socketRef = useRef();

  const token = Cookies.get("token");

  useEffect(() => {
    socketRef.current = io("http://localhost:5000", {
      withCredentials: true,
      transportOptions: {
        polling: {
          extraHeaders: {
            Authorization: `Bearer ${token}`,
          },
        },
      },
    });

    socketRef.current.on("join_announcement", (data) => {
      const item = document.createElement("li");
      item.textContent = data.msg;
      document.getElementById("messages").appendChild(item);
      window.scrollTo(0, document.body.scrollHeight);
    });

    socketRef.current.on("leave_announcement", (data) => {
      const item = document.createElement("li");
      item.textContent = data.msg;
      document.getElementById("messages").appendChild(item);
      window.scrollTo(0, document.body.scrollHeight);
    });

    socketRef.current.on("new_message", (data) => {
      const item = document.createElement("li");
      item.textContent = `${data.username}: ${data.msg}`;
      document.getElementById("messages").appendChild(item);
      window.scrollTo(0, document.body.scrollHeight);
    });

    socketRef.current.on("rooms_list", (roomsList) => {
      const roomsContainer = document.getElementById("rooms-container");
      roomsContainer.innerHTML = ""; // Clear current list

      Object.keys(roomsList).forEach((room) => {
        const roomElement = document.createElement("div");
        roomElement.textContent = `Room: ${room} (${roomsList[room]} members)`;
        roomsContainer.appendChild(roomElement);
      });
    });

    return () => {
      socketRef.current.disconnect();
    };
  }, []);

  const joinRoom = () => {
    if (socketRef.current) {
      socketRef.current.emit("join_game", { username, room });
      setInRoom(true);
    }
  };

  const leaveRoom = () => {
    if (socketRef.current) {
      socketRef.current.emit("leave_game", { username, room });
      setInRoom(false);
    }
  };

  const sendMessage = () => {
    if (socketRef.current) {
      socketRef.current.emit("send_message", { username, room, message });
    }
  };

  const requestRoomList = () => {
    if (socketRef.current) {
      socketRef.current.emit("list_rooms");
    }
  };

  requestRoomList();

  // useEffect(() => {
  //   const initialX = Math.floor(Math.random() * 5);
  //   const initialY = Math.floor(Math.random() * 5);
  //   setBlueSquarePosition({ x: initialX, y: initialY });
  //  }, []);

  const handleClick = (x, y) => {
    if (x === blueSquarePosition.x && y === blueSquarePosition.y) {
      setClicks(clicks + 1);
      const randX = Math.floor(Math.random() * 5);
      const randY = Math.floor(Math.random() * 5);
      setBlueSquarePosition({ x: randX, y: randY });
    } else {
      setClicks(clicks - 1);
      const randX = Math.floor(Math.random() * 5);
      const randY = Math.floor(Math.random() * 5);
      setBlueSquarePosition({ x: randX, y: randY });
    }
   };
   
   const generateSquares = () => {
    let squares = [];
    for (let i = 0; i < 5; i++) {
      for (let j = 0; j < 5; j++) {
        squares.push(
          <div
            key={`${i}-${j}`}
            style={{
              backgroundColor: `${
                i === blueSquarePosition.x && j === blueSquarePosition.y
                  ? "blue"
                  : "white"
              }`,
              width: "100px",
              height: "100px",
              border: "1px solid black",
            }}
            onClick={() => handleClick(i, j)}
          ></div>
        );
      }
    }
    return squares;
   };

  return (
    <div className="page">
      <div className="chat-container">
        <h1>Multiplayer Game Room</h1>
        <div id="rooms-container"></div>
        <button onClick={requestRoomList}>Refresh Rooms</button>
        <div id="room-form">
          <input
            id="username"
            type="text"
            placeholder="Enter your username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <input
            id="room"
            type="text"
            placeholder="Enter room name"
            value={room}
            onChange={(e) => setRoom(e.target.value)}
          />
          <button onClick={joinRoom}>Join Room</button>
          <button onClick={leaveRoom}>Leave Room</button>
        </div>
        <div id="message-form">
          <input
            id="message"
            type="text"
            placeholder="Enter message"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
          />
          <button onClick={sendMessage}>Send Message</button>
        </div>
        <ul id="messages"></ul>
      </div>
      <div className="game-container">
      <p className="num_clicks">Number of clicks: {clicks}</p>
        
        {inRoom && (
          <>
            {generateSquares()}
          </>
        )}
      </div>
    </div>
  );
}

export default Game;