import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { userAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function Auth() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [username, setUsername] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await userAPI.register(email, password, username);
      
      // Auto-login after registration
      const userData = {
        id: response.user_id,
        email: response.email,
        username: username,
        bankroll: 1000,
        created_at: new Date().toISOString(),
      };
      
      login(userData);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Email may already exist.');
      console.error('Registration error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // For now, we'll use a simple email-based login
      // In production, this would verify credentials on backend
      
      // TODO: Implement proper JWT authentication
      const userData = {
        id: 'demo_' + Date.now(),
        email: email,
        username: email.split('@')[0],
        bankroll: 1000,
        created_at: new Date().toISOString(),
      };
      
      login(userData);
      navigate('/dashboard');
    } catch (err) {
      setError('Login failed');
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = () => {
    const demoUser = {
      id: 'demo_user_123',
      email: 'demo@betsystem.ai',
      username: 'DemoUser',
      bankroll: 5000,
      created_at: new Date().toISOString(),
    };
    login(demoUser);
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">🎰 BetSystem AI</h1>
          <p className="text-slate-400 text-lg">Sports Betting Strategy Platform</p>
        </div>

        {/* Auth Card */}
        <div className="bg-slate-800 rounded-lg shadow-2xl p-8 border border-slate-700">
          {/* Disclaimer */}
          <div className="bg-amber-900/20 border border-amber-700/50 rounded-lg p-4 mb-6">
            <p className="text-amber-100 text-sm">
              ⚠️ <strong>Educational Only:</strong> This platform provides betting strategy analysis for educational purposes. 
              Betting involves financial risk. Results are not guaranteed. You must be 18+ to use this application.
            </p>
          </div>

          {/* Tabs */}
          <div className="flex gap-4 mb-6">
            <button
              onClick={() => {
                setIsLogin(true);
                setError('');
              }}
              className={`flex-1 py-2 px-4 rounded-lg font-semibold transition-colors ${
                isLogin
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              Login
            </button>
            <button
              onClick={() => {
                setIsLogin(false);
                setError('');
              }}
              className={`flex-1 py-2 px-4 rounded-lg font-semibold transition-colors ${
                !isLogin
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              Register
            </button>
          </div>

          {/* Error Alert */}
          {error && (
            <div className="bg-red-500/10 border border-red-500/50 text-red-200 px-4 py-3 rounded-lg mb-4 text-sm">
              {error}
            </div>
          )}

          {/* Form */}
          <form onSubmit={isLogin ? handleLogin : handleRegister} className="space-y-4 mb-6">
            {!isLogin && (
              <div>
                <label className="block text-slate-300 text-sm font-medium mb-2">Username</label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Your username"
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                  required={!isLogin}
                />
              </div>
            )}

            <div>
              <label className="block text-slate-300 text-sm font-medium mb-2">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-slate-300 text-sm font-medium mb-2">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Please wait...' : (isLogin ? 'Login' : 'Create Account')}
            </button>
          </form>

          {/* Demo Login */}
          <div className="border-t border-slate-700 pt-4">
            <button
              onClick={handleDemoLogin}
              className="w-full bg-slate-700 hover:bg-slate-600 text-slate-100 font-semibold py-2 px-4 rounded-lg transition-colors"
            >
              📊 Try Demo Account ($5000 starting bankroll)
            </button>
          </div>
        </div>

        {/* Footer */}
        <p className="text-center text-slate-500 text-sm mt-6">
          Gamble responsibly. Get help: <a href="https://www.gamcare.org.uk" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline">GamCare.org</a>
        </p>
      </div>
    </div>
  );
}
