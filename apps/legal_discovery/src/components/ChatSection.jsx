import React, { useState, useEffect, useRef } from "react";
import { io } from "socket.io-client";

function ChatSection() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const boxRef = useRef(null);

  useEffect(() => {
    const socket = io("/chat");
    socket.on("update_speech", (d) =>
      setMessages((m) => [...m, { type: "assistant", text: d.data }])
    );
    socket.on("update_user_input", (d) =>
      setMessages((m) => [...m, { type: "user", text: d.data }])
    );
    return () => socket.disconnect();
  }, []);

  useEffect(() => {
    if (boxRef.current) {
      boxRef.current.scrollTop = boxRef.current.scrollHeight;
    }
  }, [messages]);

  const send = () => {
    if (!input.trim()) return;
    fetch("/api/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: input }),
    }).then(() => setInput(""));
  };

  return (
    <section className="card">
      <h2>Chat</h2>
      <div
        ref={boxRef}
        className="chat-box overflow-y-auto" 
        style={{ maxHeight: "200px" }}
      >
        {messages.map((m, i) => (
          <div
            key={i}
            className={
              m.type === "user" ? "text-right text-blue-400" : "text-left text-green-300"
            }
          >
            {m.text}
          </div>
        ))}
      </div>
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        rows="2"
        className="w-full mb-2 p-2 rounded bg-gray-800 text-gray-100"
        placeholder="Ask the assistant..."
      ></textarea>
      <button className="button-primary" onClick={send}>
        Send
      </button>
    </section>
  );
}

export default ChatSection;
