/**
 * API Client for FraudShield Platform
 * Handles all backend communication with authentication, error handling, and request interceptors
 */

// Use environment variable for API base URL (fallback to localhost for development)
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

// Token storage key
const TOKEN_KEY = 'fraudshield_access_token'

/**
 * Core fetch wrapper with automatic JSON parsing and error handling
 */
class ApiClient {
  constructor() {
    this.baseURL = API_BASE_URL
    this.defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    }
  }

  /**
   * Get stored authentication token
   */
  getToken() {
    return localStorage.getItem(TOKEN_KEY)
  }

  /**
   * Set authentication token (call after login)
   */
  setToken(token) {
    if (token) {
      localStorage.setItem(TOKEN_KEY, token)
    } else {
      localStorage.removeItem(TOKEN_KEY)
    }
  }

  /**
   * Clear token on logout
   */
  clearToken() {
    localStorage.removeItem(TOKEN_KEY)
  }

  /**
   * Build request headers with auth if available
   */
  getHeaders(includeAuth = true) {
    const headers = { ...this.defaultHeaders }
    if (includeAuth) {
      const token = this.getToken()
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }
    }
    return headers
  }

  /**
   * Handle API response, parse JSON, and throw errors for non-2xx statuses
   */
  async handleResponse(response) {
    let data
    const contentType = response.headers.get('content-type')
    if (contentType && contentType.includes('application/json')) {
      data = await response.json()
    } else {
      data = await response.text()
    }

    if (!response.ok) {
      const error = new Error(data.message || data.detail || `HTTP ${response.status}: ${response.statusText}`)
      error.status = response.status
      error.data = data
      throw error
    }

    return data
  }

  /**
   * Generic request method
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    const config = {
      ...options,
      headers: {
        ...this.getHeaders(options.includeAuth !== false),
        ...options.headers,
      },
    }

    try {
      const response = await fetch(url, config)
      return await this.handleResponse(response)
    } catch (error) {
      console.error(`API Error [${endpoint}]:`, error)
      throw error
    }
  }

  // ========== Transaction Endpoints ==========

  /**
   * Submit a single transaction for fraud detection
   * @param {Object} transactionData - Transaction details
   * @returns {Promise<Object>} Fraud prediction result
   */
  async predictTransaction(transactionData) {
    return this.request('/predict', {
      method: 'POST',
      body: JSON.stringify(transactionData),
    })
  }

  /**
   * Batch predict multiple transactions
   * @param {Array<Object>} transactions - Array of transaction objects
   * @returns {Promise<Array<Object>>} Array of prediction results
   */
  async batchPredict(transactions) {
    return this.request('/predict/batch', {
      method: 'POST',
      body: JSON.stringify({ transactions }),
    })
  }

  /**
   * Get transaction by ID with fraud analysis
   * @param {string} transactionId
   * @returns {Promise<Object>} Transaction details + risk score
   */
  async getTransaction(transactionId) {
    return this.request(`/transactions/${transactionId}`)
  }

  /**
   * List recent transactions with pagination and filters
   * @param {Object} params - { page, limit, status, risk_level, from_date, to_date }
   */
  async listTransactions(params = {}) {
    const queryString = new URLSearchParams(params).toString()
    return this.request(`/transactions${queryString ? `?${queryString}` : ''}`)
  }

  // ========== Risk & Fraud Endpoints ==========

  /**
   * Get overall risk score for dashboard
   */
  async getRiskScore() {
    return this.request('/risk/overall')
  }

  /**
   * Get fraud alerts (paginated)
   * @param {Object} params - { page, limit, severity, status }
   */
  async getAlerts(params = {}) {
    const queryString = new URLSearchParams(params).toString()
    return this.request(`/alerts${queryString ? `?${queryString}` : ''}`)
  }

  /**
   * Update alert status (resolve, investigate, etc.)
   * @param {string} alertId
   * @param {string} status - 'new', 'investigating', 'resolved'
   */
  async updateAlertStatus(alertId, status) {
    return this.request(`/alerts/${alertId}`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    })
  }

  // ========== Analytics Endpoints ==========

  /**
   * Get fraud trends over time
   * @param {string} period - 'day', 'week', 'month', 'year'
   * @param {string} from - ISO date
   * @param {string} to - ISO date
   */
  async getFraudTrends(period = 'month', from = null, to = null) {
    const params = { period }
    if (from) params.from = from
    if (to) params.to = to
    const queryString = new URLSearchParams(params).toString()
    return this.request(`/analytics/trends${queryString ? `?${queryString}` : ''}`)
  }

  /**
   * Get risk distribution by category
   */
  async getRiskDistribution() {
    return this.request('/analytics/risk-distribution')
  }

  /**
   * Get fraud by category / type breakdown
   */
  async getFraudByCategory() {
    return this.request('/analytics/fraud-categories')
  }

  /**
   * Get hourly risk pattern
   */
  async getHourlyRiskPattern() {
    return this.request('/analytics/hourly-risk')
  }

  /**
   * Get dashboard summary stats (cards)
   */
  async getDashboardStats() {
    return this.request('/dashboard/stats')
  }

  // ========== Behavioral Biometrics Endpoints ==========

  /**
   * Submit behavioral data for session
   * @param {Object} behavioralData - { session_id, keystrokes, mouse_movements, etc. }
   */
  async submitBehavioralData(behavioralData) {
    return this.request('/behavioral/analyze', {
      method: 'POST',
      body: JSON.stringify(behavioralData),
    })
  }

  /**
   * Get behavioral risk score for a user/session
   * @param {string} sessionId
   */
  async getBehavioralRisk(sessionId) {
    return this.request(`/behavioral/risk/${sessionId}`)
  }

  // ========== Model Management (Admin) ==========

  /**
   * Trigger model retraining
   */
  async retrainModel() {
    return this.request('/admin/retrain', {
      method: 'POST',
    })
  }

  /**
   * Get model performance metrics
   */
  async getModelMetrics() {
    return this.request('/admin/model-metrics')
  }

  // ========== Authentication ==========

  /**
   * Login and obtain access token
   * @param {string} username
   * @param {string} password
   */
  async login(username, password) {
    // Using form-urlencoded for OAuth2 style
    const formData = new URLSearchParams()
    formData.append('username', username)
    formData.append('password', password)

    const response = await fetch(`${this.baseURL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    })

    const data = await this.handleResponse(response)
    if (data.access_token) {
      this.setToken(data.access_token)
    }
    return data
  }

  /**
   * Logout – clear token
   */
  logout() {
    this.clearToken()
  }

  /**
   * Get current user profile
   */
  async getCurrentUser() {
    return this.request('/auth/me')
  }
}

// Export singleton instance
export const apiClient = new ApiClient()

// Also export individual functions for convenience (optional)
export const {
  predictTransaction,
  batchPredict,
  getTransaction,
  listTransactions,
  getRiskScore,
  getAlerts,
  updateAlertStatus,
  getFraudTrends,
  getRiskDistribution,
  getFraudByCategory,
  getHourlyRiskPattern,
  getDashboardStats,
  submitBehavioralData,
  getBehavioralRisk,
  retrainModel,
  getModelMetrics,
  login,
  logout,
  getCurrentUser,
} = apiClient

export default apiClient