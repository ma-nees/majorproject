import React from 'react'
import { CreditCard, Search, Filter } from 'lucide-react'

const Transactions = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-800">Transactions</h1>
        <p className="text-slate-500 mt-1">Monitor and investigate all payment transactions</p>
      </div>
      
      <div className="bg-white rounded-2xl p-6 shadow-soft border border-white/50">
        <div className="flex flex-wrap gap-4 items-center justify-between mb-6">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input 
              type="text" 
              placeholder="Search by transaction ID, customer..." 
              className="w-full pl-10 pr-4 py-2 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-300"
            />
          </div>
          <button className="flex items-center gap-2 px-4 py-2 border border-slate-200 rounded-xl text-slate-600 hover:bg-slate-50">
            <Filter className="w-4 h-4" /> Filter
          </button>
        </div>
        
        <div className="text-center py-12 text-slate-400">
          <CreditCard className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>Transaction list will appear here</p>
          <p className="text-sm">Connect to your backend API to see real data</p>
        </div>
      </div>
    </div>
  )
}

export default Transactions