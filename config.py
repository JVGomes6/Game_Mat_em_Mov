"""Valores fixos e caminhos dos arquivos de Matemática em Movimento."""

from pathlib import Path


PASTA_DO_JOGO = Path(__file__).resolve().parent
LARGURA, ALTURA = 1920, 1080
TAMANHO_DA_JANELA = (1280, 720)
QUADROS_POR_SEGUNDO = 60
TITULO_DO_JOGO = "Matemática em Movimento"
TEMPO_DA_QUESTAO = 30.0
SEGUNDOS_POR_FASE = 10
PRETO = (0, 0, 0)

# As paletas de texto e brilho seguem a ordem das fases do cronômetro.
CORES_DO_CRONOMETRO = ((32, 158, 70), (238, 139, 34), (214, 48, 48))
CORES_DA_BORDA = ((32, 255, 51), (255, 143, 16), (255, 39, 39))
LARGURA_DO_BRILHO = 36

# As coordenadas são relativas à imagem do painel de pausa.
BOTOES_DA_PAUSA = {
    "continuar": (464, 456, 585, 134),
    "jogar_novamente": (465, 610, 586, 133),
    "inicio_dos_resultados": (466, 760, 589, 139),
}
# Cada entrada associa uma área clicável à imagem do estado pressionado.
BOTOES_DOS_MENUS = {
    "inicio": {
        "jogar": ((590, 588, 755, 390), "telaStart/botao_jogar_pressionado.png"),
        "sair": ((289, 840, 159, 159), "telaStart/botao_sair_pressionado.png"),
    },
    "modo": {
        "modo_1": ((337, 535, 596, 365), "telaMod/botao_um_jogador_pressionado.png"),
        "modo_2": ((1010, 535, 608, 365), "telaMod/botao_dois_jogadores_pressionado.png"),
        "voltar_do_modo": ((58, 912, 337, 127), "telaMod/botao_voltar_pressionado.png"),
    },
    "ano": {
        "voltar_do_ano": ((77, 916, 345, 128), "telaAno/botao_voltar_pressionado.png"),
    },
}


# As áreas dos cinco anos têm dimensões fixas e espaçamento uniforme.
for ano in range(1, 6):
    BOTOES_DOS_MENUS["ano"][f"ano_{ano}"] = (
        (250 + (ano - 1) * 298, 545, 296, 310),
        f"telaAno/botao_ano_{ano}_normal.png",
    )


# Os sufixos c e e identificam os estados normal e pressionado, respectivamente.
ARQUIVOS_DE_IMAGEM = {
    "inicio": "telas/telaStart/fundo.png",
    "modo": "telas/telaMod/fundo.png",
    "ano": "telas/telaAno/fundo.png",
    "fundo_duplo": "telas/telaJogo/mult/fundo.png",
    "fundo_individual": "telas/telaJogo/one/fundo.png",
    "menu_de_pausa": "telas/telaPause/menu_de_pausa.png",
    "resultados_duplo": "telas/TelaGameO/TelGO_2/fundo.png",
    "resultados_individual": "telas/TelaGameO/telGO_1/fundo.png",
    "coracao_vermelho": "telas/telaJogo/vida/vida2/coracao_vermelho.png",
    "coracao_cinza": "telas/telaJogo/vida/vida2/coracao_cinza.png",
    "individual_coracao_vermelho": "telas/telaJogo/vida/vida_1/coracao_vermelho.png",
    "individual_coracao_cinza": "telas/telaJogo/vida/vida_1/coracao_cinza.png",
    "individual_pausa_c": "telas/telaJogo/one/botao_pausa_normal.png",
    "individual_pausa_e": "telas/telaJogo/one/botao_pausa_pressionado.png",
    "pausa_c": "telas/telaJogo/mult/botao_pausa_normal.png",
    "pausa_e": "telas/telaJogo/mult/botao_pausa_pressionado.png",
    "jogar_novamente_c": "telas/TelaGameO/TelGO_2/botao_jogar_novamente_normal.png",
    "jogar_novamente_e": "telas/TelaGameO/TelGO_2/botao_jogar_novamente_pressionado.png",
    "inicio_dos_resultados_c": "telas/TelaGameO/TelGO_2/botao_inicio_normal.png",
    "inicio_dos_resultados_e": "telas/TelaGameO/TelGO_2/botao_inicio_pressionado.png",
    "individual_jogar_novamente_e": "telas/TelaGameO/telGO_1/botao_jogar_novamente_pressionado.png",
    "individual_inicio_dos_resultados_e": "telas/TelaGameO/telGO_1/botao_inicio_pressionado.png",
    "individual_apagar_c": "telas/telaJogo/teclado/tecle1/tecla_apagar_normal.png",
    "apagar_1_c": "telas/telaJogo/teclado/tecle2/jogador1/tecla_apagar_normal.png",
    "apagar_2_c": "telas/telaJogo/teclado/tecle2/jogador2/tecla_apagar_normal.png",
}

# Os trechos são listados na ordem das fases da questão.
ARQUIVOS_DA_TRILHA = (
    "audio/1-10segundos.mp3",
    "audio/11-20segundos.mp3",
    "audio/21-30segundos.mp3",
)


ARQUIVOS_DE_EFEITOS = {
    "clique": "audio/clique no botão.mp3",
    "acerto": "audio/acertou a conta.mp3",
    "erro": "audio/errou a conta.mp3",
    "resultado": "audio/resultados de acertos e erros.mp3",
}

CAMINHO_DO_MILHO = "telas/telaJogo/milho.png"
PASTA_TECLADO_INDIVIDUAL = "telas/telaJogo/teclado/tecle1"
PASTAS_TECLADO_DUPLO = (
    "telas/telaJogo/teclado/tecle2/jogador1",
    "telas/telaJogo/teclado/tecle2/jogador2",
)

# As áreas da interface usam a resolução original da arte e o formato (x, y, largura, altura).
AREA_EXTRA_DE_SAIR = (289, 999, 159, 69)
CENTRO_DO_ICONE_DE_INFORMACOES = (1799, 954)
RAIO_DO_ICONE_DE_INFORMACOES = 79
AREA_DO_TEXTO_DE_INFORMACOES = (260, 262, 1400, 590)
BOTOES_DE_INFORMACOES = {
    "voltar": (255, 896, 406, 80),
    "subir": (1450, 896, 95, 80),
    "descer": (1565, 896, 95, 80),
}
# As chaves 1 e 2 nas tabelas de posição correspondem à quantidade de jogadores.
AREAS_DE_PAUSA = {1: (194, 920, 115, 118), 2: (1728, 913, 125, 119)}
CENTROS_DO_BOTAO_DE_PAUSA = {1: (251, 979), 2: (1791, 972)}
BOTOES_DOS_RESULTADOS = {
    1: {
        "jogar_novamente": (235, 849, 687, 184),
        "inicio_dos_resultados": (980, 848, 732, 186),
    },
    2: {
        "jogar_novamente": (315, 891, 598, 172),
        "inicio_dos_resultados": (992, 886, 633, 175),
    },
}
AREAS_DE_CONFIRMAR = {
    1: ((1247, 879, 183, 125),),
    2: ((800, 855, 140, 135), (1518, 855, 140, 135)),
}
POSICOES_DE_APAGAR = {1: ((1124, 969),), 2: ((732, 987), (1454, 987))}

# Os deslocamentos das teclas são relativos à origem de cada teclado.
POSICOES_DO_TECLADO_DUPLO = {
    7: (0, 0), 8: (61, 0), 9: (120, 0),
    4: (0, 40), 5: (61, 40), 6: (120, 40),
    1: (0, 80), 2: (61, 80), 3: (120, 80),
    0: (61, 121),
}
POSICOES_DO_TECLADO_INDIVIDUAL = {
    7: (0, 0), 8: (94, 0), 9: (188, 0),
    4: (0, 49), 5: (94, 49), 6: (188, 49),
    1: (0, 98), 2: (94, 98), 3: (188, 98),
    0: (101, 147),
}
ORIGENS_DO_TECLADO_DUPLO = ((610, 859), (1332, 859))
ORIGEM_DO_TECLADO_INDIVIDUAL = (936, 824)
TAMANHO_DA_TECLA_DUPLA = (60, 40)
TAMANHO_DA_TECLA_INDIVIDUAL = (85, 49)

# No modo duplo, as posições seguem a ordem dos jogadores.
AREAS_DAS_QUESTOES = {
    1: ((502, 728, 914, 73),),
    2: ((487, 711, 452, 60), (981, 711, 452, 60)),
}
AREAS_DAS_RESPOSTAS = {
    1: ((518, 875, 381, 90),),
    2: ((285, 876, 285, 80), (1000, 876, 290, 80)),
}
POSICOES_DOS_CRONOMETROS = {1: ((1231, 83),), 2: ((617, 207), (1226, 207))}
POSICOES_DOS_PULOS = {1: ((1770, 83),), 2: ((888, 207), (1533, 207))}

# As áreas do placar sobrepõem a tabela impressa na arte de resultados.
AREAS_DO_PLACAR = {
    1: ((927, 425, 558, 349),),
    2: ((363, 552, 429, 275), (1126, 552, 430, 275)),
}
NOMES_DAS_OPERACOES = {
    "contagem": "Contagem",
    "adicao": "Soma",
    "subtracao": "Subtração",
    "multiplicacao": "Multiplicação",
    "divisao": "Divisão",
}
