"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowRight, Lock, Mail, ShieldCheck } from "lucide-react";
import { useAuth } from "@/components/AuthProvider";

export default function LoginPage() {
  const { login, userId } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (userId) {
      router.replace("/");
    }
  }, [userId, router]);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setLoading(true);

    const success = await login(email, password);
    setLoading(false);

    if (success) {
      router.push("/");
      return;
    }

    setError("Please enter a valid email and a password with at least 6 characters.");
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-10 bg-slate-950">
      <div className="w-full max-w-md rounded-3xl border border-slate-800 bg-slate-900/95 p-10 shadow-2xl shadow-black/20">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 inline-flex h-16 w-16 items-center justify-center rounded-3xl bg-indigo-500/10 text-indigo-300 ring-1 ring-indigo-500/20">
            <ShieldCheck className="h-8 w-8" />
          </div>
          <h1 className="text-3xl font-semibold text-white">Sign in to Memory OS</h1>
          <p className="mt-2 text-sm text-slate-400">
            Securely access your personalized memory workspace. Use any email to demo login.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label htmlFor="email" className="text-sm font-medium text-slate-300">
              Email address
            </label>
            <div className="flex items-center gap-3 rounded-2xl border border-slate-800 bg-slate-950 px-4 py-3 focus-within:ring-2 focus-within:ring-indigo-500/40">
              <Mail className="h-5 w-5 text-slate-500" />
              <input
                id="email"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                required
                placeholder="you@example.com"
                className="w-full bg-transparent outline-none text-slate-100 placeholder:text-slate-600"
              />
            </div>
          </div>

          <div className="space-y-2">
            <label htmlFor="password" className="text-sm font-medium text-slate-300">
              Password
            </label>
            <div className="flex items-center gap-3 rounded-2xl border border-slate-800 bg-slate-950 px-4 py-3 focus-within:ring-2 focus-within:ring-indigo-500/40">
              <Lock className="h-5 w-5 text-slate-500" />
              <input
                id="password"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
                placeholder="At least 6 characters"
                className="w-full bg-transparent outline-none text-slate-100 placeholder:text-slate-600"
              />
            </div>
          </div>

          {error && <p className="rounded-2xl bg-rose-500/10 border border-rose-500/20 px-4 py-3 text-sm text-rose-300">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-indigo-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? "Signing in..." : "Sign in"}
            <ArrowRight className="h-4 w-4" />
          </button>
        </form>

        <div className="mt-8 rounded-3xl border border-slate-800 bg-slate-950/80 p-5 text-sm text-slate-400">
          <p className="font-medium text-slate-200">Demo login info</p>
          <p className="mt-2 leading-6">Use any email address and a password of at least 6 characters to simulate an authenticated session.</p>
        </div>
      </div>
    </div>
  );
}
