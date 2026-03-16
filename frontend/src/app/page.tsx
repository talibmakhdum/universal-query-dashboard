'use client'

import React, { useState, useEffect } from 'react';
import { ChatPanel } from '@/components/chat_panel';
import { ThoughtProcess } from '@/components/thought_process';
import { Charts } from '@/components/charts';
import { Upload, Database, LayoutDashboard, Table as TableIcon } from 'lucide-react';
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

    const userMsg = { id: Date.now().toString(), type: 'user' as const, text: inputValue };
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
      
      if (res.data.success) {
        setMessages(prev => [...prev, {
          id: (Date.now() + 1).toString(),
          type: 'bot',
          text: res.data.insight || "I've analyzed the data for you.",
          sql: res.data.sql
        }]);
        setSteps(res.data.thought_process || []);
        setCurrentData(res.data.data || []);
        setChartType(res.data.chartType || 'bar');
      } else {
        setMessages(prev => [...prev, {
          id: (Date.now() + 1).toString(),
          type: 'bot',
          text: `Error: ${res.data.error}`
        }]);
      }
    } catch (e) {
      console.error(e);
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        text: "Sorry, I encountered an error connecting to the agent."
      }]);
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

  return (
    <div className="flex flex-col h-screen overflow-hidden p-6 gap-6">
      {/* Top Header */}
      <header className="flex justify-between items-center glass-card p-4 px-8 shrink-0">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-indigo-600 rounded-xl">
             <LayoutDashboard className="w-6 h-6" />
          </div>
          <h1 className="text-xl font-bold tracking-tight">Universal Query Dashboard <span className="text-xs font-mono text-indigo-400 ml-2">AGENTIC v2.0</span></h1>
        </div>
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 cursor-pointer bg-white/5 hover:bg-white/10 px-4 py-2 rounded-lg border border-white/10 transition-all text-sm font-medium">
            <Upload className="w-4 h-4" />
            Upload CSV
            <input type="file" className="hidden" accept=".csv" onChange={handleFileUpload} />
          </label>
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
          <div className="h-[300px] shrink-0">
            <ThoughtProcess steps={steps} />
          </div>
        </div>

        {/* Right Column: Visualization & Data */}
        <div className="col-span-12 lg:col-span-8 flex flex-col gap-6 overflow-hidden">
          {/* Chart Section */}
          <div className="flex-1 min-h-0">
            {chartType !== 'none' ? (
                <Charts data={currentData} type={chartType} />
            ) : (
              <div className="glass-card h-full flex items-center justify-center text-gray-500 italic">
                No visualization to display. Ask a query to see results.
              </div>
            )}
          </div>

          {/* Table Section */}
          <div className="h-[300px] glass-card p-4 overflow-hidden flex flex-col shrink-0">
            <div className="flex items-center gap-2 mb-4 text-gray-400">
               <TableIcon className="w-4 h-4" />
               <span className="text-xs font-bold uppercase tracking-widest">Result Dataset</span>
               {currentData.length > 0 && <span className="text-[10px] bg-white/10 px-2 py-0.5 rounded-full">{currentData.length} rows</span>}
            </div>
            <div className="flex-1 overflow-auto">
                {currentData.length > 0 ? (
                  <table className="w-full text-left text-xs border-collapse">
                    <thead className="sticky top-0 bg-[#0f172a] z-10">
                      <tr>
                        {Object.keys(currentData[0]).map(k => (
                          <th key={k} className="p-2 border-b border-white/10 font-medium text-gray-400">{k}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                      {currentData.slice(0, 50).map((row, idx) => (
                        <tr key={idx} className="hover:bg-white/5">
                          {Object.values(row).map((v: any, i) => (
                            <td key={i} className="p-2 font-mono text-gray-300">{v?.toString() || '-'}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : (
                  <div className="h-full flex items-center justify-center text-gray-600 italic">
                     Query the database to see tabular results...
                  </div>
                )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}