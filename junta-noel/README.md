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
