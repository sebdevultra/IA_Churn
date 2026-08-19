/**
 * @file ui_controller.js
 * @description UI Rendering Controller for KPIs, Tables, Modals, Badges, Filters & Toast Notifications.
 */

class UIController {
  constructor() {
    this.activeFilter = 'ALL'; // ALL | CRITICAL | PENDING
    this.searchQuery = '';
    this.currentCaseInModal = null;
    this.onStatusUpdateCallback = null;
  }

  /**
   * Render Top Executive KPI Cards
   * @param {import('./api_client.js').KPIAnalytics} kpis
   */
  renderKPIs(kpis) {
    if (!kpis) return;

    // 1. Total Interactions
    const totalElem = document.getElementById('kpi-total-interactions');
    if (totalElem) {
      totalElem.textContent = kpis.totalInteractions.toLocaleString();
    }

    // 2. Sentiment Health Index
    const healthElem = document.getElementById('kpi-sentiment-health');
    const barPos = document.getElementById('bar-positive');
    const barNeu = document.getElementById('bar-neutral');
    const barNeg = document.getElementById('bar-negative');

    if (healthElem) healthElem.textContent = `${kpis.positivePercentage}% Positivo`;
    if (barPos) barPos.style.width = `${kpis.positivePercentage}%`;
    if (barNeu) barNeu.style.width = `${kpis.neutralPercentage}%`;
    if (barNeg) barNeg.style.width = `${kpis.negativePercentage}%`;

    const legendPos = document.getElementById('legend-positive');
    const legendNeu = document.getElementById('legend-neutral');
    const legendNeg = document.getElementById('legend-negative');
    if (legendPos) legendPos.textContent = `${kpis.positivePercentage}% Pos.`;
    if (legendNeu) legendNeu.textContent = `${kpis.neutralPercentage}% Neu.`;
    if (legendNeg) legendNeg.textContent = `${kpis.negativePercentage}% Neg.`;

    // 3. Predictive NPS
    const npsElem = document.getElementById('kpi-predictive-nps');
    const npsStatusElem = document.getElementById('kpi-nps-status');
    if (npsElem) {
      const sign = kpis.predictiveNps > 0 ? '+' : '';
      npsElem.textContent = `${sign}${kpis.predictiveNps}`;
    }
    if (npsStatusElem) {
      npsStatusElem.textContent = `Salud general: ${kpis.npsStatus || 'Saludable'}`;
    }

    // 4. Churn Risk Cases Breakdown
    const totalRiskElem = document.getElementById('kpi-risk-total');
    const pillHigh = document.getElementById('pill-high-count');
    const pillCrit = document.getElementById('pill-critical-count');
    
    const totalRisk = (kpis.highRiskCount || 0) + (kpis.criticalRiskCount || 0);
    if (totalRiskElem) totalRiskElem.textContent = `${totalRisk} Casos`;
    if (pillHigh) pillHigh.textContent = `${kpis.highRiskCount || 0} Alto`;
    if (pillCrit) pillCrit.textContent = `${kpis.criticalRiskCount || 0} Críticos`;

    // 5. Header Badge
    this.updateHeaderCriticalBadge(kpis.criticalRiskCount || 0);
  }

  /**
   * Updates critical alerts count in header bar
   * @param {number} criticalCount
   */
  updateHeaderCriticalBadge(criticalCount) {
    const badge = document.getElementById('header-critical-badge');
    const countText = document.getElementById('header-critical-count');
    if (!badge || !countText) return;

    countText.textContent = criticalCount;
    if (criticalCount > 0) {
      badge.classList.add('has-alerts');
    } else {
      badge.classList.remove('has-alerts');
    }
  }

  /**
   * Updates Connection Status UI element
   * @param {boolean} isOnline
   */
  updateConnectionStatus(isOnline) {
    const statusElem = document.getElementById('header-connection-status');
    const labelElem = document.getElementById('connection-status-text');
    if (!statusElem || !labelElem) return;

    if (isOnline) {
      statusElem.className = 'connection-status online';
      labelElem.textContent = 'Online';
    } else {
      statusElem.className = 'connection-status offline';
      labelElem.textContent = 'Demo Mode (Offline)';
    }
  }

  /**
   * Renders High Risk Cases Table with active filter & search query
   * @param {Array<import('./api_client.js').ChurnRiskCase>} cases
   */
  renderHighRiskTable(cases) {
    const tbody = document.getElementById('risk-table-body');
    if (!tbody) return;

    if (!Array.isArray(cases) || cases.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="6" class="table-empty">
            <i class="fa-solid fa-folder-open"></i>
            <p>No se encontraron casos de riesgo en la bandeja.</p>
          </td>
        </tr>
      `;
      return;
    }

    // Filter Logic
    const filteredCases = cases.filter(item => {
      // Status Filter
      if (this.activeFilter === 'CRITICAL' && item.riskScore < 80) return false;
      if (this.activeFilter === 'PENDING' && item.status === 'RESOLVED') return false;

      // Text Search Filter
      if (this.searchQuery.trim() !== '') {
        const q = this.searchQuery.toLowerCase();
        const matchName = item.customerName.toLowerCase().includes(q);
        const matchTier = item.tier.toLowerCase().includes(q);
        const matchFriction = item.friction.toLowerCase().includes(q);
        const matchEvidence = item.maskedEvidence.toLowerCase().includes(q);
        const matchId = item.id.toLowerCase().includes(q);
        return matchName || matchTier || matchFriction || matchEvidence || matchId;
      }

      return true;
    });

    if (filteredCases.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="6" class="table-empty">
            <i class="fa-solid fa-filter"></i>
            <p>No hay coincidencias con los filtros aplicados.</p>
          </td>
        </tr>
      `;
      return;
    }

    tbody.innerHTML = filteredCases.map(item => this._generateRowHTML(item)).join('');

    // Attach Event Listeners to Manage Buttons
    tbody.querySelectorAll('.btn-manage').forEach(button => {
      button.addEventListener('click', (e) => {
        const caseId = e.currentTarget.getAttribute('data-case-id');
        const targetCase = cases.find(c => c.id === caseId);
        if (targetCase) {
          this.openInterventionModal(targetCase);
        }
      });
    });
  }

  /**
   * Helper to generate HTML for a table row
   * @param {import('./api_client.js').ChurnRiskCase} item
   */
  _generateRowHTML(item) {
    const tierClass = item.tier.toLowerCase() === 'enterprise'
      ? 'tier-enterprise'
      : item.tier.toLowerCase() === 'pro'
        ? 'tier-pro'
        : 'tier-standard';

    const riskLevel = item.riskScore >= 80 ? 'critical'
      : item.riskScore >= 60 ? 'high'
      : item.riskScore >= 30 ? 'medium' : 'low';

    const riskIcon = riskLevel === 'critical' ? 'fa-triangle-exclamation'
      : riskLevel === 'high' ? 'fa-circle-exclamation'
      : riskLevel === 'medium' ? 'fa-triangle-exclamation' : 'fa-circle-check';

    const frictionIcon = this._getFrictionIcon(item.friction);
    const statusClass = item.status === 'PENDING' ? 'status-pending'
      : item.status === 'IN_REVIEW' ? 'status-review' : 'status-resolved';

    const statusLabel = item.status === 'PENDING' ? 'Pendiente'
      : item.status === 'IN_REVIEW' ? 'En Revisión' : 'Resuelto';

    return `
      <tr id="row-${item.id}">
        <td>
          <div style="font-weight: 600;">${this._escapeHTML(item.customerName)}</div>
          <div style="font-size: 0.75rem; color: var(--text-muted);">${item.id}</div>
        </td>
        <td>
          <span class="tier-badge ${tierClass}">
            <i class="fa-solid fa-crown" style="font-size: 0.7rem;"></i>
            ${item.tier}
          </span>
        </td>
        <td>
          <span class="score-badge ${riskLevel}">
            <i class="fa-solid ${riskIcon}"></i>
            ${item.riskScore} pts
          </span>
        </td>
        <td>
          <span class="friction-tag">
            <i class="fa-solid ${frictionIcon}"></i>
            ${this._formatFrictionName(item.friction)}
          </span>
        </td>
        <td>
          <div class="evidence-text" title="${this._escapeHTML(item.maskedEvidence)}">
            "${this._escapeHTML(item.maskedEvidence)}"
            <span class="pii-tag">PII OK</span>
          </div>
        </td>
        <td>
          <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span class="status-chip ${statusClass}">${statusLabel}</span>
            <button class="btn-manage" data-case-id="${item.id}">
              <i class="fa-solid fa-sliders"></i>
              Gestionar
            </button>
          </div>
        </td>
      </tr>
    `;
  }

  _getFrictionIcon(frictionKey) {
    switch (frictionKey) {
      case 'billing_pricing': return 'fa-file-invoice-dollar';
      case 'customer_support': return 'fa-headset';
      case 'product_reliability': return 'fa-bug';
      case 'sla_delay': return 'fa-clock';
      case 'feature_gap': return 'fa-puzzle-piece';
      default: return 'fa-circle-info';
    }
  }

  _formatFrictionName(key) {
    const map = {
      customer_support: 'Soporte Técnico',
      billing_pricing: 'Facturación / Precios',
      product_reliability: 'Confiabilidad',
      sla_delay: 'Retraso SLA',
      feature_gap: 'Funcionalidad'
    };
    return map[key] || key;
  }

  /**
   * Opens the Intervention Detail Modal
   * @param {import('./api_client.js').ChurnRiskCase} caseItem
   */
  openInterventionModal(caseItem) {
    this.currentCaseInModal = caseItem;

    const modal = document.getElementById('intervention-modal');
    if (!modal) return;

    document.getElementById('modal-customer-name').textContent = caseItem.customerName;
    document.getElementById('modal-case-id').textContent = caseItem.id;
    document.getElementById('modal-tier').textContent = caseItem.tier;
    
    const engineElem = document.getElementById('modal-ai-engine');
    if (engineElem) {
      engineElem.textContent = caseItem.aiEngine === 'cloud_gemini' ? 'Google Gemini 2.5 AI' : 'Local NLP Risk Engine';
    }

    // Score Badge in Modal
    const modalScore = document.getElementById('modal-risk-score');
    if (modalScore) {
      modalScore.textContent = `${caseItem.riskScore} / 100`;
    }

    // Evidence
    const modalEvidence = document.getElementById('modal-evidence-text');
    if (modalEvidence) {
      modalEvidence.textContent = caseItem.maskedEvidence;
    }

    // Score Factors Breakdown List
    const factorsContainer = document.getElementById('modal-score-factors');
    if (factorsContainer && Array.isArray(caseItem.scoreFactors)) {
      factorsContainer.innerHTML = caseItem.scoreFactors.map(f => `
        <div class="factor-item">
          <span class="factor-name"><i class="fa-solid fa-angle-right"></i> ${this._escapeHTML(f.factor)}</span>
          <span class="factor-impact">+${f.impact} pts</span>
        </div>
      `).join('');
    }

    // Status Radio Inputs
    const statusRadio = document.querySelector(`input[name="modal-status"][value="${caseItem.status}"]`);
    if (statusRadio) statusRadio.checked = true;

    // Notes Input
    const notesInput = document.getElementById('modal-notes-input');
    if (notesInput) notesInput.value = caseItem.notes || '';

    modal.classList.add('open');
  }

  /**
   * Closes Intervention Detail Modal
   */
  closeInterventionModal() {
    const modal = document.getElementById('intervention-modal');
    if (modal) modal.classList.remove('open');
    this.currentCaseInModal = null;
  }

  /**
   * Displays non-intrusive Toast Notification
   * @param {string} title
   * @param {string} message
   * @param {'success'|'error'|'info'} type
   */
  showToast(title, message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const iconMap = {
      success: 'fa-circle-check',
      error: 'fa-circle-xmark',
      info: 'fa-circle-info'
    };

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
      <i class="fa-solid ${iconMap[type] || 'fa-circle-info'} font-size: 1.1rem;"></i>
      <div class="toast-content">
        <div class="toast-title">${this._escapeHTML(title)}</div>
        <div class="toast-message">${this._escapeHTML(message)}</div>
      </div>
      <button class="btn-close" aria-label="Cerrar"><i class="fa-solid fa-xmark"></i></button>
    `;

    toast.querySelector('.btn-close').addEventListener('click', () => {
      toast.remove();
    });

    container.appendChild(toast);

    // Auto remove after 5 seconds
    setTimeout(() => {
      if (toast.parentNode) {
        toast.remove();
      }
    }, 5000);
  }

  _escapeHTML(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }
}

export const uiController = new UIController();
