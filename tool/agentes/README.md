# Avatares animados da equipe

Proposta para aprovação na branch `basilio/agentes-animados`, em PR rascunho, sem publicação do site.

O card da **Sheila, Personagens e Cenas**, entra junto destes seis, com a animação que ela entregou e teve aprovada pelo Alisson via Claudio. A manutenção de avatares, retratos, cenas e painéis passa à Sheila. Basílio conclui a integração deste pedido em andamento e mantém os assets de jogabilidade.

Seis animações manuais sobre a grade original de 48 x 48 pixels. Os rostos, cabelos e roupas vêm da fonte local `personas_base.py`, copiada sem alterações de `estudio/plugins/fabrica/skills/arte-jogos/assets/exemplos/personas.py`. Os fallbacks em `img/equipe/{nome}.webp` e os avatares dos sócios permanecem intactos.

A produção usa somente seis folhas PNG em `img/equipe/animados/{nome}.png`: 576 x 48 pixels, com 12 quadros de 48 x 48 em uma linha. Os atributos de tamanho continuam 240 x 240 e o CSS responsivo preserva as dimensões já usadas pela seção. O site aplica `image-rendering:pixelated`, `object-fit:cover` e um único conjunto de keyframes compartilhado para escolher cada recorte. A integração de HTML/CSS/JS pertence ao site; o gerador não modifica esses arquivos.

## Ações

| Agente | Movimento |
|---|---|
| Claudio | Mão e caneta fazem anotações em duas linhas da prancheta. |
| Valdir | Dedos alternam sobre a borda do teclado e o símbolo `</>` pulsa na tela. |
| Samara | A lupa passa em direção à checklist, amplia um check e os três checks aparecem em sequência. |
| Antonio | A barra listrada gira na dobradiça e fecha sobre a claquete. |
| Josefa | Recolhe o megafone alguns pixels para abrir espaço a duas ondas de som visíveis dentro do quadro. |
| Basílio | Baixa o pincel, leva a ponta à paleta à esquerda e deixa um pequeno traço de tinta. |

Todos piscam em duas poses. As fases variam entre os agentes, com sobreposição parcial entre Claudio e Basílio. O primeiro e o último quadro são pixel a pixel iguais ao render original da fonte. O último mantém uma pausa de 300 ms; o primeiro também segura a pose de descanso.

Durações em milissegundos: `240,180,180,240,180,240,240,180,120,120,240,300`. Ciclo total: **2.460 ms**. Não há áudio, geração por IA ou player de quadros em JavaScript.

## Comparação dos formatos

Os candidatos usam os mesmos pixels, quadros e tempos. GIF e WebP foram decodificados para conferir pixels e duração; as folhas PNG foram conferidas recorte por recorte. A paleta é indexada por correspondência exata, sem dithering ou quantização aproximada.

| Opção, seis agentes | Assets | CSS adicional compartilhado | Total |
|---|---:|---:|---:|
| PNG 48 + CSS, escolhido | 6.157 B | 670 B | **6.827 B** |
| WebP lossless 48 | 11.838 B | 0 B | 11.838 B |
| GIF lossless 48 | 47.259 B | 0 B | 47.259 B |
| PNG 240 + CSS | 16.909 B | 670 B | 17.579 B |
| WebP lossless 240 | 15.458 B | 0 B | 15.458 B |
| GIF lossless 240 | 264.198 B | 0 B | 264.198 B |

O CSS contado são as três linhas reais de `site.css`: seletor de imagem, classe ativa e `@keyframes retratos`. Ele é contado uma única vez para os seis PNG, sem duplicar keyframes. O fallback, IntersectionObserver e preferências de movimento usam a integração comum do site em todas as opções. A folha exige apenas a classe ativa e o CSS compartilhado, sem temporizador ou DOM extra. O conjunto escolhido economiza **5.011 bytes, 42,33%**, em relação ao WebP nativo.

A folha nativa decodificada equivale a aproximadamente 110.592 bytes RGBA por agente, 663.552 nos seis. A mesma folha em 240 exigiria 25 vezes mais pixels. Esses números são estimativas do raster, não medições da memória real do navegador ou do cache de GIF/WebP.

`benchformatos.json` registra tamanho por agente, totais e hash do CSS medido. Os candidatos GIF, WebP e PNG 240 ficam fora do repositório, em `~/.fabrica/ponte/arquivos/site-agentes-animados/formatos/`.

## Sétimo card, de autoria da Sheila

`importar_sheila.py` converte o WebP aprovado de 240 para sua grade original de 48, sem redesenhar. Compara cada quadro reampliado com os pixels aprovados, mantém os tempos e verifica os hashes dos insumos em `insumos/sheila/`. Exporta `img/equipe/animados/sheila.webp`, 1.208 B, e copia o fallback aprovado para `img/equipe/sheila.webp`, 580 B. O WebP nativo é menor que a folha PNG medida da Sheila, 1.685 B mesmo sem contar outro conjunto de keyframes.

Ela tem sete quadros codificados em um ciclo próprio de 2,8 s. O CSS de sprites é ativado somente nas seis folhas PNG; o WebP da Sheila usa sua animação nativa com os mesmos controles de visibilidade, preferência e fallback. As animações somam **8.035 B** com o CSS compartilhado; o novo fallback estático acrescenta 580 B. A grade dos agentes tem sete colunas largas; até 900 px, três colunas com o último card isolado centralizado. A grade dos sócios permanece igual.

Os originais aprovados ficam versionados como insumos, acompanhados de autoria, aprovação e hashes. `sheila.json` registra a conversão e o ciclo preservado. Para regenerar só essa integração:

```bash
python3 tool/agentes/importar_sheila.py
```

## Reprodução dos seis primeiros

Na raiz do site, com `oxipng` disponível no PATH:

```bash
uv run --with pillow --with numpy python tool/agentes/gerar.py
```

O comando regenera os quadros, compara os formatos e instala somente os seis PNG escolhidos. O local de artefatos pode ser definido com `--artifacts CAMINHO`. Para conferir candidatos já codificados e atualizar exports/relatórios sem repetir a codificação:

```bash
uv run --with pillow --with numpy python tool/agentes/gerar.py --reuse-encodings
```

O gerador lê o bloco CSS compartilhado do próprio site para medir o custo real. Não depende do checkout de estudio para funcionar. `personas_base.py` é o snapshot local da fonte original; a geometria das ações e a separação de camadas estão em `gerar.py`.

Os objetos móveis são reconstruídos sobre corpo e cabeça completos. Não são buracos preenchidos com uma cor neutra. A lupa revela uma sombra que antes ficava totalmente oculta: essa única cor é substituída pela sombra de pele já presente no render original, preservando a paleta exigida.

## Verificação e prévias

Asserções conferem os seis nomes, 12 quadros, limites dos novos desenhos, primeiro/último iguais à fonte, poses distintas, mudanças de piscada no rosto, correspondência exata de cada bloco de 5 x 5 no tamanho visual e uso exclusivo da união de **80 cores** dos seis renders originais. O raster é opaco, sem antialias; em RGBA o alpha é 255. Os 72 recortes dos PNG de produção são conferidos contra os quadros gerados.

`validacao.json` inclui hashes da fonte, dos pixels originais, das paletas, dos fallbacks preservados e dos seis PNG finais. O primeiro quadro é comparado ao render original da fonte, não ao WebP estático que pode ter perdas de compressão.

Fora do repositório:

- `maquete-6-agentes.gif`: contato animado 3 x 2, rotulado como maquete.
- `maquete-contato.png`: uma pose do contato para inspeção rápida.
- `quadros/{nome}/00.png` a `11.png`: quadros em 240 x 240 para compor prévias do site.
- `formatos/`: todos os candidatos e uma cópia do CSS compartilhado medido.

O HTML conserva os WebP estáticos no `src`. A folha e sua classe de animação são ativadas somente quando o retrato está visível, a aba está ativa e a preferência não reduz movimentos. Ao sair da tela ou ativar a redução, o `src` volta ao original e a classe é removida. Sem JS, IntersectionObserver ou suporte ao recorte quadrado por `aspect-ratio`, o retrato permanece estático. Erro de carregamento da folha também conserva o fallback, sem tentativas em loop. Não há player ou temporizador de quadros em JavaScript.

Os testes Node em `test/agentes-motion.test.cjs` cobrem esses estados e as referências reais dos seis assets; os testes existentes do logo e dos vídeos continuam passando. A fonte/PNG foi reproduzida em pasta isolada, com bytes idênticos e recortes conferidos. As prévias `secao-*.gif` na Ponte usam os mesmos assets e tempos, em composições de 360, 760 e 1240 px; não são capturas do navegador.

Não houve navegador conectado, teste em aparelho ou áudio. O PR permanece rascunho, sem merge ou publicação. A aparência no navegador e o desempenho real no celular ainda precisam de conferência; os números de raster acima não são um benchmark do aparelho.
