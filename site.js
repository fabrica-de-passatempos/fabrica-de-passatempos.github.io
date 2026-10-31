// Entrada em cascata ao rolar. Sem JS, ou com movimento reduzido, tudo já aparece.
if (!matchMedia('(prefers-reduced-motion: reduce)').matches && 'IntersectionObserver' in window) {
  document.documentElement.classList.add('js');
  document.querySelectorAll('.bento, .dev, .tl, .sel').forEach(g => [...g.children].forEach((el, i) => el.style.setProperty('--i', i)));
  const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('vis'); io.unobserve(e.target); } }), { rootMargin: '0px 0px -8% 0px' });
  document.querySelectorAll('.sobe').forEach(el => io.observe(el));
}

// Vídeos pausam fora da tela e respeitam mudanças de movimento reduzido.
const movimento = matchMedia('(prefers-reduced-motion: reduce)');
const vids = document.querySelectorAll('video');
const visiveis = new Set();
const falharam = new WeakSet();
function atualizarVideo(v) {
  const logo = v.hasAttribute('data-logo-animado');
  if (movimento.matches || !visiveis.has(v) || (logo && (v.ended || falharam.has(v)))) {
    v.pause();
    if (logo) v.hidden = true;
    return;
  }
  if (logo) v.hidden = false;
  v.play().catch(error => { if (logo && error?.name !== 'AbortError') { falharam.add(v); v.hidden = true; } });
}
vids.forEach(v => {
  v.removeAttribute('autoplay');
  if (v.hasAttribute('data-logo-animado')) {
    v.addEventListener('ended', () => { v.hidden = true; });
    v.addEventListener('error', () => { falharam.add(v); v.hidden = true; }, true);
  }
});
if ('IntersectionObserver' in window) {
  const vo = new IntersectionObserver(es => es.forEach(e => {
    const v = e.target.tagName === 'VIDEO' ? e.target : e.target.querySelector('video');
    if (e.isIntersecting) visiveis.add(v); else visiveis.delete(v);
    atualizarVideo(v);
  }));
  // O logo começa oculto sobre o pôster; observar o contêiner mantém sua área visível.
  vids.forEach(v => vo.observe(v.hasAttribute('data-logo-animado') ? v.parentElement : v));
} else {
  vids.forEach(v => { visiveis.add(v); atualizarVideo(v); });
}
movimento.addEventListener('change', () => vids.forEach(atualizarVideo));

// Retratos só animam visíveis; o src original também atende sem JS ou sem observador.
const retratos = document.querySelectorAll('img[data-retrato-animado]');
if (retratos.length && 'IntersectionObserver' in window && window.CSS?.supports('aspect-ratio', '1')) {
  const estados = new Map([...retratos].map(im => [im, { parado: im.getAttribute('src'), visivel: false, falhou: false }]));
  function atualizarRetrato(im) {
    const estado = estados.get(im);
    const animar = estado.visivel && !document.hidden && !movimento.matches && !estado.falhou;
    const src = animar ? im.dataset.retratoAnimado : estado.parado;
    if (im.getAttribute('src') !== src) im.setAttribute('src', src);
    im.classList.toggle('retrato-em-movimento', animar && im.dataset.retratoAnimado.endsWith('.png'));
  }
  const ro = new IntersectionObserver(es => es.forEach(e => {
    estados.get(e.target).visivel = e.isIntersecting;
    atualizarRetrato(e.target);
  }));
  retratos.forEach(im => {
    im.addEventListener('error', () => {
      if (im.getAttribute('src') !== im.dataset.retratoAnimado) return;
      estados.get(im).falhou = true;
      atualizarRetrato(im);
    });
    ro.observe(im);
  });
  movimento.addEventListener('change', () => retratos.forEach(atualizarRetrato));
  document.addEventListener('visibilitychange', () => retratos.forEach(atualizarRetrato));
}
