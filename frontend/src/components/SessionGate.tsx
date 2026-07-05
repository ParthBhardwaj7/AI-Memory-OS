"use client";

import React, { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import Sidebar from "@/components/Sidebar";

export default function SessionGate({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [authenticated, setAuthenticated] = useState<boolean | null>(null);

  useEffect(() => {
    const userId = localStorage.getItem("userId");
    
    if (!userId) {
      if (pathname !== "/login") {
        setAuthenticated(false);
        router.push("/login");
      } else {
        setAuthenticated(true); // Render login page
      }
    } else {
      if (pathname === "/login") {
        router.push("/");
      }
      setAuthenticated(true);
    }
  }, [pathname, router]);

  // Loading state spinner
  if (authenticated === null) {
    return (
      <div className="min-h-screen w-full bg-[#0b0c10] flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-[#66fcf1]"></div>
      </div>
    );
  }

  // Hide sidebar on the login screen
  if (pathname === "/login") {
    return <div className="w-full min-h-screen bg-[#0b0c10]">{children}</div>;
  }

  return (
    <div className="h-full flex bg-[#0b0c10] text-[#c5c6c7]">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        {children}
      </main>
    </div>
  );
}
