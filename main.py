"""Interface Pygame do jogo Matemática em Movimento."""

import math
import sys

import pygame

from audio_jogo import (
    carregar_audio, iniciar_trilha, parar_trilha,
    pausar_trilha, sincronizar_trilha, tocar_acerto, tocar_clique, tocar_erro,
)
from config import (
    ALTURA, AREA_DO_TEXTO_DE_INFORMACOES, AREA_EXTRA_DE_SAIR,
    AREAS_DAS_QUESTOES, AREAS_DAS_RESPOSTAS,
    AREAS_DE_CONFIRMAR, AREAS_DE_PAUSA, AREAS_DO_PLACAR,
    ARQUIVOS_DE_IMAGEM, BOTOES_DA_PAUSA, BOTOES_DE_INFORMACOES, BOTOES_DOS_MENUS,
    BOTOES_DOS_RESULTADOS, CAMINHO_DO_MILHO, CENTROS_DO_BOTAO_DE_PAUSA,
    CENTRO_DO_ICONE_DE_INFORMACOES, CORES_DA_BORDA, CORES_DO_CRONOMETRO,
    LARGURA, LARGURA_DO_BRILHO,
    NOMES_DAS_OPERACOES, ORIGEM_DO_TECLADO_INDIVIDUAL,
    ORIGENS_DO_TECLADO_DUPLO, PASTA_DO_JOGO, PASTA_TECLADO_INDIVIDUAL,
    PASTAS_TECLADO_DUPLO, POSICOES_DE_APAGAR, POSICOES_DO_TECLADO_DUPLO,
    POSICOES_DO_TECLADO_INDIVIDUAL, POSICOES_DOS_CRONOMETROS,
    POSICOES_DOS_PULOS, PRETO, QUADROS_POR_SEGUNDO, RAIO_DO_ICONE_DE_INFORMACOES,
    SEGUNDOS_POR_FASE, TAMANHO_DA_JANELA, TAMANHO_DA_TECLA_DUPLA,
    TAMANHO_DA_TECLA_INDIVIDUAL, TEMPO_DA_QUESTAO, TITULO_DO_JOGO,
)
from informacoes_jogo import desenhar_guia, preparar_texto_do_guia
from game_logic import (
    apagar_numero, atualizar_tempo,
    confirmar_resposta, criar_partida, digitar_numero, partida_encerrada,
    texto_da_questao,
)


# O controlador concentra as transições e o estado compartilhado entre as telas.
class ControladorDeTelas:
    def __init__(self, jogo):
        self.jogo = jogo
        self.telas = {
            "inicio": TelaInicio(self),
            "informacoes": TelaInformacoes(self),
            "modo": TelaModo(self),
            "ano": TelaAno(self),
            "partida": TelaPartida(self),
            "pausa": TelaPausa(self),
            "resultados": TelaResultados(self),
        }
        self.nome_atual = "inicio"

    # Descarta entradas pendentes para evitar que uma ação seja concluída em outra tela.
    def mudar_tela(self, nome):
        self.nome_atual = nome
        self.jogo['botao_do_mouse'] = None
        self.jogo['teclas_pressionadas'].clear()
        self.jogo['toques_pressionados'].clear()

    def tela_atual(self):
        return self.telas[self.nome_atual]

    def voltar_ao_inicio(self):
        self.jogo['partida'] = None
        parar_trilha(self.jogo['audio'])
        pygame.mixer.Channel(4).stop()
        self.mudar_tela("inicio")


class Tela:
    def __init__(self, controlador):
        self.controlador = controlador
        self.jogo = controlador.jogo

    def atualizar(self, tempo_decorrido):
        # Somente as telas que dependem do tempo precisam implementar a atualização por quadro.
        pass

    def soltar_mouse(self, ponto):
        self.jogo['botao_do_mouse'] = None

    def pressionar_tecla(self, tecla):
        if tecla == pygame.K_ESCAPE:
            self.controlador.voltar_ao_inicio()

    def rolar_mouse(self, passos):
        pass


class TelaComBotoes(Tela):
    def encontrar_botao(self, ponto):
        for botao, retangulo in self.areas_dos_botoes().items():
            if retangulo.collidepoint(ponto):
                return botao
        return None

    def pressionar_mouse(self, ponto):
        botao = self.encontrar_botao(ponto)
        self.jogo['botao_do_mouse'] = botao
        if botao:
            tocar_clique(self.jogo['audio'])

    # Soltar o ponteiro fora do botão cancela a ação iniciada no pressionamento.
    def soltar_mouse(self, ponto):
        pressionado = self.jogo['botao_do_mouse']
        self.jogo['botao_do_mouse'] = None
        if pressionado and pressionado == self.encontrar_botao(ponto):
            self.ativar_botao(pressionado)


class TelaMenu(TelaComBotoes):
    # Os menus inicial, de modo e de ano usam a mesma estrutura de arte e áreas clicáveis.
    def areas_dos_botoes(self):
        areas = {}
        for botao, (coordenadas, _) in BOTOES_DOS_MENUS[self.nome].items():
            areas[botao] = pygame.Rect(coordenadas)
        return areas

    def desenhar(self):
        jogo = self.jogo
        desenhar_fundo(jogo, self.nome)
        botao = jogo['botao_do_mouse']
        botoes = BOTOES_DOS_MENUS[self.nome]
        if botao in botoes:
            retangulo, _ = botoes[botao]
            jogo['tela_base'].blit(jogo['imagens'][botao], retangulo[:2])


class TelaInicio(TelaMenu):
    nome = "inicio"

    def encontrar_botao(self, ponto):
        # A área adicional inclui a parte inferior do botão Sair na arte original.
        if pygame.Rect(AREA_EXTRA_DE_SAIR).collidepoint(ponto):
            return "sair"
        x, y = CENTRO_DO_ICONE_DE_INFORMACOES
        if (ponto[0] - x) ** 2 + (ponto[1] - y) ** 2 <= RAIO_DO_ICONE_DE_INFORMACOES ** 2:
            return "informacoes"
        return super().encontrar_botao(ponto)

    def ativar_botao(self, botao):
        if botao == "jogar":
            self.controlador.mudar_tela("modo")
        elif botao == "informacoes":
            self.controlador.telas["informacoes"].reiniciar_rolagem()
            self.controlador.mudar_tela("informacoes")
        elif botao == "sair":
            self.jogo['deve_continuar'] = False

    def pressionar_tecla(self, tecla):
        if tecla == pygame.K_ESCAPE:
            self.jogo['deve_continuar'] = False


class TelaInformacoes(TelaComBotoes):
    # Pré-renderiza as linhas do guia para reutilizá-las durante a rolagem.
    def __init__(self, controlador):
        super().__init__(controlador)
        self.area_texto = pygame.Rect(AREA_DO_TEXTO_DE_INFORMACOES)
        self.botoes = {
            nome: pygame.Rect(area) for nome, area in BOTOES_DE_INFORMACOES.items()
        }
        self.linhas, altura = preparar_texto_do_guia(self.area_texto.width - 70)
        self.limite = max(0, altura - self.area_texto.height)
        self.reiniciar_rolagem()

    def reiniciar_rolagem(self):
        self.deslocamento = 0
        self.destino = 0

    def areas_dos_botoes(self):
        return self.botoes

    def ativar_botao(self, botao):
        if botao == "voltar":
            self.controlador.mudar_tela("inicio")
        elif botao == "subir":
            self.rolar(-self.area_texto.height * 0.85)
        elif botao == "descer":
            self.rolar(self.area_texto.height * 0.85)

    # Limita o destino ao intervalo entre o topo e o fim do conteúdo.
    def rolar(self, distancia):
        self.destino = max(0, min(self.limite, self.destino + distancia))

    def rolar_mouse(self, passos):
        self.rolar(-passos * 95)

    def pressionar_tecla(self, tecla):
        if tecla == pygame.K_ESCAPE:
            self.ativar_botao("voltar")
        elif tecla == pygame.K_UP:
            self.rolar(-95)
        elif tecla == pygame.K_DOWN:
            self.rolar(95)
        elif tecla == pygame.K_PAGEUP:
            self.ativar_botao("subir")
        elif tecla == pygame.K_PAGEDOWN:
            self.ativar_botao("descer")
        elif tecla == pygame.K_HOME:
            self.destino = 0
        elif tecla == pygame.K_END:
            self.destino = self.limite

    def atualizar(self, tempo_decorrido):
        # Interpola o deslocamento exibido em direção ao destino da rolagem.
        distancia = self.destino - self.deslocamento
        if abs(distancia) < 1:
            self.deslocamento = self.destino
        else:
            self.deslocamento += distancia * min(1, tempo_decorrido * 14)

    def desenhar(self):
        desenhar_fundo(self.jogo, "inicio")
        self.jogo['tela_base'].fill((151, 165, 194), special_flags=pygame.BLEND_RGB_MULT)
        desenhar_guia(
            self.jogo['tela_base'], self.area_texto, self.botoes, self.linhas,
            round(self.deslocamento), self.limite, self.jogo['botao_do_mouse'],
        )


class TelaModo(TelaMenu):
    nome = "modo"

    def ativar_botao(self, botao):
        if botao == "voltar_do_modo":
            self.controlador.voltar_ao_inicio()
        else:
            # O sufixo do identificador do botão indica a quantidade de jogadores.
            self.jogo['modo'] = int(botao[-1])
            self.controlador.mudar_tela("ano")


class TelaAno(TelaMenu):
    nome = "ano"

    def ativar_botao(self, botao):
        if botao == "voltar_do_ano":
            self.controlador.mudar_tela("modo")
        else:
            self.jogo['ano'] = int(botao[-1])
            iniciar_partida(self.jogo)


class TelaPartida(Tela):
    def atualizar(self, tempo_decorrido):
        atualizar_partida(self.jogo, tempo_decorrido)

    def pressionar_mouse(self, ponto):
        tratar_clique_na_partida(self.jogo, ponto)

    def pressionar_tecla(self, tecla):
        if tecla in (pygame.K_ESCAPE, pygame.K_p, pygame.K_SPACE):
            definir_pausa(self.jogo, True)
        else:
            digitar_pelo_teclado(self.jogo, tecla)

    def desenhar(self):
        desenhar_partida(self.jogo)


class TelaPausa(TelaComBotoes):
    def areas_dos_botoes(self):
        return areas_dos_botoes_de_pausa(self.jogo)

    def ativar_botao(self, botao):
        if botao == "continuar":
            definir_pausa(self.jogo, False)
        elif botao == "jogar_novamente":
            iniciar_partida(self.jogo)
        elif botao == "inicio_dos_resultados":
            self.controlador.voltar_ao_inicio()

    def pressionar_tecla(self, tecla):
        if tecla in (pygame.K_ESCAPE, pygame.K_p, pygame.K_SPACE):
            definir_pausa(self.jogo, False)

    def desenhar(self):
        # Desenha a partida congelada como fundo do painel de pausa.
        desenhar_partida(self.jogo)
        desenhar_menu_de_pausa(self.jogo)


class TelaResultados(TelaComBotoes):
    def areas_dos_botoes(self):
        return areas_dos_botoes_de_resultado(individual=self.jogo['modo'] == 1)

    def ativar_botao(self, botao):
        if botao == "jogar_novamente":
            iniciar_partida(self.jogo)
        elif botao == "inicio_dos_resultados":
            self.controlador.voltar_ao_inicio()

    def desenhar(self):
        desenhar_resultados(self.jogo)


# Resolve os recursos em relação à pasta do projeto, independentemente do diretório de execução.
def caminho_do_arquivo(caminho_relativo):
    return PASTA_DO_JOGO / caminho_relativo


def preparar_jogo():
    jogo = {}
    # A superfície base usa a resolução das artes e é redimensionada na apresentação.
    pygame.mixer.pre_init(size=-16, allowedchanges=0)
    pygame.init()
    pygame.mixer.init()
    jogo['janela'] = pygame.display.set_mode(TAMANHO_DA_JANELA, pygame.RESIZABLE)
    pygame.display.set_caption(TITULO_DO_JOGO)
    jogo['tela_base'] = pygame.Surface((LARGURA, ALTURA))
    jogo['relogio'] = pygame.time.Clock()
    jogo['fontes'] = {}
    jogo['imagens'] = {}
    jogo['brilhos_da_borda'] = {}
    carregar_imagens(jogo)
    jogo['audio'] = carregar_audio()

    jogo['modo'] = 1
    jogo['ano'] = 1
    jogo['partida'] = None
    jogo['botao_do_mouse'] = None
    jogo['teclas_pressionadas'] = {}
    jogo['toques_pressionados'] = {}
    jogo['deve_continuar'] = True
    jogo['controlador'] = ControladorDeTelas(jogo)
    return jogo

# As imagens, os textos e as áreas clicáveis compartilham o sistema de coordenadas das artes.
def carregar_imagens(jogo):
    for chave, caminho_relativo in ARQUIVOS_DE_IMAGEM.items():
        jogo['imagens'][chave] = carregar_imagem(caminho_relativo)

    # Recorta as margens transparentes antes de reduzir a figura proporcionalmente.
    milho = carregar_imagem(CAMINHO_DO_MILHO)
    milho = milho.subsurface(milho.get_bounding_rect())
    for chave, altura in (("milho", 24), ("milho_individual", 34)):
        largura = round(milho.get_width() * altura / milho.get_height())
        jogo['imagens'][chave] = pygame.transform.smoothscale(milho, (largura, altura))

    for chave in ("individual_apagar", "apagar_1", "apagar_2"):
        pressionado = jogo['imagens'][f"{chave}_c"].copy()
        pressionado.fill((185, 185, 185, 255), special_flags=pygame.BLEND_RGBA_MULT)
        jogo['imagens'][f"{chave}_e"] = pressionado

    for botoes in BOTOES_DOS_MENUS.values():
        for chave, (retangulo, caminho) in botoes.items():
            imagem = carregar_imagem(f"telas/{caminho}")
            if chave == "voltar_do_ano":
                remover_borda_branca(imagem)
            jogo['imagens'][chave] = ajustar_imagem_botao(imagem, pygame.Rect(retangulo))

    for chave, retangulo in areas_dos_botoes_de_resultado(individual=True).items():
        nome = f"individual_{chave}_e"
        jogo['imagens'][nome] = ajustar_imagem_botao(jogo['imagens'][nome], retangulo)

    for prefixo, tamanho in (("", (65, 55)), ("individual_", (76, 66))):
        for cor in ("vermelho", "cinza"):
            chave = f"{prefixo}coracao_{cor}"
            figura = jogo['imagens'][chave]
            jogo['imagens'][chave] = pygame.transform.smoothscale(
                figura.subsurface(figura.get_bounding_rect()), tamanho
            )

    jogo['imagens_dos_digitos'] = {}
    jogo['digitos_individuais_pressionados'] = {}
    for digito in range(10):
        imagem = carregar_imagem(f"{PASTA_TECLADO_INDIVIDUAL}/tecla_{digito}_pressionada.png")
        remover_borda_branca(imagem)
        jogo['digitos_individuais_pressionados'][digito] = imagem
    imagem = carregar_imagem(f"{PASTA_TECLADO_INDIVIDUAL}/tecla_confirmar_pressionada.png")
    remover_borda_branca(imagem)
    jogo['imagens']["individual_confirmar_e"] = ajustar_imagem_botao(imagem, area_de_confirmar_individual())

    for numero_jogador, pasta in enumerate(PASTAS_TECLADO_DUPLO, 1):
        for digito in range(10):
            for estado in ("c", "e"):
                sufixo = "normal" if estado == "c" else "pressionada"
                # A variante pressionada da tecla 8 do jogador 1 é derivada da imagem normal.
                if (numero_jogador, digito, estado) == (1, 8, "e"):
                    imagem = jogo['imagens_dos_digitos'][(1, 8, "c")].copy()
                    imagem.fill((185, 185, 185, 255), special_flags=pygame.BLEND_RGBA_MULT)
                else:
                    imagem = carregar_imagem(f"{pasta}/tecla_{digito}_{sufixo}.png")
                    remover_borda_branca(imagem)
                jogo['imagens_dos_digitos'][(numero_jogador, digito, estado)] = imagem

        caminho_confirmar = caminho_do_arquivo(f"{pasta}/tecla_confirmar_normal.png")
        caminho_confirmar_pressionado = caminho_do_arquivo(f"{pasta}/tecla_confirmar_pressionada.png")
        jogo['imagens'][f"confirmar_{numero_jogador}_c"] = abrir_imagem(caminho_confirmar)
        jogo['imagens'][f"confirmar_{numero_jogador}_e"] = abrir_imagem(caminho_confirmar_pressionado)
        for estado in ("c", "e"):
            remover_borda_branca(jogo['imagens'][f"confirmar_{numero_jogador}_{estado}"])


def remover_borda_branca(imagem):
    # Torna transparente apenas a região branca conectada ao canto superior esquerdo.
    branco = pygame.mask.from_threshold(imagem, (255, 255, 255, 255), (18, 18, 18, 1))
    borda = branco.connected_component((0, 0))
    transparencia = borda.to_surface(setcolor=(0, 0, 0, 0), unsetcolor=(255, 255, 255, 255))
    imagem.blit(transparencia, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)


def ajustar_imagem_botao(imagem, retangulo):
    return pygame.transform.smoothscale(imagem.subsurface(imagem.get_bounding_rect()), retangulo.size)


def carregar_imagem(caminho_relativo):
    return abrir_imagem(caminho_do_arquivo(caminho_relativo))


def abrir_imagem(caminho):
    if not caminho.is_file():
        raise FileNotFoundError(f"Imagem não encontrada: {caminho}")
    return pygame.image.load(str(caminho)).convert_alpha()


def executar_jogo(jogo):
    while jogo['deve_continuar']:
        tempo_decorrido = jogo['relogio'].tick(QUADROS_POR_SEGUNDO) / 1000.0
        # Atualiza o prazo antes de processar as respostas recebidas no quadro.
        jogo['controlador'].tela_atual().atualizar(tempo_decorrido)
        tratar_eventos(jogo)
        desenhar_tela(jogo)
    pygame.quit()


# Inverte a escala e as margens da apresentação para obter coordenadas da superfície base.
def converter_posicao_da_janela(jogo, posicao):
    largura_janela, altura_janela = jogo['janela'].get_size()
    escala = min(largura_janela / LARGURA, altura_janela / ALTURA)
    largura_desenhada, altura_desenhada = int(LARGURA * escala), int(ALTURA * escala)
    margem_x = (largura_janela - largura_desenhada) // 2
    margem_y = (altura_janela - altura_desenhada) // 2
    x = int((posicao[0] - margem_x) / escala)
    y = int((posicao[1] - margem_y) / escala)
    return x, y

def tratar_eventos(jogo):
    controlador = jogo['controlador']
    for evento in pygame.event.get():
        tela = controlador.tela_atual()
        if evento.type == pygame.QUIT:
            jogo['deve_continuar'] = False
        elif evento.type in (pygame.FINGERDOWN, pygame.FINGERUP):
            tratar_toque(jogo, evento)
        elif evento.type == pygame.MOUSEWHEEL:
            sentido = -1 if getattr(evento, "flipped", False) else 1
            tela.rolar_mouse(sentido * getattr(evento, "precise_y", evento.y))
        elif evento.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            # Ignora eventos de mouse sintetizados por toque para evitar ações duplicadas.
            if evento.button != 1 or getattr(evento, "touch", False):
                continue
            if controlador.nome_atual != "partida" and jogo['toques_pressionados']:
                continue
            ponto = converter_posicao_da_janela(jogo, evento.pos)
            if evento.type == pygame.MOUSEBUTTONDOWN:
                tela.pressionar_mouse(ponto)
            else:
                tela.soltar_mouse(ponto)
        elif evento.type == pygame.WINDOWFOCUSLOST:
            jogo['botao_do_mouse'] = None
            jogo['teclas_pressionadas'].clear()
            jogo['toques_pressionados'].clear()
        elif evento.type == pygame.KEYDOWN:
            tela.pressionar_tecla(evento.key)
        elif evento.type == pygame.KEYUP:
            jogo['teclas_pressionadas'].pop(evento.key, None)


def tratar_toque(jogo, evento):
    # As coordenadas de toque são normalizadas pelo Pygame e precisam ser convertidas em pixels da janela.
    largura, altura = jogo['janela'].get_size()
    ponto = converter_posicao_da_janela(jogo, (evento.x * largura, evento.y * altura))
    dedo = (evento.touch_id, evento.finger_id)
    toques = jogo['toques_pressionados']
    controlador = jogo['controlador']
    tela = controlador.tela_atual()
    na_partida = controlador.nome_atual == "partida"

    if evento.type == pygame.FINGERUP:
        if dedo in toques:
            toques.pop(dedo)
            if not na_partida:
                tela.soltar_mouse(ponto)
        return

    if dedo in toques or (not na_partida and toques):
        return
    if not na_partida:
        # Nos menus, apenas um dedo é acompanhado por vez e a ação é confirmada na soltura.
        toques[dedo] = None
        tela.pressionar_mouse(ponto)
        return

    # O rastreamento por dedo permite que os dois jogadores digitem simultaneamente.
    botao_do_mouse = jogo['botao_do_mouse']
    jogo['botao_do_mouse'] = None
    tela.pressionar_mouse(ponto)
    if controlador.nome_atual == "partida":
        toques[dedo] = jogo['botao_do_mouse']
        jogo['botao_do_mouse'] = botao_do_mouse


def digitar_pelo_teclado(jogo, tecla):
    if tecla in jogo['teclas_pressionadas']:
        return

    indice_jogador, digito = identificar_digito_do_teclado(tecla)
    if indice_jogador is not None and digito is not None:
        if jogo['modo'] == 1:
            indice_jogador = 0
        if digitar_numero(jogo['partida'], indice_jogador, digito):
            id_botao = f"digito_{indice_jogador + 1}_{digito}"
            jogo['teclas_pressionadas'][tecla] = id_botao
            tocar_clique(jogo['audio'])
        return

    if tecla in (pygame.K_BACKSPACE, pygame.K_KP_PERIOD):
        indice_jogador = int(tecla == pygame.K_KP_PERIOD and jogo['modo'] == 2)
        if jogo['partida']['jogadores'][indice_jogador]['ativo']:
            jogo['teclas_pressionadas'][tecla] = area_de_apagar(jogo, indice_jogador)[0]
            apagar_numero(jogo['partida'], indice_jogador)
        return
    if tecla in (pygame.K_RETURN, pygame.K_KP_ENTER):
        indice_jogador = int(tecla == pygame.K_KP_ENTER and jogo['modo'] == 2)
        if not jogo['partida']['jogadores'][indice_jogador]['ativo']:
            return
        botao = "individual_confirmar" if jogo['modo'] == 1 else f"confirmar_{indice_jogador + 1}"
        jogo['teclas_pressionadas'][tecla] = botao
        tocar_clique(jogo['audio'])
        enviar_resposta(jogo, indice_jogador)


def identificar_digito_do_teclado(tecla):
    # A fileira superior atende ao jogador 1, e o teclado numérico, ao jogador 2.
    numeros_da_fileira = {
        pygame.K_0: 0,
        pygame.K_1: 1,
        pygame.K_2: 2,
        pygame.K_3: 3,
        pygame.K_4: 4,
        pygame.K_5: 5,
        pygame.K_6: 6,
        pygame.K_7: 7,
        pygame.K_8: 8,
        pygame.K_9: 9,
    }
    teclado_numerico = {
        pygame.K_KP0: 0,
        pygame.K_KP1: 1,
        pygame.K_KP2: 2,
        pygame.K_KP3: 3,
        pygame.K_KP4: 4,
        pygame.K_KP5: 5,
        pygame.K_KP6: 6,
        pygame.K_KP7: 7,
        pygame.K_KP8: 8,
        pygame.K_KP9: 9,
    }
    if tecla in numeros_da_fileira:
        return 0, numeros_da_fileira[tecla]
    if tecla in teclado_numerico:
        return 1, teclado_numerico[tecla]
    return None, None


def botao_pressionado(jogo, id_botao):
    return (
        jogo['botao_do_mouse'] == id_botao
        or id_botao in jogo['teclas_pressionadas'].values()
        or id_botao in jogo['toques_pressionados'].values()
    )


def areas_dos_botoes_de_resultado(individual):
    modo = 1 if individual else 2
    areas = {}
    for botao, coordenadas in BOTOES_DOS_RESULTADOS[modo].items():
        areas[botao] = pygame.Rect(coordenadas)
    return areas


def tratar_clique_na_partida(jogo, ponto):
    if jogo['partida'] is None:
        return
    area_da_pausa = pygame.Rect(AREAS_DE_PAUSA[jogo['modo']])
    if area_da_pausa.collidepoint(ponto):
        definir_pausa(jogo, True)
        tocar_clique(jogo['audio'])
        return

    for indice, jogador in enumerate(jogo['partida']['jogadores']):
        botao, retangulo = area_de_apagar(jogo, indice)
        if jogador['ativo'] and retangulo.collidepoint(ponto):
            jogo['botao_do_mouse'] = botao
            apagar_numero(jogo['partida'], indice)
            tocar_clique(jogo['audio'])
            return

    # As áreas clicáveis variam por modo. A lógica de entrada é compartilhada.
    for indice_jogador, jogador in enumerate(jogo['partida']['jogadores']):
        if not jogador['ativo']:
            continue
        numero_jogador = indice_jogador + 1
        if jogo['modo'] == 1:
            areas_numeros = areas_do_teclado_individual()
            area_confirmar = area_de_confirmar_individual()
            botao_confirmar = "individual_confirmar"
        else:
            areas_numeros = areas_do_teclado_duplo(numero_jogador)
            area_confirmar = area_de_confirmar_duplo(numero_jogador)
            botao_confirmar = f"confirmar_{numero_jogador}"

        for digito, retangulo in areas_numeros.items():
            if retangulo.collidepoint(ponto):
                if digitar_numero(jogo['partida'], indice_jogador, digito):
                    jogo['botao_do_mouse'] = f"digito_{numero_jogador}_{digito}"
                    tocar_clique(jogo['audio'])
                return
        if area_confirmar.collidepoint(ponto):
            jogo['botao_do_mouse'] = botao_confirmar
            tocar_clique(jogo['audio'])
            enviar_resposta(jogo, indice_jogador)
            return


# Os dois teclados compartilham os deslocamentos das teclas a partir de suas respectivas origens.
def areas_do_teclado_duplo(numero_jogador):
    esquerda, topo = ORIGENS_DO_TECLADO_DUPLO[numero_jogador - 1]
    largura, altura = TAMANHO_DA_TECLA_DUPLA
    areas = {}
    for digito, (dx, dy) in POSICOES_DO_TECLADO_DUPLO.items():
        areas[digito] = pygame.Rect(esquerda + dx, topo + dy, largura, altura)
    return areas


def area_de_confirmar_duplo(numero_jogador):
    return pygame.Rect(AREAS_DE_CONFIRMAR[2][numero_jogador - 1])


def areas_do_teclado_individual():
    esquerda, topo = ORIGEM_DO_TECLADO_INDIVIDUAL
    largura, altura = TAMANHO_DA_TECLA_INDIVIDUAL
    areas = {}
    for digito, (dx, dy) in POSICOES_DO_TECLADO_INDIVIDUAL.items():
        areas[digito] = pygame.Rect(esquerda + dx, topo + dy, largura, altura)
    return areas


def area_de_confirmar_individual():
    return pygame.Rect(AREAS_DE_CONFIRMAR[1][0])


def area_de_apagar(jogo, indice_jogador):
    if jogo['modo'] == 1:
        botao = "individual_apagar"
    else:
        botao = f"apagar_{indice_jogador + 1}"
    posicao = POSICOES_DE_APAGAR[jogo['modo']][indice_jogador]
    return botao, jogo['imagens'][f"{botao}_c"].get_rect(topleft=posicao)


def enviar_resposta(jogo, indice_jogador):
    partida = jogo['partida']
    if partida is None or indice_jogador >= len(partida['jogadores']):
        return
    resultado = confirmar_resposta(partida, indice_jogador)
    if resultado is True:
        tocar_acerto(jogo['audio'])
    elif resultado is False:
        tocar_erro(jogo['audio'])
    verificar_fim_da_partida(jogo)
    if resultado is not None:
        atualizar_trilha(jogo)


# Mantém a tela, o estado da partida e a trilha sincronizados durante a pausa.
def definir_pausa(jogo, pausada):
    if jogo['partida'] is None:
        return
    jogo['partida']['pausada'] = pausada
    tela = "pausa" if pausada else "partida"
    jogo['controlador'].mudar_tela(tela)
    pausar_trilha(jogo['audio'], pausada)

def iniciar_partida(jogo):
    jogo['partida'] = criar_partida(jogo['ano'], jogo['modo'])
    parar_trilha(jogo['audio'])
    iniciar_trilha(jogo['audio'])
    jogo['controlador'].mudar_tela("partida")


def atualizar_partida(jogo, tempo_decorrido):
    if jogo['controlador'].nome_atual == "partida" and jogo['partida'] is not None:
        expirados = atualizar_tempo(jogo['partida'], tempo_decorrido)
        for _ in expirados:
            tocar_erro(jogo['audio'])
        verificar_fim_da_partida(jogo)
        atualizar_trilha(jogo, tempo_decorrido)


def atualizar_trilha(jogo, intervalo_do_quadro=0.0):
    if jogo['controlador'].nome_atual == "partida" and jogo['partida'] is not None:
        sincronizar_trilha(jogo['audio'], TEMPO_DA_QUESTAO - menor_tempo_restante(jogo), intervalo_do_quadro)


def menor_tempo_restante(jogo):
    # A trilha e o brilho seguem o cronômetro ativo com menos tempo restante.
    menor_tempo = TEMPO_DA_QUESTAO
    for jogador in jogo['partida']['jogadores']:
        if jogador['ativo']:
            menor_tempo = min(menor_tempo, jogador['segundos_restantes'])
    return menor_tempo


def verificar_fim_da_partida(jogo):
    if jogo['controlador'].nome_atual == "partida" and jogo['partida'] is not None and partida_encerrada(jogo['partida']):
        jogo['controlador'].mudar_tela("resultados")
        parar_trilha(jogo['audio'])
        pygame.mixer.Channel(4).play(jogo['audio']['resultado'])

def desenhar_tela(jogo):
    jogo['tela_base'].fill(PRETO)
    jogo['controlador'].tela_atual().desenhar()

    # Mantém a proporção da arte e centraliza a superfície base na janela.
    largura_janela, altura_janela = jogo['janela'].get_size()
    escala = min(largura_janela / LARGURA, altura_janela / ALTURA)
    tela_redimensionada = pygame.transform.smoothscale(
        jogo['tela_base'],
        (int(LARGURA * escala), int(ALTURA * escala)),
    )
    jogo['janela'].fill(PRETO)
    jogo['janela'].blit(
        tela_redimensionada,
        ((largura_janela - tela_redimensionada.get_width()) // 2,
         (altura_janela - tela_redimensionada.get_height()) // 2),
    )
    pygame.display.update()


def desenhar_fundo(jogo, nome):
    jogo['tela_base'].blit(jogo['imagens'][nome], (0, 0))


def desenhar_partida(jogo):
    if jogo['partida'] is None:
        return
    fundo = "fundo_duplo" if jogo['modo'] == 2 else "fundo_individual"
    desenhar_fundo(jogo, fundo)
    if jogo['modo'] == 2:
        desenhar_modo_duplo(jogo)
    else:
        desenhar_modo_individual(jogo)

    desenhar_botao_de_pausa(jogo)
    desenhar_brilho_da_borda(jogo)


# Mantém uma superfície de brilho em cache para cada fase do cronômetro.
def desenhar_brilho_da_borda(jogo):
    fase = fase_do_cronometro(menor_tempo_restante(jogo))
    brilho = jogo['brilhos_da_borda'].get(fase)
    if brilho is None:
        cor = CORES_DA_BORDA[fase]
        brilho = pygame.Surface(jogo['tela_base'].get_size(), pygame.SRCALPHA)
        limites = brilho.get_rect()
        # A opacidade diminui em direção ao centro para suavizar o brilho.
        for recuo in range(LARGURA_DO_BRILHO):
            opacidade = round(245 * (1 - recuo / LARGURA_DO_BRILHO) ** 2)
            pygame.draw.rect(brilho, (*cor, opacidade), limites.inflate(-2 * recuo, -2 * recuo), 1)
        jogo['brilhos_da_borda'][fase] = brilho
    jogo['tela_base'].blit(brilho, (0, 0))


def desenhar_modo_duplo(jogo):
    for indice, jogador in enumerate(jogo['partida']['jogadores']):
        numero_jogador = indice + 1
        cor_tempo = cor_do_cronometro(jogador['segundos_restantes'])
        desenhar_texto(
            jogo,
            f"{math.ceil(jogador['segundos_restantes']):02d}",
            POSICOES_DOS_CRONOMETROS[2][indice],
            49,
            cor_tempo,
        )
        desenhar_texto(
            jogo,
            str(jogador['pulos']),
            POSICOES_DOS_PULOS[2][indice],
            38,
            (27, 154, 71),
        )
        desenhar_vidas(jogo, jogador['vidas'], indice)
        desenhar_questao(jogo, jogador, indice)
        desenhar_resposta(jogo, jogador, indice)
        desenhar_teclado_duplo(jogo, numero_jogador)


def desenhar_modo_individual(jogo):
    jogador = jogo['partida']['jogadores'][0]
    desenhar_texto(
        jogo,
        f"{math.ceil(jogador['segundos_restantes']):02d}",
        POSICOES_DOS_CRONOMETROS[1][0],
        46,
        cor_do_cronometro(jogador['segundos_restantes']),
    )
    desenhar_texto(jogo, str(jogador['pulos']), POSICOES_DOS_PULOS[1][0], 46, (26, 108, 202))
    desenhar_vidas(jogo, jogador['vidas'], 0, individual=True)
    desenhar_questao(jogo, jogador, 0, individual=True)
    desenhar_resposta(jogo, jogador, 0, individual=True)
    desenhar_teclado_individual(jogo)


def desenhar_botao_de_pausa(jogo):
    prefixo = "" if jogo['modo'] == 2 else "individual_"
    estado = "e" if jogo['controlador'].nome_atual == "pausa" else "c"
    imagem = jogo['imagens'][f"{prefixo}pausa_{estado}"]
    centro = CENTROS_DO_BOTAO_DE_PAUSA[jogo['modo']]
    visivel = imagem.subsurface(imagem.get_bounding_rect())
    desenhar_imagem_centralizada(jogo, visivel, centro)


def fase_do_cronometro(segundos_restantes):
    # O tempo decorrido determina a fase e a cor associada, em ordem verde, laranja e vermelha.
    tempo_decorrido = TEMPO_DA_QUESTAO - segundos_restantes
    if tempo_decorrido < SEGUNDOS_POR_FASE:
        return 0
    if tempo_decorrido < 2 * SEGUNDOS_POR_FASE:
        return 1
    return 2


def cor_do_cronometro(segundos_restantes):
    return CORES_DO_CRONOMETRO[fase_do_cronometro(segundos_restantes)]


def desenhar_vidas(jogo, vidas, indice_jogador, individual=False):
    if individual:
        centros = (706, 791, 877)
        y = 65
        prefixo = "individual_"
    else:
        centros = (507, 585, 663) if indice_jogador == 0 else (1264, 1342, 1420)
        y = 355
        prefixo = ""

    for indice, x in enumerate(centros):
        cor = "vermelho" if indice < vidas else "cinza"
        figura = jogo['imagens'][f"{prefixo}coracao_{cor}"]
        retangulo = figura.get_rect(center=(x, y))
        # Cobre os corações da arte de fundo antes de desenhar o estado atual das vidas.
        pygame.draw.rect(jogo['tela_base'], (248, 249, 253), retangulo.inflate(8, 10))
        jogo['tela_base'].blit(figura, retangulo)


def desenhar_questao(
    jogo,
    jogador,
    indice_jogador,
    individual=False,
):
    modo = 1 if individual else 2
    retangulo = pygame.Rect(AREAS_DAS_QUESTOES[modo][indice_jogador])
    if individual:
        borda = (33, 125, 213)
    elif indice_jogador == 0:
        borda = (28, 132, 238)
    else:
        borda = (214, 37, 143)
    pygame.draw.rect(jogo['tela_base'], (255, 255, 255), retangulo, border_radius=18)
    pygame.draw.rect(jogo['tela_base'], borda, retangulo, width=5, border_radius=18)
    cor = (26, 48, 115)
    if jogador['ativo'] and jogador['questao']['operacao'] == "contagem":
        desenhar_texto(jogo, "Quantos milhos?", (retangulo.centerx, retangulo.centery - 15), 24, cor)
        milho = jogo['imagens']["milho_individual" if individual else "milho"]
        quantidade = jogador['questao']['resposta']
        passo = milho.get_width() + 4
        # O espaçamento a cada cinco espigas facilita a contagem em grupos.
        espaco_entre_grupos = 8
        largura_da_fileira = (quantidade - 1) * passo + milho.get_width() + ((quantidade - 1) // 5) * espaco_entre_grupos
        x = retangulo.centerx - largura_da_fileira // 2
        y = retangulo.centery + 13 - milho.get_height() // 2
        for indice in range(quantidade):
            jogo['tela_base'].blit(milho, (x + indice * passo + (indice // 5) * espaco_entre_grupos, y))
        return

    expressao = texto_da_questao(jogador['questao']) if jogador['ativo'] else "Sem vidas"
    tamanho_da_fonte = 43 if individual else 39
    while tamanho_da_fonte > 18:
        fonte = obter_fonte(jogo, tamanho_da_fonte)
        if fonte.size(expressao)[0] <= retangulo.width - 24:
            break
        tamanho_da_fonte -= 2
    desenhar_texto(
        jogo,
        expressao,
        retangulo.center,
        tamanho_da_fonte,
        cor,
    )


def desenhar_resposta(
    jogo,
    jogador,
    indice_jogador,
    individual=False,
):
    modo = 1 if individual else 2
    retangulo = pygame.Rect(AREAS_DAS_RESPOSTAS[modo][indice_jogador])
    pygame.draw.rect(jogo['tela_base'], (255, 255, 255), retangulo, border_radius=8)
    if jogador['resposta_digitada']:
        desenhar_texto(
            jogo,
            jogador['resposta_digitada'],
            (retangulo.x + 18, retangulo.centery),
            42,
            (29, 48, 109),
            meio_esquerda=True,
        )
    else:
        desenhar_texto(
            jogo,
            "Digite o resultado..." if jogador['ativo'] else "",
            retangulo.center,
            29,
            (117, 126, 158),
        )


def desenhar_teclado_duplo(jogo, numero_jogador):
    for digito, retangulo in areas_do_teclado_duplo(numero_jogador).items():
        id_botao = f"digito_{numero_jogador}_{digito}"
        estado = "e" if botao_pressionado(jogo, id_botao) else "c"
        imagem = jogo['imagens_dos_digitos'][(numero_jogador, digito, estado)]
        jogo['tela_base'].blit(imagem, retangulo.topleft)

    id_botao = f"confirmar_{numero_jogador}"
    estado = "e" if botao_pressionado(jogo, id_botao) else "c"
    jogo['tela_base'].blit(
        jogo['imagens'][f"confirmar_{numero_jogador}_{estado}"],
        area_de_confirmar_duplo(numero_jogador).topleft,
    )
    desenhar_botao_de_apagar(jogo, numero_jogador - 1)


# A arte individual já contém as teclas numéricas no estado normal.
def desenhar_teclado_individual(jogo):
    for digito, retangulo in areas_do_teclado_individual().items():
        id_botao = f"digito_1_{digito}"
        if botao_pressionado(jogo, id_botao):
            imagem = jogo['digitos_individuais_pressionados'][digito]
            jogo['tela_base'].blit(imagem, retangulo.topleft)

    if botao_pressionado(jogo, "individual_confirmar"):
        jogo['tela_base'].blit(jogo['imagens']["individual_confirmar_e"], area_de_confirmar_individual().topleft)
    desenhar_botao_de_apagar(jogo, 0)


def desenhar_botao_de_apagar(jogo, indice_jogador):
    botao, retangulo = area_de_apagar(jogo, indice_jogador)
    estado = "e" if botao_pressionado(jogo, botao) else "c"
    jogo['tela_base'].blit(jogo['imagens'][f"{botao}_{estado}"], retangulo)


def area_do_menu_de_pausa(jogo):
    return jogo['imagens']["menu_de_pausa"].get_rect(center=(LARGURA // 2, ALTURA // 2))


# Translada as áreas clicáveis pela posição do painel na superfície base.
def areas_dos_botoes_de_pausa(jogo):
    menu = area_do_menu_de_pausa(jogo)
    areas = {}
    for botao, retangulo in BOTOES_DA_PAUSA.items():
        areas[botao] = pygame.Rect(retangulo).move(menu.x, menu.y)
    return areas


def desenhar_menu_de_pausa(jogo):
    camada = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    camada.fill((15, 25, 55, 150))
    jogo['tela_base'].blit(camada, (0, 0))
    jogo['tela_base'].blit(jogo['imagens']["menu_de_pausa"], area_do_menu_de_pausa(jogo))
    retangulo = areas_dos_botoes_de_pausa(jogo).get(jogo['botao_do_mouse'])
    if retangulo:
        sombra = pygame.Surface(retangulo.size, pygame.SRCALPHA)
        pygame.draw.rect(sombra, (0, 0, 0, 55), sombra.get_rect(), border_radius=retangulo.height // 2)
        jogo['tela_base'].blit(sombra, retangulo)


def desenhar_resultados(jogo):
    chave = "resultados_duplo" if jogo['modo'] == 2 else "resultados_individual"
    desenhar_fundo(jogo, chave)
    for indice, jogador in enumerate(jogo['partida']['jogadores']):
        desenhar_placar(jogo, jogador, indice)

    for botao, retangulo in areas_dos_botoes_de_resultado(individual=jogo['modo'] == 1).items():
        if jogo['modo'] == 2:
            estado = "e" if botao_pressionado(jogo, botao) else "c"
            jogo['tela_base'].blit(jogo['imagens'][f"{botao}_{estado}"], retangulo.topleft)
        elif botao_pressionado(jogo, botao):
            jogo['tela_base'].blit(jogo['imagens'][f"individual_{botao}_e"], retangulo.topleft)


def desenhar_placar(jogo, jogador, indice):
    modo = jogo['modo']
    if modo == 1:
        posicao_dos_pulos, tamanho_dos_pulos = (815, 568), 54
    else:
        posicao_dos_pulos = ((714, 514), (1490, 514))[indice]
        tamanho_dos_pulos = 36
    azul = (25, 48, 109)
    verde = (20, 110, 54)
    vermelho = (160, 40, 50)
    desenhar_texto(jogo, str(jogador['pulos']), posicao_dos_pulos, tamanho_dos_pulos, azul)

    # Os totais são agrupados por operação para cada jogador.
    quadro = pygame.Rect(AREAS_DO_PLACAR[modo][indice])
    pygame.draw.rect(jogo['tela_base'], (233, 241, 255), quadro, border_radius=14)
    x_operacao = quadro.left + 15
    x_acertos = quadro.left + quadro.width * 63 // 100
    x_erros = quadro.left + quadro.width * 88 // 100
    altura_linha = quadro.height // 6
    y = quadro.top + altura_linha // 2
    tamanho_fonte = 28 if modo == 1 else 23
    desenhar_texto(jogo, "Operação", (x_operacao, y), tamanho_fonte, azul, meio_esquerda=True)
    desenhar_texto(jogo, "Acertos", (x_acertos, y), tamanho_fonte, verde)
    desenhar_texto(jogo, "Erros", (x_erros, y), tamanho_fonte, vermelho)

    for operacao, nome in NOMES_DAS_OPERACOES.items():
        y += altura_linha
        acertos = jogador['acertos_por_operacao'][operacao]
        erros = jogador['erros_por_operacao'][operacao]
        desenhar_texto(jogo, nome, (x_operacao, y), tamanho_fonte, azul, meio_esquerda=True)
        desenhar_texto(jogo, str(acertos), (x_acertos, y), tamanho_fonte, verde)
        desenhar_texto(jogo, str(erros), (x_erros, y), tamanho_fonte, vermelho)


def desenhar_texto(
    jogo,
    texto,
    posicao,
    tamanho,
    cor,
    meio_esquerda=False,
):
    fonte = obter_fonte(jogo, tamanho)
    imagem = fonte.render(texto, True, cor)
    if meio_esquerda:
        retangulo = imagem.get_rect(midleft=posicao)
    else:
        retangulo = imagem.get_rect(center=posicao)
    jogo['tela_base'].blit(imagem, retangulo)


# Mantém uma fonte em cache por tamanho para reutilização entre quadros.
def obter_fonte(jogo, tamanho):
    if tamanho not in jogo['fontes']:
        jogo['fontes'][tamanho] = pygame.font.SysFont("arial", tamanho, bold=True)
    return jogo['fontes'][tamanho]


def desenhar_imagem_centralizada(jogo, imagem, centro):
    jogo['tela_base'].blit(imagem, imagem.get_rect(center=centro))

def principal():
    try:
        executar_jogo(preparar_jogo())
    except (FileNotFoundError, pygame.error) as erro:
        print(f"Não foi possível iniciar o jogo: {erro}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(principal())
