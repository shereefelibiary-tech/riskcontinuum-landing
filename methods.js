/* Progressive enhancement only; all methods and tables are in the HTML. */
(() => {
  const links = [...document.querySelectorAll('.methods-nav a[href^="#"]')];
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      const entry = entries.filter(item => item.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)[0];
      if (!entry) return;
      links.forEach(link => {
        if (link.hash === `#${entry.target.id}`) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      });
    }, { rootMargin: '-12% 0px -65% 0px' });
    document.querySelectorAll('.method-section').forEach(section => observer.observe(section));
  }
  const openForHash = () => {
    const target = document.getElementById(decodeURIComponent(location.hash.slice(1)));
    if (!target) return;
    const detail = target.closest('details');
    if (detail) detail.open = true;
  };
  window.addEventListener('hashchange', openForHash);
  openForHash();
  let printState = [];
  window.addEventListener('beforeprint', () => {
    printState = [...document.querySelectorAll('.method-detail')].map(detail => [detail, detail.open]);
    printState.forEach(([detail]) => { detail.open = true; });
  });
  window.addEventListener('afterprint', () => printState.forEach(([detail, open]) => { detail.open = open; }));
})();
