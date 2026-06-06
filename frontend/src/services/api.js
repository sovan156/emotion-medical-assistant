import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth APIs
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
};

// Chat APIs
export const chatAPI = {
  sendMessage: (data) => api.post('/chat/message', data),
  getHistory: (conversationId) => api.get(`/chat/history/${conversationId}`),
  listConversations: () => api.get('/chat/conversations'),
};

// Voice APIs
export const voiceAPI = {
  transcribe: (formData) =>
    api.post('/voice/transcribe', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
};

// Report APIs
export const reportAPI = {
  upload: (formData) =>
    api.post('/report/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  getReport: (reportId) => api.get(`/report/${reportId}`),
  listReports: () => api.get('/report/'),
};

// Emotion APIs
export const emotionAPI = {
  analyze: (data) => api.post('/emotion/analyze', data),
};

export default api;
