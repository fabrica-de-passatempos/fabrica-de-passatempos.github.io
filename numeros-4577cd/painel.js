'use strict';
const $ = id => document.getElementById(id);
const fmt = value => value == null ? 'ND' : typeof value === 'number' ? new Intl.NumberFormat('pt-BR', {maximumFractionDigits:2}).format(value) : String(value);
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const date = value => value ? esc(value.replace('T', ' ').replace(/:\d{2}(?:\.\d+)?-03:00$/, ' BRT')) : 'ND (sem coleta)';
const meta = m => `<div class="meta"><b>Coleta:</b> ${date(m.coletado_em)}<br><b>Fonte:</b> ${esc(m.fonte)}<br><b>Período:</b> ${esc(m.periodo)}${m.nota ? '<br>'+esc(m.nota) : ''}</div>`;
const metric = (label, m) => `<article class="metric"><span class="label">${esc(label)}</span><strong class="value ${m.valor == null ? 'nd' : ''}">${esc(fmt(m.valor))}</strong><details><summary>Fonte e período</summary>${meta(m)}</details></article>`;
const safeLink = url => { try { const u = new URL(url); return u.protocol === 'https:' && ['github.com','youtu.be','www.youtube.com','www.instagram.com','www.facebook.com','www.tiktok.com','play.google.com'].includes(u.hostname) && !u.username && !u.password ? esc(u.href) : null; } catch { return null; } };
const link = (url, label) => safeLink(url) ? `<a href="${safeLink(url)}" target="_blank" rel="noopener noreferrer">${esc(label)}</a>` : `<span class="muted">${esc(label)}: ND</span>`;
let state;
function renderPosts() {
 const network = $('rede').value, direction = $('ordem').value;
 const rows = state.posts.filter(p => p.corte.startsWith($('coleta-posts').value) && (!network || p.rede === network)).slice().sort((a,b) => {
  if (a.views == null) return b.views == null ? 0 : 1;
  if (b.views == null) return -1;
  return direction === 'asc' ? a.views-b.views : b.views-a.views;
 });
 $('post-count').textContent = `${rows.length} posts na amostra histórica. Ordenação por contador; não compara desempenho entre redes.`;
 $('post-list').innerHTML = rows.map(p => `<article class="post"><span class="tag">${esc(p.rede)}</span><h3>${esc(p.pauta)}</h3><p class="muted">${esc(p.jogo)} · ${esc(p.formato)}</p><span class="views">${esc(fmt(p.views))}</span> views<div class="post-stats">${[['Curtidas','likes'],['Comentários','comentarios'],['Compart.','shares'],['Salvos','saves']].map(([l,k])=>`<span>${l}: <b>${esc(fmt(p[k]))}</b></span>`).join('')}</div>${link(p.permalink,'Ver post')}<details><summary>Coleta e limites</summary><div class="meta"><b>Publicado:</b> ${date(p.publicado_em)}<br><b>Coleta:</b> ${date(p.corte)}<br><b>Fonte:</b> ${esc(p.fonte)}<br><b>Janela:</b> ${esc(p.serie)}<br>${esc(p.nota)}</div></details></article>`).join('');
}
function render(d) {
 state = d;
 $('coleta-posts').innerHTML=[...new Set(d.posts.map(p=>p.corte.slice(0,10)))].sort().reverse().map(day=>`<option value="${esc(day)}">${esc(day)}</option>`).join('');
 $('atualizacao').textContent = `Consolidado: ${d.coletado_em.replace('T',' ')} · Datas de coleta em cada indicador`;
 const labels = {publicados:'Jogos publicados',revisao:'Primeiro lançamento em revisão',desenvolvimento:'Em desenvolvimento',seguidores:'Seguidores + inscritos¹',instalacoes:'Instalações totais',avaliacao:'Avaliação ponderada',receita:'Receita do estúdio'};
 $('macro').innerHTML = Object.entries(labels).map(([k,l])=>metric(l,d.estudio[k])).join('')+'<article class="metric"><span class="label">¹ Soma de perfis</span><p>Uma pessoa pode seguir mais de uma rede.</p><p class="meta">Sem deduplicação de audiência. Não equivale a jogadores.</p></article>';
 const fields = {instalacoes:'Instalações',ativos:'Ativos (escopo na fonte)',avaliacao:'Avaliação média',numero_avaliacoes:'Nº de avaliações',retencao_d1:'Retenção D1',retencao_d7:'Retenção D7',receita:'Receita',versao:'Versão na loja'};
 $('game-list').innerHTML = d.jogos.map(g=>`<article class="game"><div class="game-top"><h3>${esc(g.nome)}</h3><span class="tag ${g.etapa==='Publicado'?'live':''}">${esc(g.etapa)}</span></div><p>${esc(g.status_loja.valor)}</p><details><summary>Fonte do status</summary>${meta(g.status_loja)}</details><dl>${Object.entries({...fields,...Object.fromEntries(Object.keys(g.adicionais||{}).map(k=>[k,k]))}).map(([k,l])=>`<div class="data-row"><dt>${l}</dt><dd>${esc(fmt((g[k]||g.adicionais[k]).valor))}</dd><div class="meta">${date((g[k]||g.adicionais[k]).coletado_em)} · ${esc((g[k]||g.adicionais[k]).fonte)} · ${esc((g[k]||g.adicionais[k]).periodo)+' · '+esc((g[k]||g.adicionais[k]).nota||'')}</div></div>`).join('')}</dl></article>`).join('');
 $('network-list').innerHTML = d.redes.map(n=>`<article class="network"><h3>${esc(n.rede)}</h3><div class="big">${esc(fmt(n.seguidores.valor))}</div><p class="muted">${n.rede==='YouTube'?'Inscritos':'Seguidores'}</p>${meta(n.seguidores)}<hr><p>Views: <b>${esc(fmt(n.views.valor))}</b>${n.views.rotulo?' · '+esc(n.views.rotulo):''}</p>${meta(n.views)}<p>Alcance: <b>${esc(fmt(n.alcance.valor))}</b></p><details><summary>Fonte do alcance</summary>${meta(n.alcance)}</details>${n.publico?'<p>Público / espectadores: <b>'+esc(fmt(n.publico.valor))+'</b></p>'+meta(n.publico):''}</article>`).join('');
 $('medians').innerHTML = d.medianas_72h.length ? d.medianas_72h.map(m=>`<p>${esc(m.rede)} · ${esc(m.formato)} · base ${esc(m.base)} · n=${m.n} · M72=${fmt(m.mediana)} · G do perfil=${fmt(m.gatilho)} (M72 perfil=${fmt(m.mediana_perfil)}, n=${m.n_perfil})<br><span class="meta">${date(m.coletado_em)} · ${esc(m.fonte)}</span></p>`).join('') : '<p class="notice"><strong>M72: ND · G: ND · n = 0 cortes72h elegíveis.</strong><br>Os snapshots acumulados não fecham essa base.</p>';
 const prodLabels = {prs_mergeados:'PRs mergeados',testes:'Testes aprovados',videos_aprovados:'Vídeos aprovados no lote',flow_creditos_mes:'Flow · créditos no mês',flow_creditos_lote:'Flow · créditos E1-A',elevenlabs_caracteres_mes:'ElevenLabs · caracteres no mês',elevenlabs_creditos_mes:'ElevenLabs · créditos no mês',elevenlabs_requisicoes_mes:'ElevenLabs · requisições no mês',receita_admob_mtd:'AdMob · estimado MTD',testes_painel:'Testes deste painel/site'};
 $('production-list').innerHTML = Object.entries(prodLabels).map(([k,l])=>metric(l,d.producao[k])).join('');
 $('inventory').innerHTML = `<p>${d.cobertura.posts} snapshots no histórico, incluindo coletas repetidas. Abaixo, inventário atual de10/11; não somar como peças únicas.</p>`+Object.entries(d.inventario_atual||{}).map(([net,v])=>`<p><b>${esc(net)}</b> · Publicados: ${esc(fmt(v.publicados.valor))} · Agendados: ${esc(fmt(v.agendados.valor))}</p><details><summary>Escopo, fonte e divergências</summary>${meta(v.publicados)}${meta(v.agendados)}</details>`).join('');
 $('schedule-list').innerHTML = d.agendamentos.map(p=>`<article class="schedule"><span class="tag">${esc(p.rede)}</span><h3>${esc(p.jogo)}</h3><p>${esc(p.data)} · <strong>${esc(fmt(p.hora))} BRT</strong></p><p class="meta">ID ${esc(p.id)} · ${esc(p.IA)}<br>Coleta ${date(p.coletado_em)}<br>Fonte ${esc(p.fonte)}</p>${p.link?link(p.link,'Link do vídeo'):''}</article>`).join('');
 $('pending-list').innerHTML = d.pendencias.map(p=>`<article><h3>${esc(p.fonte)}</h3><p>${esc(p.campos)}</p><p class="meta">${esc(p.periodo)}</p></article>`).join('');
 $('source-list').innerHTML = d.fontes_importadas.map(f=>`<p class="meta"><b>${esc(f.arquivo)}</b> · ${esc(f.coleta)}<br>${esc(f.metodo)}</p>`).join('');
 renderPosts();
}
$('coleta-posts').addEventListener('change',()=>{if(state)renderPosts();});
$('rede').addEventListener('change',()=>{if(state)renderPosts();});
$('ordem').addEventListener('change',()=>{if(state)renderPosts();});
fetch('dados.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error('HTTP '+r.status);return r.json();}).then(render).catch(()=>{
 $('atualizacao').textContent='Dados indisponíveis';
 $('erro').hidden=false;
 $('erro').textContent='Não foi possível carregar dados.json. Recarregue a página ou confira o arquivo de dados. Nenhum número foi presumido como zero.';
});
