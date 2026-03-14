export type ChartType = 'bar' | 'line' | 'pie' | 'kpi'

export interface QueryHistoryItem {
  id: number
  question: string
  sql: string
  data: Record<string, any>[]
  chartType: ChartType
  insight: string
  timestamp: string
}

export interface QueryResponse {
  success: boolean
  data?: any[]
  chartType: ChartType
  insight?: string
  sql?: string
  error?: string
}