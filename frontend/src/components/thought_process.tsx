import React from 'react';
import { Brain, Search, Code, CheckCircle, Database, AlertCircle } from 'lucide-react';

interface ThoughtProcessProps {
  steps: string[];
}

export const ThoughtProcess: React.FC<ThoughtProcessProps> = ({ steps }) => {
  const getIcon = (text: string) => {
    if (text.includes('Planner')) return <Brain className="w-4 h-4 text-purple-400" />;
    if (text.includes('Writer')) return <Code className="w-4 h-4 text-blue-400" />;
    if (text.includes('Critic')) return <AlertCircle className="w-4 h-4 text-yellow-400" />;
    if (text.includes('Executor')) return <Database className="w-4 h-4 text-green-400" />;
    return <CheckCircle className="w-4 h-4 text-gray-400" />;
  };

  return (
    <div className="glass-card p-4 h-full overflow-y-auto">
      <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Thinking Process</h3>
      <div className="space-y-4">
        {steps.map((step, idx) => (
          <div key={idx} className="flex items-start gap-3 thought-step animate-in fade-in slide-in-from-left-2 duration-300">
            <div className="mt-1">{getIcon(step)}</div>
            <p className="text-sm text-gray-200 leading-relaxed">{step}</p>
          </div>
        ))}
        {steps.length === 0 && (
          <p className="text-sm text-gray-500 italic">Waiting for query...</p>
        )}
      </div>
    </div>
  );
};
