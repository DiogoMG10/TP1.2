# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "marimo>=0.24.2",
#     "ortools>=9.15",
# ]
# ///

import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md(r"""
    # Trabalho Prático: Sudoku Genérico como CSP

    ## Contexto

    O Sudoku clássico — uma grelha $n^2 \times n^2$ onde cada linha,
    cada coluna e cada bloco $n \times n$ tem de conter todos os
    valores de $1$ a $n^2$ sem repetições — é um exemplo canónico de
    **problema de satisfação de restrições (CSP)**: a "regra" é sempre
    a mesma (um conjunto de células tem de ter valores todos
    diferentes), o que muda de linha para linha, de coluna para
    coluna e de bloco para bloco é apenas **que células pertencem a
    esse conjunto**.

    Isso sugere uma abstração única — um grupo de células com a
    restrição "todos diferentes", opcionalmente com algumas células já
    fixas a um valor — a partir da qual linhas, colunas, blocos e
    ainda outras variantes de Sudoku (diagonais, regiões irregulares,
    grelhas sobrepostas, etc.) podem ser todas construídas sem
    duplicar lógica de restrição nenhuma.

    Este é um problema de **modelação e resolução de CSP**. Cabe-te a
    ti escolher a técnica de resolução e justificá-la — o enunciado
    não fornece código de modelação nem de apresentação de resultados,
    apenas a interface que o teu notebook tem de expor (secção
    seguinte) para poder ser testado automaticamente.

    ## Objetivo

    Construir, num notebook Marimo, um gerador/resolvedor de Sudoku
    $n^2 \times n^2$ (com $n$ parametrizável, tipicamente $n=3$) que:

    1. representa qualquer **grupo de células com restrição "todos
       diferentes"** através de uma classe genérica (secção
       "`box` — grupo genérico de células"),
    2. constrói **linhas, colunas e blocos** como casos particulares
       dessa classe genérica — os blocos através de uma especialização
       dedicada a blocos $n \times n$, as linhas e colunas através de
       uma especialização dedicada a sequências retas de células
       (secção "`cube` e `path`"),
    3. gera **aleatoriamente** um subconjunto de células já
       preenchidas (as "pistas" iniciais do puzzle), usando a mesma
       abstração genérica (secção "Geração aleatória de pistas"),
    4. monta o modelo completo (linhas + colunas + blocos + pistas) e
       o resolve como CSP, devolvendo a grelha preenchida ou sinalizando
       que não há solução (secção "Resolução").
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Requisitos obrigatórios

    O teu notebook tem de expor, com este comportamento, os seguintes
    elementos (os nomes propostos abaixo são sugestões que facilitam a
    correção automática — podes usar outros, desde que documentes a
    correspondência):

    ### `box` — grupo genérico de células (R1)

    Uma classe que representa **qualquer** conjunto de células da
    grelha às quais se aplica a restrição "todos os valores
    diferentes", com algumas delas possivelmente já fixas:

    - guarda internamente uma associação `(linha, coluna) → valor ou
      None` (`None` = célula livre; um inteiro = célula fixa/pinada a
      esse valor);
    - um construtor que aceita opcionalmente esse conjunto inicial de
      células (vazio por omissão);
    - um método `add(i, j, val=None)` que acrescenta a célula `(i,
      j)` ao grupo, opcionalmente fixando-a a `val`, e que **rejeita**
      (levanta exceção) coordenadas fora da grelha ou valores fora do
      intervalo $[1, n^2]$;
    - uma forma de obter a representação do grupo como matriz $n^2
      \times n^2$, com zeros nas células não pertencentes ao grupo ou
      não fixas, e o valor fixo nas restantes.

    Esta classe **não deve saber nada** sobre linhas, colunas, blocos
    ou Sudoku — só sabe lidar com "um conjunto de células, algumas
    fixas". Essa generalidade é o que te vai permitir, mais tarde,
    tratar da mesma forma linhas, colunas, blocos, pistas aleatórias
    e (nas extensões opcionais) diagonais ou regiões irregulares.

    ### `cube` e `path` — duas formas concretas de grupo (R2, R3)

    A partir da classe genérica, define duas especializações:

    - **R2.** Um grupo que representa o **bloco $n \times n$** cujo
      canto superior esquerdo é a célula $(i \cdot n,\ j \cdot n)$,
      parametrizado pelos índices de bloco $(i, j)$ com $0 \le i, j <
      n$.
    - **R3.** Um grupo que representa o **troço reto** (horizontal ou
      vertical) de células entre duas coordenadas `inicio` e `fim`,
      inclusive — tem de funcionar tanto para `fim` "depois" de
      `inicio` como "antes" (ou seja, percorrer a sequência em
      qualquer sentido).

    ### Geração aleatória de pistas (R4)

    Uma função que devolve um grupo (`box`) com $k$ células escolhidas
    aleatoriamente na grelha, cada uma fixa a um valor também escolhido
    aleatoriamente em $[1, n^2]$ ($k$ deve ter um valor por omissão
    razoável, por exemplo da ordem de $n$). Repara que esta função
    **não precisa de nenhuma classe nova** — o resultado é, de novo,
    apenas um `box`.

    ### Modelo e resolução (R5, R6)

    - **R5.** Um modelo de CSP para a grelha $n^2 \times n^2$, com uma
      variável inteira por célula, cada uma no intervalo $[1, n^2]$;
      um método que recebe **um número arbitrário de grupos**
      (`box`, `cube`, `path`, ou pistas aleatórias — o modelo não deve
      distinguir a sua origem) e, para cada um, impõe que as suas
      células sejam todas diferentes e fixa as que tiverem valor
      atribuído; e um método de resolução que devolve a grelha
      preenchida ou sinaliza, de forma distinguível, que o puzzle não
      tem solução.
    - **R6.** Um Sudoku $n^2 \times n^2$ completo é montado juntando:
      todas as linhas, todas as colunas, todos os blocos $n \times n$
      e (pelo menos) um grupo de pistas aleatórias — e resolvido.
    """)
    return


@app.class_definition
# ============================================================
# Contribuição LLM:
# Implementação da classe genérica `box`, desenvolvida a partir
# da formalização e das decisões discutidas no diálogo LLM
# associado ao relatório do TP1.2.
# ============================================================

class box:
    """
    Grupo genérico de células de uma grelha n^2 x n^2.

    Cada coordenada pertencente ao grupo está associada a:
      - None, se a célula estiver livre;
      - um inteiro entre 1 e n^2, se estiver fixada.
    """

    def __init__(self, n, cells=None):
        if not isinstance(n, int) or n <= 0:
            raise ValueError("n deve ser um inteiro positivo.")

        self.n = n
        self.size = n ** 2
        self._cells = {}

        if cells is not None:
            for (i, j), val in cells.items():
                self.add(i, j, val)

    def add(self, i, j, val=None):
        """
        Acrescenta uma célula ao grupo, opcionalmente com valor fixo.
        """

        if not isinstance(i, int) or not isinstance(j, int):
            raise ValueError("As coordenadas devem ser inteiros.")

        if not (0 <= i < self.size and 0 <= j < self.size):
            raise ValueError("Coordenada fora da grelha.")

        if (i, j) in self._cells:
            raise ValueError("A célula já pertence ao grupo.")

        if val is not None:
            if not isinstance(val, int) or not (1 <= val <= self.size):
                raise ValueError(
                    f"O valor deve pertencer ao intervalo [1, {self.size}]."
                )

        self._cells[(i, j)] = val

    @property
    def cells(self):
        """
        Devolve uma cópia da associação interna de células.
        """
        return dict(self._cells)

    def to_matrix(self):
        """
        Representa o grupo como uma matriz n^2 x n^2.

        Células não pertencentes ao grupo e células livres
        são representadas por 0.
        """

        matrix = [
            [0 for _ in range(self.size)]
            for _ in range(self.size)
        ]

        for (i, j), val in self._cells.items():
            if val is not None:
                matrix[i][j] = val

        return matrix


@app.cell
def _():
    # ============================================================
    # Contribuição LLM:
    # Testes automáticos básicos do requisito R1 (`box`).
    # ============================================================

    # 1. Criação vazia
    b = box(2)
    assert b.cells == {}

    # 2. Construtor com células iniciais
    b_inicial = box(2, {
        (0, 0): None,
        (1, 2): 3
    })

    assert b_inicial.cells[(0, 0)] is None
    assert b_inicial.cells[(1, 2)] == 3

    # 3. Célula livre
    b.add(0, 1)
    assert b.cells[(0, 1)] is None

    # 4. Célula fixa
    b.add(2, 3, 4)
    assert b.cells[(2, 3)] == 4

    # 5. Representação matricial
    m = b_inicial.to_matrix()

    assert len(m) == 4
    assert all(len(row) == 4 for row in m)

    assert m[0][0] == 0      # célula livre
    assert m[1][2] == 3      # célula fixa
    assert m[3][3] == 0      # célula fora do grupo


    # Função auxiliar apenas para os testes de exceção
    def deve_lancar_value_error(func):
        try:
            func()
            assert False, "Era esperado ValueError."
        except ValueError:
            pass


    # 6. Coordenadas inválidas
    deve_lancar_value_error(lambda: b.add(-1, 0))
    deve_lancar_value_error(lambda: b.add(4, 0))
    deve_lancar_value_error(lambda: b.add(0, 4))

    # 7. Valor inválido
    deve_lancar_value_error(lambda: b.add(1, 1, 0))
    deve_lancar_value_error(lambda: b.add(1, 1, 5))

    # 8. Coordenada duplicada
    deve_lancar_value_error(lambda: b.add(0, 1))

    print("R1: testes concluídos com sucesso")
    return (deve_lancar_value_error,)


@app.cell
def _():
    # ============================================================
    # Contribuição LLM:
    # Implementação das especializações `cube` e `path`
    # correspondentes aos requisitos R2 e R3, desenvolvida a partir
    # da formalização discutida no diálogo LLM do TP1.2.
    # ============================================================

    class cube(box):
        """
        Bloco n x n de uma grelha n^2 x n^2.

        (i, j) são os índices do bloco, com 0 <= i, j < n.
        """

        def __init__(self, n, i, j):
            super().__init__(n)

            if not isinstance(i, int) or not isinstance(j, int):
                raise ValueError("Os índices do bloco devem ser inteiros.")

            if not (0 <= i < n and 0 <= j < n):
                raise ValueError("Índice de bloco fora da grelha.")

            for r in range(n):
                for c in range(n):
                    self.add(i * n + r, j * n + c)


    class path(box):
        """
        Troço horizontal ou vertical, inclusive, entre duas coordenadas.
        """

        def __init__(self, n, inicio, fim):
            super().__init__(n)

            r1, c1 = inicio
            r2, c2 = fim

            if r1 == r2:
                # Percurso horizontal
                passo = 1 if c2 >= c1 else -1

                for c in range(c1, c2 + passo, passo):
                    self.add(r1, c)

            elif c1 == c2:
                # Percurso vertical
                passo = 1 if r2 >= r1 else -1

                for r in range(r1, r2 + passo, passo):
                    self.add(r, c1)

            else:
                raise ValueError(
                    "Um path tem de ser horizontal ou vertical."
                )

    return cube, path


@app.cell
def _(cube, deve_lancar_value_error, path):
    # ============================================================
    # Contribuição LLM:
    # Testes automáticos dos requisitos R2 (`cube`) e R3 (`path`).
    # Reutiliza `deve_lancar_value_error`, definida nos testes de R1.
    # ============================================================


    # ------------------------------------------------------------
    # R2 - cube
    # ------------------------------------------------------------

    # Bloco superior direito numa grelha 4 x 4
    c1 = cube(2, 0, 1)

    assert isinstance(c1, box)

    assert set(c1.cells.keys()) == {
        (0, 2), (0, 3),
        (1, 2), (1, 3)
    }

    assert all(val is None for val in c1.cells.values())
    assert len(c1.cells) == 4


    # Outro bloco: inferior direito
    c2 = cube(2, 1, 1)

    assert set(c2.cells.keys()) == {
        (2, 2), (2, 3),
        (3, 2), (3, 3)
    }


    # Índices de bloco inválidos
    deve_lancar_value_error(lambda: cube(2, -1, 0))
    deve_lancar_value_error(lambda: cube(2, 2, 0))
    deve_lancar_value_error(lambda: cube(2, 0, 2))


    # ------------------------------------------------------------
    # R3 - path
    # ------------------------------------------------------------

    # Horizontal crescente
    p1 = path(2, (1, 0), (1, 3))

    assert isinstance(p1, box)

    assert set(p1.cells.keys()) == {
        (1, 0),
        (1, 1),
        (1, 2),
        (1, 3)
    }


    # Horizontal decrescente
    p2 = path(2, (1, 3), (1, 0))

    assert set(p2.cells.keys()) == {
        (1, 0),
        (1, 1),
        (1, 2),
        (1, 3)
    }


    # Vertical crescente
    p3 = path(2, (0, 2), (3, 2))

    assert set(p3.cells.keys()) == {
        (0, 2),
        (1, 2),
        (2, 2),
        (3, 2)
    }


    # Vertical decrescente
    p4 = path(2, (3, 2), (0, 2))

    assert set(p4.cells.keys()) == {
        (0, 2),
        (1, 2),
        (2, 2),
        (3, 2)
    }


    # inicio == fim
    p5 = path(2, (2, 2), (2, 2))

    assert set(p5.cells.keys()) == {
        (2, 2)
    }


    # Percurso que não é horizontal nem vertical
    deve_lancar_value_error(
        lambda: path(2, (0, 0), (2, 2))
    )


    # Coordenadas fora da grelha
    deve_lancar_value_error(
        lambda: path(2, (0, 0), (0, 4))
    )

    deve_lancar_value_error(
        lambda: path(2, (-1, 1), (2, 1))
    )


    print("R2 e R3: testes concluídos com sucesso")
    return


@app.cell
def _():
    # ============================================================
    # Contribuição LLM:
    # Implementação da geração aleatória de pistas correspondente
    # ao requisito R4, segundo a formalização e decisões discutidas
    # no diálogo LLM do TP1.2.
    # ============================================================

    import random


    def gerar_pistas(n, k=None, seed=None):
        """
        Gera um box com k células distintas escolhidas aleatoriamente.

        Cada célula recebe um valor aleatório entre 1 e n^2.
        Se k não for indicado, é usado k = n.
        """

        pistas = box(n)

        if k is None:
            k = n

        total_celulas = pistas.size ** 2

        if not isinstance(k, int) or k < 0 or k > total_celulas:
            raise ValueError(
                f"k deve ser um inteiro entre 0 e {total_celulas}."
            )

        rng = random.Random(seed)

        coordenadas = [
            (i, j)
            for i in range(pistas.size)
            for j in range(pistas.size)
        ]

        escolhidas = rng.sample(coordenadas, k)

        for i, j in escolhidas:
            val = rng.randint(1, pistas.size)
            pistas.add(i, j, val)

        return pistas

    return (gerar_pistas,)


@app.cell
def _(deve_lancar_value_error, gerar_pistas):
    # ============================================================
    # Contribuição LLM:
    # Testes automáticos do requisito R4 - geração aleatória
    # e reproduzível de pistas.
    # ============================================================

    # ------------------------------------------------------------
    # Resultado e número de pistas
    # ------------------------------------------------------------

    p1 = gerar_pistas(2, k=5, seed=123)

    assert isinstance(p1, box)
    assert len(p1.cells) == 5


    # ------------------------------------------------------------
    # Coordenadas e valores válidos
    # ------------------------------------------------------------

    for (i, j), val in p1.cells.items():
        assert 0 <= i < 4
        assert 0 <= j < 4
        assert 1 <= val <= 4


    # As coordenadas são distintas
    assert len(set(p1.cells.keys())) == 5


    # ------------------------------------------------------------
    # Reprodutibilidade com a mesma semente
    # ------------------------------------------------------------

    p2 = gerar_pistas(2, k=5, seed=123)

    assert p1.cells == p2.cells


    # ------------------------------------------------------------
    # Valor por omissão: k = n
    # ------------------------------------------------------------

    p_default = gerar_pistas(3, seed=123)

    assert len(p_default.cells) == 3


    # ------------------------------------------------------------
    # Valores inválidos de k
    # ------------------------------------------------------------

    deve_lancar_value_error(
        lambda: gerar_pistas(2, k=-1, seed=123)
    )

    deve_lancar_value_error(
        lambda: gerar_pistas(2, k=17, seed=123)
    )


    print("R4: testes concluídos com sucesso")
    return


@app.cell
def _():
    # ============================================================
    # Contribuição LLM:
    # Implementação do modelo CSP correspondente ao requisito R5,
    # usando OR-Tools CP-SAT, a partir da formalização discutida
    # no diálogo LLM do TP1.2.
    # ============================================================

    from ortools.sat.python import cp_model


    class sudoku_csp:
        """
        Modelo CSP para uma grelha n^2 x n^2.
        """

        def __init__(self, n):
            self.n = n
            self.size = n ** 2

            self.model = cp_model.CpModel()

            # Uma variável inteira por célula, com domínio [1, n^2].
            self.x = [
                [
                    self.model.NewIntVar(
                        1,
                        self.size,
                        f"x_{i}_{j}"
                    )
                    for j in range(self.size)
                ]
                for i in range(self.size)
            ]

        def add_groups(self, *groups):
            """
            Acrescenta ao modelo um número arbitrário de grupos.

            Para cada grupo:
              - impõe AllDifferent às células pertencentes ao grupo;
              - transforma cada valor fixo numa igualdade.
            """

            for group in groups:
                if group.n != self.n:
                    raise ValueError(
                        "O grupo e o modelo devem usar o mesmo valor de n."
                    )

                variables = [
                    self.x[i][j]
                    for (i, j) in group.cells.keys()
                ]

                if len(variables) > 1:
                    self.model.AddAllDifferent(variables)

                for (i, j), val in group.cells.items():
                    if val is not None:
                        self.model.Add(
                            self.x[i][j] == val
                        )

        def solve(self):
            """
            Resolve o CSP.

            Devolve:
              - uma matriz n^2 x n^2 se existir uma solução;
              - None se o modelo for INFEASIBLE.

            Outros estados do solver não são confundidos com inviabilidade.
            """

            solver = cp_model.CpSolver()
            status = solver.Solve(self.model)

            if status in (
                cp_model.FEASIBLE,
                cp_model.OPTIMAL
            ):
                return [
                    [
                        solver.Value(self.x[i][j])
                        for j in range(self.size)
                    ]
                    for i in range(self.size)
                ]

            if status == cp_model.INFEASIBLE:
                return None

            raise RuntimeError(
                "O solver terminou sem determinar satisfatibilidade."
            )

    return (sudoku_csp,)


@app.cell
def _(cube, deve_lancar_value_error, path, sudoku_csp):
    # ============================================================
    # Contribuição LLM:
    # Testes automáticos do requisito R5:
    # solução matricial, AllDifferent, valores fixos,
    # grupos arbitrários, incompatibilidade de n e inviabilidade.
    # ============================================================


    # ------------------------------------------------------------
    # 1. Caso satisfazível
    # ------------------------------------------------------------

    csp = sudoku_csp(2)

    # Três grupos de origens diferentes:
    # path, cube e box de pistas.
    linha = path(2, (0, 0), (0, 3))
    bloco = cube(2, 0, 0)

    pistas = box(2, {
        (0, 0): 1,
        (1, 0): 2
    })

    # O modelo recebe todos da mesma forma.
    csp.add_groups(linha, bloco, pistas)

    solucao = csp.solve()


    # Deve existir uma solução.
    assert solucao is not None


    # A solução devolvida deve ser uma matriz 4 x 4.
    assert isinstance(solucao, list)
    assert len(solucao) == 4
    assert all(isinstance(row, list) for row in solucao)
    assert all(len(row) == 4 for row in solucao)


    # ------------------------------------------------------------
    # 2. AllDifferent
    # ------------------------------------------------------------

    # A primeira linha pertence ao grupo `linha`, que contém
    # exatamente quatro variáveis com domínio {1, 2, 3, 4}.
    assert set(solucao[0]) == {1, 2, 3, 4}


    # O bloco superior esquerdo também recebeu AllDifferent.
    valores_bloco = [
        solucao[0][0],
        solucao[0][1],
        solucao[1][0],
        solucao[1][1]
    ]

    assert len(set(valores_bloco)) == 4


    # ------------------------------------------------------------
    # 3. Valores fixos preservados
    # ------------------------------------------------------------

    assert solucao[0][0] == 1
    assert solucao[1][0] == 2


    # ------------------------------------------------------------
    # 4. Grupo com n incompatível
    # ------------------------------------------------------------

    grupo_incompativel = box(3)

    deve_lancar_value_error(
        lambda: csp.add_groups(grupo_incompativel)
    )


    # ------------------------------------------------------------
    # 5. CSP deliberadamente contraditório
    # ------------------------------------------------------------

    csp_inviavel = sudoku_csp(2)

    linha_inviavel = path(
        2,
        (0, 0),
        (0, 3)
    )

    # AllDifferent exige que estas duas células tenham valores
    # distintos, mas as pistas fixam ambas ao valor 1.
    pistas_incompativeis = box(2, {
        (0, 0): 1,
        (0, 1): 1
    })

    csp_inviavel.add_groups(
        linha_inviavel,
        pistas_incompativeis
    )

    resultado_inviavel = csp_inviavel.solve()

    # solve() só devolve None quando o estado é INFEASIBLE.
    # Qualquer outro estado originaria RuntimeError.
    assert resultado_inviavel is None


    print("R5: testes concluídos com sucesso")
    return


@app.cell
def _(cube, gerar_pistas, path, sudoku_csp):
    # ============================================================
    # Contribuição LLM:
    # Implementação de R6 - construção de um Sudoku completo
    # n^2 x n^2 através de path, cube, pistas e do modelo genérico
    # sudoku_csp desenvolvido em R5.
    # ============================================================

    def resolver_sudoku(n, k=None, seed=None):
        """
        Constrói e resolve um Sudoku n^2 x n^2.

        O modelo contém:
          - todas as linhas;
          - todas as colunas;
          - todos os blocos n x n;
          - um grupo de pistas aleatórias.

        Devolve:
          - a solução, ou None se o CSP for INFEASIBLE;
          - o box de pistas usado na construção.
        """

        size = n ** 2

        # Todas as linhas
        linhas = [
            path(n, (i, 0), (i, size - 1))
            for i in range(size)
        ]

        # Todas as colunas
        colunas = [
            path(n, (0, j), (size - 1, j))
            for j in range(size)
        ]

        # Todos os blocos n x n
        blocos = [
            cube(n, i, j)
            for i in range(n)
            for j in range(n)
        ]

        # Grupo de pistas aleatórias
        pistas = gerar_pistas(
            n,
            k=k,
            seed=seed
        )

        # Modelo CSP genérico de R5
        modelo = sudoku_csp(n)

        modelo.add_groups(
            *(linhas + colunas + blocos + [pistas])
        )

        solucao = modelo.solve()

        return solucao, pistas

    return (resolver_sudoku,)


@app.function
# ============================================================
# Contribuição LLM:
# Validador independente da solução de R6.
# Verifica diretamente dimensão, linhas, colunas, blocos
# e preservação das pistas, sem consultar o solver.
# ============================================================

def validar_sudoku(solucao, n, pistas):
    """
    Verifica independentemente uma solução de Sudoku.

    Devolve True apenas se:
      - a matriz tiver dimensão n^2 x n^2;
      - todas as linhas contiverem exatamente 1..n^2;
      - todas as colunas contiverem exatamente 1..n^2;
      - todos os blocos n x n contiverem exatamente 1..n^2;
      - todas as pistas forem preservadas.
    """

    if solucao is None:
        return False

    size = n ** 2
    valores_esperados = set(range(1, size + 1))

    # --------------------------------------------------------
    # Dimensão n^2 x n^2
    # --------------------------------------------------------

    if len(solucao) != size:
        return False

    if any(len(linha) != size for linha in solucao):
        return False

    # --------------------------------------------------------
    # Linhas
    # --------------------------------------------------------

    for i in range(size):
        if set(solucao[i]) != valores_esperados:
            return False

    # --------------------------------------------------------
    # Colunas
    # --------------------------------------------------------

    for j in range(size):
        coluna = {
            solucao[i][j]
            for i in range(size)
        }

        if coluna != valores_esperados:
            return False

    # --------------------------------------------------------
    # Blocos n x n
    # --------------------------------------------------------

    for bloco_i in range(n):
        for bloco_j in range(n):

            valores_bloco = []

            for di in range(n):
                for dj in range(n):
                    i = bloco_i * n + di
                    j = bloco_j * n + dj

                    valores_bloco.append(
                        solucao[i][j]
                    )

            if set(valores_bloco) != valores_esperados:
                return False

    # --------------------------------------------------------
    # Preservação das pistas
    # --------------------------------------------------------

    for (i, j), val in pistas.cells.items():
        if val is not None:
            if solucao[i][j] != val:
                return False

    return True


@app.cell
def _(resolver_sudoku):
    # ============================================================
    # Execução controlada de R6 para n = 2.
    # Grelha: 4 x 4
    # ============================================================

    solucao_2, pistas_2 = resolver_sudoku(
        n=2,
        k=2,
        seed=123
    )

    print("Pistas n=2:", pistas_2.cells)

    if solucao_2 is None:
        print("n=2: INFEASIBLE")

    else:
        print("Solução n=2:")

        for linha_solucao_2 in solucao_2:
            print(linha_solucao_2)

        assert validar_sudoku(
            solucao_2,
            2,
            pistas_2
        )

        print(
            "n=2: validação independente concluída com sucesso"
        )
    return


@app.cell
def _(resolver_sudoku):
    # ============================================================
    # Execução controlada de R6 para n = 3.
    # Grelha: 9 x 9
    # ============================================================

    solucao_3, pistas_3 = resolver_sudoku(
        n=3,
        k=3,
        seed=123
    )

    print("Pistas n=3:", pistas_3.cells)

    if solucao_3 is None:
        print("n=3: INFEASIBLE")

    else:
        print("Solução n=3:")

        for linha_solucao_3 in solucao_3:
            print(linha_solucao_3)

        assert validar_sudoku(
            solucao_3,
            3,
            pistas_3
        )

        print(
            "n=3: validação independente concluída com sucesso"
        )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Como testar/validar

    O teu notebook (ou um ficheiro de testes à parte) tem de verificar
    automaticamente, para uma grelha resolvida:

    - que cada linha, cada coluna e cada bloco $n \times n$ contém
      exatamente os valores $1 \ldots n^2$, sem repetições;
    - que as células fixadas pelas pistas aleatórias mantêm, na
      solução, o valor com que foram fixadas;
    - que `add` (ou equivalente) rejeita coordenadas fora da grelha e
      valores fora de $[1, n^2]$.

    Corre o fluxo completo (gerar pistas aleatórias → montar linhas +
    colunas + blocos + pistas → resolver → validar) pelo menos uma vez
    com $n=3$ (Sudoku clássico $9\times9$) e confirma que também
    funciona com outro valor de $n$ (ex.: $n=2$, grelha $4\times4$),
    para garantires que nada está fixo a $9\times9$ no teu código.

    ## O que é deixado ao teu critério

    O enunciado define **que abstrações** o notebook tem de expor e
    **que comportamento** têm de ter, não **como** as deves
    implementar. Ficam ao teu critério, desde que justificadas no
    notebook:

    - a técnica e biblioteca de resolução do CSP (CP-SAT do OR-Tools
      é a sugestão da disciplina, mas és livre de escolher outra
      abordagem de Lógica Computacional, justificando a escolha);
    - a estrutura de dados interna do grupo genérico (dicionário,
      matriz esparsa, etc.);
    - a forma de apresentar a grelha resultante (texto, tabela,
      `mo.ui`, gráfico — o que achares mais claro);
    - o comportamento exato quando o puzzle gerado aleatoriamente não
      tem solução (podes, por exemplo, tentar novas pistas aleatórias
      até obteres um puzzle solúvel, ou simplesmente reportar o
      insucesso — justifica a escolha).



    ## Extensões opcionais (bónus)

    A generalidade do `box` é o que torna estas extensões possíveis
    sem tocar no modelo CSP em si — cada uma acrescenta apenas **novos
    grupos** de células:

    - **Sudoku diagonal (X-Sudoku)**: acrescenta um grupo (`box`, sem
      precisar de nova subclasse) para cada uma das duas diagonais
      principais, também elas restritas a "todos diferentes".
    - **Sudoku irregular (jigsaw)**: substitui os blocos $n \times n$
      regulares por regiões de forma arbitrária mas do mesmo tamanho,
      cada uma representada como um `box` construído célula a célula
      em vez de por `cube`.
    - **Hyper-Sudoku / Windoku**: acrescenta 4 blocos extra (também
      `box`, de forma semelhante a `cube` mas sem estarem alinhados
      com a grelha $n \times n$ de blocos) sobrepostos aos existentes.
    - **Escala**: mostra que o teu código funciona (talvez mais devagar)
      para $n=6$ (grelha $36\times36$) sem alterações, e discute os
      limites de desempenho que encontraste.
    - **Sudoku tridimensional** define a estrutura de "boxes" numa grelha $n^2\times n^2\times n^2$.
    """)
    return


if __name__ == "__main__":
    app.run()
