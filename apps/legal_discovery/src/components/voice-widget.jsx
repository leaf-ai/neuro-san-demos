import React, { useEffect, useRef, useState } from "react";
import { io } from "socket.io-client";
import ObjectionBar from "./trial/ObjectionBar";

export default function VoiceWidget({ sessionId }) {
  const socketRef = useRef(null);
  const recRef = useRef(null);
  const [segments, setSegments] = useState([]);
  const [objection, setObjection] = useState(null);
  const [listening, setListening] = useState(false);

  useEffect(() => {
    const socket = io("/ws/trial", { transports: ["websocket"] });
    socket.emit("join", { session_id: sessionId });
    socket.on("transcript_update", (s) => setSegments((prev) => [...prev, s]));
    socket.on("objection_event", (evt) => setObjection(evt));
    socketRef.current = socket;
    return () => socket.disconnect();
  }, [sessionId]);

  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return;
    const rec = new SpeechRecognition();
    rec.continuous = true;
    rec.interimResults = true;
    rec.lang = "en-US";
    rec.onresult = (e) => {
      let final = "";
      for (let i = e.resultIndex; i < e.results.length; i++) {
        if (e.results[i].isFinal) final += e.results[i][0].transcript;
      }
      const text = final.trim();
      if (text && socketRef.current) {
        const now = Date.now();
        socketRef.current.emit("segment", {
          session_id: sessionId,
          text,
          t0_ms: now,
          t1_ms: now,
          speaker: "local",
          confidence: 100,
        });
      }
    };
    recRef.current = rec;
    return () => rec.stop();
  }, [sessionId]);

  const toggle = () => {
    if (!recRef.current) return;
    if (listening) {
      recRef.current.stop();
      setListening(false);
    } else {
      try {
        recRef.current.start();
        setListening(true);
      } catch (e) {
        console.error(e);
      }
    }
  };

  const chooseCure = (id, key) => {
    if (socketRef.current) {
      socketRef.current.emit("objection_cure_chosen", {
        event_id: id,
        cure: key,
      });
    }
    setObjection(null);
  };

  return (
    <div className="p-4 bg-white/5 rounded-xl text-white backdrop-blur relative">
      <button
        onClick={toggle}
        className={`mb-4 rounded-full px-4 py-2 transition-colors ${
          listening ? "bg-red-600" : "bg-white/10 hover:bg-white/20"
        }`}
      >
        {listening ? "Stop" : "Start"} Mic
      </button>
      <div className="space-y-1 max-h-48 overflow-y-auto text-sm">
        {segments.map((s) => (
          <div key={s.segment_id || Math.random()}>
            <span className="font-semibold mr-2">{s.speaker}:</span>
            <span>{s.text}</span>
          </div>
        ))}
      </div>
      {objection && (
        <ObjectionBar
          event_id={objection.event_id}
          ground={objection.ground}
          confidence={objection.confidence}
          suggested_cures={objection.suggested_cures}
          onChoose={chooseCure}
        />
      )}
    </div>
  );
}

