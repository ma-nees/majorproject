import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Navbar from './components/Navbar'
import Dashboard from './pages/Dashboard'
import Alerts from './pages/Alerts'
import Analytics from './pages/Analytics'
import Transactions from './pages/Transactions'
import RiskMonitor from './pages/RiskMonitor'
import Settings from './pages/Settings'     // ← import Settings

function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen overflow-hidden">
        <Sidebar />
        <div className="flex-1 flex flex-col overflow-hidden">
          <Navbar />
          <main className="flex-1 overflow-y-auto p-6 md:p-8">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/transactions" element={<Transactions />} />
              <Route path="/risk-monitor" element={<RiskMonitor />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/alerts" element={<Alerts />} />
              <Route path="/settings" element={<Settings />} />  {/* ← add this */}
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  )
}

export default App