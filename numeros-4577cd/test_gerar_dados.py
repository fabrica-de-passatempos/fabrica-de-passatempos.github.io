import copy
import unittest
from gerar_dados import build, counter


def sample():
    date = '2026-11-10T16:00:00-03:00'
    return dict(coletado_em=date,
        jogos=[dict(nome='Lançado', publicado=True, downloads=10, fonte='Play: instalações totais', coletado_em=date),
               dict(nome='Em revisão', publicado=False, downloads=90, fonte='Play', coletado_em=date)],
        pecas=[dict(id='a', titulo='Mesmo título', jogo='Lançado', fonte='Master A'),
               dict(id='b', titulo='Mesmo título', jogo='Lançado', fonte='Master B')],
        posts=[dict(rede='YouTube', id='1', peca='a', views=100, fonte='Studio', coletado_em=date),
               dict(rede='Instagram', id='2', peca='a', views=30, fonte='Meta', coletado_em=date),
               dict(rede='TikTok', id='3', peca='b', views=0, fonte='Studio', coletado_em=date)])


class Tests(unittest.TestCase):
    def test_group_by_piece_not_title_and_only_published_apps(self):
        result = build(sample())
        self.assertEqual(result['downloads_totais'], 10)
        self.assertEqual(result['jogos'], [dict(nome='Lançado', downloads=10)])
        self.assertEqual([p['views'] for p in result['posts']], [130, 0])
        self.assertEqual(result['visualizacoes_totais'], 130)

    def test_latest_snapshot_once_including_decreasing_count(self):
        source = sample()
        previous = copy.deepcopy(source['posts'][0])
        previous.update(coletado_em='2026-11-09T16:00:00-03:00', views=120)
        source['posts'].extend([previous, copy.deepcopy(source['posts'][0])])
        self.assertEqual(build(source)['visualizacoes_totais'], 130)

    def test_unknown_and_unsourced_are_not_zero(self):
        source = sample()
        source['jogos'][0]['downloads'] = None
        source['posts'][0]['fonte'] = ''
        result = build(source)
        self.assertIsNone(result['downloads_totais'])
        self.assertEqual(result['jogos'], [])
        self.assertEqual(result['visualizacoes_totais'], 30)
        source['posts'] = []
        self.assertIsNone(build(source)['visualizacoes_totais'])

    def test_total_is_not_only_top_ten(self):
        source = sample()
        for i in range(11):
            source['pecas'].append(dict(id=str(i), titulo=str(i), jogo='Lançado', fonte='Master'))
            source['posts'].append(dict(rede='Facebook', id=str(i), peca=str(i), views=1,
                                        fonte='Meta', coletado_em=source['coletado_em']))
        result = build(source)
        self.assertEqual(len(result['posts']), 10)
        self.assertEqual(result['visualizacoes_totais'], 141)

    def test_counter_locale_and_invalid_values(self):
        self.assertEqual(counter('1.213'), 1213)
        for value in [1.213, True, -1, '1,2 mil', '1,213', float('nan')]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                counter(value)

    def test_conflicting_identity_and_snapshot_rejected(self):
        for field, value in [('peca', 'b'), ('views', 101)]:
            source = sample()
            duplicate = dict(source['posts'][0], **{field: value})
            source['posts'].append(duplicate)
            with self.assertRaises(ValueError):
                build(source)

    def test_combined_meta_not_counted_twice(self):
        source = sample()
        source['posts'][0]['rede'] = 'Meta (IG+FB)'
        with self.assertRaises(ValueError):
            build(source)
        source['posts'].pop(1)
        self.assertEqual(build(source)['visualizacoes_totais'], 100)

    def test_privacy(self):
        for field, value in [('email', 'pessoa@example.com'), ('nota', 'https://play.google.com/console/apps/123')]:
            source = sample()
            source[field] = value
            with self.assertRaises(ValueError):
                build(source)

    def test_public_output_is_minimal(self):
        result = build(sample())
        self.assertEqual(set(result), {'schema', 'coletado_em', 'downloads_totais', 'visualizacoes_totais', 'jogos', 'posts'})
        self.assertNotIn('rede', result['posts'][0])
        self.assertNotIn('fonte', result['posts'][0])


if __name__ == '__main__':
    unittest.main()
