(() => {
  'use strict';

  const body = document.body;
  const modalEl = document.getElementById('apModal');
  const modalTitle = document.getElementById('apModalTitle');
  const modalBody = document.getElementById('apModalBody');
  const toastEl = document.getElementById('apToastFixed');
  let bsModal = null;

  if (modalEl && window.bootstrap) {
    bsModal = bootstrap.Modal.getOrCreateInstance(modalEl);
  }

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

  document.body.addEventListener('htmx:afterSwap', (e) => {
    if (modalBody && e.detail.target === modalBody) {
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
  });

  document.body.addEventListener('apModalClose', () => bsModal?.hide());

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
  Object.keys(refreshMap).forEach((ev) => {
    document.body.addEventListener(ev, () => {
      const el = document.getElementById(refreshMap[ev]);
      const url = el?.getAttribute('hx-get');
      if (el && url && window.htmx) {
        htmx.ajax('GET', url, { target: `#${refreshMap[ev]}`, swap: 'innerHTML' });
      }
    });
  });

  document.body.addEventListener('htmx:afterRequest', (e) => {
    try {
      const trig = e.detail.xhr.getResponseHeader('HX-Trigger');
      if (!trig) return;
      const data = JSON.parse(trig);
      if (data.apToast) showToast(data.apToast);
      if (data.apModalClose) document.body.dispatchEvent(new Event('apModalClose'));
      Object.keys(data).forEach((k) => {
        if (k.startsWith('apRefresh')) {
          document.body.dispatchEvent(new Event(k));
        }
      });
    } catch (_) {}
  });

  document.querySelectorAll('[hx-get][hx-target="#apModalBody"]').forEach((el) => {
    el.addEventListener('click', () => {
      if (window.innerWidth < 992) body.classList.remove('ap-sidebar-open');
    });
  });
})();
