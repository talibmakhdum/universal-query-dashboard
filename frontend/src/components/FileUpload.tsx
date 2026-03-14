import React, { useState } from 'react'
import { Upload as UploadIcon } from 'lucide-react'

interface FileUploadProps {
  onFileUpload: (file: File) => void
}

export const FileUpload: React.FC<FileUploadProps> = ({ onFileUpload }) => {
  const [isDragging, setIsDragging] = useState(false)
  const [fileName, setFileName] = useState<string | null>(null)

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0]
      if (file.type === 'text/csv' || file.name.endsWith('.csv')) {
        setFileName(file.name)
        onFileUpload(file)
      }
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0]
      if (file.type === 'text/csv' || file.name.endsWith('.csv')) {
        setFileName(file.name)
        onFileUpload(file)
      }
    }
  }

  return (
    <div className="space-y-4">
      <label
        htmlFor="file-upload"
        className={`block cursor-pointer border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          isDragging 
            ? 'border-blue-500 bg-blue-50' 
            : 'border-gray-300 hover:border-blue-400'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <UploadIcon className="mx-auto w-12 h-12 text-gray-400 mb-3" />
        <p className="text-gray-600 mb-1">
          <span className="font-medium text-blue-600">Click to upload</span> or drag and drop
        </p>
        <p className="text-sm text-gray-500">CSV files only (max 10MB)</p>
      </label>
      <input
        id="file-upload"
        type="file"
        accept=".csv"
        onChange={handleChange}
        className="hidden"
      />
      
      {fileName && (
        <div className="p-3 bg-green-50 border border-green-200 rounded-md">
          <p className="text-sm text-green-800 truncate">
            ✓ Uploaded: {fileName}
          </p>
        </div>
      )}
    </div>
  )
}