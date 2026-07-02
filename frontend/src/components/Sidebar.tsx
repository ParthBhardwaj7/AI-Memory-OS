"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  LayoutDashboard, 
  UploadCloud, 
  MessageSquare, 
  Clock, 
  Network, 
  BrainCircuit 
} from "lucide-react";

export default function Sidebar() {
  const pathname = usePathname();

  const navItems = [
    { name: "Dashboard", href: "/", icon: LayoutDashboard },
    { name: "Upload Memories", href: "/upload", icon: UploadCloud },
    { name: "Chat Assistant", href: "/chat", icon: MessageSquare },
    { name: "Timeline", href: "/timeline", icon: Clock },
    { name: "Memory Graph", href: "/graph", icon: Network },
  ];

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 text-slate-100 flex flex-col h-screen sticky top-0">
      {/* Brand Header */}
      <div className="p-6 border-b border-slate-800 flex items-center space-x-3">
        <BrainCircuit className="h-8 w-8 text-indigo-400 animate-pulse" />
        <span className="text-xl font-bold tracking-wider bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
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
                isActive ? "text-white" : "text-slate-400 group-hover:text-indigo-400"
              }`} />
              <span className="font-medium">{item.name}</span>
            </Link>
          );
        })}
      </nav>

      {/* User Footer Stub */}
      <div className="p-4 border-t border-slate-800 flex items-center space-x-3">
        <div className="h-9 w-9 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center font-semibold text-white">
          U
        </div>
        <div>
          <p className="text-sm font-semibold">Hackathon User</p>
          <p className="text-xs text-slate-500">default-user</p>
        </div>
      </div>
    </aside>
  );
}
