# voice interview agent follows a microservices-style architecture with clear separation of concerns

┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND (HTML/JS)                     │
│  - Microphone capture                                       │
│  - WebSocket client                                         │
│  - Audio playback                                           │
│  - UI state management                                      │
└────────────────────┬────────────────────────────────────────┘
                     │ WebSocket Connection
                     │ (bidirectional audio + control messages)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  FASTAPI BACKEND (main.py)                  │
│  - WebSocket endpoint (/ws/voice)                           │
│  - REST endpoints (/roles, /experience-levels)              │
│  - Session management                                       │
│  - CORS middleware                                          │
└─────────┬───────────────────────────────┬───────────────────┘
          │                               │
          ▼                               ▼
┌──────────────────────┐      ┌──────────────────────┐
│   SERVICE LAYER      │      │    MODELS LAYER      │
│                      │      │                      │
│ • STT Service        │      │ • RoleType (enum)    │
│ • TTS Service        │      │ • ExperienceLevel    │
│ • LLM Service        │      │ • InterviewPhase     │
│ • Interview Service  │      │ • InterviewSession   │
│                      │      │ • InterviewConfig    │
└──────────┬───────────┘      │ • Message            │
           │                  │ • Evaluation         │
           │                  └──────────────────────┘
           ▼
┌─────────────────────────────────────────────┐
│         EXTERNAL APIs (3rd Party)           │
│                                             │
│ • Assembly AI → Speech-to-Text              │
│ • Cartesia AI → Text-to-Speech              │
│ • Groq → LLM (Llama 3.3 70B)                │
└─────────────────────────────────────────────┘

## Complete Data Flow Pipeline

Phase 1: User Speaks (Frontend → Backend)

1. User clicks "Click to Speak" button
   ↓
2. Browser captures microphone audio (MediaRecorder API)
   ↓
3. Audio chunks collected in buffer (Blob array)
   ↓
4. User clicks end button
   ↓
5. Audio chunks combined into single Blob
   ↓
6. Blob converted to base64 string
   ↓
7. Sent via WebSocket:
   {
     "type": "audio",
     "audio": "base64_encoded_audio_data"
   }

Phase 2: Speech-to-Text (Backend Processing)

1. WebSocket handler receives message
   ↓
2. Base64 decoded → raw audio bytes
   ↓
3. Audio bytes sent to Assembly AI STT service
    ↓
4. Assembly AI returns transcribed text
    {
      "text": "I am a full stack developer..."
    }
    ↓
5. Text stored in session message history:
    Message(role="user", content="I am a full stack...")

Phase 3: LLM Processing (Brain)

1. Interview Service receives user text
    ↓
2. Context built:
    - Current interview phase (intro/technical/behavioral)
    - User's selected role (Backend/Frontend/etc.)
    - Experience level (Junior/Mid/Senior)
    - Previous conversation history
    ↓
3. Prompt constructed:
    SYSTEM: "You are conducting a {role} interview..."
    HISTORY: [previous messages...]
    USER: "I am a full stack developer..."
    ↓
4. Sent to Groq LLM (via LangChain ChatGroq)
    ↓
5. LLM generates contextual response:
    "That's great! Can you tell me about a recent
     project where you integrated frontend and backend?"
    ↓
6. Response stored in session:
    Message(role="assistant", content="That's great...")

Phase 4: Text-to-Speech (Backend Processing)

1. AI response text sent to Cartesia TTS service
    ↓
2. Cartesia generates audio:
    - Model: sonic-english
    - Voice ID: a0e99841-438c-4a64-b679-ae501e7d6091
    - Encoding: PCM 32-bit float
    - Sample rate: 44100 Hz
    ↓
3. Audio returned as chunks (iterator)
    ↓
4. Chunks collected into complete audio buffer

Phase 5: Response Delivery (Backend → Frontend)

1. Audio buffer converted to base64
    ↓
2. Sent via WebSocket:
    {
      "type": "audio",
      "audio": "base64_audio_data"
    }
    ↓
3. Also send transcript for display:
    {
      "type": "transcript",
      "text": "That's great! Can you tell...",
      "phase": "technical"
    }

Phase 6: Audio Playback (Frontend)

1. Browser receives WebSocket messages
    ↓
2. Base64 decoded → Blob
    ↓
3. Blob converted to Object URL
    ↓
4. Audio element created dynamically
    ↓
5. Audio.play() → User hears AI voice
    ↓
6. Transcript displayed in chat UI

## File Structure & Responsibilities

voice-interview-agent/
│
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app, WebSocket endpoint
│   │   ├── config.py               # Environment variables, settings
│   │   │
│   │   ├── models/
│   │   │   └── interview.py        # Pydantic models (data validation)
│   │   │
│   │   ├── services/
│   │   │   ├── stt_service.py      # Assembly AI integration
│   │   │   ├── tts_service.py      # Cartesia AI integration
│   │   │   ├── llm_service.py      # Groq LLM integration
│   │   │   └── interview_service.py # Business logic coordinator
│   │   │
│   │   └── routes/
│   │       └── interview.py        # REST API endpoints
│   │
│   └── tests/
│       ├── test_stt.py             # STT testing in isolation
│       ├── test_tts.py             # TTS testing in isolation
│       └── test_voice_pipeline.py  # Full pipeline test
│
├── test_voice_client.html          # Frontend UI
├── .env                            # API keys
└── pyproject.toml                  # Dependencies (uv)
