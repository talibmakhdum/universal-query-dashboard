import React from 'react';
import { Send, User, Bot, Terminal, Database, Shield, Zap, Clock, AlertTriangle } from 'lucide-react';

interface Message {
  id: string;
  type: 'user' | 'bot';
  text: string;
  sql?: string;
  sqlType?: 'success' | 'warning' | 'error';
  metadata?: {
    agentSteps?: number;
    executionTime?: number;
    resultCount?: number;
  };
}

interface ChatPanelProps {
  messages: Message[];
  inputValue: string;
  setInputValue: (val: string) => void;
  onSend: () => void;
  isLoading: boolean;
}

export const ChatPanel: React.FC<ChatPanelProps> = ({ messages, inputValue, setInputValue, onSend, isLoading }) => {
  const getSqlIcon = (sqlType?: string) => {
    switch (sqlType) {
      case 'success': return <Database className="w-3 h-3 text-green-400" />;
      case 'warning': return <Zap className="w-3 h-3 text-yellow-400" />;
      case 'error': return <Shield className="w-3 h-3 text-red-400" />;
      default: return <Terminal className="w-3 h-3" />;
    }
  };

  const getSqlLabel = (sqlType?: string) => {
    switch (sqlType) {
      case 'success': return "OPTIMIZED SQL";
      case 'warning': return "SQL WITH WARNINGS";
      case 'error': return "INVALID SQL";
      default: return "GENERATED SQL";
    }
  };

  const getSqlBorderColor = (sqlType?: string) => {
    switch (sqlType) {
      case 'success': return "border-green-500/30";
      case 'warning': return "border-yellow-500/30";
      case 'error': return "border-red-500/30";
      default: return "border-blue-500/30";
    }
  };

  const getSqlBgColor = (sqlType?: string) => {
    switch (sqlType) {
      case 'success': return "bg-green-900/20";
      case 'warning': return "bg-yellow-900/20";
      case 'error': return "bg-red-900/20";
      default: return "bg-black/40";
    }
  };

  const formatExecutionTime = (ms?: number) => {
    if (!ms) return '';
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  };

  return (
    <div className="flex flex-col h-full glass-card overflow-hidden">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex gap-3 ${msg.type === 'user' ? 'justify-end' : ''}`}>
            {msg.type === 'bot' && (
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center shrink-0 shadow-lg">
                <Bot className="w-5 h-5 text-white" />
              </div>
            )}
            <div className={`max-w-[80%] rounded-2xl p-3 ${
              msg.type === 'user' 
                ? 'bg-gradient-to-br from-indigo-600 to-blue-600 text-white rounded-tr-none shadow-lg' 
                : 'bg-white/10 text-gray-100 rounded-tl-none border border-white/10 backdrop-blur-sm'
            }`}>
              <p className="text-sm whitespace-pre-wrap leading-relaxed">{msg.text}</p>
              
              {msg.sql && (
                <div className={`mt-3 ${getSqlBgColor(msg.sqlType)} rounded-lg p-2 border ${getSqlBorderColor(msg.sqlType)} transition-all`}>
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center gap-2 opacity-80">
                      {getSqlIcon(msg.sqlType)}
                      <span className="text-[10px] font-mono uppercase tracking-wider">{getSqlLabel(msg.sqlType)}</span>
                      {msg.sqlType === 'warning' && <AlertTriangle className="w-3 h-3 text-yellow-400" />}
                      {msg.sqlType === 'error' && <AlertTriangle className="w-3 h-3 text-red-400" />}
                    </div>
                    {msg.metadata?.executionTime && (
                      <span className="text-[9px] text-gray-400 font-mono">
                        {formatExecutionTime(msg.metadata.executionTime)}
                      </span>
                    )}
                  </div>
                  <code className="text-[11px] font-mono text-blue-300 block overflow-x-auto whitespace-pre break-words">
                    {msg.sql}
                  </code>
                  {msg.metadata?.resultCount !== undefined && (
                    <div className="flex justify-between items-center mt-2 text-[9px] text-gray-400 font-mono">
                      <span>Results: {msg.metadata.resultCount}</span>
                      <span>Steps: {msg.metadata.agentSteps || 'N/A'}</span>
                    </div>
                  )}
                </div>
              )}
              
              {msg.metadata && (msg.metadata.agentSteps || msg.metadata.executionTime) && !msg.sql && (
                <div className="mt-2 flex items-center gap-3 text-[10px] text-gray-400 font-mono">
                  {msg.metadata.agentSteps && (
                    <span className="bg-white/10 px-2 py-1 rounded">Steps: {msg.metadata.agentSteps}</span>
                  )}
                  {msg.metadata.executionTime && (
                    <span className="bg-white/10 px-2 py-1 rounded">Time: {formatExecutionTime(msg.metadata.executionTime)}</span>
                  )}
                </div>
              )}
            </div>
            {msg.type === 'user' && (
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-800 to-blue-800 flex items-center justify-center shrink-0 shadow-lg">
                <User className="w-5 h-5 text-white" />
              </div>
            )}
          </div>
        ))}
        
        {isLoading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center shrink-0 shadow-lg">
              <Bot className="w-5 h-5 text-white animate-pulse" />
            </div>
            <div className="max-w-[80%] rounded-2xl p-3 bg-white/10 text-gray-100 rounded-tl-none border border-white/10 backdrop-blur-sm">
              <div className="flex items-center gap-2 mb-2">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
                <span className="text-xs text-gray-400">Analyzing your query...</span>
              </div>
              <div className="space-y-2">
                <div className="h-2 bg-white/20 rounded w-3/4 animate-pulse"></div>
                <div className="h-2 bg-white/20 rounded w-1/2 animate-pulse"></div>
              </div>
            </div>
          </div>
        )}
      </div>
      
      <div className="p-4 border-t border-white/10 bg-white/5">
        <div className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && !isLoading && onSend()}
            placeholder={isLoading ? "Processing..." : "Ask something about the data..."}
            className="flex-1 glass-input px-4 py-2 focus:ring-2 focus:ring-blue-500/50 transition-all"
            disabled={isLoading}
          />
          <button
            onClick={onSend}
            disabled={isLoading || !inputValue.trim()}
            className={`p-2 rounded-lg transition-all duration-200 transform hover:scale-105 ${
              isLoading || !inputValue.trim() 
                ? 'bg-gray-600 cursor-not-allowed opacity-50' 
                : 'bg-gradient-to-br from-indigo-600 to-blue-600 hover:from-indigo-500 hover:to-blue-500 shadow-lg hover:shadow-xl'
            }`}
          >
            <Send className={`w-5 h-5 ${isLoading ? 'text-gray-400' : 'text-white'}`} />
          </button>
        </div>
        
        {isLoading && (
          <div className="mt-2 flex items-center justify-between text-xs text-gray-500">
            <span className="flex items-center gap-2">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              Connected to Agentic Analytics System
            </span>
            <span>Real-time processing enabled</span>
          </div>
        )}
      </div>
    </div>
  );
};
