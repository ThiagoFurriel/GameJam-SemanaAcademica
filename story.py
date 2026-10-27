#textos da história

from dataclasses import dataclass

LINK = "LINK"
GRACE = "GRACE"
JANIS = "JANIS"
PLANT = "PLANT"
OZZY = "OZZY"


@dataclass(frozen=True)
class Page:
    text: str
    speaker: str | None = None
    # cena de fundo nas falas fora das fases: "park", "storm", "god" (só o deus que fala),
    # "black" (só o texto, sem caixa), "night" e "farewell" (o deus que fala, na noite do final)
    scene: str | None = None
    # raio ao abrir a página (só na cena "storm")
    flash: bool = False


@dataclass(frozen=True)
class God:
    name: str
    epithet: str
    intro: tuple
    approve: tuple
    disapprove: tuple


INTRO = (
    Page("Link odiava rock. Odiava o barulho, as guitarras e qualquer um que gostasse delas.", scene="park"),
    Page("Num domingo no parque, uma banda de rua começou a tocar. Link subiu num banco e gritou pro céu:", scene="park"),
    Page("Eu queria que o rock NUNCA tivesse existido!", LINK, scene="park"),
    Page("O céu rachou em raios. Do alto, quatro gigantes se debruçaram sobre ele: os Deuses do Rock.", scene="storm", flash=True),
    Page("Eu sou Grace, a Deusa da Psicodelia. Paz e amor, pequeno... mas não pra quem odeia música.", GRACE, scene="god"),
    Page("Janis, a Deusa do Glamour Sonoro. Querido, você acabou de ofender uma diva.", JANIS, scene="god"),
    Page("Plant, o Deus do Caos Distorcido. Que engraçado, cara. Ninguém nunca tinha pedido isso.", PLANT, scene="god"),
    Page("E eu sou Ozzy, o Príncipe das Trevas. Mortal... você vai aprender o que é PESO.", OZZY, scene="god"),
    Page("Eles não o mataram. Fizeram pior: amaldiçoaram sua vida com a Ressonância.", scene="storm"),
    Page("Desde então tudo desafina. Os passos tropeçam no compasso, e o mundo só volta ao normal quando ele toca.", scene="storm"),
    Page("Cada nota precisa devolve cor ao mundo. Cada nota errada tira um pouco. Se a cor acabar, o silêncio vence.", scene="storm"),
    Page("Uma guitarra surgiu em suas mãos. Pra quebrar a maldição, Link vai ter que agradar os quatro.", scene="black"),
)

GODS = {
    "folk": God(
        GRACE,
        "a Deusa da Psicodelia",
        intro=(
            Page("Paz, pequeno. Sente esse vento? É o mundo respirando no compasso.", GRACE),
            Page("Você pediu silêncio... mas silêncio também é música. Só precisa de notas em volta.", GRACE),
            Page("Não força a corda. Escuta primeiro, depois toca. Eu começo devagar com você.", GRACE),
        ),
        approve=(
            Page("Viu só? Quando você para de brigar com a música, ela te carrega.", GRACE),
            Page("Vai em frente. A Janis te espera, e ela não tem a minha paciência.", GRACE),
        ),
        disapprove=(
            Page("Você tocou com pressa, meu bem. A música sentiu.", GRACE),
            Page("Respira fundo e tenta de novo. O vento não vai a lugar nenhum.", GRACE),
        ),
    ),
    "glam": God(
        JANIS,
        "a Deusa do Glamour Sonoro",
        intro=(
            Page("Então você é o mortal que quis apagar o rock? Que coisa mais... sem graça.", JANIS),
            Page("Na minha passarela não basta acertar. Tem que ter elegância, timing e emoção.", JANIS),
            Page("Querido, tocar errado é pecado. Tocar sem sentir é crime.", JANIS),
        ),
        approve=(
            Page("Ah... isso teve alma. Não conta pra ninguém, mas eu me arrepiei.", JANIS),
            Page("Pode passar. O Plant vai odiar o quanto você está ficando bom.", JANIS),
        ),
        disapprove=(
            Page("Que horror. Você tocou como quem lê a lista do mercado.", JANIS),
            Page("Volta pro começo da passarela e me emociona dessa vez.", JANIS),
        ),
    ),
    "punk": God(
        PLANT,
        "o Deus do Caos Distorcido",
        intro=(
            Page("Você disse que o rock nunca devia ter existido? Que engraçado, cara.", PLANT),
            Page("Relaxa, eu não ligo se você errar. Eu ligo se você tocar com medo.", PLANT),
            Page("Pega essa guitarra e faz barulho de verdade. Toca isso aqui.", PLANT),
        ),
        approve=(
            Page("Hm. Sujo, torto e com raiva. Do jeito que eu gosto.", PLANT),
            Page("Vai lá falar com o Ozzy. Só não chora quando ele começar.", PLANT),
        ),
        disapprove=(
            Page("Bocejo. Certinho demais e sem atitude nenhuma.", PLANT),
            Page("De novo. Toca como se alguém tivesse roubado a sua bicicleta.", PLANT),
        ),
    ),
    "metal": God(
        OZZY,
        "o Príncipe das Trevas",
        intro=(
            Page("Pequeno mortal... você pediu o silêncio. Eu vou te ensinar o que é PESO.", OZZY),
            Page("Aqui o palco é escuro e o volume é infinito. Os fracos ficam pelo caminho.", OZZY),
            Page("Mostra que a maldição não te quebrou. Toca até as cordas pegarem fogo!", OZZY),
        ),
        approve=(
            Page("HAHAHA! Isso sim foi metal! Até as trevas bateram cabeça!", OZZY),
            Page("Você não é mais aquele chato do parque. Agora vai, termina o que começou.", OZZY),
        ),
        disapprove=(
            Page("Fraco! O silêncio que você pediu faz mais barulho que isso.", OZZY),
            Page("De novo! E dessa vez com o volume no máximo!", OZZY),
        ),
    ),
}

ENDING = (
    Page("Quando a última nota ecoou, a tempestade passou e o céu se encheu de cor de novo.", scene="night"),
    Page("Vou fingir que não chorei no seu solo. Mas eu chorei.", JANIS, scene="farewell"),
    Page("Admito: você tem mais atitude do que eu imaginava.", PLANT, scene="farewell"),
    Page("A maldição nunca foi castigo, pequeno. Foi um convite.", GRACE, scene="farewell"),
    Page("Agora vai! O mundo inteiro é o seu palco!", OZZY, scene="farewell"),
    Page("Os deuses sumiram sorrindo. Link voltou ao parque, e a banda de rua ainda estava lá.", scene="park"),
    Page("Dessa vez ele não reclamou. Pediu pra tocar junto.", scene="park"),
    Page("Fim de jogo. Mas o show continua.", scene="park"),
)
