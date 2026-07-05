"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import Sidebar from "@/components/Sidebar";
import { useAuth } from "@/components/AuthProvider";

export default function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { userId } = useAuth();
  const showSidebar = !pathname.startsWith("/login");

  useEffect(() => {
    if (!userId && !pathname.startsWith("/login")) {
      router.replace("/login");
    }
    if (userId && pathname === "/login") {
      router.replace("/");
    }
  }, [userId, pathname, router]);

  return (
    <div className="h-full min-h-screen bg-white text-slate-900">
      {showSidebar ? (
        <div className="flex h-full">
          <Sidebar />
          <main className="flex-1 overflow-y-auto bg-white">{children}</main>
        </div>
      ) : (
        <main className="min-h-screen">{children}</main>
      )}
    </div>
  );
}
