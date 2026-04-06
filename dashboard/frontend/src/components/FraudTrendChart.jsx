import React from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area } from 'recharts'

const data = [
  { day: 'Mon', fraudCases: 12 },
  { day: 'Tue', fraudCases: 18 },
  { day: 'Wed', fraudCases: 14 },
  { day: 'Thu', fraudCases: 22 },
  { day: 'Fri', fraudCases: 30 },
  { day: 'Sat', fraudCases: 25 },
  { day: 'Sun', fraudCases: 19 },
]

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white/95 backdrop-blur-sm px-3 py-2 rounded-lg shadow-lg border border-indigo-100">
        <p className="text-sm font-semibold text-slate-700">{label}</p>
        <p className="text-indigo-600 text-sm">Fraud Cases: {payload[0].value}</p>
      </div>
    )
  }
  return null
}

const FraudTrendChart = () => {
  return (
    <div className="bg-white rounded-2xl p-6 shadow-soft border border-white/50 h-full">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-bold text-slate-800">Fraud Trends</h3>
          <p className="text-sm text-slate-500">Weekly detected fraud cases</p>
        </div>
        <div className="flex gap-2">
          <span className="text-xs font-medium text-indigo-600 bg-indigo-50 px-2 py-1 rounded-lg">Last 7 days</span>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
          <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} />
          <YAxis axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} />
          <Tooltip content={<CustomTooltip />} cursor={{ stroke: '#cbd5e1', strokeWidth: 1 }} />
          <Area type="monotone" dataKey="fraudCases" stroke="none" fill="url(#colorGradient)" />
          <Line type="monotone" dataKey="fraudCases" stroke="#6366f1" strokeWidth={3} dot={{ fill: '#6366f1', r: 4, strokeWidth: 2, stroke: '#fff' }} activeDot={{ r: 6, fill: '#4f46e5' }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export default FraudTrendChart