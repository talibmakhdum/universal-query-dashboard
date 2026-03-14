import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'


interface QueryRequest {
  question: string
  tableName: string
  history: Array<{
    question: string
    insight: string
  }>
}

interface UploadResponse {
  tableName: string
  schema: Record<string, string>
}

interface QueryResponse {
  success: boolean
  data?: any[]
  chartType: 'bar' | 'line' | 'pie' | 'kpi'
  insight?: string
  sql?: string
  error?: string
}

class ApiService {
  private client = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000,
  })

  async queryData(request: QueryRequest): Promise<QueryResponse> {
    try {
      const response = await this.client.post('/api/query', request)
      return response.data
    } catch (error) {
      if (axios.isAxiosError(error)) {
        return {
          success: false,
          error: error.response?.data?.message || 'Network error occurred',
          chartType: 'bar'
        }
      }
      return {
        success: false,
        error: 'Unknown error occurred',
        chartType: 'bar'
      }
    }
  }

  async uploadFile(file: File): Promise<UploadResponse> {
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await this.client.post('/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      return response.data
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.message || 'Upload failed')
      }
      throw new Error('Upload failed')
    }
  }

  async healthCheck(): Promise<boolean> {
    try {
      await this.client.get('/health')
      return true
    } catch {
      return false
    }
  }
}

export const api = new ApiService()