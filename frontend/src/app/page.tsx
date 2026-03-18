'use client'

import React from 'react';
import Link from 'next/link';
import { LayoutDashboard, Zap, Shield, Sparkles, Database, BarChart3, ChevronRight, Globe, Lock, Cpu } from 'lucide-react';
import '@/styles/glass.css';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-white selection:bg-purple-500/30 overflow-x-hidden">
      {/* Dynamic Background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-purple-600/20 blur-[120px] rounded-full animate-pulse"></div>
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-600/20 blur-[120px] rounded-full animate-pulse delay-700"></div>
        <div className="absolute top-[20%] right-[10%] w-[30%] h-[30%] bg-indigo-600/10 blur-[100px] rounded-full"></div>
      </div>

      {/* Navigation */}
      <nav className="relative z-50 flex justify-between items-center p-6 px-12 glass-card m-6 border-white/10">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl shadow-[0_0_20px_rgba(99,102,241,0.3)]">
            <LayoutDashboard className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-white via-white to-gray-500 bg-clip-text text-transparent">
            Universal Query
          </span>
        </div>
        
        <div className="hidden md:flex items-center gap-8 text-sm font-medium text-gray-400">
          <a href="#features" className="hover:text-white transition-colors">Features</a>
          <a href="#technology" className="hover:text-white transition-colors">Technology</a>
          <a href="#enterprise" className="hover:text-white transition-colors">Enterprise</a>
        </div>

        <div className="flex items-center gap-4">
          <Link href="/login" className="px-5 py-2 text-sm font-semibold hover:text-purple-400 transition-all">
            Sign In
          </Link>
          <Link href="/dashboard" className="px-6 py-2.5 bg-white text-black rounded-lg text-sm font-bold hover:bg-gray-200 transition-all shadow-xl hover:scale-105 active:scale-95">
            Get Started
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-20 pb-32 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 mb-8 backdrop-blur-md animate-fade-in-up">
            <Sparkles className="w-4 h-4 text-purple-400" />
            <span className="text-xs font-semibold text-gray-300 uppercase tracking-widest">Powered by Gemini 2.0 Flash</span>
          </div>
          
          <h1 className="text-6xl md:text-8xl font-black mb-8 tracking-tighter leading-[1.1]">
            Turn Your Data Into <br/>
            <span className="bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-500 bg-clip-text text-transparent animate-gradient-x">
              Narrative Intelligence
            </span>
          </h1>
          
          <p className="max-w-2xl mx-auto text-lg md:text-xl text-gray-400 mb-12 leading-relaxed">
            The next generation of agentic analytics. Chat with your databases and CSVs using natural language, powered by a multi-agent orchestration of specialist models.
          </p>

          <div className="flex flex-col md:flex-row items-center justify-center gap-6">
            <Link href="/dashboard" className="group relative px-8 py-4 bg-gradient-to-br from-indigo-600 to-purple-700 rounded-2xl text-lg font-bold shadow-[0_0_30px_rgba(99,102,241,0.4)] hover:shadow-[0_0_50px_rgba(99,102,241,0.6)] transition-all hover:scale-105 overflow-hidden">
               <div className="absolute inset-0 bg-white/10 group-hover:bg-transparent transition-colors"></div>
               <div className="relative flex items-center gap-3">
                 Explore Dashboard <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
               </div>
            </Link>
            <button className="px-8 py-4 glass-card border-white/10 text-lg font-bold hover:bg-white/5 transition-all">
              Watch Demo
            </button>
          </div>
        </div>
      </section>

      {/* Feature Grid */}
      <section id="features" className="py-24 px-6 relative">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4 tracking-tight">Built for Data Sovereignty</h2>
            <p className="text-gray-400">Everything you need to master your data workflows.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="glass-card p-8 border-white/5 hover:border-purple-500/30 transition-all group">
              <div className="w-12 h-12 bg-purple-500/10 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Database className="w-6 h-6 text-purple-400" />
              </div>
              <h3 className="text-xl font-bold mb-3">Multi-Source Sync</h3>
              <p className="text-gray-500 leading-relaxed text-sm">
                Seamlessly toggle between live SQL databases and static CSV uploads with automated schema detection.
              </p>
            </div>

            <div className="glass-card p-8 border-white/5 hover:border-blue-500/30 transition-all group">
              <div className="w-12 h-12 bg-blue-500/10 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <BarChart3 className="w-6 h-6 text-blue-400" />
              </div>
              <h3 className="text-xl font-bold mb-3">Auto Visualization</h3>
              <p className="text-gray-500 leading-relaxed text-sm">
                Our AI critics don't just output data—they select the optimal chart mapping for maximum business impact.
              </p>
            </div>

            <div className="glass-card p-8 border-white/5 hover:border-indigo-500/30 transition-all group">
              <div className="w-12 h-12 bg-indigo-500/10 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Cpu className="w-6 h-6 text-indigo-400" />
              </div>
              <h3 className="text-xl font-bold mb-3">Agentic Loops</h3>
              <p className="text-gray-500 leading-relaxed text-sm">
                Self-correcting SQL agents that analyze errors, rewrite queries, and ensure perfect data accuracy.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-32 px-6">
        <div className="max-w-5xl mx-auto glass-card p-16 border-white/10 relative overflow-hidden text-center">
          <div className="absolute top-0 right-0 w-64 h-64 bg-purple-500/10 blur-[80px] rounded-full"></div>
          <div className="absolute bottom-0 left-0 w-64 h-64 bg-blue-500/10 blur-[80px] rounded-full"></div>
          
          <h2 className="text-4xl font-black mb-6 relative z-10">Ready to unlock your data?</h2>
          <p className="text-gray-300 text-lg mb-10 relative z-10">
            Join the elite teams using Agentic Analytics to make better decisions, faster.
          </p>
          <Link href="/dashboard" className="inline-flex items-center gap-3 px-10 py-5 bg-white text-black rounded-2xl font-bold hover:bg-gray-200 transition-all scale-100 hover:scale-105 relative z-10">
            Get Instant Access <Zap className="w-5 h-5 fill-current" />
          </Link>
        </div>
      </section>

      <footer className="py-12 px-6 text-center border-t border-white/5 text-gray-600 text-xs font-medium uppercase tracking-[0.2em]">
        &copy; 2026 Universal Query Dashboard. Built for the era of Narrative Intelligence.
      </footer>
    </div>
  );
}
