"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";
import { 
  LayoutDashboard, 
  UploadCloud, 
  MessageSquare, 
  Clock, 
  Network, 
  BrainCircuit,
  LogOut,
  User as UserIcon,
  HelpCircle
} from "lucide-react";
import { memoryApi } from "@/lib/api";

export default function Sidebar() {
  const pathname = usePathname();
  const { userId, username, logout } = useAuth();

  // Detect guest session using our localStorage key
  const isGuest = typeof window !== "undefined" && localStorage.getItem("isGuest") === "true";

  const handleLogout = async () => {
    if (isGuest && userId) {
      try {
        // Trigger background cleanup task in FastAPI to wipe guest memory
        await memoryApi.clearGuest(userId);
      } catch (err) {
        console.error("Guest cleanup failed:", err);
      }
    }

    // Clear guest flag from localStorage
    if (typeof window !== "undefined") {
      localStorage.removeItem("isGuest");
    }

    // Call AuthProvider logout (clears userId, email, localStorage token)
    logout();

    // Redirect to login portal
    window.location.href = "/login";
  };

  const navItems = [
    { name: "Dashboard", href: "/", icon: LayoutDashboard },
    { name: "Upload Memories", href: "/upload", icon: UploadCloud },
    { name: "Chat Assistant", href: "/chat", icon: MessageSquare },
    { name: "Timeline", href: "/timeline", icon: Clock },
    { name: "Memory Graph", href: "/graph", icon: Network },
  ];

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 text-slate-100 flex flex-col h-screen sticky top-0 shadow-sm">
      {/* Brand Header */}
      <div className="p-6 border-b border-slate-800 flex items-center space-x-3">
        <BrainCircuit className="h-8 w-8 text-indigo-400 animate-pulse" />
        <span className="text-xl font-bold tracking-wider text-white">
          Memory OS
        </span>
      </div>

      {/* Navigation Menu */}
      <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;

          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200 group ${
                isActive
                  ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/20"
                  : "text-slate-400 hover:bg-slate-800 hover:text-slate-100"
              }`}
            >
              <Icon className={`h-5 w-5 transition-transform duration-200 group-hover:scale-110 ${
                isActive ? "text-white" : "text-slate-500 group-hover:text-indigo-400"
              }`} />
              <span className="font-medium">{item.name}</span>
            </Link>
          );
        })}
      </nav>

      {/* User Footer with LogOut Button */}
      <div className="p-4 border-t border-slate-800 flex items-center justify-between">
        <div className="flex items-center space-x-3 overflow-hidden">
          <div className="h-9 w-9 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center font-semibold text-white shrink-0">
            {isGuest ? <HelpCircle className="w-5 h-5 text-white" /> : <UserIcon className="w-5 h-5 text-white" />}
          </div>
          <div className="overflow-hidden">
            <p className="text-sm font-semibold truncate text-white">
              {isGuest ? "Transient Guest" : (username ?? userId ?? "User")}
            </p>
            <p className="text-[10px] text-slate-500 truncate">
              {isGuest ? "Session will be cleared" : "Logged in"}
            </p>
          </div>
        </div>
        
        <button
          onClick={handleLogout}
          type="button"
          title="Sign Out & Clear Session"
          className="p-2 text-slate-500 hover:text-red-400 hover:bg-slate-800 rounded-lg transition-all duration-150"
        >
          <LogOut className="w-4 h-4" />
        </button>
      </div>
    </aside>
  );
}
