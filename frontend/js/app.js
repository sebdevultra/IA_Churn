/**
 * @file app.js
 * @description Main Application Orchestrator, DOM Event Listeners, Polling Timers & Live Simulator Testbed.
 */

import { apiClient } from './api_client.js?v=8';
import { chartsManager } from './charts.js?v=8';
import { uiController } from './ui_controller.js?v=8';

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
    console.log('[App] Initializing JDS Sentinel AI Dashboard...');

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

    uiController.showToast('Sistema Listo', 'Dashboard de JDS Sentinel AI sincronizado.', 'success');
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

          // Trigger immediate data refresh for tables and KPIs
          await this.refreshFastData();
          await this.refreshSlowData();
        } catch (err) {
          uiController.showToast('Error', 'No se pudo actualizar el estado de la alerta.', 'error');
        } finally {
          modalSaveBtn.disabled = false;
          modalSaveBtn.innerHTML = '<i class="fa-solid fa-check"></i> Guardar Cambios';
        }
      });
    }

    // 5. Hatsune Miku Interactive Widget
    this._bindMikuWidget();

    // 6. CSV Batch Ingestion Controls
    this._bindCsvUploadControls();

    // 7. Sidebar Navigation Smooth Scroll
    document.querySelectorAll('.sidebar-nav-link').forEach(link => {
      link.addEventListener('click', (e) => {
        const href = link.getAttribute('href');
        if (href && href.startsWith('#')) {
          const targetElem = document.querySelector(href);
          if (targetElem) {
            e.preventDefault();
            document.querySelectorAll('.sidebar-nav-link').forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            targetElem.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }
        }
      });
    });
  }

  /**
   * Binds Drag & Drop and File Upload for CSV datasets
   */
  _bindCsvUploadControls() {
    const dropZone = document.getElementById('csv-drop-zone');
    const fileInput = document.getElementById('csv-file-input');
    const fileNameLabel = document.getElementById('csv-file-name-label');
    const submitBtn = document.getElementById('btn-csv-upload-submit');
    const maxRecordsSelect = document.getElementById('csv-max-records-select');
    const presetBtn = document.getElementById('btn-load-10k-preset');
    const resultBox = document.getElementById('csv-result-box');
    const resultDetails = document.getElementById('csv-result-details');

    if (!dropZone || !fileInput || !submitBtn) return;

    let selectedFile = null;

    dropZone.addEventListener('click', (e) => {
      e.preventDefault();
      fileInput.click();
    });

    fileInput.addEventListener('click', (e) => {
      e.stopPropagation();
    });

    dropZone.addEventListener('dragover', (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropZone.style.borderColor = 'var(--hz-primary-light)';
      dropZone.style.background = 'rgba(67, 24, 255, 0.08)';
    });

    dropZone.addEventListener('dragleave', (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropZone.style.borderColor = 'var(--hz-border)';
      dropZone.style.background = 'rgba(255, 255, 255, 0.02)';
    });

    // Global variable on window for cross-handler state
    window.selectedCsvFile = null;

    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropZone.style.borderColor = 'var(--hz-border)';
      dropZone.style.background = 'rgba(255, 255, 255, 0.02)';

      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        const file = e.dataTransfer.files[0];
        if (file.name.toLowerCase().endsWith('.csv')) {
          window.selectedCsvFile = file;
          fileNameLabel.innerHTML = `<i class="ti ti-file-spreadsheet" style="color: var(--hz-success);"></i> Archivo Seleccionado: <strong>${file.name}</strong> (${(file.size / 1024).toFixed(1)} KB)`;
          uiController.showToast('Archivo Cargado', `Listo para procesar: ${file.name}`, 'info');
        } else {
          uiController.showToast('Archivo Inválido', 'Por favor seleccione un archivo con formato .CSV', 'error');
        }
      }
    });

    fileInput.addEventListener('change', (e) => {
      if (e.target.files && e.target.files.length > 0) {
        window.selectedCsvFile = e.target.files[0];
        fileNameLabel.innerHTML = `<i class="ti ti-file-spreadsheet" style="color: var(--hz-success);"></i> Archivo Seleccionado: <strong>${window.selectedCsvFile.name}</strong> (${(window.selectedCsvFile.size / 1024).toFixed(1)} KB)`;
        uiController.showToast('Archivo Cargado', `Listo para procesar: ${window.selectedCsvFile.name}`, 'info');
      }
    });

    // Define global action handlers for both inline and listener invocation
    window.loadPreset10kDataset = async (e) => {
      if (e && e.preventDefault) { e.preventDefault(); e.stopPropagation(); }
      const pBtn = document.getElementById('btn-load-10k-preset');
      const fLabel = document.getElementById('csv-file-name-label');

      try {
        if (pBtn) {
          pBtn.disabled = true;
          pBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Cargando 10K...';
        }

        const res = await fetch('/data/dataset_10k_interactions.csv');
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}: No se pudo descargar el dataset`);
        }

        const blob = await res.blob();
        window.selectedCsvFile = new File([blob], 'dataset_10k_interactions.csv', { type: 'text/csv' });
        if (fLabel) {
          fLabel.innerHTML = `<i class="ti ti-file-spreadsheet" style="color: var(--hz-success);"></i> Dataset 10K Cargado: <strong>dataset_10k_interactions.csv</strong> (${(window.selectedCsvFile.size / 1024).toFixed(1)} KB)`;
        }
        uiController.showToast('Dataset 10K Listo', 'Archivo preparado. Haz clic en "Iniciar Ingesta Batch".', 'info');
      } catch (err) {
        console.error('[PresetLoad Error]', err);
        uiController.showToast('Error', err.message || 'No se pudo cargar el dataset 10K.', 'error');
      } finally {
        if (pBtn) {
          pBtn.disabled = false;
          pBtn.innerHTML = '<i class="ti ti-file-text" style="color: var(--hz-info);"></i> Cargar Dataset 10K';
        }
      }
    };

    window.submitBatchCsvUpload = async (e) => {
      if (e && e.preventDefault) { e.preventDefault(); e.stopPropagation(); }
      const sBtn = document.getElementById('btn-csv-upload-submit');
      const maxSelect = document.getElementById('csv-max-records-select');
      const fLabel = document.getElementById('csv-file-name-label');
      const rBox = document.getElementById('csv-result-box');
      const rDetails = document.getElementById('csv-result-details');

      try {
        if (sBtn) {
          sBtn.disabled = true;
          sBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Procesando Batch...';
        }

        // Auto-load 10K dataset if no file was uploaded
        if (!window.selectedCsvFile) {
          if (fLabel) {
            fLabel.innerHTML = `<i class="fa-solid fa-spinner fa-spin" style="color: var(--hz-info);"></i> Cargando dataset 10K...`;
          }
          const res = await fetch('/data/dataset_10k_interactions.csv');
          if (!res.ok) {
            throw new Error(`HTTP ${res.status}: No se pudo descargar el dataset`);
          }
          const blob = await res.blob();
          window.selectedCsvFile = new File([blob], 'dataset_10k_interactions.csv', { type: 'text/csv' });
          if (fLabel) {
            fLabel.innerHTML = `<i class="ti ti-file-spreadsheet" style="color: var(--hz-success);"></i> Dataset 10K: <strong>dataset_10k_interactions.csv</strong> (${(window.selectedCsvFile.size / 1024).toFixed(1)} KB)`;
          }
        }

        const limitVal = parseInt(maxSelect?.value || '1000', 10);
        const maxRecords = limitVal > 0 ? limitVal : null;

        const res = await apiClient.uploadCsvFile(window.selectedCsvFile, maxRecords);

        if (res && res.success) {
          uiController.showToast(
            'Ingesta Completada',
            `Se procesaron ${res.processed_count} registros en ${(res.duration_ms / 1000).toFixed(2)}s.`,
            'success'
          );

          if (rBox && rDetails) {
            rBox.style.display = 'block';
            const rps = res.duration_ms > 0 ? ((res.processed_count / res.duration_ms) * 1000).toFixed(0) : 0;
            rDetails.innerHTML = `
              <span><strong>Registros Procesados:</strong> ${res.processed_count}</span>
              <span><strong>Duplicados Filtrados:</strong> ${res.duplicates_count}</span>
              <span><strong>Errores:</strong> ${res.errors_count}</span>
              <span><strong>Tiempo de Ejecución:</strong> ${(res.duration_ms / 1000).toFixed(2)}s (${rps} reg/seg)</span>
            `;
          }

          // Trigger instant refresh of KPIs and Table
          if (window.app) {
            await window.app.refreshFastData();
            await window.app.refreshSlowData();
          }
        }
      } catch (err) {
        console.error('[Upload CSV Error]', err);
        uiController.showToast('Error de Ingesta', err.message || 'Error al procesar el archivo CSV.', 'error');
      } finally {
        if (sBtn) {
          sBtn.disabled = false;
          sBtn.innerHTML = '<i class="ti ti-rocket"></i> Iniciar Ingesta Batch';
        }
      }
    };

    // Preset 10K Loader Button Listener
    if (presetBtn) {
      presetBtn.addEventListener('click', window.loadPreset10kDataset);
    }

    // Submit CSV Upload Listener
    if (submitBtn) {
      submitBtn.addEventListener('click', window.submitBatchCsvUpload);
    }
  }

  /**
   * Binds Hatsune Miku Widget Click Animation & Audio Playback
   */
  _bindMikuWidget() {
    const mikuBtn = document.getElementById('chibi-miku-btn');
    if (!mikuBtn) return;

    mikuBtn.addEventListener('click', (e) => {
      e.stopPropagation();

      const mikuImg = document.getElementById('miku-gif-img');
      if (mikuImg) {
        mikuImg.style.transform = 'scale(1.25) rotate(8deg)';
        setTimeout(() => { mikuImg.style.transform = 'scale(1)'; }, 350);
      }

      // 1. First attempt: Play via HTMLAudioElement directly
      const htmlAudio = document.getElementById('miku-audio-player');
      if (htmlAudio) {
        htmlAudio.currentTime = 0;
        const playPromise = htmlAudio.play();
        if (playPromise !== undefined) {
          playPromise.then(() => {
            uiController.showToast('♪ Tole Tole Kawaii~!', 'Hatsune Miku dice: ¡Hola!', 'info');
          }).catch(() => {
            // 2. Fallback: Dynamic Audio constructor with absolute URL
            try {
              const audioObj = new Audio('/assets/miku-sound.mp3');
              audioObj.volume = 1.0;
              audioObj.play().then(() => {
                uiController.showToast('♪ Tole Tole Kawaii~!', 'Hatsune Miku dice: ¡Hola!', 'info');
              }).catch(err => {
                console.warn('[MikuAudio Error]', err);
              });
            } catch (err) {
              console.error('[MikuAudio Exception]', err);
            }
          });
          return;
        }
      }

      // 3. Direct constructor fallback
      try {
        const audioObj = new Audio('/assets/miku-sound.mp3');
        audioObj.volume = 1.0;
        audioObj.play();
      } catch (err) {
        console.warn('[Audio Init Error]', err);
      }
    });
  }
}

// Instantiate and start app on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  const app = new App();
  app.init();
});
