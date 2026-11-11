'use strict';
const format = new Intl.NumberFormat('pt-BR');
function ranking(id, rows, field, empty) {
  const list = document.getElementById(id);
  list.replaceChildren();
  if (!rows.length) {
    const item = document.createElement('li');
    item.className = 'empty';
    item.textContent = empty;
    list.append(item);
    return;
  }
  const max = Math.max(1, ...rows.map(row => row[field]));
  rows.forEach((row, index) => {
    const item = document.createElement('li');
    const heading = document.createElement('div');
    heading.className = 'row';
    const label = document.createElement('div');
    const title = document.createElement('strong');
    title.textContent = `${index + 1}. ${row.titulo || row.nome}`;
    label.append(title);
    if (row.jogo) {
      const game = document.createElement('small');
      game.textContent = row.jogo;
      label.append(game);
    }
    const value = document.createElement('span');
    value.className = 'count';
    value.textContent = format.format(row[field]);
    heading.append(label, value);
    const track = document.createElement('div');
    track.className = 'track';
    track.setAttribute('aria-hidden', 'true');
    const bar = document.createElement('div');
    bar.style.width = `${100 * row[field] / max}%`;
    track.append(bar);
    item.append(heading, track);
    list.append(item);
  });
}
async function load() {
  try {
    const response = await fetch('dados.json', {cache: 'no-store'});
    if (!response.ok) throw new Error('Falha ao carregar dados');
    const data = await response.json();
    document.getElementById('downloads').textContent = data.downloads_totais === null ? '—' : format.format(data.downloads_totais);
    document.getElementById('views').textContent = data.visualizacoes_totais === null ? '—' : format.format(data.visualizacoes_totais);
    ranking('apps', data.jogos, 'downloads', 'Coleta de downloads pendente.');
    ranking('posts', data.posts, 'views', 'Nenhum post com contagem confirmada.');
    const date = new Date(data.coletado_em);
    document.getElementById('coleta').textContent = 'Coleta: ' + date.toLocaleDateString('pt-BR', {timeZone: 'America/Sao_Paulo'});
  } catch (error) {
    const alert = document.getElementById('erro');
    alert.hidden = false;
    alert.textContent = 'Não foi possível carregar os números. Tente novamente mais tarde.';
    document.getElementById('coleta').textContent = 'Coleta indisponível';
  }
}
load();
