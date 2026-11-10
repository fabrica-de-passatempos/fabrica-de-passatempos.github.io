# Números da Fábrica

Painel estático de uso interno, com o mesmo padrão de HTML + fetch de `dados.json` da Sala dos Devs. Decisão de Alisson via Claudio em 10/11/2026: pasta com sufixo aleatório, noindex,nofollow, fora do sitemap e sem links públicos. **Isso não é autenticação.** Repo e arquivos são públicos a quem conhece o endereço. Só números agregados e links de posts públicos; sem contas, credenciais, e-mails, dados de jogadores ou pagamentos.

## Atualização sem dependências

1. Atualize `fontes/observacoes.json` somente com agregados conferidos. Em cada métrica informe `valor`, `coletado_em`, `fonte`, `periodo`; null significa ND. Não use a data de hoje como data de coleta de um dado antigo. Estado no código não comprova versão publicada na loja.
2. Execute na raiz do repo:

```bash
python3 numeros-4577cd/gerar_dados.py
python3 -m unittest discover -s numeros-4577cd -p 'test_*.py'
node --check numeros-4577cd/painel.js
```

O script usa só biblioteca padrão, não acessa navegador, conta, rede ou Keychain. Valida dados antes de substituir o JSON; recusa e-mails, campos privados, padrões comuns de credenciais, links de consoles e contadores negativos/não finitos. Essa validação é uma defesa adicional: revise sempre o diff antes do PR. Não copiar exports brutos para este repo.

Importação opcional do `dados-posts.csv` produzido pelo `metricas-mkt-20261102/gerar_relatorio.py` original:

```bash
python3 numeros-4577cd/gerar_dados.py --posts-csv /caminho/local/dados-posts.csv
```

Isso substitui o inventário de posts no JSON de saída pelo CSV, mantendo outros agregados. Para preservar uma base com várias coletas, normalize/adicione os novos registros em `fontes/observacoes.json` e regenere sem a opção. Não executamos o script original: ele copia/descompacta exports da pasta Downloads e inclui URLs de consoles. Reaproveitamos os dados estruturados que ele já produziu e sanitizamos os campos.

Handoff confirmado, sem publicar caminhos, legendas ou o arquivo bruto:

```bash
python3 numeros-4577cd/gerar_dados.py --handoff /caminho/local/handoff.json --coletado-em '2026-11-10T10:46:00-03:00'
```

Só aceita handoff marcado CONCLUIDO e importa os campos agregados das três redes. A data é a da verificação real, não da execução. Para tornar uma atualização reproduzível sem o arquivo externo, incorpore os registros normalizados ao array `agendamentos` em `fontes/observacoes.json`. O snapshot inicial já está incorporado.

## Regras das contas

- Estoque documental: sete jogos; três publicados na Google Play, Pula-Pulso em revisão conforme envio do PM e três em desenvolvimento. Fonte: home do site main67a5245 e relato de envio07/11. A Sala/PORTFOLIO têm status antigos em alguns jogos, por isso não são copiados como verdade atual. Sem nova leitura de lojas.
- Seguidores: coleta09/11, 44+1+8+3=56 assinaturas de perfis. Não são pessoas únicas. Views e alcance de período: coletas02/11, com janelas/fusos próprios; não somar como alcance total nem fingir atualização09/11.
- Posts: 49 snapshots em02/11 e09/11; podem conter o mesmo post em coletas diferentes. Filtro separa coletas. Ranking por views descreve a amostra e não prova melhor formato. Views zero com processamento não são falha criativa comprovada.
- Agenda: seis inserções dos dois masters aprovados em10/11; não é calendário completo. Publicação futura ainda não foi verificada.
- M72: somente registros explicitamente `corte_tipo: "72h"`, com `base_72h` identificando período/critério comparável. Agrupa por rede e base para M72 do perfil; formatos são detalhamento. Mostra n e G=5×M72 do perfil. Não deduplicar pessoas; deduplicar IDs repetidos no mesmo corte/base. Acumulados com idade acima de72h **não** entram. Base inicial elegível vazia: ND, sem gasto autorizado pelo painel.
- PRs: GitHub Search API, consulta01-10/11 até timestamp, organização inteira, total_count146/incomplete_resultsfalse, não apenas os100 itens da primeira página. URL pública da consulta no JSON; o valor pode evoluir após a coleta.
- Créditos:20Flow é apenas E1-A, uma geração Veo3.1Fast. Total mensalFlow/ElevenLabs ND por falta de conciliação. Não inferir gasto mensal do saldo/quota ou somar uma voz descartada sem fechamento.
- Retenção: distinguir instaladores retidos da Play e retorno ao app; D1/D7 pedem coortes maduras e denominador. Receita ND não é zero, inclusive com AdMob reprovado no último relato.

## Prévia

```bash
python3 -m http.server 8847 --bind 127.0.0.1
```

Abra `http://127.0.0.1:8847/numeros-4577cd/`. Teste em390px e1440px. Sem autoplay, mídia, analytics, cookies ou dependência de build. Fontes tipográficas seguem o Google Fonts já usado pela Sala; há fontes de sistema como fallback. Falha no fetch mostra erro explícito.

A hospedagem de produção só existe depois de merge. Decisão posterior de Alisson em10/11~16h: merge autorizado para este PR e rotina diária, somente se o diff inteiro tocar exclusivamente esta pasta e os testes passarem. Qualquer outra pasta exige PR sem merge. A branch pode ser pré-visualizada pelo checkout servido localmente; o link de produção não deve ser apresentado como publicado antes do merge.


## Primeira coleta direta e rotina diária (decisão10/11~16h)

Vera consulta painéis em abas próprias, com som bloqueado e sem play. Leitura somente: nunca alterar conta, campanha, configuração ou posts; sem login, credenciais, CAPTCHA ou gasto. Não criar outro agendamento: o PM administra o disparo launchd das08h00. Login/trava viraND com motivo e aviso na ponte.

Atualizar observações, gerar JSON, testar, revisar diff e publicar por PR. Antes do merge, verificar **todos** os caminhos contra a base atual: cada um deve começar por `numeros-4577cd/`. Commit como Alisson, sem coautor. Após merge, conferir a página publicada. Relatório diário curto ao PM com delta eND; sem novidade relevante, uma linha.

A coleta10/11 percorreu54posts/reels Meta,34agendamentos Meta válidos,44Shorts YouTube (31publicados/13agendados) e37linhas TikTok. TikTok tem26linhas passadas/11futuras, mas o cabeçalho mostrou25Publicações; total publicado definitivo permaneceND, com divergência explícita. Uma entrada Meta antiga com falha não entra como agendamento. IDs de publicadosMeta foram lidos em atributos DOM `data-surface`; os de agendados emIdentificação/Detalhes. Não usar seletor genérico de botão em listas de conteúdo, pois pode acionar Turbinar; para identificação, preferir leitura de atributos DOM do item.

Não inferir D7: os três relatórios Play consultados mostraram Dados indisponíveis. D1 não aparece no seletor que oferece2/3/7/14/28dias. AdMob01-09/11 por app não oferece dados; apenas home exibe estimativaMTD US$0,00 incluindo dia parcial, mostrada separada. Receita Play exige comerciante, sem configurar. Flow só expõe créditos diários restantes no menu, não consumo mensal. ElevenLabs Uso11/2026 expõe rótulos arredondados, preservados no painel.
