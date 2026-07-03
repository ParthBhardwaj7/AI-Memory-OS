"use client";

import { useEffect, useState } from "react";
import { 
  FileText, 
  Image as ImageIcon, 
  Headphones, 
  Link2, 
  Database,
  RefreshCw,
  Sparkles,
  BookOpen
} from "lucide-react";
import { memoryApi } from "@/lib/api";

export default function Dashboard() {
  const [stats, setStats] = useState({
    total: 0,
    pdfs: 0,
    images: 0,
    audio: 0,
    urls: 0,
  });
  const [loadingDigest, setLoadingDigest] = useState(false);
  const [digest, setDigest] = useState<string | null>(null);
  const [summary, setSummary] = useState<string | null>(null);

  useEffect(() => {
    // Load overall summary on mount
    const loadSummary = async () => {
      try {
        const res = await memoryApi.getOverallSummary("default-user");
        if (res.status === "success") {
          setSummary(res.summary);
        }
      } catch (err) {
        console.error("Failed to load overall summary:", err);
      }
    };
    loadSummary();
  }, []);

  const handleGenerateDigest = async () => {
    setLoadingDigest(true);
    try {
      const res = await memoryApi.getDailyDigest("default-user");
      if (res.status === "success") {
        setDigest(res.digest);
      }
    } catch (err) {
      console.error("Failed to fetch digest:", err);
    } finally {
      setLoadingDigest(false);
    }
  };

  const statCards = [
    { name: "Total Memories", value: stats.total, icon: Database, color: "text-blue-400 bg-blue-500/10 border-blue-500/20" },
    { name: "PDF Documents", value: stats.pdfs, icon: FileText, color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20" },
    { name: "Images / Screenshots", value: stats.images, icon: ImageIcon, color: "text-purple-400 bg-purple-500/10 border-purple-500/20" },
    { name: "Audio Files", value: stats.audio, icon: Headphones, color: "text-amber-400 bg-amber-500/10 border-amber-500/20" },
    { name: "Websites / URLs", value: stats.urls, icon: Link2, color: "text-rose-400 bg-rose-500/10 border-rose-500/20" },
  ];

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Welcome Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-indigo-950 via-slate-900 to-indigo-900 border border-slate-800 p-8">
        <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl -mr-20 -mt-20"></div>
        <h1 className="text-3xl font-extrabold tracking-tight text-white mb-2">
          Welcome to your Cognitive Memory OS
        </h1>
        <p className="text-slate-400 max-w-2xl text-lg">
          AI Memory OS acts as a digital twin of your mind. Upload files, images, audio, or bookmarks, and ask your memory assistant questions dynamically.
        </p>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {statCards.map((card) => {
          const Icon = card.icon;
          return (
            <div 
              key={card.name} 
              className={`p-5 rounded-xl border flex flex-col justify-between transition-all duration-200 hover:scale-105 bg-slate-900/60 backdrop-blur-sm ${card.color}`}
            >
              <div className="flex justify-between items-start mb-4">
                <span className="text-sm font-medium opacity-80">{card.name}</span>
                <Icon className="h-5 w-5" />
              </div>
              <span className="text-3xl font-bold tracking-tight text-white">{card.value}</span>
            </div>
          );
        })}
      </div>

      {/* Dashboard Contents Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Knowledge Summary Card */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 flex flex-col space-y-4">
          <div className="flex items-center space-x-2 border-b border-slate-800 pb-4">
            <BookOpen className="h-5 w-5 text-indigo-400" />
            <h2 className="text-xl font-bold text-white">AI Overall Memory Summary</h2>
          </div>
          
          <div className="flex-1 text-slate-300 text-sm overflow-y-auto max-h-[300px] leading-relaxed whitespace-pre-line">
            {summary || (
              <p className="text-slate-500 italic">No memories ingested yet. Head over to the Upload page to feed files to the memory graph!</p>
            )}
          </div>
        </div>

        {/* Daily Digest Generator */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 flex flex-col space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div className="flex items-center space-x-2">
              <Sparkles className="h-5 w-5 text-purple-400" />
              <h2 className="text-xl font-bold text-white">AI Daily Digest</h2>
            </div>
            
            <button
              onClick={handleGenerateDigest}
              disabled={loadingDigest}
              className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-purple-600 hover:bg-purple-700 text-xs font-semibold text-white transition-colors duration-200 disabled:opacity-50"
            >
              <RefreshCw className={`h-3 w-3 ${loadingDigest ? 'animate-spin' : ''}`} />
              <span>{loadingDigest ? "Generating..." : "Generate Digest"}</span>
            </button>
          </div>

          <div className="flex-1 text-slate-300 text-sm overflow-y-auto max-h-[300px] leading-relaxed whitespace-pre-line">
            {digest ? (
              <div className="prose prose-invert text-slate-300 prose-sm">{digest}</div>
            ) : (
              <p className="text-slate-500 italic">Generate a recap of today's memory nodes by clicking the button above.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
