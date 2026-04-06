import React, { useState } from 'react'
import { 
  Settings as SettingsIcon,
  Bell, 
  Shield, 
  User, 
  Globe, 
  Database, 
  Save, 
  RefreshCw,
  Lock,
  AlertTriangle
} from 'lucide-react'

const Settings = () => {
  const [notifications, setNotifications] = useState({
    emailAlerts: true,
    pushAlerts: true,
    fraudSummary: 'daily',
    criticalOnly: false,
  })

  const [security, setSecurity] = useState({
    twoFactorAuth: true,
    sessionTimeout: '30',
    ipWhitelist: false,
  })

  const [theme, setTheme] = useState('light')

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-800">Settings</h1>
        <p className="text-slate-500 mt-1">Manage your platform preferences and security</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sidebar navigation for settings */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-2xl shadow-soft border border-white/50 sticky top-6">
            <nav className="p-2 space-y-1">
              {[
                { icon: Bell, label: 'Notifications', id: 'notifications' },
                { icon: Shield, label: 'Security', id: 'security' },
                { icon: User, label: 'Profile', id: 'profile' },
                { icon: Globe, label: 'API & Integrations', id: 'api' },
                { icon: Database, label: 'Data Management', id: 'data' },
              ].map((item) => (
                <a
                  key={item.id}
                  href={`#${item.id}`}
                  className="flex items-center gap-3 px-4 py-3 rounded-xl text-slate-600 hover:bg-indigo-50 hover:text-indigo-600 transition-all"
                >
                  <item.icon className="w-5 h-5" />
                  <span className="font-medium">{item.label}</span>
                </a>
              ))}
            </nav>
          </div>
        </div>

        {/* Main settings content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Notifications Section */}
          <div id="notifications" className="bg-white rounded-2xl p-6 shadow-soft border border-white/50">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-indigo-50 rounded-xl">
                <Bell className="w-5 h-5 text-indigo-600" />
              </div>
              <h2 className="text-xl font-bold text-slate-800">Notification Preferences</h2>
            </div>
            <div className="space-y-4">
              <label className="flex items-center justify-between cursor-pointer">
                <div>
                  <p className="font-medium text-slate-700">Email Alerts</p>
                  <p className="text-sm text-slate-400">Receive fraud alerts via email</p>
                </div>
                <div className="relative">
                  <input
                    type="checkbox"
                    className="sr-only peer"
                    checked={notifications.emailAlerts}
                    onChange={(e) => setNotifications({...notifications, emailAlerts: e.target.checked})}
                  />
                  <div className="w-11 h-6 bg-slate-200 rounded-full peer peer-checked:bg-indigo-600 peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all"></div>
                </div>
              </label>
              <label className="flex items-center justify-between cursor-pointer">
                <div>
                  <p className="font-medium text-slate-700">Push Notifications</p>
                  <p className="text-sm text-slate-400">Real-time alerts in dashboard</p>
                </div>
                <div className="relative">
                  <input
                    type="checkbox"
                    className="sr-only peer"
                    checked={notifications.pushAlerts}
                    onChange={(e) => setNotifications({...notifications, pushAlerts: e.target.checked})}
                  />
                  <div className="w-11 h-6 bg-slate-200 rounded-full peer peer-checked:bg-indigo-600 peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all"></div>
                </div>
              </label>
              <div>
                <p className="font-medium text-slate-700 mb-2">Fraud Summary Frequency</p>
                <select 
                  className="w-full px-4 py-2 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-300"
                  value={notifications.fraudSummary}
                  onChange={(e) => setNotifications({...notifications, fraudSummary: e.target.value})}
                >
                  <option value="daily">Daily Summary</option>
                  <option value="weekly">Weekly Summary</option>
                  <option value="monthly">Monthly Summary</option>
                </select>
              </div>
            </div>
          </div>

          {/* Security Section */}
          <div id="security" className="bg-white rounded-2xl p-6 shadow-soft border border-white/50">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-red-50 rounded-xl">
                <Shield className="w-5 h-5 text-red-600" />
              </div>
              <h2 className="text-xl font-bold text-slate-800">Security Settings</h2>
            </div>
            <div className="space-y-4">
              <label className="flex items-center justify-between cursor-pointer">
                <div>
                  <p className="font-medium text-slate-700">Two-Factor Authentication</p>
                  <p className="text-sm text-slate-400">Add an extra layer of security</p>
                </div>
                <div className="relative">
                  <input
                    type="checkbox"
                    className="sr-only peer"
                    checked={security.twoFactorAuth}
                    onChange={(e) => setSecurity({...security, twoFactorAuth: e.target.checked})}
                  />
                  <div className="w-11 h-6 bg-slate-200 rounded-full peer peer-checked:bg-indigo-600 peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all"></div>
                </div>
              </label>
              <div>
                <p className="font-medium text-slate-700 mb-2">Session Timeout (minutes)</p>
                <input
                  type="number"
                  className="w-full px-4 py-2 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-300"
                  value={security.sessionTimeout}
                  onChange={(e) => setSecurity({...security, sessionTimeout: e.target.value})}
                />
              </div>
              <button className="w-full py-2 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 transition flex items-center justify-center gap-2">
                <Lock className="w-4 h-4" /> Change Password
              </button>
            </div>
          </div>

          {/* Profile Section */}
          <div id="profile" className="bg-white rounded-2xl p-6 shadow-soft border border-white/50">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-cyan-50 rounded-xl">
                <User className="w-5 h-5 text-cyan-600" />
              </div>
              <h2 className="text-xl font-bold text-slate-800">Profile Information</h2>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Full Name</label>
                <input type="text" defaultValue="John Doe" className="w-full px-4 py-2 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-300" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Email Address</label>
                <input type="email" defaultValue="john.doe@fraudshield.com" className="w-full px-4 py-2 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-300" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Role</label>
                <input type="text" defaultValue="Security Administrator" disabled className="w-full px-4 py-2 border border-slate-200 rounded-xl bg-slate-50 text-slate-500" />
              </div>
            </div>
          </div>

          {/* API & Integrations */}
          <div id="api" className="bg-white rounded-2xl p-6 shadow-soft border border-white/50">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-purple-50 rounded-xl">
                <Globe className="w-5 h-5 text-purple-600" />
              </div>
              <h2 className="text-xl font-bold text-slate-800">API & Integrations</h2>
            </div>
            <div className="space-y-4">
              <div className="flex justify-between items-center p-4 bg-slate-50 rounded-xl">
                <div>
                  <p className="font-medium text-slate-700">API Key</p>
                  <p className="text-xs text-slate-400 font-mono">fs_live_xxxxxxxxxxxxx</p>
                </div>
                <button className="px-3 py-1.5 text-sm border border-slate-300 rounded-lg hover:bg-white transition">
                  Regenerate
                </button>
              </div>
              <button className="w-full py-2 border border-slate-200 rounded-xl text-slate-700 font-medium hover:bg-slate-50 transition flex items-center justify-center gap-2">
                <RefreshCw className="w-4 h-4" /> Generate New API Key
              </button>
            </div>
          </div>

          {/* Data Management */}
          <div id="data" className="bg-white rounded-2xl p-6 shadow-soft border border-white/50">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-yellow-50 rounded-xl">
                <Database className="w-5 h-5 text-yellow-600" />
              </div>
              <h2 className="text-xl font-bold text-slate-800">Data Management</h2>
            </div>
            <div className="space-y-3">
              <button className="w-full py-2 border border-slate-200 rounded-xl text-slate-700 font-medium hover:bg-slate-50 transition">
                Export All Data (CSV)
              </button>
              <button className="w-full py-2 border border-red-200 rounded-xl text-red-600 font-medium hover:bg-red-50 transition flex items-center justify-center gap-2">
                <AlertTriangle className="w-4 h-4" /> Clear Audit Logs
              </button>
            </div>
          </div>

          {/* Save Button */}
          <div className="flex justify-end">
            <button className="px-6 py-2.5 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 transition flex items-center gap-2 shadow-sm">
              <Save className="w-4 h-4" /> Save All Changes
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Settings