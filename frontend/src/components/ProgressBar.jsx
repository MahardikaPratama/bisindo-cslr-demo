import React, { useEffect, useState } from 'react'

export default function ProgressBar({ jobId, isActive }) {
  const [progress, setProgress] = useState(0)
  const [stage, setStage] = useState('Initializing')

  useEffect(() => {
    if (!isActive || !jobId) return

    const interval = setInterval(async () => {
      try {
        const { checkStatus } = await import('../services/api')
        const response = await checkStatus(jobId)
        
        if (response.progress) {
          setProgress(response.progress.percent)
          setStage(response.progress.stage)
        }
      } catch (error) {
        console.error('Progress update error:', error)
      }
    }, 1000)

    return () => clearInterval(interval)
  }, [jobId, isActive])

  if (!isActive) return null

  const stages = [
    { name: 'frame_extraction', label: 'Extracting Frames' },
    { name: 'skeleton_extraction', label: 'Extracting Skeleton' },
    { name: 'preprocessing', label: 'Preprocessing' },
    { name: 'model_inference', label: 'Running Model' },
    { name: 'decoding', label: 'Decoding Results' },
  ]

  return (
    <div className="card">
      <h3 className="text-lg font-semibold mb-6">Processing Video...</h3>
      
      <div className="space-y-4">
        {stages.map((s) => (
          <div key={s.name}>
            <div className="flex justify-between items-center mb-2">
              <label className="text-sm font-medium text-gray-700">
                {s.label}
              </label>
              <span className="text-xs text-gray-500">
                {stage === s.name ? 'In Progress' : 'Pending'}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all duration-300 ${
                  stage === s.name ? 'bg-blue-600' : 
                  stages.findIndex(st => st.name === stage) > stages.findIndex(st => st.name === s.name) ?
                  'bg-green-600' : 'bg-gray-300'
                }`}
                style={{
                  width: stage === s.name ? `${progress}%` : 
                         stages.findIndex(st => st.name === stage) > stages.findIndex(st => st.name === s.name) ?
                         '100%' : '0%'
                }}
              />
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 flex justify-between items-center">
        <p className="text-sm text-gray-600">
          Overall: <span className="font-semibold">{progress}%</span>
        </p>
        <p className="text-xs text-gray-500">Please wait...</p>
      </div>
    </div>
  )
}
