import { useEffect, useState } from "react";
import wsInstance from "../socket/websocketService";
import "./Chat.css";

function Chat() {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState("");

  // useEffect(() => {
  //   wsInstance.connect("ws://192.168.1.3:8765", () => {
  //     console.log("WebSocket connection opened");
  //   });

  //   wsInstance.ws.onerror = (error) => {
  //     console.error(`WebSocket error: ${error}`);
  //   };

  //   wsInstance.ws.onmessage = (event) => {
  //       setMessages((prevMessages) => [...prevMessages, { text: event.data, sentByUser: false }]);
  //      };
  // }, []);

  // const sendMessage = () => {
  //   if (newMessage.trim() !== "") {
  //   wsInstance.send(newMessage);
  //   setMessages((prevMessages) => [...prevMessages, { text: `You: ${newMessage}`, sentByUser: true }]);
  //   setNewMessage('');
  //   }
  //  };

  return (
    <div className="container">
      <div className="chatbox">
        {messages.map((message, index) => (
          <p
            key={index}
            className={message.sentByUser ? "message sent-message" : "message"}
          >
            {message.text}
          </p>
        ))}
      </div>
      <div>
        <input
          type="text"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          className="inputbox"
        />
        <button onClick={sendMessage} className="send-btn">
          Send
        </button>
      </div>
    </div>
  );
}

export default Chat;
