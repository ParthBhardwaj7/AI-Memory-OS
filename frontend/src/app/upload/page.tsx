"use client";

import { useState } from "react";
import { useDropzone } from "react-dropzone";
import { 
  FileText, 
  Image as ImageIcon, 
  Headphones, 
  Link2, 
  UploadCloud, 
  CheckCircle, 
  AlertCircle 
} from "lucide-react";
import { memoryApi } from "@/lib/api";

type UploadType = "pdf" | "image" | "audio" | "url";

export default function UploadPage() {
  const [activeTab, setActiveTab] = useState<UploadType>("pdf");
  const [urlInput, setUrlInput] = useState("");
  const [uploading, setUploading] = useState(false);
  const [status, setStatus] = useState<{ type: "success" | "error"; message: string } | null>(null);

  // TODO IMPLEMENTATION STEPS FOR DEVELOPER 2:
  // 1. Hook up the file drop callbacks to `memoryApi.uploadPdf`, `memoryApi.uploadImage`, or `memoryApi.uploadAudio`.
  // 2. Hook up URL submission to `memoryApi.uploadUrl`.
  // 3. Render file upload progress or success indicators.

  const onDrop = async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;
    const file = acceptedFiles[0];
    setUploading(true);
    setStatus(null);

    try {
      let res;
      if (activeTab === "pdf") {
        res = await memoryApi.uploadPdf(file);
      } else if (activeTab === "image") {
        res = await memoryApi.uploadImage(file);
      } else if (activeTab === "audio") {
        res = await memoryApi.uploadAudio(file);
      }
      
      if (res && res.status === "success") {
        setStatus({ type: "success", message: res.message });
      } else {
        setStatus({ type: "error", message: "Failed to process document memory." });
      }
    } catch (err: any) {
      console.error(err);
      setStatus({ type: "error", message: err.response?.data?.detail || "Upload error occurred" });
    } finally {
      setUploading(false);
    }
  };

  const handleUrlSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!urlInput.trim()) return;
    
    setUploading(true);
    setStatus(null);

    try {
      const res = await memoryApi.uploadUrl(urlInput);
      if (res && res.status === "success") {
        setStatus({ type: "success", message: res.message });
        setUrlInput("");
      } else {
        setStatus({ type: "error", message: "Failed to scrape web page memory." });
      }
    } catch (err: any) {
      console.error(err);
      setStatus({ type: "error", message: err.response?.data?.detail || "URL scraping error occurred" });
    } finally {
      setUploading(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: false,
    accept: activeTab === "pdf" 
      ? { "application/pdf": [".pdf"] }
      : activeTab === "image"
      ? { "image/*": [".png", ".jpg", ".jpeg", ".webp"] }
      : { "audio/*": [".mp3", ".wav", ".m4a"] }
  });

  const tabs = [
    { id: "pdf", name: "PDF Document", icon: FileText },
    { id: "image", name: "Screenshot / Image", icon: ImageIcon },
    { id: "audio", name: "Meeting Audio", icon: Headphones },
    { id: "url", name: "Web Page Link", icon: Link2 },
  ];

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight text-white mb-2">Ingest Memories</h1>
        <p className="text-slate-400">Add documents, images, audio records, or website articles to build your AI memory base.</p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-800 bg-slate-900/50 p-1.5 rounded-lg">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => {
                setActiveTab(tab.id as UploadType);
                setStatus(null);
              }}
              className={`flex-1 flex items-center justify-center space-x-2 py-2 px-3 rounded-md text-sm font-semibold transition-all duration-200 ${
                isActive 
                  ? "bg-indigo-600 text-white shadow-lg" 
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <Icon className="h-4 w-4" />
              <span>{tab.name}</span>
            </button>
          );
        })}
      </div>

      {/* Status Indicators */}
      {status && (
        <div className={`p-4 rounded-xl border flex items-center space-x-3 ${
          status.type === "success" 
            ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-400" 
            : "bg-rose-500/10 border-rose-500/20 text-rose-400"
        }`}>
          {status.type === "success" ? <CheckCircle className="h-5 w-5" /> : <AlertCircle className="h-5 w-5" />}
          <span className="text-sm font-medium">{status.message}</span>
        </div>
      )}

      {/* Form / Dropzone Section */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8">
        {activeTab === "url" ? (
          <form onSubmit={handleUrlSubmit} className="space-y-4">
            <label className="block text-sm font-semibold text-slate-300">Target Web URL</label>
            <div className="flex space-x-3">
              <input
                type="url"
                required
                placeholder="https://example.com/article-name"
                value={urlInput}
                onChange={(e) => setUrlInput(e.target.value)}
                className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-600 focus:outline-none focus:border-indigo-500"
              />
              <button
                type="submit"
                disabled={uploading}
                className="px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold transition-all duration-200 disabled:opacity-50"
              >
                {uploading ? "Scraping..." : "Scrape URL"}
              </button>
            </div>
            <p className="text-xs text-slate-500">Website content will be parsed and cognified into your knowledge graph.</p>
          </form>
        ) : (
          <div 
            {...getRootProps()} 
            className={`border-2 border-dashed rounded-2xl p-12 flex flex-col items-center justify-center cursor-pointer transition-all duration-200 ${
              isDragActive 
                ? "border-indigo-500 bg-indigo-500/5" 
                : "border-slate-800 hover:border-slate-700 hover:bg-slate-950/20"
            }`}
          >
            <input {...getInputProps()} />
            <UploadCloud className="h-12 w-12 text-slate-500 mb-4 animate-bounce" />
            <p className="text-lg font-bold text-slate-300 mb-1">
              {isDragActive ? "Drop the file here..." : "Drag and drop your file here"}
            </p>
            <p className="text-sm text-slate-500 mb-4">
              or click to browse your local computer
            </p>
            <span className="text-xs px-3 py-1 bg-slate-800 text-slate-400 rounded-full font-medium">
              Supported file: {activeTab.toUpperCase()}
            </span>
          </div>
        )}

        {/* Upload Loading Overlay */}
        {uploading && activeTab !== "url" && (
          <div className="mt-4 flex items-center justify-center space-x-2 text-indigo-400 text-sm font-semibold">
            <span className="h-4 w-4 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin"></span>
            <span>Uploading & Cognifying Memory. Please wait...</span>
          </div>
        )}
      </div>
    </div>
  );
}
