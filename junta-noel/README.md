# Junta Noel: página em preparação

Página isolada `/junta-noel/`, marcada Em breve/nome provisório, e política PT/EN em `/junta-noel/privacidade.html`. Não altera home, /jogar, contagens ou carrosséis. Sem link de loja, anúncio de data ou APK. Navegação e imagens funcionam sem JavaScript.

Política conferida contra junta-noel runtime632c324 (PR #9, HEADc220332):

- lib/progress.dart: SharedPreferences, estrelas por fase e desbloqueio derivado; sem envio de dados/placar.
- lib/audio.dart e lib/haptics.dart: preferências locais de efeitos, música e vibração.
- lib/audio_backend.dart: áudio empacotado em assets e arquivo temporário local; nenhum stream remoto ou microfone.
- pubspec.yaml, lib/, AndroidManifest.xml e Info.plist: sem SDK de anúncios/Analytics/Crashlytics, cadastro, endpoint de telemetria ou acesso a identificador de publicidade. A presença transitiva de http no lockfile não é uma chamada do app.
- O manifest Android não desativa explicitamente o backup do sistema; o texto diferencia salvamento local do jogo e backups geridos pelo sistema/aparelho.
- Ainda não há tela de privacidade no aplicativo; a integração interna da mesma política é pendência para o lançamento, em PR próprio do jogo.

Assets e hashes em assets/origens.json. As seis capturas foram refeitas com HUD realista e fundos, em1080×1920, sem resize/crop e sem injeção de progresso. O bot fez toques/retries/avanços pela UI desde zero até a fase14. PixelsRGB do raw e do PNGexportado são idênticos. A arte de apresentação aprovada permanece inalterada. Não publicar esta branch antes da revisão do Claudio.

## Atualização de 23/11: Android para público 13+ com Unity Ads

A auditoria histórica sem anúncios acima foi superada. A fonte nativa agora é o candidato integrado `0fe8b3d`, Unity Ads Android direto **4.21.0**, ainda em modo teste. A política PT/EN foi sincronizada às 11 seções por idioma embarcadas no app; `tool/verificar_politica_html.py` do repo do jogo compara títulos e parágrafos, sem normalizar diferenças.

O SDK pode inicializar/preparar a oferta depois de uma derrota elegível, antes da escolha de assistir. O vídeo é opcional; isso não torna a coleta automaticamente opcional. A política informa localização aproximada, IDs de usuário, histórico de compras, interações, diagnósticos e IDs do aparelho, segundo a declaração oficial do SDK. O app não tem conta/compras/Analytics próprios. Acquire Optimization depende do dashboard futuro, ainda não conferido. Recusa de personalização não significa coleta zero. iOS permanece sem o SDK.

Não há banner/intersticial nem anúncio no menu, mapa, Relax ou durante jogadas. Completar o vídeo derrete a neve ao nível inicial e continua a mesma fase, uma vez por fase, sem acrescentar quedas. A política explica os controles e pedidos à Unity; apagar o save não apaga os dados do serviço.

Fontes: [Unity 4.21 — Segurança dos dados](https://docs.unity.com/en-us/ads-android/4.21.0/privacy/developer-consent/disclosures/google-data-safety), [orientação Play](https://support.google.com/googleplay/android-developer/answer/10787469), rascunhos `docs/play/` do jogo e conciliação com Josefa. Antes de publicar: Game ID próprio/dashboard, smoke do anúncio, revisão regional/menores, decisões pendentes e aceite de política/ficha. Tela interna já existe no app e usa estes mesmos textos.

A página continua Em breve, fora da home/carrosséis, sem link Play. PR #50 sem merge/deploy. Capturas da página continuam sendo as históricas descritas acima; esta revisão só muda texto de privacidade e sua auditoria.
