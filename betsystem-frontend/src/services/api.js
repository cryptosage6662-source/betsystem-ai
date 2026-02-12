import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ==================== USER ENDPOINTS ====================

export const userAPI = {
  register: async (email, password, username) => {
    const response = await api.post('/users/register', {
      email,
      password,
      username,
    });
    return response.data;
  },

  getProfile: async (userId) => {
    const response = await api.get(`/users/${userId}`);
    return response.data;
  },
};

// ==================== BANKROLL ENDPOINTS ====================

export const bankrollAPI = {
  update: async (userId, bankrollData) => {
    const response = await api.put(`/bankroll/${userId}`, bankrollData);
    return response.data;
  },
};

// ==================== MATCH ENDPOINTS ====================

export const matchAPI = {
  create: async (userId, matchData) => {
    const response = await api.post(`/matches/${userId}`, matchData);
    return response.data;
  },

  list: async (userId) => {
    const response = await api.get(`/matches/${userId}`);
    return response.data;
  },
};

// ==================== BET ENDPOINTS ====================

export const betAPI = {
  suggestBet: async (userId, matchData) => {
    const response = await api.post(`/suggest-bet/${userId}`, matchData);
    return response.data;
  },

  placeBet: async (userId, betData) => {
    const response = await api.post(`/bets/${userId}`, betData);
    return response.data;
  },

  listBets: async (userId) => {
    const response = await api.get(`/bets/${userId}`);
    return response.data;
  },
};

// ==================== ANALYTICS ENDPOINTS ====================

export const analyticsAPI = {
  getRoi: async (userId) => {
    const response = await api.get(`/analytics/${userId}/roi`);
    return response.data;
  },
};

export default api;
