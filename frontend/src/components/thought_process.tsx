import React from 'react';
import { Brain, Search, Code, CheckCircle, Database, AlertCircle, RefreshCw, Shield, Zap, Clock, MessageCircle } from 'lucide-react';

interface ThoughtProcessProps {
  steps: string[];
  isLoading?: boolean;
}

export const ThoughtProcess: React.FC<ThoughtProcessProps> = ({ steps, isLoading = false }) => {
  const getIcon = (text: string) => {
    const textLower = text.toLowerCase();
    
    if (textLower.includes('planner')) return <Brain className="w-4 h-4 text-purple-400" />;
    if (textLower.includes('writer')) return <Code className="w-4 h-4 text-blue-400" />;
    if (textLower.includes('critic')) return <Shield className="w-4 h-4 text-yellow-400" />;
    if (textLower.includes('executor')) return <Database className="w-4 h-4 text-green-400" />;
    if (textLower.includes('retry')) return <RefreshCw className="w-4 h-4 text-orange-400" />;
    if (textLower.includes('security')) return <Shield className="w-4 h-4 text-red-400" />;
    if (textLower.includes('performance')) return <Zap className="w-4 h-4 text-cyan-400" />;
    if (textLower.includes('timeout')) return <Clock className="w-4 h-4 text-red-400" />;
    if (textLower.includes('history')) return <MessageCircle className="w-4 h-4 text-indigo-400" />;
    
    return <CheckCircle className="w-4 h-4 text-gray-400" />;
  };

  const getStatusColor = (text: string) => {
    const textLower = text.toLowerCase();
    
    if (textLower.includes('error') || textLower.includes('failed')) return 'text-red-400';
    if (textLower.includes('warning') || textLower.includes('performance')) return 'text-yellow-400';
    if (textLower.includes('success') || textLower.includes('completed')) return 'text-green-400';
    if (textLower.includes('retry')) return 'text-orange-400';
    
    return 'text-gray-200';
  };

  const getStepType = (text: string) => {
    const textLower = text.toLowerCase();
    
    if (textLower.includes('planner')) return 'Planning';
    if (textLower.includes('writer')) return 'Generation';
    if (textLower.includes('critic')) return 'Validation';
    if (textLower.includes('executor')) return 'Execution';
    if (textLower.includes('retry')) return 'Retry';
    if (textLower.includes('history')) return 'Context';
    
    return 'Processing';
  };

  return (
    <div className="glass-card p-4 h-full overflow-y-auto">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Agent Reasoning</h3>
        {isLoading && (
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
            <span>Thinking...</span>
          </div>
        )}
      </div>
      
      <div className="space-y-3">
        {steps.map((step, idx) => (
          <div 
            key={idx} 
            className="flex items-start gap-3 thought-step animate-in fade-in slide-in-from-left-2 duration-300 border-l-2 border-transparent hover:border-blue-500/30 pl-3 transition-all"
          >
            <div className="mt-1 flex-shrink-0">
              {getIcon(step)}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-medium text-gray-500 bg-white/5 px-2 py-0.5 rounded-full">
                  {getStepType(step)}
                </span>
                {step.toLowerCase().includes('error') && (
                  <span className="text-xs text-red-400 font-medium">CRITICAL</span>
                )}
                {step.toLowerCase().includes('warning') && (
                  <span className="text-xs text-yellow-400 font-medium">WARNING</span>
                )}
              </div>
              <p className={`text-sm leading-relaxed ${getStatusColor(step)}`}>
                {step}
              </p>
            </div>
          </div>
        ))}
        
        {steps.length === 0 && !isLoading && (
          <div className="text-center py-8">
            <div className="w-12 h-12 mx-auto mb-4 bg-white/5 rounded-full flex items-center justify-center">
              <Brain className="w-6 h-6 text-gray-500" />
            </div>
            <p className="text-sm text-gray-500 italic">No reasoning steps yet. Ask a question to see the agent's thought process.</p>
          </div>
        )}
        
        {isLoading && steps.length === 0 && (
          <div className="space-y-2">
            <div className="flex items-center gap-3 animate-pulse">
              <div className="w-4 h-4 bg-gray-600 rounded-full"></div>
              <div className="h-3 bg-gray-600 rounded w-3/4"></div>
            </div>
            <div className="flex items-center gap-3 animate-pulse">
              <div className="w-4 h-4 bg-gray-600 rounded-full"></div>
              <div className="h-3 bg-gray-600 rounded w-1/2"></div>
            </div>
            <div className="flex items-center gap-3 animate-pulse">
              <div className="w-4 h-4 bg-gray-600 rounded-full"></div>
              <div className="h-3 bg-gray-600 rounded w-5/6"></div>
            </div>
          </div>
        )}
      </div>
      
      {steps.length > 0 && (
        <div className="mt-4 pt-3 border-t border-white/10">
          <div className="flex justify-between text-xs text-gray-500">
            <span>Total steps: {steps.length}</span>
            <span>Real-time processing</span>
          </div>
        </div>
      )}
    </div>
  );
};
