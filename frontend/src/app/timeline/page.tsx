"use client";

import { useEffect, useState } from "react";
import { Clock, FileText, Image as ImageIcon, Headphones, Link2 } from "lucide-react";
import { memoryApi } from "@/lib/api";

interface TimelineEvent {
  title: string;
  category: string;
  time: string;
  desc: string;
}

interface TimelineData {
  [period: string]: TimelineEvent[];
}

export default function TimelinePage() {
  const [timeline, setTimeline] = useState<TimelineData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTimelineData = async () => {
      try {
        const res = await memoryApi.getTimeline("default-user");
        if (res.status === "success") {
          setTimeline(res.timeline);
        }
      } catch (err) {
        console.error("Failed to load timeline:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchTimelineData();
  }, []);

  const getCategoryIcon = (category: string) => {
    switch (category.toLowerCase()) {
      case "pdf": return FileText;
      case "image": return ImageIcon;
      case "audio": return Headphones;
      case "url": return Link2;
      default: return Clock;
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category.toLowerCase()) {
      case "pdf": return "text-teal-600 bg-teal-100 border-teal-200";
      case "image": return "text-blue-600 bg-blue-100 border-blue-200";
      case "audio": return "text-emerald-600 bg-emerald-100 border-emerald-200";
      case "url": return "text-cyan-600 bg-cyan-100 border-cyan-200";
      default: return "text-slate-500 bg-slate-100 border-slate-200";
    }
  };

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight text-slate-900 mb-2">Memory Timeline</h1>
        <p className="text-slate-600">Track and review the chronological order in which your brain ingested knowledge.</p>
      </div>

      {loading ? (
        <div className="flex items-center space-x-2 text-teal-700 text-sm font-semibold py-12 justify-center">
          <span className="h-4 w-4 border-2 border-teal-700 border-t-transparent rounded-full animate-spin"></span>
          <span>Loading timeline records...</span>
        </div>
      ) : timeline && Object.keys(timeline).length > 0 ? (
        <div className="space-y-12">
          {Object.entries(timeline).map(([period, events]) => (
            <div key={period} className="relative pl-6 border-l border-slate-200 space-y-6">
              {/* Period marker */}
              <div className="absolute -left-[9px] top-0 px-2 py-0.5 rounded-full bg-white border border-slate-200 text-[10px] uppercase font-bold tracking-wider text-slate-500">
                {period}
              </div>

              {/* Group events */}
              <div className="space-y-6 pt-4">
                {events.map((event, index) => {
                  const Icon = getCategoryIcon(event.category);
                  const colorClass = getCategoryColor(event.category);
                  return (
                    <div 
                      key={index} 
                      className="bg-white border border-slate-200 rounded-xl p-5 flex items-start space-x-4 transition-all duration-200 hover:border-slate-300 shadow-sm"
                    >
                      <div className={`p-2.5 rounded-lg border ${colorClass}`}>
                        <Icon className="h-5 w-5" />
                      </div>
                      <div className="flex-1">
                        <div className="flex justify-between items-center mb-1">
                          <h3 className="font-bold text-slate-900 text-base">{event.title}</h3>
                          <span className="text-xs text-slate-500 font-medium">{event.time}</span>
                        </div>
                        <p className="text-slate-400 text-sm">{event.desc}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 border border-dashed border-slate-200 rounded-2xl bg-slate-50">
          <Clock className="h-12 w-12 text-slate-400 mx-auto mb-4" />
          <p className="text-slate-600 font-medium">No timeline events found. Start by uploading documents!</p>
        </div>
      )}
    </div>
  );
}
