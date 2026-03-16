'use client'

import React, { useState, useEffect } from 'react';
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

  const clearChat = () => {
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
    <div className="flex flex-col h-screen overflow-hidden p-6 gap-6 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Top Header */}
      <header className="flex justify-between items-center glass-card p-4 px-8 shrink-0 border border-white/20">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-2xl shadow-lg">
             <LayoutDashboard className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              Universal Query Dashboard
            </h1>
            <p className="text-xs text-gray-400 font-mono">Agentic Analytics System v2.0</p>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          {/* System Status */}
          <div className="flex items-center gap-2 text-sm">
            <div className={`w-2 h-2 rounded-full ${systemStatus.color.replace('text-', 'bg-')} animate-pulse`}></div>
            <span className={`text-sm font-medium ${systemStatus.color}`}>{systemStatus.status}</span>
          </div>
          
          {/* Session Stats */}
          <div className="flex items-center gap-3 text-xs text-gray-400">
            <span className="bg-white/10 px-2 py-1 rounded">Queries: {sessionStats.queries}</span>
            <span className="bg-white/10 px-2 py-1 rounded">Avg: {sessionStats.avgTime}ms</span>
            <span className="bg-white/10 px-2 py-1 rounded">Success: {sessionStats.successRate}%</span>
          </div>
          
          {/* Actions */}
          <div className="flex items-center gap-2">
            <button
              onClick={clearChat}
              className="flex items-center gap-2 bg-white/5 hover:bg-white/10 px-3 py-2 rounded-lg border border-white/10 transition-all text-sm font-medium"
            >
              <RefreshCw className="w-4 h-4" />
              Clear
            </button>
            <label className="flex items-center gap-2 cursor-pointer bg-gradient-to-br from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 px-4 py-2 rounded-lg transition-all text-sm font-medium shadow-lg">
              <Upload className="w-4 h-4" />
              Upload CSV
              <input type="file" className="hidden" accept=".csv" onChange={handleFileUpload} />
            </label>
          </div>
        </div>
      </header>

      {/* Main Grid */}
      <div className="flex-1 grid grid-cols-12 gap-6 overflow-hidden">
        {/* Left Column: Chat & Thought Process */}
        <div className="col-span-12 lg:col-span-4 flex flex-col gap-6 overflow-hidden">
          <div className="flex-1 overflow-hidden">
             <ChatPanel 
              messages={messages} 
              inputValue={inputValue} 
              setInputValue={setInputValue} 
              onSend={handleSend}
              isLoading={isLoading}
            />
          </div>
          <div className="h-[320px] shrink-0">
            <ThoughtProcess steps={steps} isLoading={isLoading} />
          </div>
        </div>

        {/* Right Column: Visualization & Data */}
        <div className="col-span-12 lg:col-span-8 flex flex-col gap-6 overflow-hidden">
          {/* Chart Section */}
          <div className="flex-1 min-h-0">
            {chartType !== 'none' ? (
              <div className="glass-card p-4 h-full">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Data Visualization</h3>
                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    <span className="bg-white/10 px-2 py-1 rounded">Chart Type: {chartType}</span>
                    {currentData.length > 0 && <span className="bg-white/10 px-2 py-1 rounded">Rows: {currentData.length}</span>}
                  </div>
                </div>
                <Charts data={currentData} type={chartType} />
              </div>
            ) : (
              <div className="glass-card h-full flex flex-col items-center justify-center text-gray-500 italic space-y-4">
                <div className="w-16 h-16 bg-white/5 rounded-full flex items-center justify-center">
                  <Database className="w-8 h-8" />
                </div>
                <div className="text-center">
                  <p className="text-lg font-medium">Ready to analyze your data</p>
                  <p className="text-sm">Upload a CSV or ask a question about your database</p>
                </div>
                <div className="flex gap-2 text-xs text-gray-400">
                  <span className="bg-white/10 px-2 py-1 rounded">Natural Language Queries</span>
                  <span className="bg-white/10 px-2 py-1 rounded">Auto Chart Generation</span>
                  <span className="bg-white/10 px-2 py-1 rounded">Agent Reasoning</span>
                </div>
              </div>
            )}
          </div>

          {/* Table Section */}
          <div className="h-[320px] glass-card p-4 overflow-hidden flex flex-col shrink-0 border border-white/20">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2 text-gray-400">
                 <TableIcon className="w-4 h-4" />
                 <span className="text-xs font-bold uppercase tracking-widest">Result Dataset</span>
                 {currentData.length > 0 && <span className="text-[10px] bg-green-500/20 text-green-400 px-2 py-0.5 rounded-full border border-green-500/30">Live Data</span>}
              </div>
              <div className="flex items-center gap-2 text-xs text-gray-500">
                <span className="bg-white/10 px-2 py-1 rounded">Columns: {currentData.length > 0 ? Object.keys(currentData[0]).length : 0}</span>
                <span className="bg-white/10 px-2 py-1 rounded">Rows: {currentData.length}</span>
              </div>
            </div>
            <div className="flex-1 overflow-auto">
                {currentData.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs border-collapse">
                      <thead className="sticky top-0 bg-gradient-to-br from-slate-800 to-slate-900 z-10 border-b border-white/20">
                        <tr>
                          {Object.keys(currentData[0]).map(k => (
                            <th key={k} className="p-3 text-xs font-semibold text-gray-300 uppercase tracking-wider border-r border-white/10 last:border-r-0">
                              {k}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-white/10">
                        {currentData.slice(0, 100).map((row, idx) => (
                          <tr key={idx} className="hover:bg-white/5 transition-colors">
                            {Object.values(row).map((v: any, i) => (
                              <td key={i} className="p-3 font-mono text-gray-300 border-r border-white/5 last:border-r-0">
                                {typeof v === 'number' ? v.toLocaleString() : v?.toString() || '-'}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="h-full flex items-center justify-center text-gray-600 italic">
                     <div className="text-center space-y-2">
                       <Database className="w-8 h-8 mx-auto text-gray-500" />
                       <p>No data to display</p>
                       <p className="text-xs text-gray-400">Execute a query to populate this table</p>
                     </div>
                  </div>
                )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
