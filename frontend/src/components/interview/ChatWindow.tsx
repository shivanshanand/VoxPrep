"use client";

import { useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Mic, Square, RefreshCcw } from "lucide-react";
import type { Message } from "@/hooks/useVoiceInterview";

interface ChatWindowProps {
  messages: Message[];
  status: string;
  isRecording: boolean;
  currentPhase: string;
  interviewEnded: boolean;
  finalScore: number | null;
  onStartRecording: () => void;
  onStopRecording: () => void;
  onEndInterview: () => void;
  onReset: () => void;
}

const PHASES = [
  { id: "introduction", label: "Introduction" },
  { id: "technical", label: "Technical" },
  { id: "behavioral", label: "Behavioral" },
  { id: "closing", label: "Closing" },
];

export function ChatWindow({
  messages,
  status,
  isRecording,
  currentPhase,
  interviewEnded,
  finalScore,
  onStartRecording,
  onStopRecording,
  onEndInterview,
  onReset
}: ChatWindowProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  if (interviewEnded && finalScore !== null) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="relative z-10 w-full max-w-2xl mx-auto p-12 rounded-3xl bg-black/40 backdrop-blur-xl border border-white/10 shadow-2xl text-center"
      >
        <div className="text-6xl mb-6">🎉</div>
        <h2 className="text-4xl font-extrabold mb-8 text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-cyan-500">
          Interview Complete
        </h2>
        <div className="text-gray-400 text-sm tracking-widest uppercase mb-4">Your Performance Score</div>
        <div className="text-7xl font-black text-cyan-400 mb-12 drop-shadow-[0_0_20px_rgba(0,240,255,0.3)]">
          {finalScore}/10
        </div>
        <button
          onClick={onReset}
          className="bg-white/10 hover:bg-white/20 transition-colors border border-white/20 rounded-xl px-8 py-4 text-white font-bold tracking-widest uppercase flex items-center gap-3 mx-auto"
        >
          <RefreshCcw className="w-5 h-5" />
          Start New Interview
        </button>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      className="relative z-10 w-full max-w-4xl mx-auto flex flex-col h-[80vh] max-h-[800px] rounded-3xl bg-black/40 backdrop-blur-xl border border-white/10 shadow-2xl overflow-hidden"
    >
      {/* Header / Phase Indicator */}
      <div className="p-6 border-b border-white/10 bg-black/20">
        <div className="flex items-center justify-between gap-2 md:gap-4 overflow-x-auto pb-2">
          {PHASES.map((phase) => (
            <div
              key={phase.id}
              className={`flex-1 text-center py-3 px-4 rounded-xl text-xs md:text-sm font-bold tracking-widest uppercase transition-all duration-300 ${
                currentPhase === phase.id
                  ? "bg-gradient-to-r from-cyan-500/20 to-pink-500/20 text-cyan-400 border border-cyan-500/50 shadow-[0_0_15px_rgba(0,240,255,0.15)]"
                  : "bg-white/5 text-gray-500 border border-transparent"
              }`}
            >
              {phase.label}
            </div>
          ))}
        </div>
      </div>

      {/* Chat Messages */}
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth custom-scrollbar"
      >
        <AnimatePresence initial={false}>
          {messages.map((msg, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: msg.isUser ? 20 : -20 }}
              animate={{ opacity: 1, x: 0 }}
              className={`flex flex-col max-w-[85%] ${
                msg.isUser ? "ml-auto" : "mr-auto"
              }`}
            >
              <span className={`text-xs font-bold tracking-widest uppercase mb-2 ${
                msg.isUser ? "text-blue-400 text-right" : "text-cyan-400"
              }`}>
                {msg.isUser ? "You" : "AI Interviewer"}
              </span>
              <div className={`p-4 rounded-2xl ${
                msg.isUser 
                  ? "bg-blue-500/10 border border-blue-500/30 text-white rounded-tr-sm" 
                  : "bg-cyan-500/10 border border-cyan-500/30 text-white rounded-tl-sm"
              }`}>
                <p className="leading-relaxed whitespace-pre-wrap">{msg.text}</p>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* Status Bar */}
      <div className="px-6 py-3 bg-black/40 border-t border-white/5">
        <p className="text-sm text-gray-400 flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
          {status}
        </p>
      </div>

      {/* Controls */}
      <div className="p-6 border-t border-white/10 bg-black/20 flex gap-4">
        <button
          onClick={isRecording ? onStopRecording : onStartRecording}
          disabled={status.includes("Connecting")}
          className={`flex-1 relative group overflow-hidden rounded-xl p-[1px] transition-all ${
            isRecording 
              ? "bg-gradient-to-r from-red-500 to-orange-500 shadow-[0_0_20px_rgba(239,68,68,0.4)]" 
              : "bg-gradient-to-r from-cyan-500 to-blue-500"
          } disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          <div className={`absolute inset-0 bg-white/20 transition-colors duration-300 ${!isRecording && 'group-hover:bg-transparent'}`} />
          <div className="relative bg-black/50 backdrop-blur-md px-8 py-4 rounded-xl flex items-center justify-center gap-3 transition-all duration-300 group-hover:bg-transparent">
            {isRecording ? (
              <>
                <Square className="w-5 h-5 text-white fill-current" />
                <span className="font-bold text-white tracking-widest uppercase">Stop Speaking</span>
              </>
            ) : (
              <>
                <Mic className="w-5 h-5 text-white" />
                <span className="font-bold text-white tracking-widest uppercase">Start Speaking</span>
              </>
            )}
          </div>
        </button>

        <button
          onClick={onEndInterview}
          className="px-8 py-4 bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 text-red-400 rounded-xl font-bold tracking-widest uppercase transition-colors"
        >
          End Interview
        </button>
      </div>
    </motion.div>
  );
}
