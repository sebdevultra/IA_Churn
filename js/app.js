/**
 * @file app.js
 * @description Main Application Orchestrator, DOM Event Listeners, Polling Timers & Live Simulator Testbed.
 */

import { apiClient } from './api_client.js';
import { chartsManager } from './charts.js';
import { uiController } from './ui_controller.js';

class App {
  constructor() {
    this.isAutoRefreshEnabled = true;
    this.kpiPollingInterval = null;
    this.chartPollingInterval = null;
    this.cachedCases = [];
  }

  /**
   * Application Entry Point
   */
  async init() {
    console.log('[App] Initializing JDS AI Dashboard...');

    // 1. Initialize Chart.js canvases
    const trendCanvas = document.getElementById('sentimentTrendChart');
    const frictionCanvas = document.getElementById('frictionChart');
    chartsManager.initCharts(trendCanvas, frictionCanvas);

    // 2. Bind DOM Event Listeners
    this._bindEventListeners();

    // 3. Initial Data Fetch
    await this.refreshFastData();
    await this.refreshSlowData();

    // 4. Start Smart Periodic Polling
    this.startPolling();

    uiController.showToast('Sistema Listo', 'Dashboard de JDS AI sincronizado.', 'success');
  }

  /**
   * Fast Polling Cycle (Every 5 seconds for KPIs & High Risk Alerts)
   */
  async refreshFastData() {
    try {
      const [kpiRes, casesRes] = await Promise.all([
        apiClient.fetchKPIs(),
        apiClient.fetchHighRiskCases()
      ]);

      if (kpiRes && kpiRes.data) {
        uiController.renderKPIs(kpiRes.data);
      }

      if (casesRes && casesRes.data) {
        this.cachedCases = casesRes.data;
        uiController.renderHighRiskTable(this.cachedCases);
      }

      uiController.updateConnectionStatus(apiClient.isOnline);
    } catch (err) {
      console.error('[App] Fast refresh error:', err);
      uiController.updateConnectionStatus(false);
      uiController.showToast('Error de Red', 'No se pudo conectar con el servidor backend.', 'error');
    }
  }

  /**
   * Slow Polling Cycle (Every 15 seconds for Sentiment Trend & Friction Charts)
   */
  async refreshSlowData() {
    try {
      const [trendRes, frictionRes] = await Promise.all([
        apiClient.fetchSentimentTrend(),
        apiClient.fetchFrictionDistribution()
      ]);

      if (trendRes && trendRes.data) {
        chartsManager.updateSentimentTrend(trendRes.data);
      }

      if (frictionRes && frictionRes.data) {
        chartsManager.updateFrictionDistribution(frictionRes.data);
      }
    } catch (err) {
      console.error('[App] Slow refresh error:', err);
    }
  }

  /**
   * Smart Periodic Polling setup
   */
  startPolling() {
    this.stopPolling();

    // Fast polling every 5000ms
    this.kpiPollingInterval = setInterval(() => {
      if (this.isAutoRefreshEnabled) {
        this.refreshFastData();
      }
    }, 5000);

    // Slow polling every 15000ms
    this.chartPollingInterval = setInterval(() => {
      if (this.isAutoRefreshEnabled) {
        this.refreshSlowData();
      }
    }, 15000);
  }

  stopPolling() {
    if (this.kpiPollingInterval) clearInterval(this.kpiPollingInterval);
    if (this.chartPollingInterval) clearInterval(this.chartPollingInterval);
  }

  /**
   * Binds user interactions and DOM events
   */
  _bindEventListeners() {
    // 1. Auto-refresh Toggle Switch
    const refreshToggle = document.getElementById('auto-refresh-toggle');
    if (refreshToggle) {
      refreshToggle.addEventListener('change', (e) => {
        this.isAutoRefreshEnabled = e.target.checked;
        const msg = this.isAutoRefreshEnabled ? 'Auto-refresh activado (5s / 15s)' : 'Auto-refresh pausado';
        uiController.showToast('Sincronización', msg, 'info');
      });
    }

    // 2. Table Filter Buttons (Todos | Solo Críticos | Pendientes)
    const filterButtons = document.querySelectorAll('.filter-btn');
    filterButtons.forEach(btn => {
      btn.addEventListener('click', (e) => {
        filterButtons.forEach(b => b.classList.remove('active'));
        e.currentTarget.classList.add('active');

        const filterValue = e.currentTarget.getAttribute('data-filter');
        uiController.activeFilter = filterValue;
        uiController.renderHighRiskTable(this.cachedCases);
      });
    });

    // 3. Search Box Input
    const searchInput = document.getElementById('table-search-input');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        uiController.searchQuery = e.target.value;
        uiController.renderHighRiskTable(this.cachedCases);
      });
    }

    // 4. Modal Action & Save Form
    const modalCloseBtn = document.getElementById('btn-modal-close');
    const modalCancelBtn = document.getElementById('btn-modal-cancel');
    const modalSaveBtn = document.getElementById('btn-modal-save');

    if (modalCloseBtn) modalCloseBtn.addEventListener('click', () => uiController.closeInterventionModal());
    if (modalCancelBtn) modalCancelBtn.addEventListener('click', () => uiController.closeInterventionModal());

    if (modalSaveBtn) {
      modalSaveBtn.addEventListener('click', async () => {
        const caseItem = uiController.currentCaseInModal;
        if (!caseItem) return;

        const selectedStatus = document.querySelector('input[name="modal-status"]:checked')?.value || caseItem.status;
        const notes = document.getElementById('modal-notes-input')?.value || '';

        try {
          modalSaveBtn.disabled = true;
          modalSaveBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Guardando...';

          await apiClient.updateAlertStatus(caseItem.id, selectedStatus, notes);
          
          uiController.closeInterventionModal();
          uiController.showToast('Alerta Actualizada', `Caso ${caseItem.id} marcado como ${selectedStatus}.`, 'success');

          // Trigger immediate data refresh
          await this.refreshFastData();
        } catch (err) {
          uiController.showToast('Error', 'No se pudo actualizar el estado de la alerta.', 'error');
        } finally {
          modalSaveBtn.disabled = false;
          modalSaveBtn.innerHTML = '<i class="fa-solid fa-check"></i> Guardar Cambios';
        }
      });
    }

    // 5. Live Testbed Simulator Controls
    this._bindSimulatorControls();
  }

  /**
   * Binds Live Testbed Simulator Preset Buttons & Ingestion Form
   */
  _bindSimulatorControls() {
    const feedbackInput = document.getElementById('sim-feedback-input');
    const customerSelect = document.getElementById('sim-customer-select');
    const tierSelect = document.getElementById('sim-tier-select');
    const simForm = document.getElementById('simulator-form');
    const simSubmitBtn = document.getElementById('btn-sim-submit');

    // Preset Buttons
    const presetButtons = document.querySelectorAll('.preset-chip');
    presetButtons.forEach(btn => {
      btn.addEventListener('click', (e) => {
        const presetType = e.currentTarget.getAttribute('data-preset');
        switch (presetType) {
          case 'positive':
            feedbackInput.value = 'Excelente servicio, la velocidad de respuesta y la atención del equipo han superado nuestras expectativas.';
            tierSelect.value = 'Enterprise';
            break;
          case 'support':
            feedbackInput.value = 'Llevamos 3 días esperando respuesta al ticket #4092. El sistema sigue fallenado y la atención ha sido decepcionante.';
            tierSelect.value = 'Pro';
            break;
          case 'churn':
            feedbackInput.value = 'Exijo la cancelación inmediata de nuestro contrato de 60k USD. Nos cobraron doble este mes y soporte no contesta a john.doe@techcorp.com.';
            tierSelect.value = 'Enterprise';
            break;
          case 'sarcasm':
            feedbackInput.value = 'Fantástico servicio, me encanta pagar el doble por un software que se congela todo el día y no deja exportar datos.';
            tierSelect.value = 'Standard';
            break;
        }
      });
    });

    // Form Submit (POST /api/interactions)
    if (simForm) {
      simForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const text = feedbackInput.value.trim();
        if (!text) {
          uiController.showToast('Campo Requerido', 'Ingrese un mensaje de feedback para analizar.', 'info');
          return;
        }

        const customerName = customerSelect.value;
        const tier = tierSelect.value;

        try {
          simSubmitBtn.disabled = true;
          simSubmitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Analizando en Vivo...';

          const res = await apiClient.submitInteraction({
            customerName,
            tier,
            text,
            aiEngine: 'cloud_gemini'
          });

          if (res && res.data) {
            const newCase = res.data;
            uiController.showToast(
              'Análisis Completado',
              `Risk Score: ${newCase.riskScore} pts (${newCase.emotion.toUpperCase()}).`,
              newCase.riskScore >= 60 ? 'error' : 'success'
            );

            // Display Live Result Box
            this._showSimulatorResult(newCase);

            // Instant sync across table & charts
            await this.refreshFastData();
            await this.refreshSlowData();
          }
        } catch (err) {
          uiController.showToast('Error', 'No se pudo procesar la ingesta en vivo.', 'error');
        } finally {
          simSubmitBtn.disabled = false;
          simSubmitBtn.innerHTML = '<i class="fa-solid fa-bolt"></i> Analizar en Vivo';
        }
      });
    }
  }

  /**
   * Helper to display instant feedback chip box under simulator
   */
  _showSimulatorResult(caseResult) {
    const box = document.getElementById('simulator-result-box');
    const metaContainer = document.getElementById('sim-result-meta');
    if (!box || !metaContainer) return;

    const riskLevel = caseResult.riskScore >= 80 ? 'critical'
      : caseResult.riskScore >= 60 ? 'high'
      : caseResult.riskScore >= 30 ? 'medium' : 'low';

    metaContainer.innerHTML = `
      <span class="ai-engine-chip">
        <i class="fa-solid fa-brain"></i> ${caseResult.aiEngine === 'cloud_gemini' ? 'Google Gemini 2.5' : 'Local NLP'}
      </span>
      <span class="score-badge ${riskLevel}">
        <i class="fa-solid fa-shield-halved"></i> Risk Score: ${caseResult.riskScore} / 100
      </span>
      <span class="friction-tag">
        <i class="fa-solid fa-tag"></i> Fricción: ${caseResult.friction}
      </span>
      <span style="font-size: 0.8rem; color: var(--text-secondary);">
        PII Enmascarada: "${caseResult.maskedEvidence}"
      </span>
    `;

    box.classList.add('active');
  }
}

// Instantiate and start app on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  const app = new App();
  app.init();
});
