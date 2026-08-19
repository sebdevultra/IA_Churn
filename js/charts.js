/**
 * @file charts.js
 * @description Horizon UI Chart.js configurations for Sentiment Evolution & Friction Points.
 */

class ChartsManager {
  constructor() {
    this.sentimentTrendChart = null;
    this.frictionChart = null;
  }

  /**
   * Initializes both charts with Horizon UI theme configuration
   * @param {HTMLCanvasElement} trendCanvas
   * @param {HTMLCanvasElement} frictionCanvas
   */
  initCharts(trendCanvas, frictionCanvas) {
    if (!trendCanvas || !frictionCanvas) return;

    if (typeof Chart === 'undefined') {
      console.error('[ChartsManager] Chart.js CDN is not loaded.');
      return;
    }

    // Chart.js Horizon UI Defaults
    Chart.defaults.color = '#7090B0';
    Chart.defaults.font.family = "'DM Sans', 'Inter', system-ui, sans-serif";
    Chart.defaults.plugins.tooltip.backgroundColor = '#111C44';
    Chart.defaults.plugins.tooltip.titleColor = '#FFFFFF';
    Chart.defaults.plugins.tooltip.borderColor = 'rgba(255, 255, 255, 0.1)';
    Chart.defaults.plugins.tooltip.borderWidth = 1;
    Chart.defaults.plugins.tooltip.padding = 12;
    Chart.defaults.plugins.tooltip.cornerRadius = 12;

    this._initSentimentTrendChart(trendCanvas);
    this._initFrictionChart(frictionCanvas);
  }

  /**
   * 30-Day Sentiment Evolution Area/Line Chart
   */
  _initSentimentTrendChart(canvas) {
    const ctx = canvas.getContext('2d');

    const gradPositive = ctx.createLinearGradient(0, 0, 0, 300);
    gradPositive.addColorStop(0, 'rgba(5, 205, 153, 0.35)');
    gradPositive.addColorStop(1, 'rgba(5, 205, 153, 0.0)');

    const gradNeutral = ctx.createLinearGradient(0, 0, 0, 300);
    gradNeutral.addColorStop(0, 'rgba(67, 24, 255, 0.35)');
    gradNeutral.addColorStop(1, 'rgba(67, 24, 255, 0.0)');

    const gradNegative = ctx.createLinearGradient(0, 0, 0, 300);
    gradNegative.addColorStop(0, 'rgba(238, 93, 80, 0.35)');
    gradNegative.addColorStop(1, 'rgba(238, 93, 80, 0.0)');

    this.sentimentTrendChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: [],
        datasets: [
          {
            label: 'Positivo',
            data: [],
            borderColor: '#05CD99',
            backgroundColor: gradPositive,
            fill: true,
            tension: 0.4,
            borderWidth: 3,
            pointRadius: 4,
            pointHoverRadius: 7
          },
          {
            label: 'Neutro',
            data: [],
            borderColor: '#4318FF',
            backgroundColor: gradNeutral,
            fill: true,
            tension: 0.4,
            borderWidth: 3,
            pointRadius: 4,
            pointHoverRadius: 7
          },
          {
            label: 'Negativo',
            data: [],
            borderColor: '#EE5D50',
            backgroundColor: gradNegative,
            fill: true,
            tension: 0.4,
            borderWidth: 3,
            pointRadius: 4,
            pointHoverRadius: 7
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: 'index',
          intersect: false
        },
        plugins: {
          legend: {
            position: 'top',
            align: 'end',
            labels: {
              usePointStyle: true,
              boxWidth: 8,
              padding: 15,
              font: { size: 12, weight: '600' }
            }
          }
        },
        scales: {
          x: {
            grid: { color: 'rgba(255, 255, 255, 0.05)', drawBorder: false },
            ticks: { font: { size: 11 } }
          },
          y: {
            grid: { color: 'rgba(255, 255, 255, 0.08)', drawBorder: false },
            ticks: { font: { size: 11 }, precision: 0 },
            beginAtZero: true
          }
        }
      }
    });
  }

  /**
   * Horizontal Bar Chart for Friction Points
   */
  _initFrictionChart(canvas) {
    const ctx = canvas.getContext('2d');

    this.frictionChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: [],
        datasets: [
          {
            label: 'Menciones de Fricción',
            data: [],
            backgroundColor: [
              '#EE5D50', // Rose Red
              '#FF763C', // Orange
              '#FFB547', // Amber
              '#4318FF', // Horizon Purple
              '#39B8FF'  // Sky Blue
            ],
            borderRadius: 8,
            borderSkipped: false,
            barThickness: 20
          }
        ]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: {
            grid: { color: 'rgba(255, 255, 255, 0.08)', drawBorder: false },
            ticks: { font: { size: 11 }, precision: 0 },
            beginAtZero: true
          },
          y: {
            grid: { display: false },
            ticks: { font: { size: 11, weight: '600' } }
          }
        }
      }
    });
  }

  updateSentimentTrend(trendData) {
    if (!this.sentimentTrendChart || !Array.isArray(trendData)) return;

    const labels = trendData.map(item => item.date);
    const positiveValues = trendData.map(item => item.positive);
    const neutralValues = trendData.map(item => item.neutral);
    const negativeValues = trendData.map(item => item.negative);

    this.sentimentTrendChart.data.labels = labels;
    this.sentimentTrendChart.data.datasets[0].data = positiveValues;
    this.sentimentTrendChart.data.datasets[1].data = neutralValues;
    this.sentimentTrendChart.data.datasets[2].data = negativeValues;
    this.sentimentTrendChart.update('none');
  }

  updateFrictionDistribution(frictionData) {
    if (!this.frictionChart || !frictionData) return;

    const categoryMap = {
      customer_support: 'Soporte Técnico',
      billing_pricing: 'Facturación y Precios',
      product_reliability: 'Confiabilidad Producto',
      sla_delay: 'Retraso de SLA',
      feature_gap: 'Funcionalidad Ausente'
    };

    const sortedCategories = Object.keys(frictionData)
      .map(key => ({
        key,
        label: categoryMap[key] || key,
        count: frictionData[key] || 0
      }))
      .sort((a, b) => b.count - a.count);

    this.frictionChart.data.labels = sortedCategories.map(c => c.label);
    this.frictionChart.data.datasets[0].data = sortedCategories.map(c => c.count);
    this.frictionChart.update('none');
  }
}

export const chartsManager = new ChartsManager();
