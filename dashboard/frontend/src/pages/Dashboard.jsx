import React from 'react'
import { CreditCard, AlertTriangle, Activity, Bell } from 'lucide-react'
import StatCard from '../components/StatCard'
import FraudTrendChart from '../components/FraudTrendChart'
import RiskBarChart from '../components/RiskBarChart'
import RiskGauge from '../components/RiskGauge'
import TransactionTable from '../components/TransactionTable'
import FraudAlertsPanel from '../components/FraudAlertsPanel'

const Dashboard = () => {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-800">Dashboard</h1>
        <p className="text-slate-500 mt-1">Real-time fraud monitoring & risk insights</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard 
          title="Total Transactions" 
          value="1,284" 
          change="+12.5%" 
          changeType="increase"
          icon={CreditCard}
          color="indigo"
        />
        <StatCard 
          title="Fraud Detected" 
          value="47" 
          change="+8.2%" 
          changeType="increase"
          icon={AlertTriangle}
          color="red"
        />
        <StatCard 
          title="Risk Score" 
          value="34.2" 
          change="-5.1%" 
          changeType="decrease"
          icon={Activity}
          color="cyan"
        />
        <StatCard 
          title="Active Alerts" 
          value="12" 
          change="+3" 
          changeType="increase"
          icon={Bell}
          color="green"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <FraudTrendChart />
        <RiskBarChart />
      </div>

      {/* Risk Gauge + Alerts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <RiskGauge score={34} />
        </div>
        <div className="lg:col-span-2">
          <FraudAlertsPanel />
        </div>
      </div>

      {/* Transactions Table */}
      <TransactionTable />
    </div>
  )
}

export default Dashboard