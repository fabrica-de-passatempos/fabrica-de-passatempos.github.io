// Google Analytics (GA4) só depois do aceite, com Consent Mode v2 negado por padrão.
// Sem ID de medição, nada carrega e o banner não aparece.
const GA_ID = ''; // ponytail: preencher com o ID de medição (G-XXXXXXXXXX) do fluxo web do GA4
const CHAVE = 'fp-cookies'; // 'aceito' | 'recusado'

window.dataLayer = window.dataLayer || [];
function gtag() { dataLayer.push(arguments); }
gtag('consent', 'default', { analytics_storage: 'denied', ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied' });

const ler = () => { try { return localStorage.getItem(CHAVE); } catch { return null; } };
const gravar = v => { try { localStorage.setItem(CHAVE, v); } catch {} };

let carregado = false;
function carregarGA() {
  if (carregado) return;
  carregado = true;
  gtag('consent', 'update', { analytics_storage: 'granted' });
  gtag('js', new Date());
  // O GA4 não guarda IP; sinais do Google e personalização de anúncios ficam desligados.
  gtag('config', GA_ID, { allow_google_signals: false, allow_ad_personalization_signals: false });
  const s = document.createElement('script');
  s.async = true;
  s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_ID;
  document.head.appendChild(s);
}

function recusar() {
  gtag('consent', 'update', { analytics_storage: 'denied' });
  // Apaga os cookies do GA que já existirem (_ga, _ga_<id>).
  document.cookie.split(';').map(c => c.split('=')[0].trim()).filter(n => n.startsWith('_ga'))
    .forEach(n => { document.cookie = `${n}=; Max-Age=0; path=/; domain=.${location.hostname}`; document.cookie = `${n}=; Max-Age=0; path=/`; });
}

const banner = document.getElementById('cookies');
function mostrar() { banner.hidden = false; banner.querySelector('button').focus(); }
function escolher(v) {
  gravar(v);
  banner.hidden = true;
  v === 'aceito' ? carregarGA() : recusar();
}

if (GA_ID && banner) {
  banner.querySelector('[data-cookies="aceitar"]').addEventListener('click', () => escolher('aceito'));
  banner.querySelector('[data-cookies="recusar"]').addEventListener('click', () => escolher('recusado'));
  document.getElementById('cookies-pref').hidden = false;
  document.querySelectorAll('[data-cookies="preferencias"]').forEach(a => { a.addEventListener('click', e => { e.preventDefault(); mostrar(); }); });
  const v = ler();
  if (v === 'aceito') carregarGA(); else if (v !== 'recusado') mostrar();

  // Eventos: clique no botão da Play (por jogo, com o utm do link) e primeira vez que o vídeo de cada card toca.
  document.addEventListener('click', e => {
    const a = e.target.closest('a[href*="play.google.com"]');
    if (!a || !carregado) return;
    const u = new URL(a.href);
    const id = u.searchParams.get('id');
    const card = document.querySelector(`.j a[href*="${id}"]`)?.closest('.j');
    gtag('event', 'clique_play', { jogo: card?.querySelector('h3')?.textContent || id, utm_campaign: u.searchParams.get('utm_campaign') || '' });
  });
  const vistos = new Set();
  document.addEventListener('play', e => {
    const v = e.target;
    if (v.tagName !== 'VIDEO' || !carregado || vistos.has(v)) return;
    vistos.add(v);
    gtag('event', 'video_card', { jogo: v.closest('.j')?.querySelector('h3')?.textContent || v.currentSrc.split('/').pop() });
  }, true);
}
