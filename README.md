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

The application follows a clean microservices-style architecture, separating concerns between a responsive React frontend and a highly concurrent FastAPI backend.

### 🔄 Data Flow Pipeline

1. **Audio Capture:** Frontend records user audio via `MediaRecorder` API.
2. **WebSocket Transmission:** Audio chunks are base64 encoded and streamed to the backend in real-time.
3. **STT Processing:** Assembly AI transcribes the incoming audio into text.
4. **LLM Reasoning:** Groq (Llama 3.3) analyzes the transcript, contextualizes it against the interview phase, and formulates the next question or response.
5. **TTS Generation:** Cartesia AI synthesizes the LLM's response into lifelike audio.
6. **Playback:** The audio is streamed back to the client and played instantly.

---

## 🚀 Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+
- API Keys for Assembly AI, Cartesia AI, and Groq

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/VoxPrep.git
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
