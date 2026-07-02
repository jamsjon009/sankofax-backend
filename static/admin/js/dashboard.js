/* SankofaX Admin Dashboard JS */

// Live Clock
(function tick() {
  var n = new Date();
  var te = document.getElementById('skx-time');
  var de = document.getElementById('skx-date');
  if (te) te.textContent = n.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  if (de) de.textContent = n.toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' });
  setTimeout(tick, 1000);
})();

// Animate progress bars relative to max value
window.addEventListener('load', function () {
  var fills = document.querySelectorAll('.prog-fill');
  var values = Array.from(fills).map(function (el) { return parseInt(el.dataset.val) || 0; });
  var maxVal = Math.max.apply(null, values.concat([1]));
  fills.forEach(function (el) {
    var val = parseInt(el.dataset.val) || 0;
    var pct = Math.round((val / maxVal) * 100) || 4;
    setTimeout(function () { el.style.width = pct + '%'; }, 200);
  });
});

function initCharts(labels, uData, lData, sLabels, sCounts) {
  var donutColors = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6'];

  // Line chart
  var lineEl = document.getElementById('lineChart');
  if (lineEl && typeof Chart !== 'undefined') {
    new Chart(lineEl, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'New Users',
            data: uData,
            borderColor: '#6366f1',
            backgroundColor: 'rgba(99,102,241,.12)',
            borderWidth: 2.5,
            pointBackgroundColor: '#6366f1',
            pointRadius: 5,
            tension: 0.4,
            fill: true,
          },
          {
            label: 'New Listings',
            data: lData,
            borderColor: '#10b981',
            backgroundColor: 'rgba(16,185,129,.10)',
            borderWidth: 2.5,
            pointBackgroundColor: '#10b981',
            pointRadius: 5,
            tension: 0.4,
            fill: true,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: 'top', labels: { font: { size: 11 }, boxWidth: 10, padding: 14 } },
          tooltip: { mode: 'index', intersect: false },
        },
        scales: {
          y: { beginAtZero: true, ticks: { stepSize: 1 }, grid: { color: 'rgba(0,0,0,.04)' } },
          x: { grid: { display: false } },
        },
      },
    });
  }

  // Donut chart
  var donutEl = document.getElementById('donutChart');
  if (donutEl && typeof Chart !== 'undefined') {
    new Chart(donutEl, {
      type: 'doughnut',
      data: {
        labels: sLabels.length ? sLabels : ['No data'],
        datasets: [{
          data: sCounts.length ? sCounts : [1],
          backgroundColor: sCounts.length ? donutColors : ['#e5e7eb'],
          borderWidth: 3,
          borderColor: '#fff',
          hoverOffset: 8,
        }],
      },
      options: {
        responsive: true,
        cutout: '70%',
        plugins: {
          legend: { display: false },
          tooltip: { callbacks: { label: function (c) { return ' ' + c.label + ': ' + c.parsed; } } },
        },
      },
    });

    // Custom legend
    var leg = document.getElementById('donut-legend');
    if (leg) {
      sLabels.forEach(function (lbl, i) {
        var d = document.createElement('div');
        d.style.cssText = 'display:flex;align-items:center;gap:8px;font-size:12px;';
        d.innerHTML =
          '<span style="width:10px;height:10px;border-radius:3px;background:' + donutColors[i] + ';flex-shrink:0;display:inline-block"></span>' +
          '<span style="color:#6b7280;flex:1">' + lbl + '</span>' +
          '<span style="font-weight:700;color:#111827">' + (sCounts[i] || 0) + '</span>';
        leg.appendChild(d);
      });
    }
  }
}

// Auto-init from embedded JSON data
window.addEventListener('load', function () {
  var el = document.getElementById('skx-chart-data');
  if (!el) return;
  var d = JSON.parse(el.textContent);
  initCharts(d.labels, d.users, d.listings, d.statusLabels, d.statusCounts);
});
