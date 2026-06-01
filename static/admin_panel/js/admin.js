(() => {
  'use strict';

  const body = document.body;
  const modalEl = document.getElementById('apModal');
  const modalTitle = document.getElementById('apModalTitle');
  const modalBody = document.getElementById('apModalBody');
  const toastEl = document.getElementById('apToastFixed');
  const mainEl = document.getElementById('apMainContent');
  const sidebarNav = document.getElementById('apSidebarNav');
  let bsModal = null;

  if (window.htmx) {
    htmx.config.allowScriptTags = true;
    htmx.config.scrollBehavior = 'smooth';
    htmx.config.requestClass = 'ap-htmx-request';
    htmx.config.indicatorClass = 'htmx-request';
  }

  if (modalEl && window.bootstrap) {
    bsModal = bootstrap.Modal.getOrCreateInstance(modalEl);
  }

  function getCookie(name) {
    const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    return match ? decodeURIComponent(match[2]) : '';
  }

  function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content')
      || getCookie('csrftoken')
      || '';
  }

  document.body.addEventListener('htmx:configRequest', (e) => {
    const method = (e.detail.verb || 'GET').toUpperCase();
    if (method !== 'GET') {
      e.detail.headers['X-CSRFToken'] = getCsrfToken();
    }
  });

  document.getElementById('apMenuBtn')?.addEventListener('click', () => {
    body.classList.add('ap-sidebar-open');
  });
  document.getElementById('apSidebarClose')?.addEventListener('click', () => {
    body.classList.remove('ap-sidebar-open');
  });
  document.getElementById('apOverlay')?.addEventListener('click', () => {
    body.classList.remove('ap-sidebar-open');
  });

  document.querySelectorAll('[data-ap-collapse]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const id = btn.getAttribute('data-ap-collapse');
      const sub = document.getElementById(id);
      const group = btn.closest('.ap-nav-group');
      if (!sub) return;
      const open = sub.classList.toggle('show');
      if (group) group.classList.toggle('is-open', open);
    });
  });

  function showToast(msg) {
    if (!toastEl || !msg) return;
    toastEl.textContent = msg;
    toastEl.hidden = false;
    clearTimeout(showToast._t);
    showToast._t = setTimeout(() => { toastEl.hidden = true; }, 2800);
  }

  function parseHxTrigger(xhr) {
    const trig = xhr?.getResponseHeader?.('HX-Trigger');
    if (!trig) return null;
    try {
      return JSON.parse(trig);
    } catch (_) {
      return null;
    }
  }

  function handleHxTrigger(data) {
    if (!data) return;
    if (data.apToast) showToast(data.apToast);
    if (data.apModalClose) closeModal();
    Object.keys(data).forEach((k) => {
      if (k.startsWith('apRefresh')) {
        document.body.dispatchEvent(new Event(k));
      }
    });
  }

  function closeModal() {
    bsModal?.hide();
  }

  function getModalForm(elt) {
    if (!elt) return null;
    if (elt.tagName === 'FORM') return elt;
    return elt.closest('form.ap-glass-form, form.ap-form-modal');
  }

  function fallbackModalSuccess(form, xhr) {
    if (!form || !xhr) return null;
    const st = xhr.status;
    const empty = !xhr.responseText || !String(xhr.responseText).trim();
    if (st !== 204 && !(st >= 200 && st < 300 && empty)) return null;
    const refresh = form.dataset.apRefresh;
    const payload = { apModalClose: true };
    if (refresh) payload[refresh] = true;
    return payload;
  }

  function updateSidebarActive() {
    if (!sidebarNav) return;
    const path = window.location.pathname;
    sidebarNav.querySelectorAll('a.ap-nav-item, .ap-nav-sub a').forEach((a) => {
      const href = a.getAttribute('href');
      if (!href || href === '#') return;
      const active = path === href || (href !== '/dashboard/' && path.startsWith(href));
      a.classList.toggle('active', active);
    });
  }

  function markDeletingRow(elt) {
    const row = elt?.closest?.('tr');
    if (row) row.classList.add('ap-row-removing');
    return row;
  }

  document.body.addEventListener('htmx:afterSwap', (e) => {
    const target = e.detail.target;

    if (target === mainEl) {
      updateSidebarActive();
      initDashboardCharts();
      if (window.innerWidth < 992) body.classList.remove('ap-sidebar-open');
    }

    if (modalBody && target === modalBody) {
      const glassForm = modalBody.querySelector('.ap-glass-form');
      const isGlass = !!glassForm;
      if (modalEl) {
        modalEl.classList.toggle('ap-modal--glass', isGlass);
        modalEl.classList.toggle('ap-modal--wide', isGlass && glassForm.classList.contains('ap-glass-form--wide'));
      }
      if (modalTitle) {
        modalTitle.textContent = isGlass ? '' : (window.AP_MODAL_TITLE || '—');
      }
      bsModal?.show();
    }
  });

  modalEl?.addEventListener('hidden.bs.modal', () => {
    modalEl.classList.remove('ap-modal--glass', 'ap-modal--wide');
    if (modalBody) modalBody.innerHTML = '';
  });

  document.body.addEventListener('apModalClose', closeModal);

  const refreshMap = {
    apRefreshCategories: 'apCategoriesTable',
    apRefreshQuestions: 'apQuestionsTable',
    apRefreshSamples: 'apSamplesTable',
    apRefreshUsers: 'apUsersTable',
    apRefreshSessions: 'apSessionsTable',
    apRefreshAnswers: 'apAnswersTable',
    apRefreshPlans: 'apPlansTable',
    apRefreshOrders: 'apOrdersTable',
    apRefreshSubscriptions: 'apSubscriptionsTable',
    apRefreshCredits: 'apCreditsTable',
    apRefreshContacts: 'apContactsTable',
  };

  function refreshTable(tableId) {
    const el = document.getElementById(tableId);
    const url = el?.getAttribute('data-ap-table-url') || el?.getAttribute('hx-get');
    if (!el || !url || !window.htmx) return;
    const filterForm = document.getElementById('apFilterForm');
    const values = filterForm ? new FormData(filterForm) : null;
    const qs = values ? new URLSearchParams(values).toString() : '';
    const fullUrl = qs ? `${url}?${qs}` : url;
    htmx.ajax('GET', fullUrl, { target: `#${tableId}`, swap: 'innerHTML' });
  }

  Object.keys(refreshMap).forEach((ev) => {
    document.body.addEventListener(ev, () => refreshTable(refreshMap[ev]));
  });

  document.body.addEventListener('htmx:beforeRequest', (e) => {
    const elt = e.detail.elt;
    if (elt?.dataset?.apDelete || elt?.closest?.('[data-ap-delete]')) {
      markDeletingRow(elt);
    }
  });

  function processHtmxResponse(e) {
    if (!e.detail.successful) {
      document.querySelectorAll('.ap-row-removing').forEach((r) => r.classList.remove('ap-row-removing'));
      return;
    }
    const xhr = e.detail.xhr;
    const form = getModalForm(e.detail.elt);
    let data = parseHxTrigger(xhr);
    if (!data) data = fallbackModalSuccess(form, xhr);
    handleHxTrigger(data);
  }

  document.body.addEventListener('htmx:afterRequest', processHtmxResponse);

  document.body.addEventListener('htmx:responseError', () => {
    document.querySelectorAll('.ap-row-removing').forEach((r) => r.classList.remove('ap-row-removing'));
    showToast('خطا در ارتباط با سرور');
  });

  document.querySelectorAll('[hx-get][hx-target="#apModalBody"]').forEach((el) => {
    el.addEventListener('click', () => {
      if (window.innerWidth < 992) body.classList.remove('ap-sidebar-open');
    });
  });

  /* داشبورد: بارگذاری نمودار بعد از ناوبری AJAX */
  let chartsLoading = false;

  function initDashboardCharts() {
    if (!document.getElementById('ap-chart-data')) return;
    if (typeof window.initApDashboardCharts === 'function') {
      window.initApDashboardCharts();
      return;
    }
    if (chartsLoading) return;
    chartsLoading = true;
    const chartsUrl = body.getAttribute('data-ap-charts-js');
    const loadCharts = () => {
      if (!chartsUrl) {
        chartsLoading = false;
        return;
      }
      const s2 = document.createElement('script');
      s2.src = chartsUrl;
      s2.onload = () => {
        chartsLoading = false;
        window.initApDashboardCharts?.();
      };
      s2.onerror = () => { chartsLoading = false; };
      document.body.appendChild(s2);
    };
    if (typeof Chart !== 'undefined') {
      loadCharts();
      return;
    }
    const s1 = document.createElement('script');
    s1.src = 'https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js';
    s1.onload = loadCharts;
    s1.onerror = () => { chartsLoading = false; };
    document.body.appendChild(s1);
  }

  updateSidebarActive();
  initDashboardCharts();
})();
