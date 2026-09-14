(() => {
  // 寬螢幕:左側章節欄標出目前讀到的章
  const railLinks = new Map();
  document.querySelectorAll('.rail a').forEach(a => railLinks.set(decodeURIComponent(a.getAttribute('href').slice(1)), a));
  const heads = [...document.querySelectorAll('.content h2[id]')];
  let current = null;
  const update = () => {
    const line = window.innerHeight * 0.3;
    let best = heads.length ? heads[0].id : null;
    for (const h of heads) {
      if (h.getBoundingClientRect().top <= line) best = h.id;
      else break;
    }
    if (best === current) return;
    current = best;
    railLinks.forEach((a, id) => a.setAttribute('aria-current', id === best ? 'true' : 'false'));
  };
  if ('IntersectionObserver' in window && heads.length) {
    const io = new IntersectionObserver(update, { rootMargin: '0px 0px -70% 0px' });
    heads.forEach(h => io.observe(h));
  }
  update();

  // 手機:點目錄裡的章節後收起目錄;浮動「目錄」按鈕打開目錄
  const toc = document.getElementById('toc-mobile');
  if (toc) {
    toc.addEventListener('click', e => { if (e.target.closest('a')) toc.open = false; });
    const fab = document.querySelector('.toc-fab');
    if (fab) fab.addEventListener('click', () => { toc.open = true; });
  }
})();
