import React from 'react'

export default function Results({ results, onNewAnalysis }) {
  if (!results) return null

  const { glosses, full_sentence, sentence_confidence } = results

  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-6">Recognition Results</h2>
      
      {/* Predicted Sentence */}
      <div className="mb-8 p-6 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
        <p className="text-xs font-semibold text-blue-600 mb-2 uppercase">
          Predicted Sentence
        </p>
        <p className="text-2xl font-bold text-blue-900 break-words">
          {full_sentence || 'No glosses detected'}
        </p>
        <p className="text-sm text-blue-700 mt-2">
          Confidence: <span className="font-semibold">{(sentence_confidence * 100).toFixed(1)}%</span>
        </p>
      </div>

      {/* Gloss Timeline */}
      {glosses && glosses.length > 0 && (
        <div className="mb-8">
          <h3 className="text-lg font-semibold mb-4">Gloss Timeline</h3>
          <div className="space-y-2">
            {glosses.map((gloss, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div className="flex-1">
                  <p className="font-medium text-gray-900">{gloss.word}</p>
                  <p className="text-xs text-gray-500">
                    {gloss.start_time} – {gloss.end_time}
                  </p>
                </div>
                <div
                  className={`px-3 py-1 rounded-full text-sm font-semibold ${
                    gloss.confidence > 0.8
                      ? 'bg-green-100 text-green-800'
                      : gloss.confidence > 0.6
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-red-100 text-red-800'
                  }`}
                >
                  {(gloss.confidence * 100).toFixed(0)}%
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-3 mt-8">
        <button
          onClick={onNewAnalysis}
          className="btn-primary"
        >
          Analyze Another Video
        </button>
        <button
          onClick={() => {
            const data = JSON.stringify(results, null, 2)
            const blob = new Blob([data], { type: 'application/json' })
            const url = URL.createObjectURL(blob)
            const a = document.createElement('a')
            a.href = url
            a.download = 'results.json'
            a.click()
          }}
          className="btn-secondary"
        >
          Download Results
        </button>
      </div>
    </div>
  )
}
