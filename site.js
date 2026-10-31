// Entrada em cascata ao rolar. Sem JS, ou com movimento reduzido, tudo já aparece.
if (!matchMedia('(prefers-reduced-motion: reduce)').matches && 'IntersectionObserver' in window) {
  document.documentElement.classList.add('js');
  document.querySelectorAll('.bento, .dev, .tl, .sel').forEach(g => [...g.children].forEach((el, i) => el.style.setProperty('--i', i)));
  const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('vis'); io.unobserve(e.target); } }), { rootMargin: '0px 0px -8% 0px' });
  document.querySelectorAll('.sobe').forEach(el => io.observe(el));
}
