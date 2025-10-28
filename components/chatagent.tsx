"use client";

declare global {
  interface Window {
    webkitSpeechRecognition: any;
    SpeechRecognition: any;
  }

  interface SpeechRecognition extends EventTarget {
    continuous: boolean;
    lang: string;
    interimResults: boolean;
    start(): void;
    stop(): void;
    onresult: ((event: any) => void) | null;
    onerror: ((event: any) => void) | null;
    onend: (() => void) | null;
  }

  interface SpeechRecognitionEvent {
    results: SpeechRecognitionResultList;
  }
}

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { MessageCircle, X, Send, Mic, Volume2 } from "lucide-react";

interface ChatAgentProps {
  open: boolean;
  setOpen: React.Dispatch<React.SetStateAction<boolean>>;
}

export default function ChatAgent({ open, setOpen }: ChatAgentProps) {
  const [showPopup, setShowPopup] = useState(true);
  const [input, setInput] = useState("");
  const [chat, setChat] = useState<{ from: string; text: string }[]>([
    { from: "bot", text: "👋 Hi! I'm UniBazaar Assistant." },
  ]);
  const [loading, setLoading] = useState(false);
  const [listening, setListening] = useState(false);
  const [voiceReply, setVoiceReply] = useState(true);
  const [language, setLanguage] = useState("en-US");
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  // 🎤 Voice Input Setup
  useEffect(() => {
    if (typeof window !== "undefined") {
      const SpeechRecognition =
        window.SpeechRecognition || window.webkitSpeechRecognition;
      if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.lang = language;
        recognition.interimResults = false;

        recognition.onresult = (event: SpeechRecognitionEvent) => {
          const transcript = event.results[0][0].transcript;
          setInput(transcript);
          setListening(false);
          sendMessage(transcript, true);
        };

        recognition.onerror = () => setListening(false);
        recognition.onend = () => setListening(false);
        recognitionRef.current = recognition;
      }
    }
  }, [language]);

  const startListening = () => {
    if (recognitionRef.current) {
      setListening(true);
      recognitionRef.current.start();
    } else {
      alert("🎙️ Sorry, your browser doesn't support Speech Recognition.");
    }
  };

  // ✉️ Send message to backend
  const sendMessage = async (message?: string, isVoice = false) => {
    const text = message || input;
    if (!text.trim()) return;

    const userMsg = { from: "user", text };
    setChat((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("/api/agent", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, language: language}),
      });

      if (!res.ok) throw new Error("Backend response not OK");
      const data = await res.json();
      const replyText = data.reply || "Sorry, I couldn't understand that.";

      setChat((prev) => [...prev, { from: "bot", text: replyText }]);

      // 🔊 Play backend audio if available
      if (voiceReply && data.audio) {
        const audio = new Audio(data.audio);
        audio.play();
      }
    } catch (err) {
      console.error("Agent error:", err);
      setChat((prev) => [
        ...prev,
        { from: "bot", text: "❌ Something went wrong. Please try again." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // 🌐 Render messages with URL fix
  const renderMessage = (text: string) => {
    const parts = text.split(/(\[.*?\]\(.*?\)|https?:\/\/[^\s]+)/g);

    return parts.map((part, idx) => {
      // Already a markdown link
      const markdownMatch = part.match(/\[(.*)\]\((.*)\)/);
      if (markdownMatch) {
        const [, label, url] = markdownMatch;
        return (
          <a
            key={idx}
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="bg-indigo-100 px-2 py-1 rounded text-indigo-600 hover:bg-indigo-200 mr-1"
          >
            {label}
          </a>
        );
      }

      // Plain URL
      if (part.match(/https?:\/\/[^\s]+/)) {
        return (
          <a
            key={idx}
            href={part}
            target="_blank"
            rel="noopener noreferrer"
            className="bg-indigo-100 px-2 py-1 rounded text-indigo-600 hover:bg-indigo-200 mr-1"
          >
            Visit Website
          </a>
        );
      }

      // Normal text
      return (
        <span key={idx} className="whitespace-pre-wrap">
          {part}
        </span>
      );
    });
  };

  useEffect(() => {
    const timer = setTimeout(() => setShowPopup(false), 5000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <>
      <AnimatePresence>
        {!open && showPopup && (
          <motion.div
            initial={{ opacity: 0, x: 80 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 80 }}
            transition={{ duration: 0.9 }}
            className="!fixed bottom-20 right-24 z-40 bg-white border border-gray-200 shadow-lg rounded-2xl px-4 py-3 max-w-[220px] text-gray-800 text-sm"
          >
            👋 Hello! I'm{" "}
            <span className="font-semibold text-indigo-600">Uni Assistant</span>.
            <br />
            How may I help you today?
            <div className="absolute -bottom-2 right-10 w-4 h-4 bg-white rotate-45 border-r border-b border-gray-200"></div>
          </motion.div>
        )}
      </AnimatePresence>

      <motion.button
        onClick={() => setOpen(!open)}
        whileHover={{ scale: 1.1 }}
        className="!fixed bottom-6 right-6 z-50 bg-gradient-to-r from-indigo-600 to-purple-600 text-white p-4 rounded-full shadow-lg"
      >
        {open ? <X size={22} /> : <MessageCircle size={26} className="animate-bounce" />}
        {!open && <span className="absolute inset-0 rounded-full bg-indigo-400 opacity-50 animate-ping"></span>}
      </motion.button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 50 }}
            className="!fixed bottom-20 right-6 z-50 w-80 bg-white shadow-xl rounded-xl flex flex-col"
          >
            <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-4 py-2 font-semibold flex justify-between items-center">
              <span>UniBazaar Chat</span>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="text-white text-sm rounded px-2 py-1"
              >
                <option value="en-US" className="text-black">English</option>
                <option value="ur-PK" className="text-black">Urdu</option>
                <option value="en-IN" className="text-black">Roman Urdu</option>
              </select>
              <button
                onClick={() => setVoiceReply((v) => !v)}
                className={`p-2 rounded-full transition ${voiceReply ? "bg-red-500 text-white" : "bg-gray-200 text-gray-700"}`}
                title="Toggle Voice Reply"
              >
                <Volume2 size={18} />
              </button>
            </div>

            <div className="p-3 space-y-2 overflow-y-auto h-64">
              {chat.map((msg, i) => (
                <div
                  key={i}
                  className={`text-gray-700 p-2 rounded-lg text-sm max-w-[90%] break-words ${
                    msg.from === "user" ? "bg-indigo-100 ml-auto text-right" : "bg-gray-100 text-left"
                  }`}
                >
                  {renderMessage(msg.text)}
                </div>
              ))}
              {loading && <p className="text-gray-700 text-sm">Typing...</p>}
            </div>

            <div className="border-t p-2 flex items-center gap-2 bg-white">
              <button
                onClick={startListening}
                className={`p-2 rounded-full transition ${listening ? "bg-red-500 text-white" : "bg-gray-200 text-gray-700"}`}
                title="Voice Input"
              >
                <Mic size={18} />
              </button>

              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask something..."
                className="flex-1 p-2 border rounded-md text-gray-900 focus:ring-2 focus:ring-indigo-400 focus:outline-none"
                onKeyDown={(e) => e.key === "Enter" && sendMessage()}
              />

              <button
                onClick={() => sendMessage()}
                className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-3 py-2 rounded-md hover:bg-indigo-700 transition"
                title="Send"
              >
                <Send size={16} />
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
