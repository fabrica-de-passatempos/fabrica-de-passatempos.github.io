import copy
import json
import unittest
from pathlib import Path
from gerar_dados import build, median72, validate

ROOT = Path(__file__).resolve().parent

class DataTests(unittest.TestCase):
    def setUp(self):
        self.source = json.loads((ROOT/'fontes/observacoes.json').read_text())

    def test_historical_counts_do_not_become_72h(self):
        result = build(self.source)
        self.assertEqual(result['medianas_72h'], [])
        self.assertIsNone(result['estudio']['instalacoes']['valor'])
        self.assertEqual(result['estudio']['seguidores']['valor'], 56)

    def test_median_only_same_declared_base_and_network(self):
        def post(id, views, **more):
            return dict(id=id,views=views,rede='Instagram',formato='Gameplay',base_72h='novembro',corte_tipo='72h',corte='2026-11-10',**more)
        sample=[post('a',100),post('b',200),post('c',900)]
        sample += [dict(sample[0],id='older',views=9000,corte_tipo='acumulado'),dict(sample[0],id='tt',rede='TikTok',views=0)]
        rows=median72(sample)
        ig=next(r for r in rows if r['rede']=='Instagram')
        self.assertEqual((ig['n'],ig['mediana'],ig['gatilho']),(3,200,1000))
        self.assertEqual(next(r for r in rows if r['rede']=='TikTok')['gatilho'],0)

    def test_privacy_and_provenance_fail_closed(self):
        for patch in [dict(email='private@example.com'),dict(token='private'),dict(url='https://play.google.com/console/developer/123')]:
            with self.subTest(patch=patch),self.assertRaises(ValueError):
                validate(dict(self.source,**patch))
        data=copy.deepcopy(self.source)
        data['redes'][0]['seguidores']['coletado_em']=None
        with self.assertRaises(ValueError):validate(data)
        data=copy.deepcopy(self.source)
        data['posts'][0]['views']=-1
        with self.assertRaises(ValueError):validate(data)

    def test_committed_data_rebuild_and_hidden_route(self):
        self.assertEqual(build(self.source),json.loads((ROOT/'dados.json').read_text()))
        self.assertIn('content="noindex,nofollow"',(ROOT/'index.html').read_text())
        for name in ['index.html','sitemap.xml','robots.txt','site.js']:
            self.assertNotIn(ROOT.name,(ROOT.parent/name).read_text())

if __name__=='__main__':unittest.main()
