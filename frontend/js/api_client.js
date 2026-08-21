/**
 * @file api_client.js
 * @description HTTP Client Wrapper using Fetch API with retry logic, JSDoc typing,
 * and seamless dynamic fallback mock state for robust offline / demo execution.
 */

/**
 * @typedef {Object} KPIAnalytics
 * @property {number} totalInteractions
 * @property {number} positivePercentage
 * @property {number} neutralPercentage
 * @property {number} negativePercentage
 * @property {number} predictiveNps
 * @property {string} npsStatus
 * @property {number} highRiskCount
 * @property {number} criticalRiskCount
 */

/**
 * @typedef {Object} SentimentPoint
 * @property {string} date
 * @property {number} positive
 * @property {number} neutral
 * @property {number} negative
 */

/**
 * @typedef {Object} FrictionDistribution
 * @property {number} customer_support
 * @property {number} billing_pricing
 * @property {number} product_reliability
 * @property {number} sla_delay
 * @property {number} feature_gap
 */

/**
 * @typedef {Object} ChurnRiskCase
 * @property {string} id
 * @property {string} customerName
 * @property {string} tier - Enterprise | Pro | Standard
 * @property {number} riskScore - 0 to 100
 * @property {string} emotion - frustration | anger | confusion | satisfied
 * @property {string} friction - customer_support | billing_pricing | product_reliability | sla_delay | feature_gap
 * @property {string} rawEvidence - Original text with PII
 * @property {string} maskedEvidence - Text with PII masked
 * @property {string} status - PENDING | IN_REVIEW | RESOLVED
 * @property {string} aiEngine - cloud_gemini | local_nlp
 * @property {Array<{factor: string, impact: number}>} scoreFactors
 * @property {string} timestamp
 * @property {string} [notes]
 */

class ApiClient {
  constructor(baseUrl = null) {
    if (baseUrl) {
      this.baseUrl = baseUrl;
    } else {
      const port = window.location.port;
      const isDifferentPort = port && port !== '8000' && port !== '';
      if (isDifferentPort) {
        this.baseUrl = `http://${window.location.hostname || 'localhost'}:8000/api`;
      } else {
        this.baseUrl = '/api';
      }
    }
    this.isOnline = true;
    this.maxRetries = 1;
    this.retryDelayMs = 800;

    // Zero-state clean fallback store (never injects synthetic or hardcoded numbers)
    this.mockState = {
      kpis: {
        totalInteractions: 0,
        positivePercentage: 0,
        neutralPercentage: 0,
        negativePercentage: 0,
        predictiveNps: 0,
        npsStatus: 'Saludable',
        highRiskCount: 0,
        criticalRiskCount: 0
      },
      sentimentTrend: [],
      frictionDistribution: {
        customer_support: 0,
        billing_pricing: 0,
        product_reliability: 0,
        sla_delay: 0,
        feature_gap: 0
      },
      highRiskCases: []
  }

  /**
   * Private helper to fetch with retry & mock fallback
   * @param {string} endpoint
   * @param {Object} options
   */
  async _request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    let lastError = null;

    for (let attempt = 0; attempt <= this.maxRetries; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000);

        const response = await fetch(url, {
          ...options,
          signal: controller.signal,
          headers: {
            'Content-Type': 'application/json',
            ...(options.headers || {})
          }
        });

        clearTimeout(timeoutId);

        if (response.ok) {
          this.isOnline = true;
          return await response.json();
        }

        const errJson = await response.json().catch(() => ({}));
        throw new Error(errJson.detail || errJson.message || `HTTP ${response.status}`);
      } catch (err) {
        lastError = err;
        if (attempt < this.maxRetries) {
          await new Promise(r => setTimeout(r, this.retryDelayMs));
        }
      }
    }

    // Server offline or endpoint unreachable -> Fallback smoothly to dynamic mock store
    this.isOnline = false;
    console.warn(`[API Client] Endpoint ${endpoint} unreachable (${lastError.message}). Using mock state.`);
    return this._handleMockFallback(endpoint, options);
  }

  /**
   * Mock fallback router for offline demonstration
   */
  _handleMockFallback(endpoint, options) {
    const method = (options.method || 'GET').toUpperCase();

    if (endpoint === '/analytics/kpis' && method === 'GET') {
      return Promise.resolve({ success: true, data: this.mockState.kpis });
    }

    if (endpoint === '/analytics/sentiment-trend' && method === 'GET') {
      return Promise.resolve({ success: true, data: this.mockState.sentimentTrend });
    }

    if (endpoint === '/analytics/friction-distribution' && method === 'GET') {
      return Promise.resolve({ success: true, data: this.mockState.frictionDistribution });
    }

    if (endpoint === '/churn/high-risk' && method === 'GET') {
      return Promise.resolve({ success: true, data: this.mockState.highRiskCases });
    }

    if (endpoint.startsWith('/alerts/') && method === 'PATCH') {
      const alertId = endpoint.split('/')[2];
      const payload = JSON.parse(options.body || '{}');
      const caseItem = this.mockState.highRiskCases.find(c => c.id === alertId);
      if (caseItem) {
        if (payload.status) caseItem.status = payload.status;
        if (payload.notes) caseItem.notes = payload.notes;
      }
      this._recalculateKPIs();
      return Promise.resolve({ success: true, data: caseItem });
    }

    if (endpoint === '/interactions' && method === 'POST') {
      const payload = JSON.parse(options.body || '{}');
      const simulatedResult = this._processSimulatedInteraction(payload);
      return Promise.resolve({ success: true, data: simulatedResult });
    }

    return Promise.reject(new Error(`Endpoint mock not implemented: ${endpoint}`));
  }

  /**
   * Internal simulation engine for live ingesting testbed messages
   */
  _processSimulatedInteraction(payload) {
    const text = (payload.text || '').toLowerCase();
    const customer = payload.customerName || 'Cliente de Prueba';
    const tier = payload.tier || 'Enterprise';

    let emotion = 'neutral';
    let friction = 'feature_gap';
    let riskScore = 15;
    let sentimentCategory = 'positive';
    let aiEngine = payload.aiEngine || 'cloud_gemini';

    if (text.includes('cancela') || text.includes('cobro') || text.includes('factura') || text.includes('precio') || text.includes('aumento')) {
      friction = 'billing_pricing';
      riskScore += 35;
    } else if (text.includes('soporte') || text.includes('atencion') || text.includes('resuelven') || text.includes('respuesta')) {
      friction = 'customer_support';
      riskScore += 30;
    } else if (text.includes('caido') || text.includes('falla') || text.includes('error') || text.includes('bug')) {
      friction = 'product_reliability';
      riskScore += 25;
    } else if (text.includes('dias') || text.includes('esperando') || text.includes('tarde')) {
      friction = 'sla_delay';
      riskScore += 20;
    }

    if (text.includes('cancelo') || text.includes('migrar') || text.includes('competencia') || text.includes('pesimo') || text.includes('frustrado')) {
      emotion = 'anger';
      riskScore += 40;
      sentimentCategory = 'negative';
    } else if (text.includes('malo') || text.includes('lento') || text.includes('no funciona') || text.includes('ironia') || text.includes('sarcasmo')) {
      emotion = 'frustration';
      riskScore += 25;
      sentimentCategory = 'negative';
    } else if (text.includes('excelente') || text.includes('bueno') || text.includes('fantastico') || text.includes('gracias')) {
      emotion = 'satisfied';
      riskScore = Math.max(5, riskScore - 30);
      sentimentCategory = 'positive';
    } else {
      sentimentCategory = 'neutral';
    }

    riskScore = Math.min(99, Math.max(5, riskScore));

    // Mask PII (Emails, Card Numbers, Amounts)
    const maskedText = payload.text
      .replace(/([a-zA-Z0-9._-]+)@([a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)/gi, (match, p1, p2) => `${p1.charAt(0)}***${p1.charAt(p1.length - 1)}@${p2}`)
      .replace(/\$?\d{3,6}\s?(usd|eur|cop)?/gi, '[Monto Enmascarado]');

    const newCase = {
      id: `ALT-${Math.floor(1000 + Math.random() * 9000)}`,
      customerName: customer,
      tier: tier,
      riskScore: riskScore,
      emotion: emotion,
      friction: friction,
      rawEvidence: payload.text,
      maskedEvidence: maskedText,
      status: riskScore >= 60 ? 'PENDING' : 'RESOLVED',
      aiEngine: aiEngine,
      scoreFactors: [
        { factor: `Emoción: ${emotion.toUpperCase()}`, impact: Math.floor(riskScore * 0.4) },
        { factor: `Fricción: ${friction.replace('_', ' ').toUpperCase()}`, impact: Math.floor(riskScore * 0.35) },
        { factor: `Tier del Cliente (${tier})`, impact: tier === 'Enterprise' ? 20 : 10 }
      ],
      timestamp: new Date().toISOString()
    };

    // Update Mock state
    this.mockState.highRiskCases.unshift(newCase);
    this.mockState.kpis.totalInteractions += 1;
    this.mockState.frictionDistribution[friction] = (this.mockState.frictionDistribution[friction] || 0) + 1;

    // Recalculate trend for today
    const todayTrend = this.mockState.sentimentTrend[this.mockState.sentimentTrend.length - 1];
    if (todayTrend) {
      if (sentimentCategory === 'positive') todayTrend.positive += 1;
      else if (sentimentCategory === 'negative') todayTrend.negative += 1;
      else todayTrend.neutral += 1;
    }

    this._recalculateKPIs();
    return newCase;
  }

  _recalculateKPIs() {
    const pendingCases = this.mockState.highRiskCases.filter(c => c.status !== 'RESOLVED');
    this.mockState.kpis.highRiskCount = pendingCases.filter(c => c.riskScore >= 60 && c.riskScore < 80).length;
    this.mockState.kpis.criticalRiskCount = pendingCases.filter(c => c.riskScore >= 80).length;
  }

  _generateInitial30dTrend() {
    return [];
  }

  // --- Public API Client Methods ---

  async fetchKPIs() {
    return this._request('/analytics/kpis');
  }

  async fetchSentimentTrend() {
    return this._request('/analytics/sentiment-trend');
  }

  async fetchFrictionDistribution() {
    return this._request('/analytics/friction-distribution');
  }

  async fetchHighRiskCases() {
    return this._request('/churn/high-risk');
  }

  async updateAlertStatus(alertId, status, notes = '') {
    return this._request(`/alerts/${alertId}`, {
      method: 'PATCH',
      body: JSON.stringify({ status, notes })
    });
  }

  async submitInteraction(interactionData) {
    return this._request('/interactions', {
      method: 'POST',
      body: JSON.stringify(interactionData)
    });
  }

  /**
   * Uploads a CSV dataset file to backend
   * @param {File} file
   * @param {number|null} maxRecords
   * @returns {Promise<Object>}
   */
  async uploadCsvFile(file, maxRecords = null) {
    const formData = new FormData();
    formData.append('file', file);

    const query = maxRecords ? `?max_records=${maxRecords}` : '';
    const url = `${this.baseUrl}/interactions/upload-csv${query}`;

    const response = await fetch(url, {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      const errJson = await response.json().catch(() => ({}));
      throw new Error(errJson.detail || errJson.message || `Error HTTP ${response.status}`);
    }

    return await response.json();
  }
}

export const apiClient = new ApiClient();
