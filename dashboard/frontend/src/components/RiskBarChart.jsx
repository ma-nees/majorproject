import React from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'

const data = [
  { riskLevel: 'Low', count: 145, color: '#22c55e' },
  { riskLevel: 'Medium', count: 87, color: '#eab308' },
  { riskLevel: 'High', count: 42, color: '#ef4444' },
  { riskLevel: 'Critical', count: 13, color: '#dc2626' },
]

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white/95 backdrop-blur-sm px-3 py-2 rounded-lg shadow-lg border border-indigo-100">
        <p className="text-sm font-semibold text-slate-700">{payload[0].payload.riskLevel}</p>
        <p className="text-indigo-600 text-sm">Transactions: {payload[0].value}</p>
      </div>
    )
  }
  return null
}

const RiskBarChart = () => {
  return (
    <div className="bg-white rounded-2xl p-6 shadow-soft border border-white/50 h-full">
      <div className="mb-4">
        <h3 className="text-lg font-bold text-slate-800">Risk Distribution</h3>
        <p className="text-sm text-slate-500">Transactions by risk level</p>
      </div>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }} barSize={50}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
          <XAxis dataKey="riskLevel" axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} />
          <YAxis axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: '#f1f5f9' }} />
          <Bar dataKey="count" radius={[8, 8, 0, 0]}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

export default RiskBarChart