import React from 'react'
import {
  LineChart,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts'
import { TrendingUp, AlertCircle } from 'lucide-react'

// Sample data – replace with real API data
const fraudTrendData = [
  { date: 'Jan', detected: 24, blocked: 18 },
  { date: 'Feb', detected: 28, blocked: 22 },
  { date: 'Mar', detected: 22, blocked: 19 },
  { date: 'Apr', detected: 35, blocked: 30 },
  { date: 'May', detected: 42, blocked: 38 },
  { date: 'Jun', detected: 38, blocked: 34 },
  { date: 'Jul', detected: 45, blocked: 40 },
  { date: 'Aug', detected: 51, blocked: 46 },
  { date: 'Sep', detected: 48, blocked: 43 },
  { date: 'Oct', detected: 56, blocked: 50 },
  { date: 'Nov', detected: 62, blocked: 55 },
  { date: 'Dec', detected: 58, blocked: 52 }
]

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white/95 backdrop-blur-sm px-4 py-2 rounded-xl shadow-lg border border-indigo-100">
        <p className="text-sm font-semibold text-slate-700 mb-1">{label}</p>
        {payload.map((entry, idx) => (
          <p key={idx} className="text-sm" style={{ color: entry.color }}>
            {entry.name}: {entry.value}
          </p>
        ))}
      </div>
    )
  }
  return null
}

const FraudChart = ({ data = fraudTrendData, height = 320, showLegend = true }) => {
  // Calculate trend direction
  const lastMonth = data[data.length - 1]
  const prevMonth = data[data.length - 2]
  const trend = lastMonth && prevMonth
    ? ((lastMonth.detected - prevMonth.detected) / prevMonth.detected * 100).toFixed(1)
    : 0
  const isUp = trend > 0

  return (
    <div className="bg-white rounded-2xl p-6 shadow-soft border border-white/50 hover:shadow-hover transition-all duration-300">
      {/* Header with title and trend indicator */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-6">
        <div>
          <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-red-500" />
            Fraud Detection Trends
          </h3>
          <p className="text-sm text-slate-500 mt-0.5">
            Monthly detected vs blocked fraud cases
          </p>
        </div>
        <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium ${
          isUp ? 'bg-red-50 text-red-600' : 'bg-green-50 text-green-600'
        }`}>
          <TrendingUp className={`w-4 h-4 ${isUp ? '' : 'rotate-180'}`} />
          <span>{Math.abs(trend)}% {isUp ? 'increase' : 'decrease'}</span>
          <span className="text-slate-400 text-xs ml-1">vs last month</span>
        </div>
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 5 }}>
          <defs>
            <linearGradient id="detectedGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#ef4444" stopOpacity={0.2} />
              <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="blockedGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#22c55e" stopOpacity={0.2} />
              <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
          <XAxis
            dataKey="date"
            axisLine={false}
            tickLine={false}
            tick={{ fill: '#64748b', fontSize: 11 }}
            dy={8}
          />
          <YAxis
            axisLine={false}
            tickLine={false}
            tick={{ fill: '#64748b', fontSize: 11 }}
            dx={-8}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ stroke: '#cbd5e1', strokeWidth: 1 }} />
          {showLegend && (
            <Legend
              verticalAlign="top"
              align="right"
              iconType="circle"
              iconSize={8}
              wrapperStyle={{ fontSize: 12, paddingBottom: 16 }}
            />
          )}
          <Area
            type="monotone"
            dataKey="detected"
            stroke="none"
            fill="url(#detectedGradient)"
            name="Detected"
          />
          <Line
            type="monotone"
            dataKey="detected"
            stroke="#ef4444"
            strokeWidth={3}
            dot={{ fill: '#ef4444', r: 4, strokeWidth: 2, stroke: '#fff' }}
            activeDot={{ r: 6, fill: '#dc2626' }}
            name="Detected"
          />
          <Area
            type="monotone"
            dataKey="blocked"
            stroke="none"
            fill="url(#blockedGradient)"
            name="Blocked"
          />
          <Line
            type="monotone"
            dataKey="blocked"
            stroke="#22c55e"
            strokeWidth={3}
            dot={{ fill: '#22c55e', r: 4, strokeWidth: 2, stroke: '#fff' }}
            activeDot={{ r: 6, fill: '#16a34a' }}
            name="Blocked"
          />
        </LineChart>
      </ResponsiveContainer>

      {/* Insight note */}
      <div className="mt-4 pt-3 border-t border-slate-100 text-xs text-slate-400 flex items-center justify-between">
        <span>Data updated daily • Last 12 months</span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-red-500"></span>
          Detection rate: 92%
        </span>
      </div>
    </div>
  )
}

export default FraudChart