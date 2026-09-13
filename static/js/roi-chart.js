// EduBridge — ROI Calculator Chart Renderer
function initRoiChart(earningsData, costsData) {
  const ctx = document.getElementById('roiChart');
  if (!ctx || typeof Chart === 'undefined') return;

  let earnings = earningsData;
  let costs = costsData;

  if (!earnings && ctx.dataset.earnings) {
    try { earnings = JSON.parse(ctx.dataset.earnings); } catch (e) { earnings = []; }
  }
  if (!costs && ctx.dataset.costs) {
    try { costs = JSON.parse(ctx.dataset.costs); } catch (e) { costs = []; }
  }

  if (!earnings || !costs || !earnings.length) return;

  new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['Yr 1', 'Yr 2', 'Yr 3', 'Yr 4', 'Yr 5', 'Yr 6', 'Yr 7', 'Yr 8', 'Yr 9', 'Yr 10'],
      datasets: [
        {
          label: 'Cumulative Net Savings (₹ Lakhs)',
          data: earnings,
          borderColor: '#0284C7',
          backgroundColor: 'rgba(2, 132, 199, 0.08)',
          fill: true,
          tension: 0.3
        },
        {
          label: 'Total Upfront Investment (₹ Lakhs)',
          data: costs,
          borderColor: '#E11D48',
          borderDash: [5, 5],
          fill: false,
          tension: 0
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } }
      },
      scales: {
        y: { grid: { color: '#F1F5F9' }, ticks: { font: { size: 10 } } },
        x: { grid: { display: false }, ticks: { font: { size: 10 } } }
      }
    }
  });
}

document.addEventListener('DOMContentLoaded', function() {
  initRoiChart();
});

