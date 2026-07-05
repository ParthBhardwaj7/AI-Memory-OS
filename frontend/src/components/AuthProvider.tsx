"use client";

import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

interface AuthContextValue {
  userId: string | null;
  email: string | null;
  username: string | null;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);
const STORAGE_KEY = "ai-memory-auth";

function normalizeEmail(email: string) {
  return email.trim().toLowerCase();
}

function buildUserId(email: string) {
  return normalizeEmail(email).replace(/[^a-z0-9@.]/g, "");
}

function buildUsername(email: string) {
  return normalizeEmail(email).split("@")[0] || null;
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [userId, setUserId] = useState<string | null>(null);
  const [email, setEmail] = useState<string | null>(null);
  const [username, setUsername] = useState<string | null>(null);

  useEffect(() => {
    if (typeof window === "undefined") return;
    try {
      const stored = window.localStorage.getItem(STORAGE_KEY);
      if (!stored) return;
      const parsed = JSON.parse(stored);
      if (parsed?.userId && parsed?.email) {
        setUserId(parsed.userId);
        setEmail(parsed.email);
        setUsername(buildUsername(parsed.email));
        // Also keep flat key so all pages can read it with getItem("userId")
        window.localStorage.setItem("userId", parsed.userId);
      }
    } catch (err) {
      console.error("Failed to restore auth state:", err);
    }
  }, []);

  const login = useCallback(async (emailInput: string, password: string) => {
    const trimmedEmail = normalizeEmail(emailInput);
    if (!trimmedEmail.includes("@") || password.length < 6) {
      return false;
    }

    const normalizedUserId = buildUserId(trimmedEmail);
    const profile = {
      userId: normalizedUserId,
      email: trimmedEmail,
    };

    setUserId(profile.userId);
    setEmail(profile.email);
    setUsername(buildUsername(profile.email));

    if (typeof window !== "undefined") {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(profile));
      // Also write flat key so upload/chat/dashboard can all read it simply
      window.localStorage.setItem("userId", profile.userId);
    }

    return true;
  }, []);

  const logout = useCallback(() => {
    setUserId(null);
    setEmail(null);
    setUsername(null);
    if (typeof window !== "undefined") {
      window.localStorage.removeItem(STORAGE_KEY);
      window.localStorage.removeItem("userId");
      window.localStorage.removeItem("isGuest");
    }
  }, []);

  const value = useMemo(
    () => ({ userId, email, username, login, logout }),
    [userId, email, username, login, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
