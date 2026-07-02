"use client";

import { useState } from "react";
import { Send, Bot, User, Brain, AlertCircle } from "lucide-react";
import { memoryApi } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: string[];
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Hello! I am your AI Memory Assistant. Ask me anything about the files, images, recordings, or links you have uploaded, and I'll retrieve the relevant memories to answer you.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  // TODO IMPLEMENTATION STEPS FOR DEVELOPER 2:
  // 1. Capture the form submission event.
  // 2. Add the user message immediately to the message array state.
  // 3. Dispatch the API request using `memoryApi.queryMemory(input)`.
  // 4. Update the messages array state with the assistant response and source documents.
  // 5. Scroll to the bottom of the chat container automatically.

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMsg = input.trim();
    setInput("");
    setLoading(true);

    // Append user message
    setMessages((prev) => [...prev, { role: "user", content: userMsg }]);

    try {
      const res = await memoryApi.queryMemory(userMsg);
      // Append assistant message with sources
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: res.answer,
          sources: res.sources,
        },
      ]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, I had trouble retrieving from memory. Please check that the backend service is running.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-5xl mx-auto p-6">
      {/* Header */}
      <div className="flex items-center space-x-3 border-b border-slate-800 pb-4 mb-4">
        <div className="p-2 bg-indigo-600/10 border border-indigo-500/20 text-indigo-400 rounded-lg">
          <Brain className="h-6 w-6" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-white">Ask your Memories</h1>
          <p className="text-xs text-slate-500">Retrieves context from Cognee knowledge graph vector db</p>
        </div>
      </div>

      {/* Messages List Area */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-2 mb-4 scrollbar-thin scrollbar-thumb-slate-800">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`flex items-start space-x-3 p-4 rounded-2xl border ${
              msg.role === "assistant"
                ? "bg-slate-900/60 border-slate-800"
                : "bg-indigo-600/10 border-indigo-500/20 ml-12"
            }`}
          >
            <div className={`p-1.5 rounded-lg ${
              msg.role === "assistant" ? "bg-slate-800 text-indigo-400" : "bg-indigo-600 text-white"
            }`}>
              {msg.role === "assistant" ? <Bot className="h-4 w-4" /> : <User className="h-4 w-4" />}
            </div>
            
            <div className="flex-1 space-y-2">
              <p className="text-slate-200 text-sm leading-relaxed whitespace-pre-line">{msg.content}</p>
              
              {/* Show sources if assistant returned them */}
              {msg.sources && msg.sources.length > 0 && (
                <div className="flex flex-wrap gap-2 pt-2 border-t border-slate-800/40">
                  <span className="text-[10px] uppercase font-bold tracking-wider text-slate-500 mt-1">Sources:</span>
                  {msg.sources.map((src, i) => (
                    <span 
                      key={i} 
                      className="text-xs px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-400"
                    >
                      {src}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex items-center space-x-2 text-indigo-400 text-xs font-semibold p-4">
            <span className="h-3 w-3 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin"></span>
            <span>AI Assistant is recalling memories...</span>
          </div>
        )}
      </div>

      {/* Input Message Form */}
      <form onSubmit={handleSend} className="flex items-center space-x-3 bg-slate-900 border border-slate-800 rounded-2xl p-2.5">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask me something: 'When did I upload my resume?' or 'Summarize meeting notes'"
          className="flex-1 bg-transparent px-4 py-2 text-slate-100 placeholder-slate-600 text-sm focus:outline-none"
        />
        <button
          type="submit"
          disabled={!input.trim() || loading}
          className="p-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold transition-all duration-200 disabled:opacity-50"
        >
          <Send className="h-4 w-4" />
        </button>
      </form>
    </div>
  );
}
