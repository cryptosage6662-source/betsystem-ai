const API_BASE_URL = process.env.VITE_API_URL || 'http://localhost:8000';

class APIClient {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.token = localStorage.getItem('auth_token');
  }

  setToken(token) {
    this.token = token;
    localStorage.setItem('auth_token', token);
  }

  getToken() {
    return this.token;
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('auth_token');
  }

  getHeaders() {
    const headers = {
      'Content-Type': 'application/json',
    };
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    return headers;
  }

  async login(username, password) {
    try {
      const response = await fetch(`${this.baseURL}/auth/login`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify({ username, password }),
      });
      
      if (!response.ok) {
        throw new Error('Login failed');
      }
      
      const data = await response.json();
      this.setToken(data.access_token);
      return data;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }

  async logout() {
    this.clearToken();
  }

  async getBankroll() {
    try {
      const response = await fetch(`${this.baseURL}/user/bankroll`, {
        method: 'GET',
        headers: this.getHeaders(),
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch bankroll');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Bankroll fetch error:', error);
      throw error;
    }
  }

  async getBetHistory() {
    try {
      const response = await fetch(`${this.baseURL}/bets/history`, {
        method: 'GET',
        headers: this.getHeaders(),
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch bet history');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Bet history fetch error:', error);
      throw error;
    }
  }

  async getBetSuggestion(matchData) {
    try {
      const response = await fetch(`${this.baseURL}/ai/suggest-bet`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(matchData),
      });
      
      if (!response.ok) {
        throw new Error('Failed to get bet suggestion');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Bet suggestion error:', error);
      throw error;
    }
  }

  async placeBet(betData) {
    try {
      const response = await fetch(`${this.baseURL}/bets/place`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(betData),
      });
      
      if (!response.ok) {
        throw new Error('Failed to place bet');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Place bet error:', error);
      throw error;
    }
  }
}

export default new APIClient();
