import React, { useState, useEffect } from 'react'
import Bankroll from '../components/Bankroll'
import BetHistory from '../components/BetHistory'
import BetSuggestion from './BetSuggestion'

export default function Dashboard({ onLogout }) {
  const [bankroll, setBankroll] = useState(null)
  const [loading, setLoading] = useState(true)
  const [currentPage, setCurrentPage] = useState('dashboard')

  useEffect(() => {
    // Simulate fetch bankroll
    setBankroll({
      current: 1000,
      starting: 1000,
      roi: 0,
      daily_loss_limit: 200,
      max_stake_percent: 5
    })
    setLoading(false)
  }, [])

  if (loading) {
    return <div className="flex items-center justify-center h-screen">Loading...</div>
  }

  return (
    <div className="bg-gradient-to-br from-gray-900 to-gray-800 min-h-screen text-white">
      {/* Header */}
      <nav className="bg-gray-900 border-b border-gray-700 px-6 py-4 flex justify-between items-center">
        <h1 className="text-2xl font-bold">🎰 BetSystem AI</h1>
        <button
          onClick={onLogout}
          className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded"
        >
          Logout
        </button>
      </nav>

      {/* Navigation */}
      <div className="bg-gray-800 border-b border-gray-700 px-6 py-3 flex gap-4">
        <button
          onClick={() => setCurrentPage('dashboard')}
          className={`px-4 py-2 rounded ${currentPage === 'dashboard' ? 'bg-blue-600' : 'bg-gray-700'}`}
        >
          📊 Dashboard
        </button>
        <button
          onClick={() => setCurrentPage('suggestion')}
          className={`px-4 py-2 rounded ${currentPage === 'suggestion' ? 'bg-blue-600' : 'bg-gray-700'}`}
        >
          🎲 Get Suggestion
        </button>
        <button
          onClick={() => setCurrentPage('history')}
          className={`px-4 py-2 rounded ${currentPage === 'history' ? 'bg-blue-600' : 'bg-gray-700'}`}
        >
          📜 History
        </button>
      </div>

      {/* Content */}
      <div className="p-6 max-w-7xl mx-auto">
        {currentPage === 'dashboard' && (
          <div>
            <Bankroll data={bankroll} />
            <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
                <p className="text-gray-400">Today's P&L</p>
                <p className="text-2xl font-bold">$0.00</p>
              </div>
              <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
                <p className="text-gray-400">Win Rate</p>
                <p className="text-2xl font-bold">0%</p>
              </div>
              <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
                <p className="text-gray-400">ROI</p>
                <p className="text-2xl font-bold">0%</p>
              </div>
            </div>
          </div>
        )}

        {currentPage === 'suggestion' && <BetSuggestion />}

        {currentPage === 'history' && <BetHistory />}
      </div>

      {/* Disclaimer */}
      <div className="bg-yellow-900 border-t border-yellow-700 px-6 py-4 text-yellow-100 text-sm">
        ⚠️ <strong>Disclaimer:</strong> BetSystem AI is for educational purposes only. Betting involves risk of financial loss. Results are not guaranteed. You must be 18+ to use this application.
      </div>
    </div>
  )
}
