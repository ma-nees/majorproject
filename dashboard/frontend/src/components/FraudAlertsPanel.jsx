import React from 'react'
import { AlertCircle, Zap, MapPin, Clock, XCircle } from 'lucide-react'

const alerts = [
  { id: 1, type: 'Unusual amount', description: 'Transaction $12,300 from unusual location', time: '5 min ago', severity: 'critical' },
  { id: 2, type: 'Velocity check', description: 'Multiple rapid transactions from same IP', time: '23 min ago', severity: 'high' },
  { id: 3, type: 'Device fingerprint', description: 'New device detected on high-risk account', time: '1 hour ago', severity: 'medium' },
  { id: 4, type: 'Geolocation mismatch', description: 'Login from two countries within 1h', time: '3 hours ago', severity: 'high' },
]

const severityColors = {
  critical: 'bg-red-100 border-l-4 border-red-500',
  high: 'bg-orange-50 border-l-4 border-orange-400',
  medium: 'bg-yellow-50 border-l-4 border-yellow-400',
}

const FraudAlertsPanel = () => {
  return (
    <div className="bg-white rounded-2xl shadow-soft border border-white/50 h-full">
      <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-slate-800">Live Fraud Alerts</h3>
          <p className="text-sm text-slate-500">Real-time suspicious activity</p>
        </div>
        <AlertCircle className="w-5 h-5 text-red-400 animate-pulse" />
      </div>

      <div className="divide-y divide-slate-100">
        {alerts.map((alert) => (
          <div key={alert.id} className={`p-4 ${severityColors[alert.severity]} hover:bg-opacity-80 transition-all`}>
            <div className="flex items-start gap-3">
              <div className="mt-0.5">
                {alert.severity === 'critical' ? (
                  <XCircle className="w-5 h-5 text-red-500" />
                ) : alert.severity === 'high' ? (
                  <Zap className="w-5 h-5 text-orange-500" />
                ) : (
                  <MapPin className="w-5 h-5 text-yellow-500" />
                )}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="font-semibold text-sm text-slate-800">{alert.type}</span>
                  <span className="text-xs text-slate-400 flex items-center gap-1">
                    <Clock className="w-3 h-3" /> {alert.time}
                  </span>
                </div>
                <p className="text-sm text-slate-600 mt-0.5">{alert.description}</p>
              </div>
              <button className="text-indigo-600 text-xs font-medium hover:text-indigo-800 transition-colors">
                Investigate
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="px-6 py-3 bg-slate-50/50 rounded-b-2xl text-center">
        <button className="text-sm text-indigo-600 font-medium hover:text-indigo-700">
          View all 12 alerts →
        </button>
      </div>
    </div>
  )
}

export default FraudAlertsPanel