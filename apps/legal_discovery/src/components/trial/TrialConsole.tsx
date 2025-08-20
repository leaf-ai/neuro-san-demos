import React, { useEffect, useRef, useState } from "react";
import { io } from "socket.io-client";
import ObjectionBar from "./ObjectionBar";

interface Segment {
  segment_id: string;
  speaker: string;
  text: string;
  t0_ms: number;
  t1_ms: number;
}

interface ObjectionEvent {
  event_id: string;
  segment_id: string;
  ground: string;
  confidence: number;
  suggested_cures: any[];
}

export default function TrialConsole({ sessionId }: { sessionId: string }) {
  const sock = useRef<any>(null);
  const [segments, setSegments] = useState<Segment[]>([]);
  const [objection, setObjection] = useState<ObjectionEvent | null>(null);
  const [highlightId, setHighlightId] = useState<string | null>(null);
  const [listening, setListening] = useState(false);

  // Voice recognition powered by the Web Speech API. Use the wake phrase
  // "assistant start listening" to begin transcription and
  // "assistant stop listening" to halt it.
  useEffect(() => {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) return;
    const rec = new SpeechRecognition();
    rec.continuous = true;
    rec.interimResults = true;
    rec.lang = "en-US";

    rec.onresult = (e: any) => {
      let final = "";
      for (let i = e.resultIndex; i < e.results.length; i++) {
        if (e.results[i].isFinal) {
          final += e.results[i][0].transcript;
        }
      }
      const norm = final.trim().toLowerCase();
      if (!norm) return;
      if (!listening) {
        if (norm.includes("assistant start listening")) {
          setListening(true);
        }
        return;
      }
      if (norm.includes("assistant stop listening")) {
        setListening(false);
        return;
      }
      if (sock.current) {
        const now = Date.now();
        sock.current.emit("segment", {
          session_id: sessionId,
          text: final.trim(),
          t0_ms: now,
          t1_ms: now,
          speaker: "local",
          confidence: 100,
        });
      }
    };

    rec.start();
    return () => rec.stop();
  }, [listening, sessionId]);

  useEffect(() => {
    const s = io("/ws/trial", { transports: ["websocket"] });
    s.emit("join", { session_id: sessionId });
    s.on("transcript_update", (msg: Segment) => {
      setSegments((prev) => [...prev, msg]);
    });
    s.on("objection_event", (evt: ObjectionEvent) => {
      setObjection(evt);
      setHighlightId(evt.segment_id);
    });
    sock.current = s;
    return () => s.disconnect();
  }, [sessionId]);

  const chooseCure = (eventId: string, cureKey: string) => {
    if (sock.current) {
      sock.current.emit("objection_cure_chosen", {
        event_id: eventId,
        cure: cureKey,
      });
    }
    setObjection(null);
    setHighlightId(null);
  };

  return (
    <div className="relative h-full w-full text-white">
      <div className="absolute top-2 left-2">
        <div
          className={`h-3 w-3 rounded-full ${listening ? "bg-red-500 animate-pulse" : "bg-gray-500"}`}
          title={listening ? "Listening" : "Idle"}
        ></div>
      </div>
      <div className="space-y-1 overflow-y-auto pr-2" style={{ maxHeight: "60vh" }}>
        {segments.map((s) => (
          <div
            key={s.segment_id}
            className={`text-sm ${
              s.segment_id === highlightId ? "bg-yellow-500/20" : ""
            }`}
          >
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
