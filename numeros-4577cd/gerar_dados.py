#!/usr/bin/env python3
"""Regenera somente dados agregados aprovados; nunca lê login, cookies ou Keychain."""
import argparse
import csv
import json
import math
import re
import statistics
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
REQUIRED = {'valor', 'coletado_em', 'fonte', 'periodo'}


def validate(data):
    """Recusa valores inválidos e dados de conta antes de escrever no site público."""
    def visit(obj):
        if isinstance(obj, dict):
            if 'valor' in obj:
                if not REQUIRED <= obj.keys():
                    raise ValueError('Métrica sem fonte, data ou período')
                value = obj['valor']
                if value is not None and not obj['coletado_em']:
                    raise ValueError('Número conhecido sem data da coleta')
                if isinstance(value, (int, float)) and (isinstance(value, bool) or not math.isfinite(value) or value < 0):
                    raise ValueError('Métrica numérica inválida')
            for k, v in obj.items():
                if k.lower() in {'email', 'token', 'senha', 'cookie', 'api_key', 'jogador_id', 'conta', 'pagamento'}:
                    raise ValueError('Campo privado recusado: ' + k)
                visit(v)
        elif isinstance(obj, list):
            for v in obj:
                visit(v)
        elif isinstance(obj, str):
            if re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', obj):
                raise ValueError('E-mail recusado')
            if re.search(r'(?:sk_[a-z0-9]{16,}|gh[pousr]_[a-zA-Z0-9]{20,}|AIza[\w-]{20,}|Bearer\s+\S+)', obj):
                raise ValueError('Possível credencial recusada')
            if obj.startswith(('http://', 'https://')):
                u = urlsplit(obj)
                if u.scheme != 'https' or u.username or u.password or u.hostname not in {
                    'github.com', 'youtu.be', 'www.youtube.com', 'www.instagram.com',
                    'www.facebook.com', 'www.tiktok.com', 'play.google.com',
                } or '/console/' in u.path:
                    raise ValueError('Somente links públicos aprovados: ' + obj)
    visit(data)
    for post in data['posts']:
        if not post.get('corte') or not post.get('fonte'):
            raise ValueError('Post sem coleta/fonte')
        for field in ['views', 'likes', 'comentarios', 'shares', 'saves']:
            v = post.get(field)
            if v is not None and (isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or v < 0):
                raise ValueError('Contador de post inválido')
    unique = [(p['rede'], p['id']) for p in data['agendamentos']]
    if len(unique) != len(set(unique)):
        raise ValueError('Agendamento duplicado')


def metric(value, source, collected, period, note=''):
    return dict(valor=value, fonte=source, coletado_em=collected, periodo=period, nota=note)


def median72(posts):
    """G usa a mediana do perfil; formatos aparecem como detalhamento da mesma base."""
    unique = {}
    for p in posts:
        if p.get('corte_tipo') == '72h' and isinstance(p.get('views'), (int, float)) and p.get('base_72h'):
            key = (p['rede'], p['base_72h'], p['id'])
            if key not in unique or p['corte'] > unique[key]['corte']:
                unique[key] = p
    profiles = {}
    for p in unique.values():
        profiles.setdefault((p['rede'],p['base_72h']),[]).append(p)
    rows=[]
    for (network,base),sample in sorted(profiles.items()):
        profile_median=statistics.median(p['views'] for p in sample)
        groups={'Perfil (todos os formatos)':sample}
        for p in sample:
            groups.setdefault(p['formato'],[]).append(p)
        for form,group in groups.items():
            rows.append(dict(rede=network,formato=form,base=base,n=len(group),
                mediana=statistics.median(p['views'] for p in group),
                mediana_perfil=profile_median,n_perfil=len(sample),gatilho=5*profile_median,
                coletado_em=max(p['corte'] for p in group),
                fonte='Cortes72h declarados: '+', '.join(p['id'] for p in group)))
    return rows


def build(source):
    validate(source)
    data = dict(source)
    date = source['coletado_em']
    games = Counter(g['etapa'] for g in data['jogos'])
    scope = 'Sete jogos do portfólio; status documental, não telemetria de loja'
    data['estudio'] = {
        'publicados': metric(games['Publicado'], 'Play Console: status por jogo, coleta10/11', date, scope),
        'revisao': metric(games['Em revisão'], 'Play Console: primeiro lançamento Pula-Pulso em análise; MdA publicado tem atualização em análise', date, scope),
        'desenvolvimento': metric(games['Em desenvolvimento'], 'Home main67a5245, Caçada/Atlas/Astrofauna', date, scope),
        'instalacoes': metric(None, 'ND: Play Console, instalações concluídas por jogo', None, 'Total a coletar'),
        'avaliacao': metric(None, 'ND: média ponderada exige nota e número de avaliações da mesma loja', None, 'Google Play'),
        'receita': metric(None, 'ND: receita agregada AdMob + compras, mesma moeda e período', None, 'Novembro2026'),
        'seguidores': metric(sum(n['seguidores']['valor'] for n in data['redes'])
                            if all(n['seguidores']['valor'] is not None for n in data['redes']) else None,
                            'Soma das métricas de seguidores por rede; ver fontes individuais',
                            min((n['seguidores']['coletado_em'] for n in data['redes'] if n['seguidores']['coletado_em']), default=None),
                            'Assinaturas de perfis, não pessoas únicas; data da coleta mais antiga entre as redes'),
    }
    rated = [g for g in data['jogos'] if g['etapa'] == 'Publicado']
    if rated and all(isinstance(g['avaliacao']['valor'], (int,float)) and isinstance(g['numero_avaliacoes']['valor'], (int,float)) for g in rated):
        count = sum(g['numero_avaliacoes']['valor'] for g in rated)
        periods = {g['avaliacao']['periodo'] for g in rated} | {g['numero_avaliacoes']['periodo'] for g in rated}
        if count and len(periods) == 1:
            data['estudio']['avaliacao'] = metric(sum(g['avaliacao']['valor']*g['numero_avaliacoes']['valor'] for g in rated)/count,
                'Média ponderada das notas28dias dos3jogos publicados; n='+str(count), date, next(iter(periods)))
    data['medianas_72h'] = median72(data['posts'])
    data['cobertura'] = dict(posts=len(data['posts']), agendamentos=len(data['agendamentos']),
                            nota='Snapshots históricos podem repetir posts. Inventário atual por rede tem escopo próprio; TikTok publicado divergente fica ND')
    data['pendencias'] = [
        {'fonte':'Play Console', 'campos':'Por jogo: instalações totais concluídas, ativos DAU/MAU com definição, nota e nº de avaliações, versão publicada e status/faixa. Instalações do estúdio e média ponderada dependem dessas bases.', 'periodo':'Total até coleta + últimos7/28dias; informar fuso e data de atualização.'},
        {'fonte':'Play Console / analytics', 'campos':'D1/D7 por jogo e coorte, com denominador. Separar instaladores retidos (não desinstalou) de retorno ao app; não tratar proxy como retenção de abertura.', 'periodo':'Coortes já maduras; se ainda indisponível, manter ND.'},
        {'fonte':'AdMob / compras', 'campos':'Receita do mês por jogo e estúdio; separar anúncios e compras, moeda e período. Só agregado; sem saldo, faturamento da conta, cadastro ou pagamento. AdMob reprovado no último relato não comprova receita zero.', 'periodo':'01/11 até data fechada da coleta.'},
        {'fonte':'Meta / YouTube / TikTok', 'campos':'Seguidores atuais; alcance e views no mesmo período por rede. Inventário completo de publicados e agendados com IDs/data/hora. Não somar alcances como pessoas únicas.', 'periodo':'Últimos7dias fechados, fuso explícito; snapshot de seguidores e agenda.'},
        {'fonte':'Meta / YouTube / TikTok', 'campos':'Views em72h exatas por post, rede e formato; curtidas, comentários, compartilhamentos e salvos com timestamp, URL e n da base. Faltam cortes72h para M72/G; acumulados tardios não substituem.', 'periodo':'Corte72h por publicação; mesma definição/base comparável.'},
        {'fonte':'GitHub / QA', 'campos':'Testes executados e aprovados por commit/suíte e data; evitar somar reruns ou contar teste apenas documentado como execução atual.', 'periodo':'Novembro2026, cobertura explícita.'},
        {'fonte':'Flow / ElevenLabs', 'campos':'Créditos Flow consumidos no mês e caracteres/créditos ElevenLabs do mês, inclusive gerações manuais. Livro agregado com data/modelo/quantidade; sem chave, pagamento ou dados de conta.', 'periodo':'Novembro2026; descontar estornos só quando comprovados.'},
    ]
    if data.get('coleta_diaria'):
        data['pendencias'] = [dict(fonte='Coleta direta de '+data['coleta_diaria']['data'], campos=motivo, periodo='Última consulta, ver fonte/escopo dos indicadores') for motivo in data['coleta_diaria']['nd_motivos']]
    return data


def import_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    posts = []
    fields = ['rede','id','permalink','jogo','pauta','formato','publicado_em','corte','serie']
    for row in rows:
        p = {k:row.get(k) or None for k in fields}
        for k in ['views','likes','comentarios','shares','saves']:
            p[k] = float(row[k]) if row.get(k) else None
        p.update(fonte='dados-posts.csv / gerar_relatorio.py, coleta02/11', corte_tipo='acumulado',
                 nota='Importação histórica; sem corte72h comprovado')
        posts.append(p)
    return posts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fonte', type=Path, default=ROOT/'fontes/observacoes.json')
    parser.add_argument('--handoff', type=Path, help='Handoff Vera já concluído; importa só IDs/agregados, nunca legendas/paths locais')
    parser.add_argument('--coletado-em', help='Timestamp real da verificação do handoff, obrigatório com --handoff')
    parser.add_argument('--posts-csv', type=Path, help='Importação opcional do CSV gerado pelo relatório02/11; substitui somente posts')
    args = parser.parse_args()
    source = json.loads(args.fonte.read_text())
    if args.posts_csv:
        source['posts'] = import_csv(args.posts_csv)
    if args.handoff:
        if not args.coletado_em:
            parser.error('--handoff exige --coletado-em com a data real da verificação')
        handoff = json.loads(args.handoff.read_text())
        if not handoff.get('status', '').startswith('CONCLUIDO'):
            raise ValueError('Handoff ainda não concluído; não presumir agendamentos')
        schedules = []
        for post in handoff['posts']:
            for network in ['Instagram','Facebook','YouTube']:
                entry = post['confirmacao_josefa'].get(network, {})
                if not entry.get('id'):
                    continue
                schedules.append(dict(jogo=post['jogo'],rede=network,id=entry['id'],
                    data=post['data'],hora=post['hora'],IA=entry.get('IA'),
                    coletado_em=args.coletado_em,fonte='Handoff concluído verificado pelo responsável',
                    link='https://youtu.be/'+entry['id'] if network=='YouTube' else None))
        source['agendamentos'] = schedules
    data = build(source)
    validate(data)
    target = ROOT/'dados.json'
    pending = target.with_suffix('.tmp')
    pending.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    pending.replace(target)
    print('dados.json regenerado: %d posts, %d inserções confirmadas; %d bases72h.' %
          (len(data['posts']),len(data['agendamentos']),len(data['medianas_72h'])))


if __name__ == '__main__':
    main()
