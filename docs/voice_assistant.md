# Voice Assistant

The voice assistant enables speech-driven interactions through standalone
Speech-to-Text (STT) and Text-to-Speech (TTS) components.

## Architecture

- **STT** – Incoming audio frames are decoded with an optional
  [Whisper](https://github.com/openai/whisper) model via `stream_transcribe`.
- **TTS** – Agent responses are rendered to audio with `synthesize_voice`,
  supporting engines such as gTTS, Coqui and the host system.
- **Orchestration** – `chat_routes.py` wires the STT and TTS utilities into
  Flask and Socket.IO endpoints for real-time conversations.

## Setup

1. Install dependencies with `make install`.
2. Launch the STT or TTS services:

   ```bash
   make stt-service   # start server with speech-to-text enabled
   make tts-service   # start server with text-to-speech enabled
   ```
3. Optionally set `VOICE_ENGINE` (e.g. `gtts`, `coqui`, `system`) before
   starting the TTS service.

## APIs

### Streaming STT

Connect to the `/chat` namespace and emit a `voice_query` event with
base64-encoded audio frames:

```json
{
  "frames": ["<base64>", "..."]
}
```

The server emits `voice_transcript` events with interim and final text or
`voice_error` on failure.

### Voice Query Endpoint

`POST /api/chat/voice`

Send a transcribed message to the agent network and receive identifiers for
follow up requests.

### Voice Synthesis

- `GET /api/chat/voices` returns available voice options for the active TTS
  engine.
- When TTS is enabled, responses include a `voice_output` Socket.IO event
  carrying base64 audio.
