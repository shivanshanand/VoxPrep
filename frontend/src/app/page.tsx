"use client";

import { useState } from "react";
import { AnimatePresence } from "framer-motion";
import { Scene } from "@/components/3d/Scene";
import { SetupScreen } from "@/components/interview/SetupScreen";
import { ChatWindow } from "@/components/interview/ChatWindow";
import { useVoiceInterview } from "@/hooks/useVoiceInterview";

export default function Home() {
  const [hasStarted, setHasStarted] = useState(false);
  const [role, setRole] = useState("BACKEND");
  const [experience, setExperience] = useState("MID");

  const {
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
  } = useVoiceInterview(role, experience);

  const handleStart = (selectedRole: string, selectedExperience: string) => {
    setRole(selectedRole);
    setExperience(selectedExperience);
    setHasStarted(true);
    connect();
  };

  const handleReset = () => {
    window.location.reload();
  };

  return (
    <main className="relative min-h-screen w-full bg-[#0a0e17] overflow-hidden flex flex-col items-center justify-center p-4">
      {/* 3D Background */}
      <Scene />

      {/* UI Layer */}
      <div className="w-full max-w-7xl mx-auto z-10">
        <AnimatePresence mode="wait">
          {!hasStarted ? (
            <SetupScreen key="setup" onStart={handleStart} />
          ) : (
            <ChatWindow 
              key="chat" 
              messages={messages}
              status={status}
              isRecording={isRecording}
              currentPhase={currentPhase}
              interviewEnded={interviewEnded}
              finalScore={finalScore}
              onStartRecording={startRecording}
              onStopRecording={stopRecording}
              onEndInterview={endInterview}
              onReset={handleReset}
            />
          )}
        </AnimatePresence>
      </div>
    </main>
  );
}
