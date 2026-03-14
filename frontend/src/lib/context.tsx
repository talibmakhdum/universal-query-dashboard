import React, { createContext, useContext, useState, ReactNode } from 'react'
import { QueryHistoryItem } from '@/types'

interface QueryContextType {
  queryHistory: QueryHistoryItem[]
  setQueryHistory: React.Dispatch<React.SetStateAction<QueryHistoryItem[]>>
  currentTable: string | null
  setCurrentTable: React.Dispatch<React.SetStateAction<string | null>>
  isProcessing: boolean
  setIsProcessing: React.Dispatch<React.SetStateAction<boolean>>
}

const QueryContext = createContext<QueryContextType | undefined>(undefined)

interface QueryProviderProps {
  children: ReactNode
}

export const QueryProvider: React.FC<QueryProviderProps> = ({ children }) => {
  const [queryHistory, setQueryHistory] = useState<QueryHistoryItem[]>([])
  const [currentTable, setCurrentTable] = useState<string | null>(null)
  const [isProcessing, setIsProcessing] = useState<boolean>(false)

  return (
    <QueryContext.Provider value={{
      queryHistory,
      setQueryHistory,
      currentTable,
      setCurrentTable,
      isProcessing,
      setIsProcessing
    }}>
      {children}
    </QueryContext.Provider>
  )
}

export const useQueryContext = (): QueryContextType => {
  const context = useContext(QueryContext)
  if (context === undefined) {
    throw new Error('useQueryContext must be used within a QueryProvider')
  }
  return context
}