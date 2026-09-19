# 🎙️ VoxPrep: Voice Based Interview Agent

![Version](https://img.shields.io/badge/version-1.0.0-green.svg)
![Status](https://img.shields.io/badge/status-production_ready-brightgreen.svg)

VoxPrep is a next-generation AI-powered mock interview application that conducts realistic, voice-based technical and behavioral interviews. Utilizing advanced STT (Speech-to-Text), LLM processing, and TTS (Text-to-Speech) pipelines, it provides an immersive practice environment for developers of all experience levels.

---

## ✨ Features

- **Real-Time Voice Interaction:** Experience fluid conversations with ultra-low latency WebSocket connections.
- **Role-Specific Scenarios:** Tailored interview tracks for Backend, Frontend, Full-Stack, ML, DevOps, Data Science, and Mobile roles.
- **Experience Levels:** Dynamic difficulty scaling from Intern to Senior levels.
- **Rate Limiting Built-in:** Production-ready backend with IP-based rate limiting (Max 3 interviews per 3 days per user).
- **Comprehensive Evaluation:** Post-interview scoring and detailed feedback on strengths and areas for improvement.
- **High-Fidelity Audio:** Powered by Cartesia AI for natural-sounding voice synthesis.

---

## 🏗️ Architecture overview

VoxPrep follows a microservices-style architecture with clear separation of concerns between a responsive  Next.js frontend and a highly concurrent FastAPI backend.

```text
┌─────────────────────────────────────────────────────────────┐
│                   FRONTEND (Next.js)                  │
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
```

### 🔄 Complete Data Flow Pipeline

**Phase 1: User Speaks (Frontend → Backend)**
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
   ```json
   {
     "type": "audio",
     "audio": "base64_encoded_audio_data"
   }
   ```

**Phase 2: Speech-to-Text (Backend Processing)**
1. WebSocket handler receives message
   ↓
2. Base64 decoded → raw audio bytes
   ↓
3. Audio bytes sent to Assembly AI STT service
    ↓
4. Assembly AI returns transcribed text
    ```json
    {
      "text": "I am a full stack developer..."
    }
    ```
    ↓
5. Text stored in session message history:
    `Message(role="user", content="I am a full stack...")`

**Phase 3: LLM Processing (Brain)**
1. Interview Service receives user text
    ↓
2. Context built:
    - Current interview phase (intro/technical/behavioral)
    - User's selected role (Backend/Frontend/etc.)
    - Experience level (Junior/Mid/Senior)
    - Previous conversation history
    ↓
3. Prompt constructed:
    *SYSTEM: "You are conducting a {role} interview..."*
    *HISTORY: [previous messages...]*
    *USER: "I am a full stack developer..."*
    ↓
4. Sent to Groq LLM (via LangChain ChatGroq)
    ↓
5. LLM generates contextual response:
    *"That's great! Can you tell me about a recent project where you integrated frontend and backend?"*
    ↓
6. Response stored in session:
    `Message(role="assistant", content="That's great...")`

**Phase 4: Text-to-Speech (Backend Processing)**
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

**Phase 5: Response Delivery (Backend → Frontend)**
1. Audio buffer converted to base64
    ↓
2. Sent via WebSocket:
    ```json
    {
      "type": "audio",
      "audio": "base64_audio_data"
    }
    ```
    ↓
3. Also send transcript for display:
    ```json
    {
      "type": "transcript",
      "text": "That's great! Can you tell...",
      "phase": "technical"
    }
    ```

**Phase 6: Audio Playback (Frontend)**
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

---

## 🚀 Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+
- API Keys for Assembly AI, Cartesia AI, and Groq

### 1. Clone the repository

```bash
git clone https://github.com/shivanshanand/VoxPrep.git
cd VoxPrep
```

### 2. Backend Setup

```bash
cd backend
# Create a virtual environment and install dependencies
uv venv
uv pip install -r requirements.txt # Or run your setup script
```

Create a `.env` file in the `backend` directory:

```env
ASSEMBLYAI_API_KEY=your_key
CARTESIA_API_KEY=your_key
GROQ_API_KEY=your_key
```

Run the backend server:

```bash
fastapi dev app/main.py
```
*(Runs on http://localhost:8000 by default)*

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```
*(Runs on http://localhost:3000 by default)*

---

## 🛡️ Rate Limiting & Production Settings

To prevent abuse and manage API costs, this project includes a robust rate-limiting system.
- **Mechanism:** IP-based tracking via SQLite.
- **Limit:** 3 interview sessions per 3 days.
- **User Feedback:** Limits and reset dates are prominently displayed on the frontend setup screen.

## 🤝 Contributions

Any contributions are welcomed! This project is open-source with no specific license attached. Feel free to fork, modify, and submit pull requests.

---

## 💖 Credits

Made with love by **Shivansh Anand**  
