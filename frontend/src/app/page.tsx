'use client'

import React, { useState, useEffect, useRef } from 'react'
import { FileUpload } from '@/components/FileUpload'
import { ChartDisplay } from '@/components/ChartDisplay'
import { QueryChips } from '@/components/QueryChips'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { QueryProvider, useQueryContext } from '@/lib/context'
import { QueryResponse, QueryHistoryItem } from '@/types'
import { api } from '@/lib/api'
import { MessageSquare, Download, Upload, Send } from 'lucide-react'

// Main component wrapped with context provider
function DashboardContent() {
  const { 
    queryHistory, 
    currentTable, 
    setQueryHistory, 
    setCurrentTable,
    isProcessing 
  } = useQueryContext()
  
  const [inputValue, setInputValue] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [suggestedQueries, setSuggestedQueries] = useState<string[]>([])
  const chatEndRef = useRef<HTMLDivElement>(null)

  // Scroll to bottom of chat when new messages arrive
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [queryHistory])

  // Handle file upload
  const handleFileUpload = async (file: File) => {
    try {
      const result = await api.uploadFile(file)
      setCurrentTable(result.tableName)
      setSuggestedQueries(generateSuggestions(result.schema))
      setError(null)
    } catch (err) {
      console.error('Upload error:', err)
      setError('Failed to upload file. Please try again.')
    }
  }

  // Generate suggested queries based on available columns
  const generateSuggestions = (schema: Record<string, string>): string[] => {
    const columns = Object.keys(schema)
    const suggestions: string[] = []
    
    // Find numeric and categorical columns
    const numericCols = columns.filter(col => 
      schema[col].toLowerCase().includes('int') || 
      schema[col].toLowerCase().includes('float')
    )
    const categoricalCols = columns.filter(col => 
      !numericCols.includes(col) && 
      col.toLowerCase() !== 'date' &&
      col.toLowerCase() !== 'datetime'
    )
    
    // Generate suggestions based on column types
    if (numericCols.length > 0 && categoricalCols.length > 0) {
      suggestions.push(
        `Average ${numericCols[0]} by ${categoricalCols[0]}`,
        `Total ${numericCols[0]} by ${categoricalCols[0]}`,
        `Top 5 ${categoricalCols[0]} by ${numericCols[0]}`
      )
    }
    
    return [...new Set(suggestions)].slice(0, 5)
  }

  // Handle query submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!inputValue.trim()) return
    
    if (!currentTable) {
      setError('Please upload a CSV file first')
      return
    }

    try {
      setError(null)
      
      const response: QueryResponse = await api.queryData({
        question: inputValue,
        tableName: currentTable,
        history: queryHistory
      })

      if (response.success) {
        const newItem: QueryHistoryItem = {
          id: Date.now(),
          question: inputValue,
          sql: response.sql || '',
          data: response.data,
          chartType: response.chartType,
          insight: response.insight,
          timestamp: new Date().toISOString()
        }
        
        setQueryHistory(prev => [...prev, newItem])
        setInputValue('')
      } else {
        setError(response.error || 'Failed to process query')
      }
    } catch (err) {
      console.error('Query error:', err)
      setError('An error occurred while processing your query')
    }
  }

  // Handle suggested query click
  const handleSuggestedQueryClick = (query: string) => {
    setInputValue(query)
  }

  // Export chart as PNG
  const handleExportPng = () => {
    // This would be implemented with html2canvas
    alert('PNG export functionality would go here')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-blue-900 text-white p-4 shadow-md">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-xl font-bold flex items-center gap-2">
            <MessageSquare className="w-6 h-6" />
            Universal Query Dashboard
          </h1>
          <button 
            onClick={handleExportPng}
            disabled={isProcessing}
            className="flex items-center gap-1 px-3 py-1 bg-white text-blue-900 rounded-md hover:bg-gray-100 transition-colors disabled:opacity-50"
          >
            <Download className="w-4 h-4" />
            Export PNG
          </button>
        </div>
      </header>

      <div className="container mx-auto p-4 grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar */}
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-white rounded-lg shadow-md p-4">
            <h2 className="text-lg font-semibold mb-4">Upload Data</h2>
            <FileUpload onFileUpload={handleFileUpload} />
            
            {currentTable && (
              <div className="mt-4 p-3 bg-blue-50 rounded-md">
                <p className="text-sm text-blue-800">
                  Current table: <span className="font-medium">{currentTable}</span>
                </p>
              </div>
            )}
          </div>

          {suggestedQueries.length > 0 && (
            <div className="bg-white rounded-lg shadow-md p-4">
              <h2 className="text-lg font-semibold mb-4">Try these queries:</h2>
              <QueryChips 
                queries={suggestedQueries} 
                onClick={handleSuggestedQueryClick} 
              />
            </div>
          )}

          {queryHistory.length > 0 && (
            <div className="bg-white rounded-lg shadow-md p-4 max-h-96 overflow-y-auto">
              <h2 className="text-lg font-semibold mb-4">Recent Queries</h2>
              <ul className="space-y-2">
                {queryHistory.slice(-5).map((item) => (
                  <li key={item.id} className="text-sm p-2 bg-gray-50 rounded">
                    <p className="font-medium truncate">{item.question}</p>
                    <p className="text-xs text-gray-500 mt-1">{item.timestamp}</p>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Main Content */}
        <div className="lg:col-span-3 space-y-6">
          {/* Error message */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 p-3 rounded-md">
              {error}
            </div>
          )}

          {/* Chat history */}
          <div className="bg-white rounded-lg shadow-md p-4 max-h-96 overflow-y-auto">
            {queryHistory.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <p>No queries yet. Upload a CSV file and start asking questions!</p>
              </div>
            ) : (
              <div className="space-y-6">
                {queryHistory.map((item) => (
                  <div key={item.id} className="border-b pb-6 last:border-b-0">
                    <div className="mb-3">
                      <p className="font-medium text-gray-800">{item.question}</p>
                      <p className="text-sm text-gray-500 mt-1">{item.timestamp}</p>
                    </div>
                    
                    {item.data && item.data.length > 0 && (
                      <div className="chart-container mb-4">
                        <ChartDisplay 
                          data={item.data} 
                          chartType={item.chartType} 
                          insight={item.insight}
                        />
                      </div>
                    )}
                    
                    {item.insight && (
                      <div className="bg-blue-50 p-3 rounded-md">
                        <p className="text-sm text-blue-800">{item.insight}</p>
                      </div>
                    )}
                  </div>
                ))}
                <div ref={chatEndRef} />
              </div>
            )}
          </div>

          {/* Input form */}
          <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-4">
            <div className="flex gap-2">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Ask a question about your data..."
                className="flex-1 p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={isProcessing || !currentTable}
              />
              <button
                type="submit"
                disabled={isProcessing || !currentTable || !inputValue.trim()}
                className="px-4 py-3 bg-blue-900 text-white rounded-md hover:bg-blue-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <Send className="w-4 h-4" />
                {isProcessing ? 'Processing...' : 'Send'}
              </button>
            </div>
          </form>
        </div>
      </div>

      {/* Loading overlay */}
      {isProcessing && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg flex flex-col items-center">
            <LoadingSpinner />
            <p className="mt-2 text-gray-600">Processing your query...</p>
          </div>
        </div>
      )}
    </div>
  )
}

// Root component with context provider
export default function Home() {
  return (
    <QueryProvider>
      <DashboardContent />
    </QueryProvider>
  )
}