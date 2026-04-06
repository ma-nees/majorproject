import React, { useState } from 'react'
import { Search, Bell, User, ChevronDown } from 'lucide-react'

const Navbar = () => {
  const [searchFocused, setSearchFocused] = useState(false)

  return (
    <header className="sticky top-0 z-10 bg-white/60 backdrop-blur-md border-b border-indigo-50/50 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Mobile menu button - could be added, but for simplicity we keep search */}
        <div className="flex items-center gap-4 flex-1 max-w-md">
          <div className={`
            relative flex items-center w-full transition-all duration-300
            ${searchFocused ? 'scale-[1.02]' : ''}
          `}>
            <Search className="absolute left-3 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search transactions, alerts..."
              className="w-full pl-10 pr-4 py-2.5 bg-slate-50/80 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-300 focus:border-transparent text-sm transition-all"
              onFocus={() => setSearchFocused(true)}
              onBlur={() => setSearchFocused(false)}
            />
          </div>
        </div>

        <div className="flex items-center gap-5">
          <button className="relative p-2 rounded-full hover:bg-indigo-50 transition-colors group">
            <Bell className="w-5 h-5 text-slate-600 group-hover:text-indigo-600" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full ring-2 ring-white"></span>
          </button>
          
          <div className="flex items-center gap-3 pl-3 border-l border-slate-200">
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-indigo-500 to-cyan-500 flex items-center justify-center text-white font-semibold shadow-md">
              JD
            </div>
            <div className="hidden sm:block">
              <p className="text-sm font-semibold text-slate-700">John Doe</p>
              <p className="text-xs text-slate-500">Security Admin</p>
            </div>
            <ChevronDown className="w-4 h-4 text-slate-400" />
          </div>
        </div>
      </div>
    </header>
  )
}

export default Navbar