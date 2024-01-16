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
  const [timeRemaining, setTimeRemaining] = useState(null);
  const [gameTimeRemaining, setGameTimeRemaining] = useState(null);
  const [gameStarted, setGameStarted] = useState(false);
  const [cancelMessage, setCancelMessage] = useState('');
  const [scores, setScores] = useState({});
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

    socketRef.current.on("update_scores", (updatedScores) => {
      setScores(updatedScores);
    });

    let countdownInterval;

    socketRef.current.on("timer_started", (data) => {
     // Clear the previous interval if it exists
     if (countdownInterval) {
       clearInterval(countdownInterval);
     }
    
     setTimeRemaining(10); // Set the countdown back to 10 seconds
     countdownInterval = setInterval(() => {
       setTimeRemaining((prevTime) => prevTime - 1);
     }, 1000);
     setTimeout(() => {
       clearInterval(countdownInterval);
       setTimeRemaining(null);
     }, 10000); // Set the timeout to 10 seconds
    });

    let gameCountdownInterval;

    socketRef.current.on("game_started", (data) => {
     setGameTimeRemaining(data.countdown);
     setGameStarted(true);
     gameCountdownInterval = setInterval(() => {
      setGameTimeRemaining((prevTime) => prevTime - 1);
     }, 1000);
     setTimeout(() => {
      clearInterval(gameCountdownInterval);
      setGameTimeRemaining(null);
      setGameStarted(false);
      setScores({});
     }, data.countdown * 1000);
    });
    
    socketRef.current.on("game_start_cancelled", ({ msg }) => {
     clearInterval(gameCountdownInterval);
     setGameTimeRemaining(null);
     setGameStarted(false);
     setCancelMessage(msg);
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
      socketRef.current.emit("join_game", { room });
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
      socketRef.current.emit("send_message", { room, message });
    }
  };

  const requestRoomList = () => {
    if (socketRef.current) {
      socketRef.current.emit("list_rooms");
    }
  };

  // requestRoomList();

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

      // Emitir o evento add_point
      if (socketRef.current) {
        socketRef.current.emit("add_point");
      }
    } else {
      setClicks(clicks - 1);
      const randX = Math.floor(Math.random() * 5);
      const randY = Math.floor(Math.random() * 5);
      setBlueSquarePosition({ x: randX, y: randY });

      // Emitir o evento subtract_point
      if (socketRef.current) {
        socketRef.current.emit("subtract_point");
      }
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
      <div className="scoreboard">
        {Object.values(scores)
          .sort((a, b) => b.score - a.score)
          .map(({ username, score }) => (
            <div key={username}>
              <span>
                {username}: {score}
              </span>
            </div>
          ))}
      </div>
      {timeRemaining !== null && <p>Time remaining: {timeRemaining} seconds</p>}
      {gameTimeRemaining !== null && (
        <p>Game time remaining: {gameTimeRemaining} seconds</p>
      )}
      <div className="game-container">
        {/* <p className="num_clicks">Number of clicks: {clicks}</p> */}

        {gameStarted && <>{generateSquares()}</>}
      </div>
    </div>
  );
}

export default Game;
