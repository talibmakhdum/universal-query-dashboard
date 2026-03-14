'use client'

import React from 'react'
import { ChartType } from '@/types'
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'

interface ChartDisplayProps {
  data: Record<string, any>[]
  chartType: ChartType
  insight?: string
}

const COLORS = ['#1e3a5f', '#3b82f6', '#60a5fa', '#93c5fd', '#bfdbfe', '#2563eb', '#1d4ed8', '#1e40af']

export const ChartDisplay: React.FC<ChartDisplayProps> = ({ data, chartType, insight }) => {
  if (!data || data.length === 0) {
    return <p className="text-gray-500 text-center py-4">No data to display</p>
  }

  const keys = Object.keys(data[0])
  const xKey = keys[0]
  const valueKeys = keys.slice(1)

  // KPI display for single-value results
  if (chartType === 'kpi' || (data.length === 1 && valueKeys.length === 1)) {
    const value = data[0][valueKeys[0]]
    return (
      <div className="text-center py-6">
        <p className="text-4xl font-bold text-blue-900">
          {typeof value === 'number' ? value.toLocaleString() : value}
        </p>
        <p className="text-sm text-gray-500 mt-2">{valueKeys[0]}</p>
      </div>
    )
  }

  const renderChart = () => {
    switch (chartType) {
      case 'line':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey={xKey} tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Legend />
              {valueKeys.map((key, i) => (
                <Line
                  key={key}
                  type="monotone"
                  dataKey={key}
                  stroke={COLORS[i % COLORS.length]}
                  strokeWidth={2}
                  dot={{ r: 4 }}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        )

      case 'pie':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={data}
                dataKey={valueKeys[0]}
                nameKey={xKey}
                cx="50%"
                cy="50%"
                outerRadius={100}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {data.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        )

      case 'bar':
      default:
        return (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey={xKey} tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Legend />
              {valueKeys.map((key, i) => (
                <Bar
                  key={key}
                  dataKey={key}
                  fill={COLORS[i % COLORS.length]}
                  radius={[4, 4, 0, 0]}
                />
              ))}
            </BarChart>
          </ResponsiveContainer>
        )
    }
  }

  return (
    <div className="w-full">
      {renderChart()}
    </div>
  )
}
