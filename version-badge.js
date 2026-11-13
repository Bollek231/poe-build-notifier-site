/* Read the canonical, public VERSION file; preserve the HTML fallback when offline. */
(() => {
  const badges = document.querySelectorAll('.site-version');
  if (!badges.length) return;
  const url = new URL('VERSION', window.location.href);
  url.searchParams.set('t', String(Date.now()));
  fetch(url.toString(), { cache: 'no-store' })
    .then(response => {
      if (!response.ok) throw new Error('Version unavailable');
      return response.text();
    })
    .then(value => {
      const version = value.trim();
      if (!/^\d+\.\d+\.\d+[a-z]?$/i.test(version)) return;
      badges.forEach(el => { el.textContent = 'v' + version; });
    })
    .catch(() => { /* Keep bundled version if the network is unavailable. */ });
})();
