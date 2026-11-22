# Matemática em Movimento

Trabalho final da disciplina **Jogos Eletrônicos e Gamificação na Educação**, do curso de Licenciatura em Computação da Universidade Federal do Paraná (UFPR), Setor Palotina.

Matemática em Movimento é um jogo educativo desenvolvido em Python com Pygame. Estudantes do 1º ao 5º ano do Ensino Fundamental praticam contagem e operações matemáticas em partidas individuais ou em dupla no mesmo computador.

## Como instalar e executar

1. Instale o Python 3.11 pelo [site oficial do Python](https://www.python.org/downloads/). No Windows, marque **Add Python to PATH** se essa opção aparecer no instalador.
2. Baixe o projeto pelo botão **Code → Download ZIP** do GitHub e extraia o arquivo. Se você já usa Git, também pode clonar o repositório:

   ```sh
   git clone https://github.com/JVGomes6/Game_Mat_em_Mov.git
   cd Game_Mat_em_Mov
   ```

3. Abra um terminal na pasta que contém `main.py` e `requirements.txt`.
4. Execute os comandos do seu sistema. Eles criam um ambiente virtual, instalam o Pygame e abrem o jogo.

   **Windows (PowerShell)**

   ```powershell
   py -3.11 -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   .\.venv\Scripts\python.exe main.py
   ```

   **macOS ou Linux**

   ```sh
   python3.11 -m venv .venv
   ./.venv/bin/python -m pip install -r requirements.txt
   ./.venv/bin/python main.py
   ```

Para jogar novamente, abra o terminal na mesma pasta e repita apenas o último comando. Mantenha as pastas `telas/` e `audio/` ao lado de `main.py`, pois o jogo carrega as imagens e os sons delas.

Se o terminal não reconhecer `py -3.11` ou `python3.11`, confira a instalação do Python. No Windows, se `python --version` mostrar Python 3.11, também é possível criar o ambiente com `python -m venv .venv`.

## Como jogar

1. Na tela inicial, clique em **Jogar**, escolha o modo individual ou em dupla e selecione o ano escolar.
2. Digite a resposta usando o teclado físico ou clique nos números da calculadora na tela. No modo em dupla, o jogador 1 usa os números da fileira superior e **Enter**. O jogador 2 usa o teclado numérico e seu **Enter**.
3. Cada jogador tem três vidas e 30 segundos por questão. Uma resposta correta vale um pulo. Uma resposta errada ou o tempo esgotado custa uma vida.
4. Use o botão de pausa ou pressione **Esc**, **P** ou **Espaço** para pausar ou retomar. No menu de pausa, também é possível recomeçar ou voltar ao início.
5. A partida termina quando todos os participantes ficam sem vidas. A tela de resultados mostra os pulos, acertos e erros por operação.

O botão **i** da tela inicial abre o guia de informações.

## Documentação do trabalho

- [Game Design Document (GDD)](GDD_Mat_em_Mov_e.pdf)
- [Ficha de Ideias](Ficha_ideias_Concluida_e.pdf)
- [Slides da apresentação](Matematica-em-Movimento.pptx.pdf)
