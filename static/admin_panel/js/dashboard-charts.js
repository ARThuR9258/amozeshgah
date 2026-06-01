(() => {
  'use strict';

  const el = document.getElementById('ap-chart-data');
  if (!el || typeof Chart === 'undefined') return;

  const data = JSON.parse(el.textContent);

  function faNum(n) {
    return Number(n).toLocaleString('fa-IR');
  }

  function gradient(ctx, c1, c2) {
    const g = ctx.createLinearGradient(0, 0, 0, 280);
    g.addColorStop(0, c1);
    g.addColorStop(1, c2);
    return g;
  }

  Chart.defaults.font.family = 'Vazirmatn, Tahoma, sans-serif';
  Chart.defaults.color = '#64748b';
  Chart.defaults.plugins.legend.display = false;
  Chart.defaults.plugins.tooltip.rtl = true;
  Chart.defaults.plugins.tooltip.titleAlign = 'right';
  Chart.defaults.plugins.tooltip.bodyAlign = 'right';
  Chart.defaults.scale.grid.color = 'rgba(148, 163, 184, 0.15)';

  const totals = data.totals || {};
  const salesEl = document.getElementById('apTotalSales');
  if (salesEl) salesEl.textContent = faNum(totals.sales_period || 0);
  const usersEl = document.getElementById('apTotalUsers');
  if (usersEl) usersEl.textContent = `${faNum(totals.users_period || 0)} نفر`;
  const quizEl = document.getElementById('apTotalQuizzes');
  if (quizEl) quizEl.textContent = `${faNum(totals.quizzes_period || 0)} بار`;

  const sharedLineOpts = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'index', intersect: false },
    plugins: {
      tooltip: {
        callbacks: {
          label(ctx) {
            const v = ctx.parsed.y;
            const suffix = ctx.dataset.label.includes('تومان') ? ' تومان' : '';
            return `${ctx.dataset.label}: ${faNum(v)}${suffix}`;
          },
        },
      },
    },
    scales: {
      x: { grid: { display: false }, ticks: { maxRotation: 0, autoSkipPadding: 12 } },
      y: { beginAtZero: true, ticks: { callback: (v) => faNum(v) } },
    },
  };

  const salesCtx = document.getElementById('chartSales');
  if (salesCtx) {
    const sctx = salesCtx.getContext('2d');
    new Chart(salesCtx, {
      type: 'line',
      data: {
        labels: data.labels,
        datasets: [{
          label: 'فروش (تومان)',
          data: data.sales_daily,
          borderColor: '#10b981',
          backgroundColor: gradient(sctx, 'rgba(16, 185, 129, 0.35)', 'rgba(16, 185, 129, 0.02)'),
          fill: true,
          tension: 0.42,
          borderWidth: 3,
          pointRadius: 4,
          pointHoverRadius: 7,
          pointBackgroundColor: '#fff',
          pointBorderColor: '#10b981',
          pointBorderWidth: 2,
        }],
      },
      options: sharedLineOpts,
    });
  }

  const usersCtx = document.getElementById('chartUsers');
  if (usersCtx) {
    const uctx = usersCtx.getContext('2d');
    new Chart(usersCtx, {
      type: 'line',
      data: {
        labels: data.labels,
        datasets: [{
          label: 'کاربر جدید',
          data: data.users_daily,
          borderColor: '#6366f1',
          backgroundColor: gradient(uctx, 'rgba(99, 102, 241, 0.3)', 'rgba(99, 102, 241, 0.02)'),
          fill: true,
          tension: 0.42,
          borderWidth: 2.5,
          pointRadius: 3,
        }],
      },
      options: sharedLineOpts,
    });
  }

  const quizActCtx = document.getElementById('chartQuizActivity');
  if (quizActCtx) {
    new Chart(quizActCtx, {
      type: 'bar',
      data: {
        labels: data.labels,
        datasets: [{
          label: 'شرکت در آزمون',
          data: data.quizzes_daily,
          backgroundColor: 'rgba(139, 92, 246, 0.75)',
          hoverBackgroundColor: '#8b5cf6',
          borderRadius: 8,
          borderSkipped: false,
        }],
      },
      options: sharedLineOpts,
    });
  }

  function doughnut(id, block, emptyText) {
    const canvas = document.getElementById(id);
    if (!canvas || !block) return;
    const sum = (block.values || []).reduce((a, b) => a + b, 0);
    if (!sum) {
      canvas.parentElement.classList.add('ap-dash-chart-empty');
      canvas.parentElement.innerHTML = `<div class="ap-dash-chart-empty-msg"><i class="fas fa-chart-pie"></i><span>${emptyText}</span></div>`;
      return;
    }
    new Chart(canvas, {
      type: 'doughnut',
      data: {
        labels: block.labels,
        datasets: [{
          data: block.values,
          backgroundColor: block.colors,
          borderWidth: 0,
          hoverOffset: 10,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '68%',
        plugins: {
          legend: {
            display: true,
            position: 'bottom',
            rtl: true,
            labels: { padding: 14, usePointStyle: true, pointStyle: 'circle', font: { size: 11 } },
          },
          tooltip: {
            callbacks: {
              label(ctx) {
                const pct = Math.round((ctx.parsed / sum) * 100);
                return `${ctx.label}: ${faNum(ctx.parsed)} (${faNum(pct)}٪)`;
              },
            },
          },
        },
      },
    });
  }

  doughnut('chartOrders', data.orders, 'سفارشی ثبت نشده');
  doughnut('chartSubscriptions', data.subscriptions, 'کاربری نیست');
  doughnut('chartQuizStatus', data.quizzes, 'جلسه\u200cای نیست');

  const plans = data.top_plans || {};
  const planCard = document.getElementById('apPlanCard');
  const planCtx = document.getElementById('chartPlans');
  if (planCtx && (!plans.labels || !plans.labels.length)) {
    if (planCard) planCard.style.display = 'none';
  } else if (planCtx && plans.labels && plans.labels.length) {
    new Chart(planCtx, {
      type: 'bar',
      data: {
        labels: plans.labels,
        datasets: [{
          label: 'درآمد (تومان)',
          data: plans.values,
          backgroundColor: ['#6366f1', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ec4899'],
          borderRadius: 10,
          borderSkipped: false,
        }],
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => `${faNum(ctx.parsed.x)} تومان`,
            },
          },
        },
        scales: {
          x: {
            beginAtZero: true,
            ticks: { callback: (v) => faNum(v) },
          },
          y: { grid: { display: false } },
        },
      },
    });
  }
})();
