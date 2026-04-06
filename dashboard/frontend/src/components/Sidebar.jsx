import React from 'react'
import { NavLink } from 'react-router-dom'   // ← import NavLink
import { 
  Shield, 
  LayoutDashboard, 
  CreditCard, 
  BarChart3, 
  Bell, 
  Settings,
  Activity
} from 'lucide-react'

const menuItems = [
  { icon: LayoutDashboard, label: 'Dashboard', path: '/', active: true },
  { icon: CreditCard, label: 'Transactions', path: '/transactions', active: false },
  { icon: Activity, label: 'Risk Monitor', path: '/risk-monitor', active: false },
  { icon: BarChart3, label: 'Analytics', path: '/analytics', active: false },
  { icon: Bell, label: 'Alerts', path: '/alerts', active: false, badge: 3 },
  { icon: Settings, label: 'Settings', path: '/settings', active: false },
]

const Sidebar = () => {
  return (
    <aside className="hidden md:flex md:flex-col w-72 bg-white/70 backdrop-blur-md border-r border-indigo-100/50 shadow-soft">
      <div className="flex items-center gap-3 px-6 py-8 border-b border-indigo-50">
        <div className="bg-gradient-to-br from-indigo-500 to-cyan-500 p-2 rounded-xl shadow-md">
          <Shield className="w-7 h-7 text-white" />
        </div>
        <span className="text-2xl font-bold bg-gradient-to-r from-indigo-700 to-cyan-600 bg-clip-text text-transparent">
          FraudShield
        </span>
      </div>

      <nav className="flex-1 px-4 py-8 space-y-1.5">
        {menuItems.map((item) => (
          <NavLink
            key={item.label}
            to={item.path}
            className={({ isActive }) => `
              flex items-center justify-between px-4 py-3 rounded-xl transition-all duration-200 group
              ${isActive 
                ? 'bg-gradient-to-r from-indigo-50 to-cyan-50 text-indigo-700 shadow-sm border border-indigo-100/50' 
                : 'text-slate-600 hover:bg-indigo-50/50 hover:text-indigo-600'
              }
            `}
          >
            {({ isActive }) => (
              <>
                <div className="flex items-center gap-3">
                  <item.icon className={`w-5 h-5 ${isActive ? 'text-indigo-600' : 'text-slate-400 group-hover:text-indigo-500'}`} />
                  <span className="font-medium">{item.label}</span>
                </div>
                {item.badge && (
                  <span className="bg-red-500 text-white text-xs px-2 py-0.5 rounded-full font-semibold">
                    {item.badge}
                  </span>
                )}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      <div className="p-6 border-t border-indigo-50">
        <div className="bg-gradient-to-r from-indigo-500/10 to-cyan-500/10 rounded-xl p-4 backdrop-blur-sm">
          <p className="text-xs font-semibold text-indigo-600 uppercase tracking-wide">System Health</p>
          <div className="flex items-center gap-2 mt-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-sm text-slate-700">All systems operational</span>
          </div>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar