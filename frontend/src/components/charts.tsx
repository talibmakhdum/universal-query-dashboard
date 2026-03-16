import React from 'react';
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';

interface ChartsProps {
  data: any[];
  type: 'bar' | 'line' | 'pie' | 'kpi' | 'none';
}

const COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f43f5e', '#f59e0b', '#10b981'];

export const Charts: React.FC<ChartsProps> = ({ data, type }) => {
  if (type === 'none' || !data || data.length === 0) return null;

  if (type === 'kpi') {
    const val = Object.values(data[0])[0];
    const key = Object.keys(data[0])[0];
    return (
      <div className="glass-card p-6 flex flex-col items-center justify-center h-full">
        <p className="text-gray-400 text-sm font-medium uppercase">{key.replace(/_/g, ' ')}</p>
        <p className="text-5xl font-bold mt-2 bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
            {typeof val === 'number' ? val.toLocaleString() : val}
        </p>
      </div>
    );
  }

  const keys = Object.keys(data[0]);
  const xKey = keys[0];
  const yKey = keys[1] || keys[0];

  return (
    <div className="glass-card p-4 h-[400px]">
      <ResponsiveContainer width="100%" height="100%">
        {type === 'bar' ? (
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
            <XAxis dataKey={xKey} stroke="#94a3b8" fontSize={12} />
            <YAxis stroke="#94a3b8" fontSize={12} />
            <Tooltip 
              contentStyle={{ background: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
              itemStyle={{ color: '#e2e8f0' }}
            />
            <Bar dataKey={yKey} fill="url(#colorBar)" radius={[4, 4, 0, 0]} />
            <defs>
              <linearGradient id="colorBar" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#6366f1" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#6366f1" stopOpacity={0.1}/>
              </linearGradient>
            </defs>
          </BarChart>
        ) : type === 'line' ? (
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
            <XAxis dataKey={xKey} stroke="#94a3b8" fontSize={12} />
            <YAxis stroke="#94a3b8" fontSize={12} />
            <Tooltip 
              contentStyle={{ background: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
            />
            <Line type="monotone" dataKey={yKey} stroke="#6366f1" strokeWidth={3} dot={{ fill: '#6366f1' }} />
          </LineChart>
        ) : (
          <PieChart>
            <Pie
              data={data}
              dataKey={yKey}
              nameKey={xKey}
              cx="50%"
              cy="50%"
              outerRadius={100}
              label={({ name }) => name}
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        )}
      </ResponsiveContainer>
    </div>
  );
};
