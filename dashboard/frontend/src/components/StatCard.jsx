import React from 'react'
import { ArrowUpRight, ArrowDownRight } from 'lucide-react'

const StatCard = ({ title, value, change, icon: Icon, changeType = 'increase', color = 'indigo' }) => {
  const colorMap = {
    indigo: 'from-indigo-500 to-indigo-600',
    cyan: 'from-cyan-500 to-cyan-600',
    red: 'from-red-500 to-red-600',
    green: 'from-green-500 to-green-600',
  }

  const bgMap = {
    indigo: 'bg-indigo-50',
    cyan: 'bg-cyan-50',
    red: 'bg-red-50',
    green: 'bg-green-50',
  }

  return (
    <div className="group bg-white rounded-2xl p-6 shadow-soft border border-white/50 hover:shadow-hover transition-all duration-300 hover:-translate-y-1">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500 uppercase tracking-wide">{title}</p>
          <p className="text-3xl font-bold text-slate-800 mt-2">{value}</p>
          {change && (
            <div className="flex items-center gap-1 mt-3">
              {changeType === 'increase' ? (
                <ArrowUpRight className="w-4 h-4 text-green-500" />
              ) : (
                <ArrowDownRight className="w-4 h-4 text-red-500" />
              )}
              <span className={`text-sm font-medium ${changeType === 'increase' ? 'text-green-600' : 'text-red-600'}`}>
                {change}
              </span>
              <span className="text-xs text-slate-400 ml-1">vs last week</span>
            </div>
          )}
        </div>
        <div className={`${bgMap[color]} p-3 rounded-xl group-hover:scale-110 transition-transform duration-200`}>
          <Icon className={`w-6 h-6 text-${color}-600`} />
        </div>
      </div>
    </div>
  )
}

export default StatCard