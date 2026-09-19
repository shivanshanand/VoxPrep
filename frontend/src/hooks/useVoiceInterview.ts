import { useState, useEffect, useRef, useCallback } from "react";

export interface Message {
  text: string;
  isUser: boolean;
  phase?: string;
}

export function useVoiceInterview(role: string, experience: string) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [status, setStatus] = useState("Connecting to interview agent...");
  const [currentPhase, setCurrentPhase] = useState("introduction");
  const [interviewEnded, setInterviewEnded] = useState(false);
  const [finalScore, setFinalScore] = useState<number | null>(null);
  
  const wsRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<BlobPart[]>([]);
  const currentAudioRef = useRef<HTMLAudioElement | null>(null);

  const stopAudio = useCallback(() => {
    if (currentAudioRef.current) {
      currentAudioRef.current.pause();
      currentAudioRef.current.currentTime = 0;
      if (currentAudioRef.current.src) {
        URL.revokeObjectURL(currentAudioRef.current.src);
      }
      currentAudioRef.current = null;
    }
  }, []);

  const initMicrophone = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      
      mediaRecorder.ondataavailable = (e) => {
        audioChunksRef.current.push(e.data);
      };
      
      mediaRecorder.onstop = () => {
        const blob = new Blob(audioChunksRef.current, { type: "audio/wav" });
        audioChunksRef.current = [];
        
        const reader = new FileReader();
        reader.onloadend = () => {
          if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN && typeof reader.result === 'string') {
            const base64data = reader.result.split(',')[1];
            wsRef.current.send(JSON.stringify({
              type: "audio",
              data: base64data
            }));
            setStatus("Processing your answer...");
          }
        };
        reader.readAsDataURL(blob);
      };
      
      mediaRecorderRef.current = mediaRecorder;
      setStatus("Connected - Waiting for first question");
    } catch (err) {
      setStatus("Microphone access denied");
    }
  }, []);

  const connect = useCallback(() => {
    if (wsRef.current) return;
    
    setStatus("Connecting to AI interviewer...");
    
    // In production, use NEXT_PUBLIC_WEBSOCKET_URL
    const wsUrl = `ws://localhost:8000/ws/voice/${role}/${experience}`;
    const ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
      setStatus("Preparing your first question...");
      setCurrentPhase("introduction");
      initMicrophone();
    };
    
    ws.onmessage = async (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === "session_start") {
        // Session started
      }
      
      if (data.type === "error") {
        setStatus(data.message || "An error occurred");
        setInterviewEnded(true);
        return;
      }
      
      if (data.type === "audio") {
        setIsRecording(false);
        setMessages(prev => [...prev, { text: data.text, isUser: false, phase: data.phase }]);
        
        if (data.phase) {
          setCurrentPhase(data.phase);
        }
        
        stopAudio();

        const audioBlob = new Blob(
          [Uint8Array.from(atob(data.data), c => c.charCodeAt(0))],
          { type: "audio/wav" }
        );
        
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        currentAudioRef.current = audio;
        
        audio.onended = () => {
          URL.revokeObjectURL(audioUrl);
          currentAudioRef.current = null;
          if (!interviewEnded) {
            setStatus("Ready - Click to speak");
          }
        };
        
        audio.play().catch(() => {
          setStatus("Audio playback error. Please try again.");
        });
      }
      
      if (data.type === "transcription") {
        setMessages(prev => [...prev, { text: data.text, isUser: true }]);
      }
      
      if (data.type === "summary") {
        stopAudio();
        setInterviewEnded(true);
        setFinalScore(data.data.overall_score || 0);
      }
    };
    
    ws.onerror = () => {
      setStatus("Connection error - please refresh");
    };
    
    ws.onclose = () => {
      if (!interviewEnded) {
        setStatus("Connection closed");
      }
    };
    
    wsRef.current = ws;
  }, [role, experience, interviewEnded, stopAudio, initMicrophone]);

  const startRecording = () => {
    if (interviewEnded || !mediaRecorderRef.current) return;
    stopAudio();
    audioChunksRef.current = [];
    mediaRecorderRef.current.start();
    setIsRecording(true);
    setStatus("Recording your answer...");
  };

  const stopRecording = () => {
    if (interviewEnded || !mediaRecorderRef.current) return;
    mediaRecorderRef.current.stop();
    setIsRecording(false);
  };

  const endInterview = () => {
    if (interviewEnded) return;
    stopAudio();
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
      mediaRecorderRef.current.stop();
    }
    setIsRecording(false);
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "end" }));
    }
  };

  // Cleanup
  useEffect(() => {
    return () => {
      stopAudio();
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
        mediaRecorderRef.current.stop();
      }
    };
  }, [stopAudio]);

  return {
    connect,
    messages,
    isRecording,
    status,
    currentPhase,
    interviewEnded,
    finalScore,
    startRecording,
    stopRecording,
    endInterview
  };
}
