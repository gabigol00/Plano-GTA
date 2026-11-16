# Plano GTA — canal GTA6ZONE.BR

Operação do canal de cortes de GTA 6 (TikTok **@gta6zone.br0**, Instagram **@gta6z.onebr**). Este repositório guarda as instruções do agente, o cronograma e os scripts de edição. Os vídeos ficam fora (pesados).

## Estrutura
- `agente/AGENTE-GTA6ZONE.md` — regras, pipeline e prompts do agente (**edite aqui para mudar o comportamento**).
- `cronograma-gta6.md` — ordem, horários, legendas e hashtags dos posts.
- `legendas-e-hashtags.md` — legendas dos primeiros cortes.
- `roteiros/` — roteiros PT-BR usados na dublagem (ElevenLabs).
- `scripts/` — edição com ffmpeg. `mkv2.py` é o template atual (foto + nome + @ no topo, título grande, vídeo no meio, legenda). Os demais são versões anteriores.
- `assets/` — `perfil.jpg` (foto de perfil) e `wm.png` (marca d'água antiga).

## Como editar
Altere os arquivos `.md` e faça commit. O agente lê o repositório antes de cada rodada de trabalho.

## Observações
- Os caminhos dentro dos scripts apontam para o ambiente de trabalho do agente; ajuste se for rodar em outro lugar.
- Não colocar senhas, tokens ou códigos de login no repositório.
