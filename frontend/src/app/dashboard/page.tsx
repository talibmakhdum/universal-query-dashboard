'use client'

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { ChatPanel } from '@/components/chat_panel';
import { ThoughtProcess } from '@/components/thought_process';
import { Charts } from '@/components/charts';
import { Upload, Database, LayoutDashboard, Table as TableIcon, RefreshCw, Shield, Zap, Clock, AlertTriangle, Sparkles } from 'lucide-react';
import axios from 'axios';
import '@/styles/glass.css';

const API_BASE = 'http://localhost:8000';

export default function Dashboard() {
  const [messages, setMessages] = useState<any[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [steps, setSteps] = useState<string[]>([]);
  const [currentData, setCurrentData] = useState<any[]>([]);
  const [chartType, setChartType] = useState<any>('none');
  const [isLoading, setIsLoading] = useState(false);
  const [tableName, setTableName] = useState('vehicles');
  const [availableTables, setAvailableTables] = useState<string[]>([]);
  const [isCsvMode, setIsCsvMode] = useState(false);
  const [csvPath, setCsvPath] = useState('');
  const [sessionStats, setSessionStats] = useState({ queries: 0, avgTime: 0, successRate: 100 });

  const [activeTab, setActiveTab] = useState<'reasoning' | 'visualization' | 'dataset'>('dataset');

  // Fetch initial tables
  useEffect(() => {
    const fetchTables = async () => {
      try {
        const res = await axios.get(`${API_BASE}/tables`);
        setAvailableTables(res.data.tables);
      } catch (e) {
        console.error("Failed to fetch tables", e);
      }
    };
    fetchTables();
  }, []);

  const handleSend = async () => {
    if (!inputValue.trim()) return;

    const startTime = Date.now();
    const userMsg = { 
      id: Date.now().toString(), 
      type: 'user' as const, 
      text: inputValue 
    };
    setMessages(prev => [...prev, userMsg]);
    setInputValue('');
    setIsLoading(true);
    setSteps([]);
    setActiveTab('reasoning'); // Auto-switch to reasoning when thinking

    try {
      const payload = {
        question: inputValue,
        table_name: tableName,
        session_id: "demo-session",
        is_csv: isCsvMode,
        csv_path: csvPath
      };

      const res = await axios.post(`${API_BASE}/query`, payload);
      const executionTime = Date.now() - startTime;
      
      if (res.data.success) {
        const botMsg = {
          id: (Date.now() + 1).toString(),
          type: 'bot',
          text: res.data.insight || "I've analyzed the data for you.",
          sql: res.data.sql,
          sqlType: res.data.sql ? 'success' : undefined,
          metadata: {
            agentSteps: res.data.thought_process?.length || 0,
            executionTime,
            resultCount: res.data.data?.length || 0
          }
        };
        
        setMessages(prev => [...prev, botMsg]);
        setSteps(res.data.thought_process || []);
        setCurrentData(res.data.data || []);
        setChartType(res.data.chartType || 'bar');
        
        // Auto-switch to visualization if available, else dataset
        if (res.data.chartType && res.data.chartType !== 'none') {
          setActiveTab('visualization');
        } else {
          setActiveTab('dataset');
        }
        
        // Update session stats
        setSessionStats(prev => ({
          queries: prev.queries + 1,
          avgTime: Math.round((prev.avgTime * prev.queries + executionTime) / (prev.queries + 1)),
          successRate: 100
        }));
      } else {
        const errorMsg = {
          id: (Date.now() + 1).toString(),
          type: 'bot',
          text: `Error: ${res.data.error}`,
          sql: res.data.sql,
          sqlType: 'error',
          metadata: {
            executionTime,
            agentSteps: res.data.thought_process?.length || 0
          }
        };
        
        setMessages(prev => [...prev, errorMsg]);
        setSteps(res.data.thought_process || []);
        
        // Update session stats
        setSessionStats(prev => ({
          queries: prev.queries + 1,
          avgTime: Math.round((prev.avgTime * prev.queries + executionTime) / (prev.queries + 1)),
          successRate: Math.round((prev.successRate * prev.queries) / (prev.queries + 1))
        }));
      }
    } catch (e) {
      console.error(e);
      const errorMsg = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        text: "Sorry, I encountered an error connecting to the agent.",
        sqlType: 'error',
        metadata: { executionTime: Date.now() - startTime }
      };
      
      setMessages(prev => [...prev, errorMsg]);
      
      // Update session stats
      setSessionStats(prev => ({
        queries: prev.queries + 1,
        avgTime: Math.round((prev.avgTime * prev.queries + (Date.now() - startTime)) / (prev.queries + 1)),
        successRate: Math.round((prev.successRate * prev.queries) / (prev.queries + 1))
      }));
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await axios.post(`${API_BASE}/upload-csv`, formData);
      setCsvPath(res.data.file_path);
      setIsCsvMode(true);
      setTableName(res.data.filename);
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        type: 'bot',
        text: `Successfully uploaded ${res.data.filename}. You can now ask questions about this dataset!`
      }]);
    } catch (e) {
      alert("Upload failed.");
    }
  };

  const clearChat = async () => {
    try {
      await axios.post(`${API_BASE}/clear-session?session_id=demo-session`);
    } catch (e) {
      console.error("Failed to clear backend session", e);
    }
    setMessages([]);
    setCurrentData([]);
    setChartType('none');
    setSteps([]);
    setSessionStats({ queries: 0, avgTime: 0, successRate: 100 });
  };

  const getSystemStatus = () => {
    const hasActiveQueries = messages.some(m => m.type === 'bot');
    const lastQueryTime = messages.filter(m => m.type === 'bot').pop()?.metadata?.executionTime;
    
    if (isLoading) return { status: 'processing', color: 'text-blue-400', icon: <Clock className="w-4 h-4" /> };
    if (hasActiveQueries) return { status: 'active', color: 'text-green-400', icon: <Sparkles className="w-4 h-4" /> };
    return { status: 'ready', color: 'text-gray-400', icon: <Database className="w-4 h-4" /> };
  };

  const systemStatus = getSystemStatus();

  return (
    <div className="flex flex-col h-screen overflow-hidden p-4 gap-4 bg-slate-950 text-white selection:bg-purple-500/30 relative">
      {/* Dynamic Background Orbs (from landing page) */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-purple-600/10 blur-[120px] rounded-full animate-pulse"></div>
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-600/10 blur-[120px] rounded-full animate-pulse delay-700"></div>
      </div>

      {/* Top Header */}
      <header className="relative z-10 flex justify-between items-center glass-card p-4 px-6 shrink-0 border border-white/10 shadow-lg">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl shadow-[0_0_15px_rgba(99,102,241,0.3)]">
             <LayoutDashboard className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-3">
              <Link href="/" className="text-gray-500 hover:text-white transition-colors cursor-pointer">
                <LayoutDashboard className="w-4 h-4" />
              </Link>
              <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-white via-white to-gray-500 bg-clip-text text-transparent">
                Universal Query
              </h1>
            </div>
            <p className="text-xs text-gray-400 font-medium tracking-wide">Agentic Analytics</p>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          {/* System Status */}
          <div className="flex items-center gap-2 text-sm bg-white/5 px-3 py-1.5 rounded-lg border border-white/5">
            <div className={`w-2 h-2 rounded-full ${systemStatus.color.replace('text-', 'bg-')} animate-pulse`}></div>
            <span className={`text-xs font-semibold uppercase tracking-wider ${systemStatus.color}`}>{systemStatus.status}</span>
          </div>
          
          {/* Actions */}
          <div className="flex items-center gap-2">
            <button
              onClick={clearChat}
              className="flex items-center gap-2 hover:text-white px-3 py-2 rounded-lg text-gray-400 transition-all text-sm font-semibold"
            >
              <RefreshCw className="w-4 h-4" />
              Reset
            </button>
            <label className="flex items-center gap-2 cursor-pointer bg-gradient-to-br from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 px-4 py-2 rounded-lg transition-all text-sm font-bold shadow-[0_0_15px_rgba(99,102,241,0.3)] hover:scale-105 active:scale-95">
              <Upload className="w-4 h-4" />
              Upload CSV
              <input type="file" className="hidden" accept=".csv" onChange={handleFileUpload} />
            </label>
            <Link href="/" className="px-4 py-2 bg-white/5 hover:bg-white/10 text-gray-300 rounded-lg text-sm font-semibold border border-white/10 transition-all ml-2">
              Sign Out
            </Link>
          </div>
        </div>
      </header>

      {/* Main Grid: 2 Column Elegant Layout */}
      <div className="relative z-10 flex-1 flex gap-4 overflow-hidden">
        {/* Left Column: Primary Chat UI */}
        <div className="w-[55%] flex flex-col overflow-hidden glass-card border-white/10 shadow-2xl">
          <div className="bg-white/5 border-b border-white/10 p-4 shrink-0 flex items-center justify-between">
            <h2 className="text-sm font-bold tracking-widest uppercase text-gray-300 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-purple-400" />
              Agentic Chat
            </h2>
            <div className="text-[10px] text-gray-500 font-mono bg-black/20 px-2 py-1 rounded">
              {tableName.toUpperCase()} DATASOURCE
            </div>
          </div>
          <div className="flex-1 overflow-hidden p-2">
             <ChatPanel 
              messages={messages} 
              inputValue={inputValue} 
              setInputValue={setInputValue} 
              onSend={handleSend}
              isLoading={isLoading}
            />
          </div>
        </div>

        {/* Right Column: Tabbed Data/Reasoning Interface */}
        <div className="w-[45%] flex flex-col overflow-hidden glass-card border-white/10 shadow-2xl">
          {/* Tab Navigation */}
          <div className="flex p-2 gap-2 bg-white/5 border-b border-white/10 shrink-0">
            <button 
              onClick={() => setActiveTab('reasoning')}
              className={`flex-1 flex items-center justify-center gap-2 py-2 text-xs font-bold uppercase tracking-wider rounded-lg transition-all ${activeTab === 'reasoning' ? 'bg-purple-500/20 text-purple-300 shadow-[inset_0_0_10px_rgba(168,85,247,0.2)] border border-purple-500/30' : 'text-gray-500 hover:bg-white/5 hover:text-gray-300'}`}
            >
              <Zap className="w-4 h-4" /> Reasoning
            </button>
            <button 
              onClick={() => setActiveTab('visualization')}
              className={`flex-1 flex items-center justify-center gap-2 py-2 text-xs font-bold uppercase tracking-wider rounded-lg transition-all ${activeTab === 'visualization' ? 'bg-blue-500/20 text-blue-300 shadow-[inset_0_0_10px_rgba(59,130,246,0.2)] border border-blue-500/30' : 'text-gray-500 hover:bg-white/5 hover:text-gray-300'}`}
            >
              <AlertTriangle className="w-4 h-4" /> Chart
            </button>
             <button 
              onClick={() => setActiveTab('dataset')}
              className={`flex-1 flex items-center justify-center gap-2 py-2 text-xs font-bold uppercase tracking-wider rounded-lg transition-all ${activeTab === 'dataset' ? 'bg-indigo-500/20 text-indigo-300 shadow-[inset_0_0_10px_rgba(99,102,241,0.2)] border border-indigo-500/30' : 'text-gray-500 hover:bg-white/5 hover:text-gray-300'}`}
            >
              <TableIcon className="w-4 h-4" /> Data
            </button>
          </div>

          {/* Tab Content Area */}
          <div className="flex-1 overflow-hidden p-4 relative">
            
            {/* Reasoning Tab */}
            {activeTab === 'reasoning' && (
              <div className="h-full w-full animate-fade-in">
                {steps.length > 0 || isLoading ? (
                  <ThoughtProcess steps={steps} isLoading={isLoading} />
                ) : (
                  <div className="h-full flex flex-col items-center justify-center text-gray-500 italic space-y-4">
                    <div className="p-4 bg-white/5 rounded-full"><Zap className="w-8 h-8 text-purple-400 opacity-50" /></div>
                    <p className="text-sm">Agent reasoning will appear here securely.</p>
                  </div>
                )}
              </div>
            )}

            {/* Visualization Tab */}
            {activeTab === 'visualization' && (
              <div className="h-full w-full animate-fade-in flex flex-col">
                <div className="flex justify-between items-center mb-4 shrink-0">
                  <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider">Dynamic Visualization</h3>
                  <div className="flex gap-2">
                    <span className="text-[10px] bg-blue-500/20 text-blue-400 px-2 py-1 rounded border border-blue-500/30 uppercase font-black">{chartType}</span>
                  </div>
                </div>
                <div className="flex-1 min-h-0 bg-white/5 rounded-xl border border-white/5 p-4 relative">
                  {chartType !== 'none' ? (
                     <Charts data={currentData} type={chartType} />
                  ) : (
                    <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-500 italic space-y-4">
                      <div className="p-4 bg-white/5 rounded-full"><AlertTriangle className="w-8 h-8 opacity-50" /></div>
                      <p className="text-sm">Ask a question to generate a dynamic chart.</p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Dataset Tab */}
            {activeTab === 'dataset' && (
              <div className="h-full w-full animate-fade-in flex flex-col">
                <div className="flex items-center justify-between mb-4 shrink-0">
                  <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider">Result Memory</h3>
                   <div className="flex gap-2 text-[10px] text-gray-500 font-mono">
                    <span className="bg-black/20 px-2 py-1 rounded border border-white/5">Cols: {currentData.length > 0 ? Object.keys(currentData[0]).length : 0}</span>
                    <span className="bg-black/20 px-2 py-1 rounded border border-white/5">Rows: {currentData.length}</span>
                  </div>
                </div>
                <div className="flex-1 min-h-0 bg-black/20 rounded-xl border border-white/5 overflow-hidden">
                  {currentData.length > 0 ? (
                    <div className="h-full overflow-auto">
                      <table className="w-full text-left text-xs border-collapse">
                        <thead className="sticky top-0 bg-slate-900 z-10 border-b border-white/10 shadow-md">
                          <tr>
                            {Object.keys(currentData[0]).map(k => (
                              <th key={k} className="p-3 text-[10px] font-black text-gray-400 uppercase tracking-widest border-r border-white/5 last:border-r-0 whitespace-nowrap">
                                {k}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                          {currentData.slice(0, 100).map((row, idx) => (
                            <tr key={idx} className="hover:bg-white/5 transition-colors group">
                              {Object.values(row).map((v: any, i) => (
                                <td key={i} className="p-3 font-mono text-gray-300 border-r border-white/5 last:border-r-0 whitespace-nowrap text-[11px] group-hover:text-white transition-colors">
                                  {typeof v === 'number' ? v.toLocaleString() : v?.toString() || '-'}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <div className="h-full flex flex-col items-center justify-center text-gray-500 italic space-y-4">
                       <div className="p-4 bg-white/5 rounded-full"><TableIcon className="w-8 h-8 opacity-50" /></div>
                       <p className="text-sm">Extracted data will be structured here.</p>
                    </div>
                  )}
                </div>
              </div>
            )}

          </div>
        </div>

      </div>
    </div>
  );
}
