import React, { useState } from 'react'
import APIClient from '../api/client'

export default function BetSuggestion() {
  const [formData, setFormData] = useState({
    sport: 'Football',
    team_a: '',
    team_b: '',
    odds: '',
    market: 'Over 2.5 Goals',
    date: new Date().toISOString().split('T')[0]
  })
  const [suggestion, setSuggestion] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    
    try {
      const response = await fetch('http://localhost:8000/suggest-bet/user_1', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      })
      
      if (!response.ok) throw new Error('Failed to get suggestion')
      
      const data = await response.json()
      setSuggestion(data)
    } catch (err) {
      setError('Failed to get bet suggestion. Make sure FastAPI backend is running.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <h2 className="text-xl font-bold mb-4">📍 Get Bet Suggestion</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Sport</label>
              <select
                name="sport"
                value={formData.sport}
                onChange={handleChange}
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
              >
                <option>Football</option>
                <option>Basketball</option>
                <option>Tennis</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Team A</label>
              <input
                type="text"
                name="team_a"
                value={formData.team_a}
                onChange={handleChange}
                placeholder="e.g., Arsenal"
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Team B</label>
              <input
                type="text"
                name="team_b"
                value={formData.team_b}
                onChange={handleChange}
                placeholder="e.g., Liverpool"
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Odds</label>
              <input
                type="number"
                name="odds"
                value={formData.odds}
                onChange={handleChange}
                placeholder="e.g., 1.92"
                step="0.01"
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Market</label>
              <input
                type="text"
                name="market"
                value={formData.market}
                onChange={handleChange}
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Date</label>
              <input
                type="date"
                name="date"
                value={formData.date}
                onChange={handleChange}
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 px-4 py-3 rounded font-semibold"
          >
            {loading ? 'Getting suggestion...' : '🎲 Get Suggestion'}
          </button>
        </form>

        {error && (
          <div className="mt-4 p-3 bg-red-900 border border-red-700 text-red-100 rounded">
            {error}
          </div>
        )}
      </div>

      {suggestion && (
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
          <h3 className="text-xl font-bold mb-4">✅ Suggestion</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-gray-700 rounded p-3">
              <p className="text-gray-400">Strategy</p>
              <p className="text-lg font-semibold">{suggestion.strategy || 'Kelly Criterion'}</p>
            </div>
            <div className="bg-gray-700 rounded p-3">
              <p className="text-gray-400">Confidence</p>
              <p className="text-lg font-semibold">{(suggestion.confidence * 100).toFixed(1)}%</p>
            </div>
            <div className="bg-gray-700 rounded p-3">
              <p className="text-gray-400">Expected Value</p>
              <p className="text-lg font-semibold">{(suggestion.expected_value * 100).toFixed(2)}%</p>
            </div>
            <div className="bg-gray-700 rounded p-3">
              <p className="text-gray-400">Recommended Stake</p>
              <p className="text-lg font-semibold">${suggestion.recommended_stake?.toFixed(2) || '0.00'}</p>
            </div>
            <div className="bg-gray-700 rounded p-3">
              <p className="text-gray-400">Risk Level</p>
              <p className="text-lg font-semibold">{suggestion.risk_level || 'Medium'}</p>
            </div>
          </div>

          {suggestion.explanation && (
            <div className="mt-4 p-3 bg-gray-700 rounded">
              <p className="font-semibold mb-2">Reasoning:</p>
              <ul className="text-sm space-y-1 text-gray-300">
                {suggestion.explanation.map((point, i) => (
                  <li key={i}>• {point}</li>
                ))}
              </ul>
            </div>
          )}

          <button className="mt-4 w-full bg-green-600 hover:bg-green-700 px-4 py-2 rounded font-semibold">
            💰 Place Bet
          </button>
        </div>
      )}
    </div>
  )
}
