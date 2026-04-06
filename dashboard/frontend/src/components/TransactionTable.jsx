import React from 'react'
import { MoreHorizontal, AlertTriangle, CheckCircle, Clock } from 'lucide-react'

const transactions = [
  { id: 'TRX-001', amount: '$2,450', risk: 'High', status: 'Flagged', date: '2024-01-15', name: 'Michael Chen' },
  { id: 'TRX-002', amount: '$890', risk: 'Low', status: 'Approved', date: '2024-01-15', name: 'Sarah Johnson' },
  { id: 'TRX-003', amount: '$12,300', risk: 'Critical', status: 'Blocked', date: '2024-01-14', name: 'David Kim' },
  { id: 'TRX-004', amount: '$560', risk: 'Medium', status: 'Review', date: '2024-01-14', name: 'Emma Wilson' },
  { id: 'TRX-005', amount: '$3,210', risk: 'High', status: 'Flagged', date: '2024-01-13', name: 'James Rodriguez' },
]

const getRiskBadge = (risk) => {
  const styles = {
    Low: 'bg-green-100 text-green-700',
    Medium: 'bg-yellow-100 text-yellow-700',
    High: 'bg-orange-100 text-orange-700',
    Critical: 'bg-red-100 text-red-700',
  }
  return <span className={`px-2 py-1 rounded-full text-xs font-semibold ${styles[risk]}`}>{risk}</span>
}

const getStatusIcon = (status) => {
  switch(status) {
    case 'Approved': return <CheckCircle className="w-4 h-4 text-green-600" />
    case 'Flagged': return <AlertTriangle className="w-4 h-4 text-orange-600" />
    case 'Blocked': return <AlertTriangle className="w-4 h-4 text-red-600" />
    default: return <Clock className="w-4 h-4 text-blue-600" />
  }
}

const TransactionTable = () => {
  return (
    <div className="bg-white rounded-2xl shadow-soft border border-white/50 overflow-hidden">
      <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-slate-800">Recent Transactions</h3>
          <p className="text-sm text-slate-500">Latest high-risk flagged activity</p>
        </div>
        <button className="text-sm text-indigo-600 hover:text-indigo-700 font-medium">View All →</button>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-slate-50/50">
            <tr className="text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
              <th className="px-6 py-3">Transaction ID</th>
              <th className="px-6 py-3">Customer</th>
              <th className="px-6 py-3">Amount</th>
              <th className="px-6 py-3">Risk</th>
              <th className="px-6 py-3">Status</th>
              <th className="px-6 py-3">Date</th>
              <th className="px-6 py-3"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {transactions.map((tx) => (
              <tr key={tx.id} className="hover:bg-indigo-50/30 transition-colors group">
                <td className="px-6 py-3 text-sm font-mono text-slate-700">{tx.id}</td>
                <td className="px-6 py-3 text-sm text-slate-700">{tx.name}</td>
                <td className="px-6 py-3 text-sm font-semibold text-slate-800">{tx.amount}</td>
                <td className="px-6 py-3">{getRiskBadge(tx.risk)}</td>
                <td className="px-6 py-3">
                  <div className="flex items-center gap-1.5">
                    {getStatusIcon(tx.status)}
                    <span className="text-sm text-slate-700">{tx.status}</span>
                  </div>
                </td>
                <td className="px-6 py-3 text-sm text-slate-500">{tx.date}</td>
                <td className="px-6 py-3">
                  <button className="opacity-0 group-hover:opacity-100 transition-opacity">
                    <MoreHorizontal className="w-4 h-4 text-slate-400" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default TransactionTable