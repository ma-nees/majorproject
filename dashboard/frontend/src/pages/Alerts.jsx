import React, { useState } from 'react'
import { 
  Bell, 
  AlertTriangle, 
  Zap, 
  MapPin, 
  Clock, 
  XCircle, 
  CheckCircle, 
  Filter, 
  Download,
  Eye,
  MoreVertical,
  Shield
} from 'lucide-react'

// Mock data for alerts
const allAlerts = [
  { 
    id: 1, 
    type: 'Unusual amount', 
    description: 'Transaction $12,300 from unusual location (Russia)',
    time: '5 min ago',
    severity: 'critical',
    status: 'new',
    transactionId: 'TRX-001',
    customer: 'Michael Chen',
    riskScore: 94
  },
  { 
    id: 2, 
    type: 'Velocity check', 
    description: 'Multiple rapid transactions from same IP (10 tx in 2 min)',
    time: '23 min ago',
    severity: 'high',
    status: 'investigating',
    transactionId: 'TRX-002',
    customer: 'David Kim',
    riskScore: 87
  },
  { 
    id: 3, 
    type: 'Device fingerprint', 
    description: 'New device detected on high-risk account',
    time: '1 hour ago',
    severity: 'medium',
    status: 'new',
    transactionId: 'TRX-003',
    customer: 'Emma Wilson',
    riskScore: 65
  },
  { 
    id: 4, 
    type: 'Geolocation mismatch', 
    description: 'Login from two countries within 1 hour (US → JP)',
    time: '3 hours ago',
    severity: 'high',
    status: 'resolved',
    transactionId: 'TRX-004',
    customer: 'James Rodriguez',
    riskScore: 78
  },
  { 
    id: 5, 
    type: 'Behavioral anomaly', 
    description: 'Unusual typing pattern detected during checkout',
    time: '5 hours ago',
    severity: 'medium',
    status: 'new',
    transactionId: 'TRX-005',
    customer: 'Sarah Johnson',
    riskScore: 58
  },
  { 
    id: 6, 
    type: 'Suspicious IP', 
    description: 'Transaction from known TOR exit node',
    time: '7 hours ago',
    severity: 'critical',
    status: 'investigating',
    transactionId: 'TRX-006',
    customer: 'Anonymous',
    riskScore: 96
  },
]

const severityConfig = {
  critical: { label: 'Critical', color: 'bg-red-100 text-red-700', icon: XCircle, iconColor: 'text-red-500' },
  high: { label: 'High', color: 'bg-orange-100 text-orange-700', icon: Zap, iconColor: 'text-orange-500' },
  medium: { label: 'Medium', color: 'bg-yellow-100 text-yellow-700', icon: MapPin, iconColor: 'text-yellow-500' },
}

const statusConfig = {
  new: { label: 'New', color: 'bg-blue-100 text-blue-700' },
  investigating: { label: 'Investigating', color: 'bg-purple-100 text-purple-700' },
  resolved: { label: 'Resolved', color: 'bg-green-100 text-green-700' },
}

const Alerts = () => {
  const [filterSeverity, setFilterSeverity] = useState('all')
  const [filterStatus, setFilterStatus] = useState('all')
  const [selectedAlerts, setSelectedAlerts] = useState([])

  const filteredAlerts = allAlerts.filter(alert => {
    if (filterSeverity !== 'all' && alert.severity !== filterSeverity) return false
    if (filterStatus !== 'all' && alert.status !== filterStatus) return false
    return true
  })

  const toggleSelectAlert = (id) => {
    setSelectedAlerts(prev =>
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    )
  }

  const stats = {
    total: allAlerts.length,
    new: allAlerts.filter(a => a.status === 'new').length,
    investigating: allAlerts.filter(a => a.status === 'investigating').length,
    critical: allAlerts.filter(a => a.severity === 'critical').length,
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-800">Fraud Alerts</h1>
          <p className="text-slate-500 mt-1">Manage and investigate suspicious activities</p>
        </div>
        <div className="flex gap-3">
          <button className="px-4 py-2 bg-white border border-slate-200 rounded-xl text-slate-700 text-sm font-medium hover:bg-slate-50 transition-colors flex items-center gap-2">
            <Download className="w-4 h-4" />
            Export
          </button>
          <button className="px-4 py-2 bg-indigo-600 text-white rounded-xl text-sm font-medium hover:bg-indigo-700 transition-colors flex items-center gap-2 shadow-sm">
            <Bell className="w-4 h-4" />
            Mark all read
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="bg-white rounded-2xl p-5 shadow-soft border border-white/50">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-500">Total Alerts</p>
              <p className="text-3xl font-bold text-slate-800">{stats.total}</p>
            </div>
            <div className="bg-indigo-50 p-3 rounded-xl">
              <Bell className="w-6 h-6 text-indigo-600" />
            </div>
          </div>
        </div>
        <div className="bg-white rounded-2xl p-5 shadow-soft border border-white/50">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-500">New Alerts</p>
              <p className="text-3xl font-bold text-blue-600">{stats.new}</p>
            </div>
            <div className="bg-blue-50 p-3 rounded-xl">
              <AlertTriangle className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>
        <div className="bg-white rounded-2xl p-5 shadow-soft border border-white/50">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-500">Investigating</p>
              <p className="text-3xl font-bold text-purple-600">{stats.investigating}</p>
            </div>
            <div className="bg-purple-50 p-3 rounded-xl">
              <Shield className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>
        <div className="bg-white rounded-2xl p-5 shadow-soft border border-white/50">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-500">Critical Alerts</p>
              <p className="text-3xl font-bold text-red-600">{stats.critical}</p>
            </div>
            <div className="bg-red-50 p-3 rounded-xl">
              <XCircle className="w-6 h-6 text-red-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-2xl p-5 shadow-soft border border-white/50">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex flex-wrap gap-3">
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-slate-400" />
              <span className="text-sm font-medium text-slate-600">Severity:</span>
            </div>
            {['all', 'critical', 'high', 'medium'].map(sev => (
              <button
                key={sev}
                onClick={() => setFilterSeverity(sev)}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                  filterSeverity === sev
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {sev.charAt(0).toUpperCase() + sev.slice(1)}
              </button>
            ))}
          </div>
          <div className="flex flex-wrap gap-3">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-slate-600">Status:</span>
            </div>
            {['all', 'new', 'investigating', 'resolved'].map(st => (
              <button
                key={st}
                onClick={() => setFilterStatus(st)}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                  filterStatus === st
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {st.charAt(0).toUpperCase() + st.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Alerts Table */}
      <div className="bg-white rounded-2xl shadow-soft border border-white/50 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-50/80 border-b border-slate-100">
              <tr className="text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                <th className="px-4 py-3 w-10">
                  <input
                    type="checkbox"
                    className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                    checked={selectedAlerts.length === filteredAlerts.length && filteredAlerts.length > 0}
                    onChange={(e) => {
                      if (e.target.checked) setSelectedAlerts(filteredAlerts.map(a => a.id))
                      else setSelectedAlerts([])
                    }}
                  />
                </th>
                <th className="px-4 py-3">Severity</th>
                <th className="px-4 py-3">Type</th>
                <th className="px-4 py-3">Description</th>
                <th className="px-4 py-3">Customer</th>
                <th className="px-4 py-3">Risk Score</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Time</th>
                <th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {filteredAlerts.map((alert) => {
                const SeverityIcon = severityConfig[alert.severity].icon
                return (
                  <tr key={alert.id} className="hover:bg-indigo-50/30 transition-colors group">
                    <td className="px-4 py-3">
                      <input
                        type="checkbox"
                        className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                        checked={selectedAlerts.includes(alert.id)}
                        onChange={() => toggleSelectAlert(alert.id)}
                      />
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-1.5">
                        <SeverityIcon className={`w-4 h-4 ${severityConfig[alert.severity].iconColor}`} />
                        <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${severityConfig[alert.severity].color}`}>
                          {severityConfig[alert.severity].label}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm font-medium text-slate-700">{alert.type}</td>
                    <td className="px-4 py-3 text-sm text-slate-600 max-w-xs truncate">{alert.description}</td>
                    <td className="px-4 py-3 text-sm text-slate-700">{alert.customer}</td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <div className="w-16 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                          <div className={`h-full rounded-full ${
                            alert.riskScore >= 80 ? 'bg-red-500' : alert.riskScore >= 60 ? 'bg-orange-500' : 'bg-yellow-500'
                          }`} style={{ width: `${alert.riskScore}%` }} />
                        </div>
                        <span className="text-xs font-mono text-slate-600">{alert.riskScore}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`text-xs font-medium px-2 py-1 rounded-full ${statusConfig[alert.status].color}`}>
                        {statusConfig[alert.status].label}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-500 flex items-center gap-1">
                      <Clock className="w-3 h-3" /> {alert.time}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button className="p-1 hover:bg-slate-100 rounded-lg transition">
                          <Eye className="w-4 h-4 text-slate-500" />
                        </button>
                        <button className="p-1 hover:bg-slate-100 rounded-lg transition">
                          <MoreVertical className="w-4 h-4 text-slate-500" />
                        </button>
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
        {selectedAlerts.length > 0 && (
          <div className="px-6 py-3 bg-indigo-50 border-t border-indigo-100 flex items-center justify-between">
            <span className="text-sm text-indigo-700">{selectedAlerts.length} alert(s) selected</span>
            <div className="flex gap-2">
              <button className="px-3 py-1.5 bg-white border border-indigo-200 rounded-lg text-indigo-700 text-sm hover:bg-indigo-100 transition">
                Mark as investigating
              </button>
              <button className="px-3 py-1.5 bg-white border border-red-200 rounded-lg text-red-600 text-sm hover:bg-red-50 transition">
                Resolve
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Alerts