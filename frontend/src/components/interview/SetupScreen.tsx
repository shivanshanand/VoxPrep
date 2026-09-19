"use client";

import { motion } from "framer-motion";
import { Mic, Activity } from "lucide-react";
import { useState, useEffect } from "react";

interface SetupScreenProps {
  onStart: (role: string, experience: string) => void;
}

export function SetupScreen({ onStart }: SetupScreenProps) {
  const [rateLimit, setRateLimit] = useState<{usage_count: number, max_usage: number, reset_time: string} | null>(null);

  useEffect(() => {
    fetch("http://localhost:8000/api/interview/rate-limit")
      .then(res => res.json())
      .then(data => setRateLimit(data))
      .catch(err => console.error("Failed to fetch rate limit", err));
  }, []);

  const handleStart = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (rateLimit && rateLimit.usage_count >= rateLimit.max_usage) {
      alert(`Rate limit reached. Try again on ${new Date(rateLimit.reset_time).toLocaleDateString()}`);
      return;
    }
    const formData = new FormData(e.currentTarget);
    const role = formData.get("role") as string;
    const experience = formData.get("experience") as string;
    onStart(role, experience);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -30 }}
      transition={{ duration: 0.8, ease: "easeOut" }}
      className="relative z-10 w-full max-w-2xl mx-auto p-8 rounded-3xl bg-black/40 backdrop-blur-xl border border-white/10 shadow-2xl"
    >
      <div className="absolute inset-0 rounded-3xl bg-gradient-to-br from-cyan-500/10 to-pink-500/10 pointer-events-none" />
      
      <div className="text-center mb-10">
        <h1 className="text-4xl md:text-6xl font-extrabold tracking-tighter mb-4 bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-pink-500">
          AI INTERVIEW STUDIO
        </h1>
        <p className="text-gray-400 text-lg">Next-Generation Technical Interview Practice</p>
      </div>

      <form onSubmit={handleStart} className="space-y-6 relative z-20">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <label className="text-xs font-bold tracking-widest text-cyan-400 uppercase">
              Select Role
            </label>
            <select
              name="role"
              className="w-full bg-white/5 border border-white/10 rounded-xl p-4 text-white appearance-none focus:outline-none focus:ring-2 focus:ring-cyan-500/50 transition-all cursor-pointer hover:bg-white/10"
              defaultValue="BACKEND"
            >
              <option value="BACKEND">Backend Developer</option>
              <option value="FRONTEND">Frontend Developer</option>
              <option value="FULLSTACK">Full-Stack Developer</option>
              <option value="ML_ENGINEER">ML Engineer</option>
              <option value="DEVOPS">DevOps Engineer</option>
              <option value="DATA_SCIENTIST">Data Scientist</option>
              <option value="MOBILE">Mobile Developer</option>
            </select>
          </div>

          <div className="space-y-2">
            <label className="text-xs font-bold tracking-widest text-cyan-400 uppercase">
              Experience Level
            </label>
            <select
              name="experience"
              className="w-full bg-white/5 border border-white/10 rounded-xl p-4 text-white appearance-none focus:outline-none focus:ring-2 focus:ring-cyan-500/50 transition-all cursor-pointer hover:bg-white/10"
              defaultValue="MID"
            >
              <option value="INTERN">Intern</option>
              <option value="JUNIOR">Junior (0-2 years)</option>
              <option value="MID">Mid-level (2-5 years)</option>
              <option value="SENIOR">Senior (5+ years)</option>
            </select>
          </div>
        </div>

        <button
          type="submit"
          className="w-full mt-8 relative group overflow-hidden rounded-xl bg-gradient-to-r from-cyan-500 to-pink-500 p-[1px]"
        >
          <div className="absolute inset-0 bg-white/20 group-hover:bg-transparent transition-colors duration-300" />
          <div className="relative bg-black/50 backdrop-blur-md px-8 py-5 rounded-xl flex items-center justify-center gap-3 transition-all duration-300 group-hover:bg-transparent">
            <span className="font-bold text-white tracking-widest uppercase">Begin Interview</span>
            <Mic className="w-5 h-5 text-white" />
          </div>
        </button>

        {rateLimit && (
          <div className="mt-6 flex items-center justify-center gap-2 text-sm text-gray-400">
            <Activity className="w-4 h-4 text-cyan-400" />
            <span>
              Interviews remaining: <strong className="text-white">{Math.max(0, rateLimit.max_usage - rateLimit.usage_count)}</strong> / {rateLimit.max_usage}
            </span>
            <span className="opacity-50">
              (Resets {new Date(rateLimit.reset_time).toLocaleDateString()})
            </span>
          </div>
        )}
      </form>
    </motion.div>
  );
}
