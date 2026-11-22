"""Conteúdo e desenho do guia acessível pelo botão de informações."""

import pygame


SECOES = (
    ("O que é o jogo?", (
        "Matemática em Movimento é um jogo educativo feito em Python com Pygame para estudantes do 1º ao 5º ano do Ensino Fundamental. A brincadeira de pular corda dá o tema aos desafios de matemática.",
        "O jogo ajuda a praticar o raciocínio lógico, a atenção, a concentração e a resolução de desafios. Pode ser usado na escola ou em casa, com acompanhamento de professores ou familiares quando necessário.",
    )),
    ("Como começar?", (
        "Na tela inicial, selecione Iniciar. Escolha jogar sozinho ou em dupla e selecione o ano escolar, do 1º ao 5º.",
        "Os desafios ficam mais difíceis dentro do ano escolhido. A versão atual segue direto para a partida depois da seleção do ano.",
    )),
    ("Modos de jogo", (
        "Individual. Você tem três vidas e até 30 segundos por questão. Cada resposta correta vale um pulo. A partida acaba quando as três vidas terminam.",
        "Dupla. Os dois jogadores começam com a mesma questão, no mesmo computador. Cada um tem suas próprias questões, resposta, vidas, pulos e cronômetro. Assim que alguém acerta, ganha um pulo e recebe outra questão. O outro jogador continua com a sua questão.",
        "Quando um jogador perde as três vidas, o outro pode continuar. Os dois resultados aparecem lado a lado quando ambos terminam.",
    )),
    ("Como responder?", (
        "Leia a questão, digite o resultado e confirme. Você pode clicar ou tocar no teclado da tela. Use o botão de apagar para remover o último dígito antes de confirmar.",
        "No teclado físico, o Jogador 1 usa os números da fileira superior, Enter e Backspace. O Jogador 2 usa os números do teclado numérico, o Enter numérico e a tecla de ponto do teclado numérico para apagar. No modo individual, os dois conjuntos de teclas funcionam.",
    )),
    ("Tempo e cores", (
        "Cada questão começa com 30 segundos. Pelo tempo decorrido, o cronômetro fica verde de 0 até antes de 10 segundos, laranja de 10 até antes de 20 e vermelho de 20 até o fim.",
        "Na dupla, cada jogador tem seu cronômetro. A borda e os três trechos da música seguem o cronômetro ativo mais perto de zerar. Quando o tempo acaba, o jogador perde uma vida. Quem ainda tem vidas recebe outra questão com 30 segundos, após acerto, erro ou tempo esgotado.",
        "O jogo também toca efeitos sonoros de clique, acerto, erro e resultados.",
    )),
    ("Vidas e pulos", (
        "Cada jogador começa com três corações vermelhos. Uma resposta errada ou o fim do tempo deixa um coração cinza. Cada resposta certa soma exatamente um pulo, sem bônus por rapidez.",
    )),
    ("Conteúdos por ano escolar", (
        "As questões praticam um recorte dos conteúdos de Matemática dos anos iniciais. Os exemplos abaixo ilustram as atividades que podem ser trabalhadas.",
        "1º ano • Contagem de até 15 espigas, adição e subtração com números naturais pequenos. Exemplos: contar 6 espigas, 4 + 3 ou 9 − 2.",
        "2º ano • Adição, subtração e multiplicações com grupos de 2, 3, 4 ou 5. Exemplos: 18 + 12, 35 − 10 ou 3 × 4.",
        "3º ano • Adição, subtração, multiplicação e divisão exata com números naturais. Exemplos: 68 + 20, 4 × 5 ou 20 ÷ 5.",
        "4º ano • As quatro operações com números naturais maiores e divisão exata. Exemplos: 340 + 125, 48 × 6 ou 96 ÷ 8. Frações ainda ficam fora deste recorte.",
        "5º ano • As quatro operações com números naturais de maior valor e divisão exata. Exemplos: 2.450 + 1.250, 24 × 12 ou 144 ÷ 12. O jogo ainda usa apenas números inteiros.",
    )),
    ("Pausar, retomar e recomeçar", (
        "Use o botão de pausa ou pressione Esc, P ou Espaço. O jogo guarda a questão e congela os cronômetros. Retomar, ou apertar a tecla de pausa novamente, continua do mesmo ponto.",
        "Recomeçar abre outra partida no mesmo modo e ano, com três vidas e os contadores zerados. Voltar ao início leva ao menu inicial.",
    )),
    ("Fim de jogo e resultados", (
        "A partida termina quando todos os participantes perdem suas três vidas. O placar mostra o total de pulos e os acertos e erros por tipo de questão. Resposta incorreta e tempo esgotado entram na coluna Erros.",
        "Use Recomeçar para jogar novamente ou Voltar ao início para abrir o menu.",
    )),
    ("Proposta educacional", (
        "A proposta é reforçar conhecimentos matemáticos de forma lúdica, estimular a concentração e o raciocínio e incentivar a participação. No modo dupla, cada jogador avança no seu próprio ritmo.",
        "É um recurso complementar e cobre parte das habilidades da BNCC. O acompanhamento pedagógico pode ajudar a transformar as tentativas em oportunidades de aprendizagem.",
        "Pular também é aprender!",
    )),
)

AZUL = (18, 52, 106)
AZUL_BOTAO = (23, 92, 168)
AZUL_PRESSIONADO = (18, 64, 123)
ROSA = (157, 37, 103)
VERDE = (19, 104, 62)
AMARELO = (255, 234, 173)
PAINEL = (249, 252, 255)
BRANCO = (255, 255, 255)


def quebrar_paragrafo(texto, fonte, largura):
    linha = ""
    for palavra in texto.split():
        candidata = f"{linha} {palavra}" if linha else palavra
        if linha and fonte.size(candidata)[0] > largura:
            yield linha
            linha = palavra
        else:
            linha = candidata
    if linha:
        yield linha


def preparar_texto_do_guia(largura):
    # Pré-renderiza as linhas e registra suas posições verticais para reutilização durante a rolagem.
    fonte_titulo = pygame.font.SysFont("arial", 35, bold=True)
    fonte_texto = pygame.font.SysFont("arial", 31)
    linhas = []
    y = 24
    for indice, (titulo, paragrafos) in enumerate(SECOES, 1):
        linhas.append((y, fonte_titulo.render(f"{indice}. {titulo}", True, ROSA)))
        y += fonte_titulo.get_linesize() + 14
        for paragrafo in paragrafos:
            for linha in quebrar_paragrafo(paragrafo, fonte_texto, largura):
                linhas.append((y, fonte_texto.render(linha, True, AZUL)))
                y += fonte_texto.get_linesize() + 5
            y += 12
        y += 20
    return linhas, y


def desenhar_guia(tela, area_texto, botoes, linhas, deslocamento, limite, pressionado):
    painel = pygame.Rect(200, 64, 1520, 950)
    pygame.draw.rect(tela, AZUL, painel.inflate(14, 14), border_radius=42)
    pygame.draw.rect(tela, PAINEL, painel, border_radius=38)
    pygame.draw.rect(tela, AMARELO, (225, 88, 1470, 152), border_radius=26)
    desenhar_rotulo(tela, "INFORMAÇÕES DO JOGO", (960, 116), 30, ROSA)
    desenhar_rotulo(tela, "MATEMÁTICA EM MOVIMENTO", (960, 169), 57, AZUL)
    desenhar_rotulo(tela, "Pular também é aprender!", (960, 216), 30, VERDE)

    pygame.draw.rect(tela, (231, 242, 255), area_texto, border_radius=18)
    # Restringe o desenho das linhas à área de texto para manter o cabeçalho e os controles visíveis.
    recorte_anterior = tela.get_clip()
    tela.set_clip(area_texto)
    for y, imagem in linhas:
        topo = area_texto.top + y - deslocamento
        if topo < area_texto.bottom and topo + imagem.get_height() > area_texto.top:
            tela.blit(imagem, (area_texto.left + 35, topo))
    tela.set_clip(recorte_anterior)

    trilho = pygame.Rect(area_texto.right + 13, area_texto.top, 13, area_texto.height)
    pygame.draw.rect(tela, (209, 226, 249), trilho, border_radius=7)
    # O indicador representa a fração visível do conteúdo e tem altura mínima.
    altura_barra = max(52, trilho.height ** 2 // (trilho.height + limite))
    y = trilho.top
    if limite:
        y += round((trilho.height - altura_barra) * deslocamento / limite)
    pygame.draw.rect(tela, AZUL_BOTAO, (trilho.x, y, trilho.width, altura_barra), border_radius=7)

    for nome, rotulo in (("voltar", "Voltar ao início"), ("subir", "↑"), ("descer", "↓")):
        botao = botoes[nome]
        cor = AZUL_PRESSIONADO if pressionado == nome else AZUL_BOTAO
        pygame.draw.rect(tela, cor, botao, border_radius=21)
        desenhar_rotulo(tela, rotulo, botao.center, 38, BRANCO)
    desenhar_rotulo(tela, "Role ou use as setas para ler", (1040, 936), 26, AZUL)


def desenhar_rotulo(tela, texto, centro, tamanho, cor):
    fonte = pygame.font.SysFont("arial", tamanho, bold=True)
    imagem = fonte.render(texto, True, cor)
    tela.blit(imagem, imagem.get_rect(center=centro))
