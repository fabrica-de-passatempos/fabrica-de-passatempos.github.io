#!/usr/bin/env python3
"""Gera os dois totais e rankings a partir de contadores agregados com fonte."""
import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
NETWORKS = {'Instagram', 'Facebook', 'YouTube', 'TikTok', 'Meta (IG+FB)'}


def privacy(obj):
    """O repositório é público, mesmo que a página não tenha link no menu."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key.lower() in {'email', 'token', 'senha', 'cookie', 'api_key', 'jogador_id', 'conta', 'pagamento'}:
                raise ValueError('Campo privado recusado: ' + key)
            privacy(value)
    elif isinstance(obj, list):
        for value in obj:
            privacy(value)
    elif isinstance(obj, str):
        if re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|sk_[a-z0-9]{16,}|gh[pousr]_[a-zA-Z0-9]{20,}|AIza[\w-]{20,}|Bearer\s+\S+', obj):
            raise ValueError('Dado privado recusado')
        if obj.startswith(('http://', 'https://')):
            u = urlsplit(obj)
            if u.scheme != 'https' or u.username or u.password or u.hostname not in {
                'github.com', 'youtu.be', 'www.youtube.com', 'www.instagram.com',
                'www.facebook.com', 'www.tiktok.com', 'play.google.com',
            } or '/console/' in u.path:
                raise ValueError('Somente links públicos aprovados')


def counter(value):
    # Contadores são inteiros; 1.213 numérico não pode virar 1 view silenciosamente.
    if value is None:
        return None
    if isinstance(value, str) and re.fullmatch(r'(?:\d+|\d{1,3}(?:\.\d{3})+)', value):
        value = int(value.replace('.', ''))
    if type(value) is not int or value < 0:
        raise ValueError('Contador deve ser inteiro não negativo ou null')
    return value


def observed(row):
    if not row.get('fonte') or not row.get('coletado_em'):
        return False
    datetime.fromisoformat(row['coletado_em'])
    return True


def build(source):
    privacy(source)
    datetime.fromisoformat(source['coletado_em'])
    games = []
    published = [g for g in source['jogos'] if g['publicado'] is True]
    if len({g['nome'] for g in source['jogos']}) != len(source['jogos']):
        raise ValueError('Jogo duplicado')
    for game in published:
        value = counter(game['downloads'])
        if value is not None and observed(game):
            games.append(dict(nome=game['nome'], downloads=value))
    pieces = {p['id']: p for p in source['pecas']}
    if len(pieces) != len(source['pecas']):
        raise ValueError('Peça duplicada')
    latest = {}
    for post in source['posts']:
        value = counter(post['views'])
        if post['rede'] not in NETWORKS or not post.get('id') or post.get('peca') not in pieces:
            raise ValueError('Publicação sem rede, ID ou peça válida')
        if value is None or not observed(post):
            continue
        key = (post['rede'], post['id'])
        previous = latest.get(key)
        if previous and previous['peca'] != post['peca']:
            raise ValueError('Mesmo post associado a duas peças')
        if previous and previous['coletado_em'] == post['coletado_em'] and counter(previous['views']) != value:
            raise ValueError('Contadores conflitantes na mesma coleta')
        if not previous or datetime.fromisoformat(post['coletado_em']) > datetime.fromisoformat(previous['coletado_em']):
            latest[key] = post
    combined = {p['peca'] for p in latest.values() if p['rede'] == 'Meta (IG+FB)'}
    if any(p['peca'] in combined and p['rede'] in {'Instagram', 'Facebook'} for p in latest.values()):
        raise ValueError('Meta combinado sobrepõe contador individual da mesma peça')
    totals = {}
    for post in latest.values():
        totals[post['peca']] = totals.get(post['peca'], 0) + counter(post['views'])
    posts = [dict(id=key, titulo=pieces[key]['titulo'], jogo=pieces[key]['jogo'], views=value)
             for key, value in totals.items() if pieces[key].get('fonte')]
    return dict(schema=2, coletado_em=source['coletado_em'],
                downloads_totais=sum(g['downloads'] for g in games) if published and len(games) == len(published) else None,
                visualizacoes_totais=sum(counter(p['views']) for p in latest.values()) if latest else None,
                jogos=sorted(games, key=lambda g: (-g['downloads'], g['nome']))[:10],
                posts=sorted(posts, key=lambda p: (-p['views'], p['id']))[:10])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fonte', type=Path, default=ROOT/'fontes/observacoes.json')
    args = parser.parse_args()
    data = build(json.loads(args.fonte.read_text(encoding='utf-8')))
    target = ROOT/'dados.json'
    pending = target.with_suffix('.tmp')
    pending.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    pending.replace(target)
    print('dados.json: %d apps e %d peças no ranking' % (len(data['jogos']), len(data['posts'])))


if __name__ == '__main__':
    main()
