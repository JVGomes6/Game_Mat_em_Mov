"""Sons dos botões, das respostas e da partida."""

from array import array

import pygame


from config import ARQUIVOS_DA_TRILHA, ARQUIVOS_DE_EFEITOS, PASTA_DO_JOGO, SEGUNDOS_POR_FASE


def carregar_audio():
    audio = {}
    # Reserva canais distintos para sobrepor os efeitos à trilha.
    pygame.mixer.set_num_channels(8)
    for nome, caminho in ARQUIVOS_DE_EFEITOS.items():
        audio[nome] = carregar_som(caminho)
    audio['canal_trilha'] = pygame.mixer.Channel(0)
    audio['trechos'] = preparar_trilha()
    frequencia, _, canais = pygame.mixer.get_init()
    audio['frequencia'] = frequencia
    # O mixer usa amostras de 16 bits, com dois bytes por canal em cada quadro de áudio.
    audio['bytes_por_quadro'] = canais * 2
    audio['tempo_anterior'] = None
    audio['fase_anterior'] = None
    return audio


def carregar_som(caminho_relativo):
    caminho = PASTA_DO_JOGO / caminho_relativo
    if not caminho.is_file():
        raise FileNotFoundError(f"Arquivo de áudio não encontrado: {caminho}")
    return pygame.mixer.Sound(str(caminho))


def tocar_clique(audio):
    pygame.mixer.Channel(1).play(audio['clique'])


def tocar_acerto(audio):
    pygame.mixer.Channel(2).play(audio['acerto'])


def tocar_erro(audio):
    pygame.mixer.Channel(3).play(audio['erro'])


# Reamostra os trechos para a duração de cada fase e preserva o PCM para reposicionar a reprodução.
def preparar_trilha():
    frequencia, _, canais = pygame.mixer.get_init()
    quadros_por_trecho = SEGUNDOS_POR_FASE * frequencia
    quadros_de_transicao = frequencia // 200  # 5 ms para suavizar as emendas.
    trechos = []
    for caminho in ARQUIVOS_DA_TRILHA:
        amostras_originais = array("h", carregar_som(caminho).get_raw())
        ultimo_quadro = len(amostras_originais) // canais - 1
        passo = ultimo_quadro / (quadros_por_trecho - 1)
        trecho = array("h")
        for quadro in range(quadros_por_trecho):
            posicao = quadro * passo
            esquerda = min(int(posicao), ultimo_quadro - 1)
            fracao = posicao - esquerda
            indice = esquerda * canais
            # A interpolação linear é feita separadamente em cada canal.
            for canal in range(canais):
                primeiro = amostras_originais[indice + canal]
                segundo = amostras_originais[indice + canal + canais]
                trecho.append(round(primeiro + (segundo - primeiro) * fracao))
        # Aplica transições de volume nas extremidades para reduzir descontinuidades.
        for quadro in range(quadros_de_transicao):
            volume = quadro / quadros_de_transicao
            for canal in range(canais):
                inicio = quadro * canais + canal
                fim = (quadros_por_trecho - 1 - quadro) * canais + canal
                trecho[inicio] = round(trecho[inicio] * volume)
                trecho[fim] = round(trecho[fim] * volume)
        amostras = trecho.tobytes()
        trechos.append((pygame.mixer.Sound(buffer=amostras), amostras))
    return trechos


def iniciar_trilha(audio):
    pygame.mixer.Channel(4).stop()
    sincronizar_trilha(audio, 0.0)


def sincronizar_trilha(audio, tempo_decorrido, intervalo_do_quadro=0.0):
    fase = min(int(tempo_decorrido // SEGUNDOS_POR_FASE), len(audio['trechos']) - 1)
    # Um cronômetro reiniciado pode recuar a posição de referência mesmo dentro da mesma fase.
    voltou_no_tempo = False
    if audio['tempo_anterior'] is not None:
        tempo_esperado = audio['tempo_anterior'] + intervalo_do_quadro
        voltou_no_tempo = tempo_decorrido + 1e-6 < tempo_esperado
    audio['tempo_anterior'] = tempo_decorrido
    if fase == audio['fase_anterior'] and not voltou_no_tempo:
        return

    audio['fase_anterior'] = fase
    som, amostras = audio['trechos'][fase]
    # Converte o tempo dentro da fase em um deslocamento alinhado a quadros de áudio.
    tempo_dentro_da_fase = tempo_decorrido - fase * SEGUNDOS_POR_FASE
    deslocamento = int(tempo_dentro_da_fase * audio['frequencia']) * audio['bytes_por_quadro']
    if deslocamento:
        deslocamento = min(deslocamento, len(amostras) - audio['bytes_por_quadro'])
        som = pygame.mixer.Sound(buffer=amostras[deslocamento:])
    audio['canal_trilha'].play(som, fade_ms=5)


def parar_trilha(audio):
    audio['canal_trilha'].stop()
    audio['fase_anterior'] = None
    audio['tempo_anterior'] = None


def pausar_trilha(audio, pausada):
    if pausada:
        audio['canal_trilha'].pause()
    else:
        audio['canal_trilha'].unpause()
