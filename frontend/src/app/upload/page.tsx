"use client";

import { useState, useEffect } from "react";
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
  const [userId, setUserId] = useState("default-user");


  useEffect(() => {
    const activeUserId = localStorage.getItem("userId");
    if (activeUserId) {
      setUserId(activeUserId);
    }
  }, []);

  const onDrop = async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;
    setUploading(true);
    setStatus(null);

    let successCount = 0;
    let failedCount = 0;

    for (const file of acceptedFiles) {
      try {
        let res;
        if (activeTab === "pdf") {
          res = await memoryApi.uploadPdf(file, userId);
        } else if (activeTab === "image") {
          res = await memoryApi.uploadImage(file, userId);
        } else if (activeTab === "audio") {
          res = await memoryApi.uploadAudio(file, userId);
        }
        
        if (res && res.status === "success") {
          successCount++;
        } else {
          failedCount++;
        }
      } catch (err) {
        console.error(`Upload failed for ${file.name}:`, err);
        failedCount++;
      }
    }

    setUploading(false);
    if (failedCount === 0) {
      setStatus({ type: "success", message: `Successfully processed all ${successCount} file(s) into memory!` });
    } else if (successCount > 0) {
      setStatus({ 
        type: "success", 
        message: `Successfully processed ${successCount} file(s). Failed for ${failedCount} file(s).` 
      });
    } else {
      setStatus({ type: "error", message: `Failed to process all ${failedCount} file(s).` });
    }
  };

  const handleUrlSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!urlInput.trim()) return;
    
    setUploading(true);
    setStatus(null);

    try {
      const res = await memoryApi.uploadUrl(urlInput, userId);
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
    multiple: true,
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
        <h1 className="text-3xl font-extrabold tracking-tight text-slate-900 mb-2">Ingest Memories</h1>
        <p className="text-slate-600">Add documents, images, audio records, or website articles to build your AI memory base.</p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-200 bg-slate-50 p-1.5 rounded-lg shadow-sm">
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
                  ? "bg-teal-600 text-white shadow-lg" 
                  : "text-slate-600 hover:text-slate-900"
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
            ? "bg-emerald-50 border-emerald-200 text-emerald-600" 
            : "bg-rose-50 border-rose-200 text-rose-600"
        }`}>
          {status.type === "success" ? <CheckCircle className="h-5 w-5" /> : <AlertCircle className="h-5 w-5" />}
          <span className="text-sm font-medium">{status.message}</span>
        </div>
      )}

      {/* Form / Dropzone Section */}
      <div className="bg-white border border-slate-200 rounded-2xl p-8 shadow-sm">
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
                className="flex-1 bg-white border border-slate-200 rounded-xl px-4 py-3 text-slate-900 placeholder-slate-500 focus:outline-none focus:border-teal-500"
              />
              <button
                type="submit"
                disabled={uploading}
                className="px-6 py-3 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-bold transition-all duration-200 disabled:opacity-50"
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
                ? "border-teal-500 bg-teal-500/10" 
                : "border-slate-200 hover:border-slate-300 hover:bg-slate-50"
            }`}
          >
            <input {...getInputProps()} />
            <UploadCloud className="h-12 w-12 text-teal-600 mb-4 animate-bounce" />
            <p className="text-lg font-bold text-slate-900 mb-1">
              {isDragActive ? "Drop the file here..." : "Drag and drop your file here"}
            </p>
            <p className="text-sm text-slate-500 mb-4">
              or click to browse your local computer
            </p>
            <span className="text-xs px-3 py-1 bg-slate-100 text-slate-600 rounded-full font-medium">
              Supported file: {activeTab.toUpperCase()}
            </span>
          </div>
        )}

        {/* Upload Loading Overlay */}
        {uploading && activeTab !== "url" && (
          <div className="mt-4 flex items-center justify-center space-x-2 text-teal-700 text-sm font-semibold">
            <span className="h-4 w-4 border-2 border-teal-700 border-t-transparent rounded-full animate-spin"></span>
            <span>Uploading & Cognifying Memory. Please wait...</span>
          </div>
        )}
      </div>
    </div>
  );
}
