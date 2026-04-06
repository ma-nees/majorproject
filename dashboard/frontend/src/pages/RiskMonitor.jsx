import React from 'react'
import { Activity, TrendingUp, AlertCircle } from 'lucide-react'
import RiskGauge from '../components/RiskGauge'

const RiskMonitor = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-800">Risk Monitor</h1>
        <p className="text-slate-500 mt-1">Real-time risk assessment and behavioral analysis</p>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RiskGauge score={34} />
        
        <div className="bg-white rounded-2xl p-6 shadow-soft border border-white/50">
          <div className="flex items-center gap-2 mb-4">
            <Activity className="w-5 h-5 text-indigo-600" />
            <h3 className="text-lg font-bold text-slate-800">Active Risk Factors</h3>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center p-3 bg-red-50 rounded-xl">
              <span className="text-sm font-medium text-red-700">Unusual transaction amount</span>
              <span className="text-xs text-red-500">High impact</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-orange-50 rounded-xl">
              <span className="text-sm font-medium text-orange-700">Velocity check triggered</span>
              <span className="text-xs text-orange-500">Medium impact</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-yellow-50 rounded-xl">
              <span className="text-sm font-medium text-yellow-700">New device detected</span>
              <span className="text-xs text-yellow-500">Low impact</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default RiskMonitor