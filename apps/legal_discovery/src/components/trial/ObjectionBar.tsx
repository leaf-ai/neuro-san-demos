import React from "react";

interface Cure {
  key: string;
  label: string;
  steps?: string[];
}

export interface ObjectionEventProps {
  event_id: string;
  ground: string;
  confidence: number;
  suggested_cures: Cure[];
  onChoose: (eventId: string, cureKey: string) => void;
}

export default function ObjectionBar({ event_id, ground, confidence, suggested_cures, onChoose }: ObjectionEventProps) {
  return (
    <div className="fixed bottom-4 right-4 w-96 rounded-2xl shadow-xl p-4 backdrop-blur bg-white/10 text-white">
      <div className="flex items-center justify-between">
        <div className="text-sm uppercase tracking-wide">{ground}</div>
        <div className="text-xs opacity-70">{confidence}%</div>
      </div>
      <div className="mt-2 space-y-2">
        {suggested_cures.slice(0, 4).map((c) => (
          <button
            key={c.key}
            onClick={() => onChoose(event_id, c.key)}
            className="w-full text-left rounded-xl px-3 py-2 hover:bg-white/10"
          >
            <div className="font-medium">{c.label}</div>
            {c.steps && c.steps.length > 0 && (
              <div className="text-xs opacity-80">{c.steps.slice(0, 2).join(" · ")}</div>
            )}
          </button>
        ))}
      </div>
      <div className="mt-2 text-[11px] opacity-70">Procedural guidance. Not legal advice.</div>
    </div>
  );
}
