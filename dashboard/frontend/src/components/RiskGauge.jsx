import React, { useEffect, useState } from 'react'

const RiskGauge = ({ score = 34 }) => {
  const [animatedScore, setAnimatedScore] = useState(0)

  useEffect(() => {
    const timer = setTimeout(() => setAnimatedScore(score), 100)
    return () => clearTimeout(timer)
  }, [score])

  const radius = 80
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (animatedScore / 100) * circumference

  const getColor = (value) => {
    if (value < 30) return '#22c55e'
    if (value < 70) return '#eab308'
    return '#ef4444'
  }

  const getRiskLabel = (value) => {
    if (value < 30) return 'Low Risk'
    if (value < 70) return 'Medium Risk'
    return 'High Risk'
  }

  return (
    <div className="bg-white rounded-2xl p-6 shadow-soft border border-white/50 h-full flex flex-col">
      <div className="mb-2">
        <h3 className="text-lg font-bold text-slate-800">Overall Risk Score</h3>
        <p className="text-sm text-slate-500">Real-time platform risk meter</p>
      </div>

      <div className="relative flex justify-center items-center py-4 flex-1">
        <svg width="220" height="220" viewBox="0 0 220 220" className="transform -rotate-90">
          {/* Background circle */}
          <circle
            cx="110"
            cy="110"
            r={radius}
            fill="none"
            stroke="#e2e8f0"
            strokeWidth="12"
            strokeLinecap="round"
          />
          {/* Progress circle */}
          <circle
            cx="110"
            cy="110"
            r={radius}
            fill="none"
            stroke={getColor(animatedScore)}
            strokeWidth="12"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        
        {/* Center text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-5xl font-bold text-slate-800">{animatedScore}</span>
          <span className="text-sm text-slate-500 mt-1">out of 100</span>
        </div>
      </div>

      <div className="mt-3 text-center">
        <div className={`inline-flex px-4 py-1.5 rounded-full text-sm font-semibold ${
          animatedScore < 30 ? 'bg-green-100 text-green-700' :
          animatedScore < 70 ? 'bg-yellow-100 text-yellow-700' :
          'bg-red-100 text-red-700'
        }`}>
          {getRiskLabel(animatedScore)}
        </div>
        <p className="text-xs text-slate-400 mt-3">Based on 1,284 transactions (last 24h)</p>
      </div>
    </div>
  )
}

export default RiskGauge