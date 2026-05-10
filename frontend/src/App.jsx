import React, { useState, useEffect } from 'react'
import Upload from './components/Upload'
import ProgressBar from './components/ProgressBar'
import Results from './components/Results'
import './styles/index.css'

function App() {
  const [videoId, setVideoId] = useState(null)
  const [jobId, setJobId] = useState(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [results, setResults] = useState(null)

  const handleUploadSuccess = async (response) => {
    setVideoId(response.video_id)
    setResults(null)
    
    // Start prediction
    try {
      const { predict } = await import('./services/api')
      const predictionResponse = await predict(response.video_id)
      
      if (predictionResponse.job_id) {
        setJobId(predictionResponse.job_id)
        setIsProcessing(true)
        
        // Poll for results
        pollForResults(response.video_id)
      }
    } catch (error) {
      console.error('Prediction start error:', error)
      setIsProcessing(false)
    }
  }

  const pollForResults = async (videoId) => {
    const maxAttempts = 60 // 60 seconds with 1-second polling
    let attempts = 0

    const interval = setInterval(async () => {
      attempts++
      
      try {
        const { getResults } = await import('./services/api')
        const response = await getResults(videoId)
        
        if (response.status === 'success' && response.results) {
          setResults(response.results)
          setIsProcessing(false)
          clearInterval(interval)
        }
      } catch (error) {
        console.error('Results polling error:', error)
      }

      if (attempts >= maxAttempts) {
        clearInterval(interval)
        setIsProcessing(false)
      }
    }, 1000)
  }

  const handleNewAnalysis = () => {
    setVideoId(null)
    setJobId(null)
    setIsProcessing(false)
    setResults(null)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="container py-6">
          <h1 className="text-3xl font-bold text-gray-900">
            🤟 BISINDO CSLR Demo
          </h1>
          <p className="text-gray-600 mt-1">
            Continuous Sign Language Recognition for Indonesian Sign Language
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="container py-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Upload & Progress */}
          <div className="lg:col-span-1">
            {!videoId ? (
              <Upload onUploadSuccess={handleUploadSuccess} />
            ) : (
              <ProgressBar jobId={jobId} isActive={isProcessing} />
            )}
          </div>

          {/* Right Column - Results */}
          <div className="lg:col-span-2">
            {results ? (
              <Results results={results} onNewAnalysis={handleNewAnalysis} />
            ) : isProcessing ? (
              <div className="card text-center">
                <div className="mb-4">
                  <div className="inline-block animate-spin">
                    <div className="w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full" />
                  </div>
                </div>
                <p className="text-gray-600 font-medium">
                  Analyzing video...
                </p>
                <p className="text-sm text-gray-500 mt-2">
                  This may take a minute depending on video length
                </p>
              </div>
            ) : (
              <div className="card text-center py-12">
                <div className="mb-4 text-4xl">📹</div>
                <p className="text-gray-600 font-medium">
                  Upload a video to get started
                </p>
                <p className="text-sm text-gray-500 mt-2">
                  The system will automatically extract skeletons and predict glosses
                </p>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="container py-6 text-center text-gray-600 text-sm">
          <p>BISINDO CSLR Demo v1.0.0 | Powered by FastAPI + React</p>
        </div>
      </footer>
    </div>
  )
}

export default App
