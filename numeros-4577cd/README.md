# Números da Fábrica

Decisão de11/11/2026: dois totais, Top10 apps lançados por downloads, Top10 posts por views e data no rodapé. Identidade visual da Sala, barras horizontais e layout para celular. Sem outras métricas ou filtros.

## Rotina diária —08h00

A rotina já existente passa a coletar **somente**:

- Play Console: instalações totais históricas por app publicado. Não usar aquisições de28dias, ativos ou instalações na faixa como substitutos. Apps em revisão/desenvolvimento ficam fora.
- Instagram, Facebook, YouTube e TikTok: views acumuladas por publicação, ID e data da coleta. Associar cada publicação ao ID da peça no catálogo `pecas`; mesma peça editorial com outro fecho ou republicada permanece na mesma linha, variantes de gancho A/B ficam separadas. Conferir o master em caso de dúvida; não agrupar automaticamente pelo título.

Somente leitura no Chrome, abas próprias e som travado. Sem login, senha, CAPTCHA, gasto, publicação ou alteração de conta. A rotina não agenda nem exclui conteúdo.

Atualize `fontes/observacoes.json`: `jogos` guarda downloads e publicação; `posts` guarda rede/ID/peça/views; `pecas` guarda título e jogo. Todo contador exige fonte e data real. Preserve o inteiro mostrado na tela; strings pt-BR como `1.213` viram1213. Não interpretar rótulos arredondados como contagem exata.

O gerador usa só o último snapshot conhecido de cada rede/ID, inclusive quando a plataforma revisa o contador para baixo. Soma todas as publicações inventariadas para o total e todas as redes por peça para o ranking. Views não são pessoas únicas. Não somar os totais das janelas diferentes de analytics. Foto de perfil e capa não fazem parte do inventário editorial. Exceção documentada: o react de03/11 veio da Meta como contador combinado IG+FB; entra uma vez em `Meta (IG+FB)`. O gerador recusa contadores individuais Meta da mesma peça enquanto esse agregado estiver presente. Na próxima coleta, preferir a separação por rede e substituir o combinado, sem somá-los.

Sem fonte, o item não entra no ranking. Downloads totais ficam `null` se faltar qualquer app publicado; a tela mostra `—`, nunca um falso zero ou soma parcial. Registrar motivo no relatório privado. A data do rodapé é a coleta real, não a execução do script.

```sh
python3 numeros-4577cd/gerar_dados.py
python3 -m unittest discover -s numeros-4577cd -p 'test_*.py'
node --check numeros-4577cd/painel.js
node --test test/*.test.cjs tests/*.test.cjs
git diff --check
```

A escrita de `dados.json` é atômica. A saída contém somente os números e rankings exibidos; a rastreabilidade permanece nas observações agregadas. Nunca inserir credencial, e-mail, informação de jogador, pagamento, conta ou URL de console. A pasta e o repo são públicos: sufixo aleatório/noindex não são autenticação.

## Publicação

Commit como Alisson, sem coautor; abrir PR. Merge automático só quando **todos** os arquivos do diff contra main começam por `numeros-4577cd/` e os testes passam. Qualquer outra pasta exige PR sem merge. Manter noindex/nofollow, fora do sitemap e sem link no site público.

Conferir celular e página publicada. Relatório curto em para-claudio: mudança, print e bloqueios. Se Chrome/painel falhar, não inventar atualização: manter última coleta comprovada e informar data e motivo. Não criar outro agendamento das08h.

## Migração desta versão

Coleta comprovada:10/11/2026.109 publicações editoriais,30 peças. Os contadores do YouTube `jyRUo1_0q5Y` e `GID44TyKCJo` foram corrigidos de1.213/1.222 numéricos para1213/1222, conforme texto da UI e relatório05/11. A migração removeu as demais métricas dos dados atuais; o histórico permanece no Git. Downloads históricos não foram comprovados na coleta anterior e a conexão Chrome está indisponível nesta atualização.
