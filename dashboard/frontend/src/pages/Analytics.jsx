import React from 'react'
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend
} from 'recharts'
import { TrendingUp, TrendingDown, Calendar, Shield, Users, AlertCircle } from 'lucide-react'

// Mock data
const fraudTrendData = [
  { month: 'Jan', fraud: 34, transactions: 1240 },
  { month: 'Feb', fraud: 42, transactions: 1350 },
  { month: 'Mar', fraud: 38, transactions: 1420 },
  { month: 'Apr', fraud: 55, transactions: 1580 },
  { month: 'May', fraud: 61, transactions: 1650 },
  { month: 'Jun', fraud: 48, transactions: 1700 },
]

const riskLevelData = [
  { name: 'Low', value: 145, color: '#22c55e' },
  { name: 'Medium', value: 87, color: '#eab308' },
  { name: 'High', value: 42, color: '#f97316' },
  { name: 'Critical', value: 13, color: '#ef4444' },
]

const fraudByCategory = [
  { category: 'Account Takeover', count: 28 },
  { category: 'Payment Fraud', count: 42 },
  { category: 'Identity Theft', count: 19 },
  { category: 'Card Testing', count: 31 },
  { category: 'Phishing', count: 15 },
]

const hourlyRiskData = [
  { hour: '00', riskScore: 32 },
  { hour: '04', riskScore: 28 },
  { hour: '08', riskScore: 45 },
  { hour: '12', riskScore: 62 },
  { hour: '16', riskScore: 58 },
  { hour: '20', riskScore: 71 },
  { hour: '23', riskScore: 55 },
]

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white/95 backdrop-blur-sm px-3 py-2 rounded-lg shadow-lg border border-indigo-100">
        <p className="text-sm font-semibold text-slate-700">{label}</p>
        {payload.map((p, idx) => (
          <p key={idx} className="text-indigo-600 text-sm">
            {p.name}: {p.value}
          </p>
        ))}
      </div>
    )
  }
  return null
}

const Analytics = () => {
  // Calculate summary metrics
  const totalFraud = fraudTrendData.reduce((sum, d) => sum + d.fraud, 0)
  const avgFraudRate = (totalFraud / fraudTrendData.reduce((sum, d) => sum + d.transactions, 0) * 100).toFixed(1)
  const peakFraudMonth = fraudTrendData.reduce((max, d) => d.fraud > max.fraud ? d : max, fraudTrendData[0])
  const totalRiskTransactions = riskLevelData.reduce((sum, d) => sum + d.value, 0)

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-800">Analytics & Insights</h1>
        <p className="text-slate-500 mt-1">Comprehensive fraud detection metrics and trends</p>
      </div>

      {/* Key Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="bg-white rounded-2xl p-5 shadow-soft border border-white/50">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-500">Total Fraud Cases</p>
              <p className="text-3xl font-bold text-slate-800">{totalFraud}</p>
            </div>
            <div className="bg-red-50 p-3 rounded-xl">
              <AlertCircle className="w-6 h-6 text-red-500" />
            </div>
          </div>
          <div className="mt-2 flex items-center gap-1 text-sm">
            <TrendingUp className="w-3 h-3 text-red-500" />
            <span className="text-red-600">+12%</span>
            <span className="text-slate-400 ml-1">vs last 6 months</span>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-5 shadow-soft border border-white/50">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-500">Fraud Rate</p>
              <p className="text-3xl font-bold text-slate-800">{avgFraudRate}%</p>
            </div>
            <div className="bg-orange-50 p-3 rounded-xl">
              <TrendingUp className="w-6 h-6 text-orange-500" />
            </div>
          </div>
          <div className="mt-2 flex items-center gap-1 text-sm">
            <span className="text-orange-600">+1.8%</span>
            <span className="text-slate-400 ml-1">increase from Q1</span>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-5 shadow-soft border border-white/50">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-500">Peak Fraud Month</p>
              <p className="text-3xl font-bold text-slate-800">{peakFraudMonth.month}</p>
            </div>
            <div className="bg-yellow-50 p-3 rounded-xl">
              <Calendar className="w-6 h-6 text-yellow-600" />
            </div>
          </div>
          <div className="mt-2 text-sm text-slate-600">
            {peakFraudMonth.fraud} cases detected
          </div>
        </div>

        <div className="bg-white rounded-2xl p-5 shadow-soft border border-white/50">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-500">High Risk Transactions</p>
              <p className="text-3xl font-bold text-slate-800">
                {riskLevelData.find(r => r.name === 'High' || r.name === 'Critical')?.value || 0}
              </p>
            </div>
            <div className="bg-indigo-50 p-3 rounded-xl">
              <Shield className="w-6 h-6 text-indigo-600" />
            </div>
          </div>
          <div className="mt-2 text-sm text-slate-600">
            {((riskLevelData.find(r => r.name === 'High')?.value + riskLevelData.find(r => r.name === 'Critical')?.value) / totalRiskTransactions * 100).toFixed(1)}% of total
          </div>
        </div>
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Fraud Trend Over Time */}
        <div className="bg-white rounded-2xl p-6 shadow-soft border border-white/50">
          <div>
            <h3 className="text-lg font-bold text-slate-800">Fraud Trend Over Time</h3>
            <p className="text-sm text-slate-500 mb-4">Monthly fraud cases vs transaction volume</p>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={fraudTrendData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
              <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fill: '#64748b' }} />
              <YAxis yAxisId="left" axisLine={false} tickLine={false} tick={{ fill: '#64748b' }} />
              <YAxis yAxisId="right" orientation="right" axisLine={false} tickLine={false} tick={{ fill: '#64748b' }} />
              <Tooltip content={<CustomTooltip />} />
              <Line yAxisId="left" type="monotone" dataKey="fraud" stroke="#ef4444" strokeWidth={3} dot={{ fill: '#ef4444', r: 4 }} name="Fraud Cases" />
              <Line yAxisId="right" type="monotone" dataKey="transactions" stroke="#6366f1" strokeWidth={3} dot={{ fill: '#6366f1', r: 4 }} name="Transactions" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Risk Level Distribution (Pie) */}
        <div className="bg-white rounded-2xl p-6 shadow-soft border border-white/50">
          <div>
            <h3 className="text-lg font-bold text-slate-800">Risk Level Distribution</h3>
            <p className="text-sm text-slate-500 mb-4">Transactions by risk category</p>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={riskLevelData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={3}
                dataKey="value"
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                labelLine={false}
              >
                {riskLevelData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} stroke="white" strokeWidth={2} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
              <Legend verticalAlign="bottom" height={36} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Fraud by Category */}
        <div className="bg-white rounded-2xl p-6 shadow-soft border border-white/50">
          <div>
            <h3 className="text-lg font-bold text-slate-800">Fraud by Category</h3>
            <p className="text-sm text-slate-500 mb-4">Most common fraud types</p>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={fraudByCategory} layout="vertical" margin={{ top: 10, right: 10, left: 80, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" horizontal={false} />
              <XAxis type="number" axisLine={false} tickLine={false} tick={{ fill: '#64748b' }} />
              <YAxis type="category" dataKey="category" axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="count" fill="#06b6d4" radius={[0, 8, 8, 0]} barSize={30} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Hourly Risk Pattern */}
        <div className="bg-white rounded-2xl p-6 shadow-soft border border-white/50">
          <div>
            <h3 className="text-lg font-bold text-slate-800">Hourly Risk Pattern</h3>
            <p className="text-sm text-slate-500 mb-4">Average risk score by time of day (UTC)</p>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={hourlyRiskData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="riskGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f97316" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#f97316" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
              <XAxis dataKey="hour" axisLine={false} tickLine={false} tick={{ fill: '#64748b' }} />
              <YAxis axisLine={false} tickLine={false} tick={{ fill: '#64748b' }} />
              <Tooltip content={<CustomTooltip />} />
              <Area type="monotone" dataKey="riskScore" stroke="#f97316" strokeWidth={2} fill="url(#riskGradient)" />
            </AreaChart>
          </ResponsiveContainer>
          <div className="mt-3 text-xs text-slate-400 text-center">
            Risk peaks during evening hours (20:00 UTC) – potential fraud patterns
          </div>
        </div>
      </div>

      {/* Additional Insights Panel */}
      <div className="bg-gradient-to-r from-indigo-500/5 to-cyan-500/5 rounded-2xl p-6 border border-indigo-100/50">
        <div className="flex items-start gap-4 flex-wrap">
          <div className="flex-1 min-w-[200px]">
            <div className="flex items-center gap-2 mb-2">
              <Users className="w-5 h-5 text-indigo-600" />
              <h4 className="font-semibold text-slate-800">Top Risk Indicators</h4>
            </div>
            <ul className="space-y-1 text-sm text-slate-600">
              <li>• Unusual transaction amount: 34% of fraud cases</li>
              <li>• Velocity (rapid transactions): 28% of fraud cases</li>
              <li>• Geolocation mismatch: 22% of fraud cases</li>
              <li>• Device fingerprint anomaly: 16% of fraud cases</li>
            </ul>
          </div>
          <div className="flex-1 min-w-[200px]">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="w-5 h-5 text-cyan-600" />
              <h4 className="font-semibold text-slate-800">Recommendations</h4>
            </div>
            <ul className="space-y-1 text-sm text-slate-600">
              <li>• Increase ML model retraining frequency (bi-weekly)</li>
              <li>• Add additional rules for high-velocity alerts</li>
              <li>• Enhance geolocation verification for cross-border tx</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Analytics