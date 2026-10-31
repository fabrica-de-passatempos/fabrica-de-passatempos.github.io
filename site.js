// Entrada em cascata ao rolar. Sem JS, ou com movimento reduzido, tudo já aparece.
if (!matchMedia('(prefers-reduced-motion: reduce)').matches && 'IntersectionObserver' in window) {
  document.documentElement.classList.add('js');
  document.querySelectorAll('.bento, .dev, .tl, .sel').forEach(g => [...g.children].forEach((el, i) => el.style.setProperty('--i', i)));
  const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('vis'); io.unobserve(e.target); } }), { rootMargin: '0px 0px -8% 0px' });
  document.querySelectorAll('.sobe').forEach(el => io.observe(el));
}

// Videos dos jogos: parados com movimento reduzido; fora da tela, pausam para poupar bateria.
const vids = document.querySelectorAll('video');
if (matchMedia('(prefers-reduced-motion: reduce)').matches) vids.forEach(v => { v.removeAttribute('autoplay'); v.pause(); });
else if ('IntersectionObserver' in window) {
  const vo = new IntersectionObserver(es => es.forEach(e => e.isIntersecting ? e.target.play().catch(() => {}) : e.target.pause()));
  vids.forEach(v => vo.observe(v));
}
