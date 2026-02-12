import React from 'react'

export default function Bankroll({ data }) {
  if (!data) return <div>Loading...</div>

  const pnl = data.current - data.starting
  const roiPercent = ((pnl / data.starting) * 100).toFixed(2)

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div className="bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg p-6 border border-blue-500">
        <p className="text-blue-100 text-sm">Starting Bankroll</p>
        <p className="text-3xl font-bold">${data.starting.toFixed(2)}</p>
      </div>

      <div className="bg-gradient-to-br from-green-600 to-green-700 rounded-lg p-6 border border-green-500">
        <p className="text-green-100 text-sm">Current Bankroll</p>
        <p className="text-3xl font-bold">${data.current.toFixed(2)}</p>
      </div>

      <div className={`bg-gradient-to-br rounded-lg p-6 border ${pnl >= 0 ? 'from-emerald-600 to-emerald-700 border-emerald-500' : 'from-red-600 to-red-700 border-red-500'}`}>
        <p className={`text-sm ${pnl >= 0 ? 'text-emerald-100' : 'text-red-100'}`}>Total P&L</p>
        <p className="text-3xl font-bold">${pnl.toFixed(2)}</p>
      </div>

      <div className="bg-gradient-to-br from-purple-600 to-purple-700 rounded-lg p-6 border border-purple-500">
        <p className="text-purple-100 text-sm">ROI</p>
        <p className="text-3xl font-bold">{roiPercent}%</p>
      </div>
    </div>
  )
}
