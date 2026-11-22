"""Regras e estado da partida de Matemática em Movimento."""

import random

from config import TEMPO_DA_QUESTAO


SIMBOLOS = {
    "adicao": "+",
    "subtracao": "-",
    "multiplicacao": "×",
    "divisao": "÷",
}

# Operações disponíveis para sorteio em cada ano escolar.
OPERACOES_POR_ANO = {
    1: ("contagem", "adicao", "subtracao"),
    2: ("adicao", "subtracao", "multiplicacao"),
    3: ("adicao", "subtracao", "multiplicacao", "divisao"),
    4: ("adicao", "subtracao", "multiplicacao", "divisao"),
    5: ("adicao", "subtracao", "multiplicacao", "divisao"),
}


def criar_questao(esquerdo, direito, operacao, resposta):
    return {
        'esquerdo': esquerdo,
        'direito': direito,
        'operacao': operacao,
        'resposta': resposta,
    }


def texto_da_questao(questao):
    # Questões de contagem são renderizadas separadamente com imagens.
    simbolo = SIMBOLOS[questao['operacao']]
    return f"{questao['esquerdo']} {simbolo} {questao['direito']} = ?"


def criar_partida(ano, quantidade_jogadores=2, sorteador=None):
    if ano not in OPERACOES_POR_ANO:
        raise ValueError("O ano escolar deve estar entre 1 e 5.")
    if quantidade_jogadores not in (1, 2):
        raise ValueError("A partida aceita um ou dois jogadores.")
    if sorteador is None:
        sorteador = random.Random()

    # Os jogadores recebem a mesma questão inicial e mantêm placares independentes.
    questao_inicial = sortear_questao(ano, sorteador=sorteador)
    jogadores = []
    for _ in range(quantidade_jogadores):
        acertos = {'contagem': 0}
        for operacao in SIMBOLOS:
            acertos[operacao] = 0
        jogadores.append({
            'questao': questao_inicial,
            'vidas': 3,
            'pulos': 0,
            'segundos_restantes': TEMPO_DA_QUESTAO,
            'resposta_digitada': "",
            'ativo': True,
            'acertos_por_operacao': acertos,
            'erros_por_operacao': acertos.copy(),
            'progresso': 0,
        })
    return {
        'ano': ano,
        'sorteador': sorteador,
        'jogadores': jogadores,
        'pausada': False,
    }


def partida_encerrada(partida):
    for jogador in partida['jogadores']:
        if jogador['ativo']:
            return False
    return True


def sortear_questao(ano, progresso=0, sorteador=None):
    """Cria uma conta adequada ao ano, sem avançar automaticamente de série."""
    if ano not in OPERACOES_POR_ANO:
        raise ValueError("O ano escolar deve estar entre 1 e 5.")
    if progresso < 0:
        raise ValueError("A progressão não pode ser negativa.")

    fonte_sorteio = sorteador
    if fonte_sorteio is None:
        fonte_sorteio = random
    operacao = fonte_sorteio.choice(OPERACOES_POR_ANO[ano])
    aumento = progresso // 3

    # O limite cresce a cada três questões concluídas, até o teto do ano selecionado.
    if ano == 1:
        limite = min(10 + aumento, 20)
    elif ano == 2:
        limite = min(50 + aumento * 2, 100)
    elif ano == 3:
        limite = min(100 + aumento * 10, 1000)
    elif ano == 4:
        limite = min(1000 + aumento * 100, 5000)
    else:
        limite = min(10000 + aumento * 1000, 100000)

    if operacao == "contagem":
        quantidade = fonte_sorteio.randint(1, min(limite, 15))
        return criar_questao(quantidade, 0, operacao, quantidade)

    if operacao == "adicao":
        esquerdo = fonte_sorteio.randint(0, limite)
        direito = fonte_sorteio.randint(0, limite)
        return criar_questao(esquerdo, direito, operacao, esquerdo + direito)

    if operacao == "subtracao":
        esquerdo = fonte_sorteio.randint(0, limite)
        # Restringe o segundo operando para que a diferença seja não negativa.
        direito = fonte_sorteio.randint(0, esquerdo)
        return criar_questao(esquerdo, direito, operacao, esquerdo - direito)

    if operacao == "multiplicacao":
        if ano == 2:
            esquerdo = fonte_sorteio.choice((2, 3, 4, 5))
            direito = fonte_sorteio.randint(1, min(10 + aumento, 20))
        elif ano == 3:
            esquerdo = fonte_sorteio.choice((2, 3, 4, 5, 10))
            direito = fonte_sorteio.randint(2, min(5 + aumento, 12))
        elif ano == 4:
            esquerdo = fonte_sorteio.randint(2, min(9 + aumento, 99))
            direito = fonte_sorteio.randint(2, min(9 + aumento, 12))
        else:
            esquerdo = fonte_sorteio.randint(2, min(20 + aumento, 99))
            direito = fonte_sorteio.randint(2, min(20 + aumento, 99))
        return criar_questao(esquerdo, direito, operacao, esquerdo * direito)

    # Calcula o dividendo a partir do divisor e do quociente para garantir uma divisão exata.
    if ano <= 3:
        divisor = fonte_sorteio.randint(2, min(5 + aumento, 10))
        quociente = fonte_sorteio.randint(2, min(5 + aumento, 12))
    elif ano == 4:
        divisor = fonte_sorteio.randint(2, min(12 + aumento, 20))
        quociente = fonte_sorteio.randint(2, min(20 + aumento, 50))
    else:
        divisor = fonte_sorteio.randint(2, min(20 + aumento, 99))
        quociente = fonte_sorteio.randint(2, min(50 + aumento, 999))
    return criar_questao(divisor * quociente, divisor, operacao, quociente)


def digitar_numero(partida, indice_jogador, digito):
    jogador = partida['jogadores'][indice_jogador]
    if partida['pausada'] or not jogador['ativo'] or not 0 <= digito <= 9:
        return False
    if len(jogador['resposta_digitada']) >= 6:
        return False
    jogador['resposta_digitada'] += str(digito)
    return True


def apagar_numero(partida, indice_jogador):
    jogador = partida['jogadores'][indice_jogador]
    if not partida['pausada'] and jogador['ativo']:
        jogador['resposta_digitada'] = jogador['resposta_digitada'][:-1]


def confirmar_resposta(partida, indice_jogador):
    """Retorna True/False para acerto/erro, ou None se não houve resposta."""
    jogador = partida['jogadores'][indice_jogador]
    if partida['pausada'] or not jogador['ativo'] or not jogador['resposta_digitada']:
        return None

    acertou = int(jogador['resposta_digitada']) == jogador['questao']['resposta']
    resolver_questao(partida, jogador, acertou)
    return acertou


def atualizar_tempo(partida, segundos_passados):
    """Avança apenas os cronômetros ativos; retorna índices que expiraram."""
    if segundos_passados < 0:
        raise ValueError("O intervalo de atualização não pode ser negativo.")
    if partida['pausada']:
        return []

    expirados = []
    # Aplica o tempo excedente às questões seguintes quando um quadro atravessa mais de um prazo.
    for indice, jogador in enumerate(partida['jogadores']):
        if not jogador['ativo']:
            continue

        tempo_a_descontar = segundos_passados
        while jogador['ativo'] and tempo_a_descontar >= jogador['segundos_restantes']:
            tempo_a_descontar -= jogador['segundos_restantes']
            resolver_questao(partida, jogador, acertou=False)
            expirados.append(indice)
        if jogador['ativo']:
            jogador['segundos_restantes'] -= tempo_a_descontar
    return expirados


def resolver_questao(partida, jogador, acertou):
    operacao = jogador['questao']['operacao']
    if acertou:
        jogador['pulos'] += 1
        jogador['acertos_por_operacao'][operacao] += 1
    else:
        # Uma resposta incorreta e um prazo expirado têm a mesma penalidade de uma vida.
        jogador['erros_por_operacao'][operacao] += 1
        jogador['vidas'] -= 1
        if jogador['vidas'] == 0:
            jogador['ativo'] = False
            jogador['segundos_restantes'] = 0.0

    # Toda questão concluída avança a progressão. O cronômetro é renovado apenas para jogadores ativos.
    jogador['resposta_digitada'] = ""
    jogador['progresso'] += 1
    if jogador['ativo']:
        questao_anterior = jogador['questao']
        nova_questao = sortear_questao(
            partida['ano'], progresso=jogador['progresso'], sorteador=partida['sorteador']
        )
        # Impede a repetição imediata da mesma questão para o jogador.
        while nova_questao == questao_anterior:
            nova_questao = sortear_questao(
                partida['ano'], progresso=jogador['progresso'], sorteador=partida['sorteador']
            )
        jogador['questao'] = nova_questao
        jogador['segundos_restantes'] = TEMPO_DA_QUESTAO
