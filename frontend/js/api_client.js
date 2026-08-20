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
  constructor(baseUrl = '/api/v1') {
    this.baseUrl = baseUrl;
    this.isOnline = true;
    this.maxRetries = 1;
    this.retryDelayMs = 800;

    // Internal reactive Mock Store for smooth demo when API backend is offline
    this.mockState = {
      kpis: {
        totalInteractions: 1248,
        positivePercentage: 58,
        neutralPercentage: 24,
        negativePercentage: 18,
        predictiveNps: 40,
        npsStatus: 'Saludable',
        highRiskCount: 6,
        criticalRiskCount: 3
      },
      sentimentTrend: this._generateInitial30dTrend(),
      frictionDistribution: {
        customer_support: 42,
        billing_pricing: 28,
        product_reliability: 19,
        sla_delay: 14,
        feature_gap: 9
      },
      highRiskCases: [
        {
          id: 'ALT-1092',
          customerName: 'TechCorp International',
          tier: 'Enterprise',
          riskScore: 92,
          emotion: 'anger',
          friction: 'billing_pricing',
          rawEvidence: 'Exijo la cancelación de nuestro contrato de 50k USD. Nos cobraron doble este mes y soporte no contesta a john.doe@techcorp.com.',
          maskedEvidence: 'Exijo la cancelación de nuestro contrato de [Monto Enmascarado]. Nos cobraron doble este mes y soporte no contesta a j***e@techcorp.com.',
          status: 'PENDING',
          aiEngine: 'cloud_gemini',
          scoreFactors: [
            { factor: 'Sentimiento fuertemente negativo', impact: 25 },
            { factor: 'Intención explícita de cancelación', impact: 35 },
            { factor: 'SLA de Soporte Vencido (>48h)', impact: 20 },
            { factor: 'Cliente Tier Enterprise (Alto Valor)', impact: 12 }
          ],
          timestamp: '2026-08-19T01:45:00Z'
        },
        {
          id: 'ALT-1088',
          customerName: 'GlobalLogistics S.A.',
          tier: 'Pro',
          riskScore: 78,
          emotion: 'frustration',
          friction: 'sla_delay',
          rawEvidence: 'Llevamos 3 días laborables sin respuesta al ticket #4092. El sistema de tracking sigue caído.',
          maskedEvidence: 'Llevamos 3 días laborables sin respuesta al ticket #4092. El sistema de tracking sigue caído.',
          status: 'PENDING',
          aiEngine: 'local_nlp',
          scoreFactors: [
            { factor: 'Frustración por retraso SLA', impact: 30 },
            { factor: 'Reincidencia en reportes de fallos', impact: 25 },
            { factor: 'Baja frecuencia de uso reciente', impact: 23 }
          ],
          timestamp: '2026-08-19T00:30:00Z'
        }
      ]
    };
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
        const timeoutId = setTimeout(() => controller.abort(), 4000);

        const response = await fetch(url, {
          ...options,
          signal: controller.signal,
          headers: {
            'Content-Type': 'application/json',
            ...(options.headers || {})
          }
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          throw new Error(`HTTP Error ${response.status}: ${response.statusText}`);
        }

        this.isOnline = true;
        const resJson = await response.json();
        if (resJson && typeof resJson === 'object' && 'data' in resJson && 'success' in resJson) {
          return resJson;
        }
        return { success: true, data: resJson };
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
    const text = (payload.text || payload.content || '').toLowerCase();
    const customer = payload.customerName || payload.customer_external_id || 'Cliente de Prueba';
    const tier = payload.tier || 'Enterprise';

    let emotion = 'neutral';
    let friction = 'feature_gap';
    let riskScore = 15;
    let sentimentCategory = 'positive';
    let aiEngine = payload.aiEngine || 'deterministic_rule';

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

    const maskedText = (payload.text || payload.content || '')
      .replace(/([a-zA-Z0-9._-]+)@([a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)/gi, (match, p1, p2) => `${p1.charAt(0)}***${p1.charAt(p1.length - 1)}@${p2}`)
      .replace(/\$?\d{3,6}\s?(usd|eur|cop)?/gi, '[Monto Enmascarado]');

    const newCase = {
      id: `ALT-${Math.floor(1000 + Math.random() * 9000)}`,
      customerName: customer,
      tier: tier,
      riskScore: riskScore,
      emotion: emotion,
      friction: friction,
      rawEvidence: payload.text || payload.content || '',
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

    this.mockState.highRiskCases.unshift(newCase);
    this.mockState.kpis.totalInteractions += 1;
    this.mockState.frictionDistribution[friction] = (this.mockState.frictionDistribution[friction] || 0) + 1;

    this._recalculateKPIs();
    return newCase;
  }

  _recalculateKPIs() {
    const pendingCases = this.mockState.highRiskCases.filter(c => c.status !== 'RESOLVED');
    this.mockState.kpis.highRiskCount = pendingCases.filter(c => c.riskScore >= 60 && c.riskScore < 80).length;
    this.mockState.kpis.criticalRiskCount = pendingCases.filter(c => c.riskScore >= 80).length;
  }

  _generateInitial30dTrend() {
    const trend = [];
    const now = new Date();
    for (let i = 29; i >= 0; i--) {
      const d = new Date(now);
      d.setDate(d.getDate() - i);
      const dateStr = `${d.getMonth() + 1}/${d.getDate()}`;
      
      const positive = Math.floor(30 + Math.sin(i * 0.3) * 10 + Math.random() * 5);
      const neutral = Math.floor(15 + Math.cos(i * 0.2) * 5 + Math.random() * 4);
      const negative = Math.floor(8 + Math.sin(i * 0.5) * 4 + Math.random() * 3);

      trend.push({ date: dateStr, positive, neutral, negative });
    }
    return trend;
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
}

export const apiClient = new ApiClient();
