import React, { useState } from 'react'

export default function Upload({ onUploadSuccess }) {
  const [file, setFile] = useState(null)
  const [isDragging, setIsDragging] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleDragEnter = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile) {
      setFile(droppedFile)
    }
  }

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      setFile(selectedFile)
    }
  }

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a video file')
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const { uploadVideo } = await import('../services/api')
      const response = await uploadVideo(file)
      onUploadSuccess(response)
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="w-full">
      <div className="card">
        <h2 className="text-2xl font-bold mb-6">Upload Video</h2>
        
        <div
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            isDragging
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 bg-gray-50 hover:border-gray-400'
          }`}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => document.getElementById('file-input').click()}
        >
          <input
            id="file-input"
            type="file"
            accept="video/*"
            onChange={handleFileSelect}
            className="hidden"
          />
          
          <div className="text-gray-600">
            <p className="text-lg font-semibold mb-2">
              Drag and drop your video here
            </p>
            <p className="text-sm text-gray-500 mb-4">
              or click to select a file
            </p>
            <p className="text-xs text-gray-400">
              Supported formats: MP4, AVI, MOV, WebM (max 500MB)
            </p>
          </div>
        </div>

        {file && (
          <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <p className="text-sm font-semibold text-blue-900">
              Selected file: {file.name}
            </p>
            <p className="text-sm text-blue-700">
              Size: {(file.size / (1024 * 1024)).toFixed(2)} MB
            </p>
          </div>
        )}

        {error && (
          <div className="mt-6 p-4 bg-red-50 rounded-lg border border-red-200">
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        <div className="mt-6 flex gap-3">
          <button
            onClick={handleUpload}
            disabled={!file || isLoading}
            className={`btn-primary disabled:opacity-50 disabled:cursor-not-allowed ${
              isLoading ? 'opacity-75' : ''
            }`}
          >
            {isLoading ? 'Uploading...' : 'Upload & Analyze'}
          </button>
          {file && (
            <button
              onClick={() => setFile(null)}
              className="btn-secondary"
              disabled={isLoading}
            >
              Clear Selection
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
