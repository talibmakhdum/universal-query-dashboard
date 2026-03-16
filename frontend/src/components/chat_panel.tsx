import React from 'react';
import { Send, User, Bot, Terminal } from 'lucide-react';

interface Message {
  id: string;
  type: 'user' | 'bot';
  text: string;
  sql?: string;
}

interface ChatPanelProps {
  messages: Message[];
  inputValue: string;
  setInputValue: (val: string) => void;
  onSend: () => void;
  isLoading: boolean;
}

export const ChatPanel: React.FC<ChatPanelProps> = ({ messages, inputValue, setInputValue, onSend, isLoading }) => {
  return (
    <div className="flex flex-col h-full glass-card overflow-hidden">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex gap-3 ${msg.type === 'user' ? 'justify-end' : ''}`}>
            {msg.type === 'bot' && (
              <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center shrink-0">
                <Bot className="w-5 h-5 text-white" />
              </div>
            )}
            <div className={`max-w-[80%] rounded-2xl p-3 ${
              msg.type === 'user' 
                ? 'bg-indigo-600 text-white rounded-tr-none' 
                : 'bg-white/10 text-gray-100 rounded-tl-none border border-white/10'
            }`}>
              <p className="text-sm whitespace-pre-wrap">{msg.text}</p>
              {msg.sql && (
                <div className="mt-3 bg-black/40 rounded-lg p-2 border border-blue-500/30">
                  <div className="flex items-center gap-2 mb-1 opacity-60">
                    <Terminal className="w-3 h-3" />
                    <span className="text-[10px] font-mono">GENERATED SQL</span>
                  </div>
                  <code className="text-[11px] font-mono text-blue-300 block overflow-x-auto whitespace-pre">
                    {msg.sql}
                  </code>
                </div>
              )}
            </div>
            {msg.type === 'user' && (
              <div className="w-8 h-8 rounded-full bg-indigo-800 flex items-center justify-center shrink-0">
                <User className="w-5 h-5 text-white" />
              </div>
            )}
          </div>
        ))}
      </div>
      
      <div className="p-4 border-t border-white/10 bg-white/5">
        <div className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && !isLoading && onSend()}
            placeholder="Ask something about the data..."
            className="flex-1 glass-input px-4 py-2"
            disabled={isLoading}
          />
          <button
            onClick={onSend}
            disabled={isLoading || !inputValue.trim()}
            className="p-2 bg-indigo-600 rounded-lg hover:bg-indigo-500 disabled:opacity-50 transition-colors"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};
