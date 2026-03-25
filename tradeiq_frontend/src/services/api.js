import axios from 'axios'

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.PROD
    ? 'https://tradeiq-5.onrender.com/api'
    : 'http://localhost:8000/api')
const AUTH_STATE_EVENT = 'tradeiq-auth-changed'

const emitAuthStateChange = () => {
  window.dispatchEvent(new Event(AUTH_STATE_EVENT))
}

const normalizeAuthResponse = (payload) => {
  const tokens = payload?.tokens || {}

  return {
    ...payload,
    access_token: payload?.access_token || tokens.access || '',
    refresh_token: payload?.refresh_token || tokens.refresh || '',
    user: payload?.user || null,
  }
}

const normalizeHistoryPoint = (point) => {
  const date = point?.date || point?.Date || ''
  const open = Number(point?.open ?? point?.Open ?? 0)
  const high = Number(point?.high ?? point?.High ?? 0)
  const low = Number(point?.low ?? point?.Low ?? 0)
  const close = Number(point?.close ?? point?.Close ?? 0)
  const volume = Number(point?.volume ?? point?.Volume ?? 0)

  return {
    date,
    Date: date,
    open,
    Open: open,
    high,
    High: high,
    low,
    Low: low,
    close,
    Close: close,
    volume,
    Volume: volume,
  }
}

const normalizeHistoryResponse = (payload) => {
  const rows = Array.isArray(payload?.history)
    ? payload.history
    : Array.isArray(payload?.data)
    ? payload.data
    : []
  const history = rows.map(normalizeHistoryPoint)

  return {
    ...payload,
    history,
    data: history,
  }
}

const normalizePredictionResponse = (payload) => {
  const recommendation = payload?.recommendation || 'HOLD'
  const trend = payload?.trend || 'Sideways'
  const currentPrice =
    payload?.current_price == null ? payload?.current_price : Number(payload.current_price)
  const predictedPrice =
    payload?.predicted_price == null ? payload?.predicted_price : Number(payload.predicted_price)
  const changePercent =
    payload?.change_percent == null
      ? (currentPrice ? ((predictedPrice - currentPrice) / currentPrice) * 100 : 0)
      : Number(payload.change_percent)
  const confidence = (payload?.confidence || 'LOW').toUpperCase()
  const isReliable = payload?.is_reliable !== false
  const warning = payload?.warning || (!isReliable ? 'Unreliable Prediction' : '')

  return {
    ...payload,
    trend,
    recommendation,
    current_price: currentPrice,
    predicted_price: predictedPrice,
    change_percent: changePercent,
    confidence,
    is_reliable: isReliable,
    warning,
  }
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add token to requests if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Handle token refresh and auth errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      authHelpers.clearAuthData()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

/**
 * Authentication APIs
 */
export const authAPI = {
  register: async (userData) => {
    const response = await api.post('/auth/register/', userData)
    return normalizeAuthResponse(response.data)
  },

  login: async (credentials) => {
    const response = await api.post('/auth/login/', credentials)
    return normalizeAuthResponse(response.data)
  },

  getProfile: async () => {
    const response = await api.get('/auth/profile/')
    return response.data
  },

  updateProfile: async (data) => {
    const response = await api.put('/auth/profile/', data)
    return response.data
  }
}

/**
 * Authentication Helper Functions
 */
export const authHelpers = {
  getToken: () => localStorage.getItem('accessToken'),

  getUserRole: () => localStorage.getItem('userRole'),

  getUsername: () => localStorage.getItem('username'),

  isAuthenticated: () => !!localStorage.getItem('accessToken'),

  setAuthData: (token, role, username) => {
    localStorage.setItem('accessToken', token)
    localStorage.setItem('userRole', role)
    if (username) {
      localStorage.setItem('username', username)
    }
    emitAuthStateChange()
  },

  clearAuthData: () => {
    localStorage.removeItem('accessToken')
    localStorage.removeItem('userRole')
    localStorage.removeItem('username')
    emitAuthStateChange()
  },

  subscribe: (listener) => {
    window.addEventListener(AUTH_STATE_EVENT, listener)
    window.addEventListener('storage', listener)

    return () => {
      window.removeEventListener(AUTH_STATE_EVENT, listener)
      window.removeEventListener('storage', listener)
    }
  },

  logout: () => {
    authHelpers.clearAuthData()
    window.location.href = '/login'
  }
}

/**
 * Prediction APIs
 */
export const predictionAPI = {
  getHistorical: async (symbol) => {
    const response = await api.get('/stock/', {
      params: { symbol, period: '5y' },
    })
    return normalizeHistoryResponse(response.data)
  },

  getLivePrice: async (symbol) => {
    const response = await api.get('/stock/', {
      params: { symbol, period: '5d' },
    })
    const normalized = normalizeHistoryResponse(response.data)
    const latest = normalized.history[normalized.history.length - 1]

    return {
      symbol: normalized.symbol || symbol.toUpperCase(),
      price: latest?.close ?? null,
    }
  },

  predict: async (payload) => {
    const response = await api.post('/predict/', payload)
    return normalizePredictionResponse(response.data)
  }
}


/**
 * Admin APIs
 */
export const adminAPI = {
  getUsers: async () => {
    const response = await api.get('/admin/users/')
    return response.data
  },

  updateUser: async (userId, data) => {
    const response = await api.patch(`/admin/users/${userId}/`, data)
    return response.data
  },

  getDatasets: async () => {
    const response = await api.get('/admin/datasets/')
    return response.data
  },

  uploadDataset: async (formData) => {
    const response = await api.post('/admin/datasets/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  },

  retrainModel: async (data) => {
    const response = await api.post('/admin/retrain/', data)
    return response.data
  },

  getModelHistory: async () => {
    const response = await api.get('/admin/models/')
    return response.data
  },

  getActivityLogs: async () => {
    const response = await api.get('/admin/logs/')
    return response.data
  },

  getPredictions: async () => {
    const response = await api.get('/admin/predictions/')
    return response.data
  },

  getDashboardStats: async () => {
    const response = await api.get('/admin/dashboard/')
    return response.data
  },

  fetchStockData: async (symbol, period = '1mo') => {
    const response = await api.get('/admin/stock-fetch/', {
      params: { symbol, period }
    })
    return response.data
  }
}

/**
 * Report APIs
 */
export const reportAPI = {
  generatePDF: async (predictionId) => {
    const response = await api.get(`/reports/pdf/?prediction_id=${predictionId}`, {
      responseType: 'blob'
    })
    return response.data
  }
}

/**
 * Portfolio APIs
 */
export const portfolioAPI = {
  addEntry: async (entry) => {
    const response = await api.post('/portfolio/add/', entry)
    return response.data
  },
  getEntries: async () => {
    const response = await api.get('/portfolio/')
    return response.data
  }
}

/**
 * Legacy APIs (for backward compatibility)
 */
export const predictPrice = async (data) => {
  return predictionAPI.predict(data)
}

export const getHistoricalData = async () => {
  const response = await predictionAPI.getHistorical('AAPL')
  return response.history
}

export const healthCheck = async () => {
  const response = await api.get('/health/')
  return response.data
}

export default api
