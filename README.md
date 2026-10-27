# Apenas um Input

Jogo de ritmo em pixel art, numa pegada de *Guitar Hero*, desenvolvido para ser apresentado na GameJam da **XII Semana da Computação da UFF**.

> Link odiava rock. Numa noite tranquila no parque, cansado do barulho de uma banda de rua, ele gritou para o céu que o rock nunca deveria ter existido. O céu respondeu: entre raios e trovões, os quatro Deuses do Rock desceram e lançaram sobre ele a maldição da Ressonância. Desde então, o mundo de Link perde a cor a cada nota errada, e só volta a brilhar quando ele toca.
>
> Com uma guitarra que surgiu em suas mãos, Link precisa enfrentar Grace, Janis, Plant e Ozzy, cada um com seu estilo e suas exigências. Só convencendo os quatro ele quebra a maldição e descobre se o rock era mesmo tão ruim assim.

## Como jogar

Precisa de Python 3.10+ e pygame.

```
pip install pygame
python main.py
```

## Controles

| tecla | o que faz |
| --- | --- |
| `A` `S` `D` `F` `G` | tocam as cordas (de cima pra baixo) |
| `Enter` / `Espaço` | avança as falas, confirma no menu |
| setas | escolhem a fase no menu |
| `Esc` | pula a fala / sai da fase / sai do jogo |

## Como o jogo funciona

- **Jornada:** Grace (Folk) → Janis (Glam) → Plant (Punk) → Ozzy (Metal). A próxima fase só abre quando o deus aprova a anterior. Depois do último vem o final.
- **Ressonância:** a barra no topo. Acertos enchem, erros esvaziam, e o mundo vai ficando cinza conforme ela cai. Se zerar, é game over. O deus aprova se a fase terminar com 50% ou mais.
- **Notas:** cada quadrado precisa ser tocado quando chega no Link. O acerto é julgado por tempo: perfeito (até 70 ms), bom (até 130 ms) ou errou.

## Estrutura

```
main.py           fluxo do jogo (abertura → menu → fala → fase → resultado → final) e o loop da fase
menu.py           seleção de fase da jornada
dialogue.py       caixa de diálogo e as cenas das falas (parque, tempestade, retratos dos deuses...)
story.py          todos os textos da história
journey.py        progresso da jornada e regra de aprovação
levels.py         as 4 fases e os arquivos de cada uma
figure.py         deus em cena (animação e entrada deslizando)
ui.py             fonte, cores e peças de interface (painel, teclas, setas)
settings.py       constantes compartilhadas (resolução, cordas, teclas, pastas)
assets.py         carregamento de sprites
display.py        escala do canvas 480x270 pra janela

rhythm/
  conductor.py    relógio da música (sincronia com o áudio)
  chart.py        formato e leitura dos charts
  judge.py        janelas de acerto (perfeito / bom / errou)
  highway.py      notas pendentes de cada corda e julgamento dos toques
  score.py        pontos e combo
  resonance.py    a barra de Ressonância
  effects.py      fogo no acerto, nota caindo no erro
  view.py         desenho das notas, HUD, resultado e game over

charts/           notas de cada fase (JSON, em beats) — por enquanto placeholders
music/            áudio de cada fase: <fase>.ogg (folk, glam, punk, metal)
sprites/          artes do jogo
fonts/            Press Start 2P (licença OFL em fonts/OFL.txt)
```

