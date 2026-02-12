import React, { useState, useEffect } from 'react'

export default function BetHistory() {
  const [bets, setBets] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Simulate fetch bet history
    setBets([
      {
        id: '1',
        match: 'Arsenal vs Liverpool',
        odds: 1.92,
        stake: 50,
        result: 'win',
        pnl: 46,
        date: '2026-02-12'
      },
      {
        id: '2',
        match: 'Chelsea vs Man City',
        odds: 2.10,
        stake: 40,
        result: 'loss',
        pnl: -40,
        date: '2026-02-11'
      }
    ])
    setLoading(false)
  }, [])

  if (loading) return <div>Loading...</div>

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
      <h2 className="text-xl font-bold mb-4">📜 Bet History</h2>

      {bets.length === 0 ? (
        <p className="text-gray-400">No bets yet</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="border-b border-gray-700">
              <tr className="text-gray-400">
                <th className="text-left py-3">Match</th>
                <th className="text-left py-3">Odds</th>
                <th className="text-left py-3">Stake</th>
                <th className="text-left py-3">Result</th>
                <th className="text-left py-3">P&L</th>
                <th className="text-left py-3">Date</th>
              </tr>
            </thead>
            <tbody>
              {bets.map(bet => (
                <tr key={bet.id} className="border-b border-gray-700 hover:bg-gray-700">
                  <td className="py-3">{bet.match}</td>
                  <td>{bet.odds}</td>
                  <td>${bet.stake}</td>
                  <td>
                    <span className={`px-2 py-1 rounded text-xs font-semibold ${
                      bet.result === 'win' ? 'bg-green-900 text-green-100' : 'bg-red-900 text-red-100'
                    }`}>
                      {bet.result.toUpperCase()}
                    </span>
                  </td>
                  <td className={bet.pnl >= 0 ? 'text-green-400' : 'text-red-400'}>
                    {bet.pnl >= 0 ? '+' : ''}{bet.pnl}
                  </td>
                  <td>{bet.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
