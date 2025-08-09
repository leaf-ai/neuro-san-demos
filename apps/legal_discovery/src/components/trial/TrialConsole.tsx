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
  ground: string;
  confidence: number;
  suggested_cures: any[];
}

export default function TrialConsole({ sessionId }: { sessionId: string }) {
  const sock = useRef<any>(null);
  const [segments, setSegments] = useState<Segment[]>([]);
  const [objection, setObjection] = useState<ObjectionEvent | null>(null);

  useEffect(() => {
    const s = io("/ws/trial", { transports: ["websocket"] });
    s.emit("join", { session_id: sessionId });
    s.on("transcript_update", (msg: Segment) => {
      setSegments((prev) => [...prev, msg]);
    });
    s.on("objection_event", (evt: ObjectionEvent) => setObjection(evt));
    sock.current = s;
    return () => s.disconnect();
  }, [sessionId]);

  const chooseCure = (eventId: string, cureKey: string) => {
    fetch("/api/trial/objection/action", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ event_id: eventId, action: cureKey }),
    });
    setObjection(null);
  };

  return (
    <div className="relative h-full w-full text-white">
      <div className="space-y-1 overflow-y-auto pr-2" style={{ maxHeight: "60vh" }}>
        {segments.map((s) => (
          <div key={s.segment_id} className="text-sm">
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
