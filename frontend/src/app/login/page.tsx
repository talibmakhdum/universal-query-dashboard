'use client'

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { LayoutDashboard, Mail, Lock, Sparkles, ChevronRight, Globe, Shield, Github } from 'lucide-react';
import '@/styles/glass.css';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    // Mock login delay
    setTimeout(() => {
      router.push('/dashboard');
    }, 1500);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center p-6 selection:bg-purple-500/30 overflow-hidden relative">
      {/* Background Orbs */}
      <div className="absolute top-[-20%] left-[-10%] w-[60%] h-[60%] bg-purple-600/10 blur-[150px] rounded-full animate-pulse"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-blue-600/10 blur-[150px] rounded-full animate-pulse delay-700"></div>

      <div className="w-full max-w-md relative z-10 glass-card p-12 py-16 border-white/10 shadow-[0_0_50px_rgba(0,0,0,0.5)]">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex p-4 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl mb-6 shadow-xl animate-bounce-slow">
            <LayoutDashboard className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-black mb-2 tracking-tight">Welcome Back</h1>
          <p className="text-gray-500 text-sm font-medium">Access your narrative intelligence platform</p>
        </div>

        {/* Login Form */}
        <form onSubmit={handleLogin} className="space-y-6">
          <div className="space-y-2">
            <label className="text-[10px] font-black uppercase tracking-widest text-gray-400 ml-1">Email Address</label>
            <div className="relative group">
              <div className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-purple-400 transition-colors">
                <Mail className="w-4 h-4" />
              </div>
              <input 
                type="email" 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@company.com"
                className="w-full bg-white/5 border border-white/10 rounded-xl p-4 pl-12 text-sm focus:outline-none focus:border-purple-500/50 focus:bg-white/[0.08] transition-all placeholder:text-gray-600"
                required
              />
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between items-center ml-1">
              <label className="text-[10px] font-black uppercase tracking-widest text-gray-400">Password</label>
              <a href="#" className="text-[10px] font-black uppercase tracking-widest text-purple-400 hover:text-purple-300 transition-colors">Forgot Password?</a>
            </div>
            <div className="relative group">
              <div className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-purple-400 transition-colors">
                <Lock className="w-4 h-4" />
              </div>
              <input 
                type="password" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-white/5 border border-white/10 rounded-xl p-4 pl-12 text-sm focus:outline-none focus:border-purple-500/50 focus:bg-white/[0.08] transition-all placeholder:text-gray-600"
                required
              />
            </div>
          </div>

          <button 
            type="submit" 
            disabled={isLoading}
            className="w-full bg-white text-black py-4 rounded-xl font-bold text-sm tracking-tight hover:bg-gray-200 active:scale-[0.98] transition-all shadow-xl flex items-center justify-center gap-2 group overflow-hidden"
          >
            {isLoading ? (
              <div className="w-5 h-5 border-2 border-black/20 border-t-black rounded-full animate-spin"></div>
            ) : (
              <>
                Sign In to Dashboard <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </>
            )}
          </button>
        </form>

        {/* Divider */}
        <div className="my-10 flex items-center gap-4">
          <div className="h-[1px] flex-1 bg-white/5"></div>
          <span className="text-[10px] font-black uppercase tracking-widest text-gray-600">Secure Access</span>
          <div className="h-[1px] flex-1 bg-white/5"></div>
        </div>

        {/* Social Link */}
        <div className="grid grid-cols-2 gap-4">
          <button className="flex items-center justify-center gap-3 bg-white/5 border border-white/10 p-3 rounded-xl hover:bg-white/10 transition-all group">
            <Github className="w-4 h-4 text-gray-400 group-hover:text-white transition-colors" />
            <span className="text-[10px] font-black uppercase tracking-widest">Github</span>
          </button>
          <button className="flex items-center justify-center gap-3 bg-white/5 border border-white/10 p-3 rounded-xl hover:bg-white/10 transition-all group">
            <Shield className="w-4 h-4 text-gray-400 group-hover:text-white transition-colors" />
            <span className="text-[10px] font-black uppercase tracking-widest">SAML</span>
          </button>
        </div>

        <p className="mt-10 text-center text-xs text-gray-600 font-medium">
          Don't have an account? <Link href="#" className="text-purple-400 font-bold hover:underline">Request Access</Link>
        </p>

        {/* Brand Link */}
        <div className="mt-12 text-center">
          <Link href="/" className="inline-flex items-center gap-2 text-[10px] font-black uppercase tracking-[0.2em] text-gray-500 hover:text-white transition-colors">
            <ChevronRight className="w-3 h-3 rotate-180" /> Back to Home
          </Link>
        </div>
      </div>
    </div>
  );
}
