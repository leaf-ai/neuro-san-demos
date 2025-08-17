import React, { useState, useEffect, useRef } from "react";
import { io } from "socket.io-client";

function ChatSection() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [recording, setRecording] = useState(false);
  const [voiceModel, setVoiceModel] = useState("en-US");
  const [conversationId, setConversationId] = useState(null);
  const boxRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  useEffect(() => {
    const socket = io("/chat");
    socket.on("update_speech", (d) =>
      setMessages((m) => [...m, { type: "assistant", text: d.data }])
    );
    socket.on("update_user_input", (d) =>
      setMessages((m) => [...m, { type: "user", text: d.data }])
    );
    socket.on("voice_output", (d) => {
      if (d.audio) {
        const audio = new Audio(`data:audio/mp3;base64,${d.audio}`);
        audio.play();
      }
    });
    return () => socket.disconnect();
  }, []);

  useEffect(() => {
    if (boxRef.current) {
      boxRef.current.scrollTop = boxRef.current.scrollHeight;
    }
  }, [messages]);

  const send = () => {
    if (!input.trim()) return;
    fetch("/api/chat/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: input,
        voice_model: voiceModel,
        conversation_id: conversationId,
      }),
    })
      .then((r) => r.json())
      .then((d) => {
        if (d.conversation_id) setConversationId(d.conversation_id);
      })
      .finally(() => setInput(""));
  };

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorderRef.current = new MediaRecorder(stream);
    audioChunksRef.current = [];
    mediaRecorderRef.current.ondataavailable = (e) => {
      if (e.data.size > 0) audioChunksRef.current.push(e.data);
    };
    mediaRecorderRef.current.onstop = handleRecordingStop;
    mediaRecorderRef.current.start();
    setRecording(true);
  };

  const handleRecordingStop = async () => {
    const blob = new Blob(audioChunksRef.current, { type: "audio/webm" });
    const reader = new FileReader();
    reader.readAsDataURL(blob);
    reader.onloadend = () => {
      const base64data = reader.result.split(",")[1];
      const recognition =
        window.SpeechRecognition || window.webkitSpeechRecognition;
      if (recognition) {
        const rec = new recognition();
        rec.lang = voiceModel;
        rec.onresult = (e) => {
          const transcript = e.results[0][0].transcript;
          sendVoice(base64data, transcript);
        };
        rec.onerror = () => sendVoice(base64data, "");
        rec.start();
      } else {
        sendVoice(base64data, "");
      }
    };
    setRecording(false);
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop();
    }
  };

  const sendVoice = (audio, transcript) => {
    fetch("/api/chat/voice", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        audio,
        transcript,
        voice_model: voiceModel,
        conversation_id: conversationId,
      }),
    })
      .then((r) => r.json())
      .then((d) => {
        if (d.conversation_id) setConversationId(d.conversation_id);
      });
    if (transcript) {
      setMessages((m) => [...m, { type: "user", text: transcript }]);
    }
  };

  return (
    <section className="card">
      <h2>Chat</h2>
      <div className="flex items-center mb-2">
        <select
          value={voiceModel}
          onChange={(e) => setVoiceModel(e.target.value)}
          className="mr-2 bg-gray-800 text-gray-100 p-1 rounded"
        >
          <option value="en-US">English US</option>
          <option value="en-GB">English UK</option>
        </select>
        {recording ? (
          <button className="button-secondary" onClick={stopRecording}>
            Stop
          </button>
        ) : (
          <button className="button-secondary" onClick={startRecording}>
            Speak
          </button>
        )}
      </div>
      <div
        ref={boxRef}
        className="chat-box overflow-y-auto p-2 bg-gray-900 rounded border border-gray-700 shadow-inner"
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
