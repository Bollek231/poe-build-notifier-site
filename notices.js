/* Optional informational notices. Visible at entry, disappear after 10 s or on demand. */
(() => {
  'use strict';
  const notices = [...document.querySelectorAll('[data-site-notice]')];
  if (!notices.length) return;
  function hide(notice) {
    if (notice.dataset.closed === 'true') return;
    notice.dataset.closed = 'true';
    notice.classList.add('site-notice--closing');
    window.setTimeout(() => { notice.hidden = true; }, 260);
  }
  notices.forEach(notice => {
    const close = notice.querySelector('[data-notice-close]');
    if (close) close.addEventListener('click', () => hide(notice));
    window.setTimeout(() => hide(notice), 10000);
  });
})();