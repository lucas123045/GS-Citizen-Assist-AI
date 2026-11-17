import sys
import unicodedata

from .logica import (
    EXPRESSAO_SIMPLIFICADA,
    canonica_pos,
    forma_nand,
    regra_original,
    simplificada,
    tabela_verdade,
    termos_ativos,
)

DATA_CONSULTA = "16/11/2026"

USO = """Uso:
  python -m citizen_assist                  modo interativo
  python -m citizen_assist --entradas 1011  informa A B C D direto
  python -m citizen_assist --tabela         testa as 16 combinações"""

AVISO = (
    "AVISO: protótipo acadêmico (GS26_2). Não é canal oficial do Inep/MEC e não\n"
    "confirma a concessão da isenção. Quem decide é o Inep, que confere as\n"
    "informações (Censo Escolar, CadÚnico, documentos). Fonte: Edital Inep\n"
    f"nº 21/2026, item 2.3 (consultado em {DATA_CONSULTA})."
)

LIMITACOES = (
    "Limitações: (1) considera só os critérios do item 2.3 do edital do Enem 2026;\n"
    "(2) não verifica prazos. O pedido de isenção do Enem 2026 terminou em\n"
    "30/04/2026 e as regras do próximo ano dependem de um novo edital;\n"
    "(3) não trata a justificativa de ausência de quem foi isento em 2025 e faltou;\n"
    "(4) as respostas são autodeclaradas e o programa não confere nada."
)

PERGUNTAS = (
    ("A", "Você está cursando a última série do ensino médio em escola pública este ano?"),
    ("B", "Você cursou todo o ensino médio em escola pública (ou como bolsista integral\n"
          "    em escola particular)?"),
    ("C", "A renda da sua família dividida pelo número de pessoas é de até 1,5 salário\n"
          "    mínimo por pessoa?"),
    ("D", "Sua família é de baixa renda e está inscrita no CadÚnico (tem NIS válido)?"),
)

DESCRICAO_TERMOS = {
    "A": "está na última série do ensino médio em escola pública (item 2.3.1)",
    "B·C": "fez todo o ensino médio na rede pública ou com bolsa integral e tem renda "
           "per capita de até 1,5 salário mínimo (item 2.3.2)",
    "D": "é de família de baixa renda inscrita no CadÚnico (item 2.3.3)",
}

SIM = {"s", "sim", "1"}
NAO = {"n", "nao", "0"}
MAX_TENTATIVAS = 3


class EntradaInvalida(ValueError):
    pass


def normalizar(texto):
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return sem_acento.strip().lower()


def interpretar_resposta(texto):
    t = normalizar(texto)
    if t in SIM:
        return 1
    if t in NAO:
        return 0
    raise EntradaInvalida(f"Resposta '{texto.strip()}' não reconhecida. Responda S (sim) ou N (não).")


def interpretar_vetor(texto):
    limpo = "".join(ch for ch in texto if ch not in " ,;")
    if len(limpo) != 4 or any(ch not in "01" for ch in limpo):
        raise EntradaInvalida(
            f"Entrada '{texto}' inválida. Digite 4 dígitos 0 ou 1 na ordem A B C D (ex.: 1011)."
        )
    return tuple(int(ch) for ch in limpo)


def decidir(a, b, c, d):
    for x in (a, b, c, d):
        if x not in (0, 1):
            raise EntradaInvalida("As entradas devem ser 0 ou 1.")
    return simplificada(a, b, c, d)


def montar_orientacao(a, b, c, d):
    s = decidir(a, b, c, d)
    linhas = [f"Entradas: A={a} B={b} C={c} D={d}  ->  {EXPRESSAO_SIMPLIFICADA} = {s}", ""]
    if s == 1:
        motivos = "; e também ".join(DESCRICAO_TERMOS[t] for t in termos_ativos(a, b, c, d))
        linhas.append("Resultado (S=1): seu perfil é compatível com a isenção da taxa do Enem.")
        linhas.append(f"Motivo: você {motivos}.")
        linhas.append("")
        linhas.append("O que fazer: pedir a isenção na Página do Participante")
        linhas.append("(enem.inep.gov.br/participante), com login gov.br, dentro do prazo do edital.")
        linhas.append("Mesmo isento, depois é preciso fazer a inscrição no período certo.")
        if d == 1:
            linhas.append("Tenha o NIS em mãos e veja se os dados do CadÚnico batem com os da Receita.")
    else:
        linhas.append("Resultado (S=0): pelas respostas, seu perfil não se enquadra nos critérios")
        linhas.append("de isenção do item 2.3 do edital.")
        linhas.append("")
        linhas.append("O que fazer: fazer a inscrição normalmente e pagar a taxa no prazo do edital.")
        if b == 1 and c == 0:
            linhas.append("Obs.: o critério 2.3.2 exige escola pública e renda de até 1,5 salário mínimo.")
        if b == 0 and c == 1:
            linhas.append("Obs.: renda de até 1,5 SM só dá isenção se todo o ensino médio foi na rede")
            linhas.append("pública ou com bolsa integral. Veja também se sua família está no CadÚnico.")
    if d == 1 and c == 0:
        linhas.append("")
        linhas.append("Atenção: família de baixa renda no CadÚnico tem renda per capita de até 1/2")
        linhas.append("salário mínimo. Confira a resposta da pergunta C. O Inep consulta o CadÚnico.")
    return "\n".join(linhas)


def perguntar(pergunta, entrada=input, saida=print):
    for tentativa in range(1, MAX_TENTATIVAS + 1):
        try:
            return interpretar_resposta(entrada(pergunta + " [S/N]: "))
        except EntradaInvalida as erro:
            restantes = MAX_TENTATIVAS - tentativa
            if restantes:
                saida(f"  {erro} ({restantes} tentativa(s) restante(s))")
            else:
                saida(f"  {erro}")
    raise EntradaInvalida("Limite de tentativas atingido. Atendimento encerrado sem resultado.")


def modo_interativo(entrada=input, saida=print):
    saida("Citizen Assist AI - Isenção da taxa de inscrição do Enem")
    saida("-" * 70)
    saida(AVISO)
    saida("Não precisa informar nome, CPF ou NIS. Responda só S ou N.\n")
    try:
        valores = []
        for letra, texto in PERGUNTAS:
            valores.append(perguntar(f"{letra}) {texto}", entrada, saida))
    except EntradaInvalida as erro:
        saida(f"\n{erro}")
        return 2
    except (EOFError, KeyboardInterrupt):
        saida("\nAtendimento interrompido. Nenhum dado foi guardado.")
        return 1
    saida("")
    saida(montar_orientacao(*valores))
    saida("")
    saida(LIMITACOES)
    return 0


def imprimir_tabela(saida=print):
    saida("Teste das 16 combinações")
    saida(" m | A B C D | Original | POS | A+BC+D | NAND | Programa | Igual")
    saida("---+---------+----------+-----+--------+------+----------+------")
    falhas = 0
    for i, a, b, c, d, s in tabela_verdade():
        r = (regra_original(a, b, c, d), canonica_pos(a, b, c, d), simplificada(a, b, c, d),
             forma_nand(a, b, c, d), decidir(a, b, c, d))
        ok = len(set(r)) == 1
        if not ok:
            falhas += 1
        saida(f"{i:2} | {a} {b} {c} {d} |    {r[0]}     |  {r[1]}  |   {r[2]}    |  {r[3]}   |    {r[4]}     | {'sim' if ok else 'NÃO'}")
    saida(f"\n{16 - falhas} de 16 combinações iguais em todas as formas.")
    return 0 if falhas == 0 else 3


def entrada_com_eco(pergunta):
    resposta = input(pergunta)
    print(resposta)
    return resposta


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        if sys.stdin.isatty():
            return modo_interativo()
        return modo_interativo(entrada=entrada_com_eco)
    if argv[0] == "--tabela":
        return imprimir_tabela()
    if argv[0] == "--entradas" and len(argv) >= 2:
        try:
            valores = interpretar_vetor(" ".join(argv[1:]))
        except EntradaInvalida as erro:
            print(f"Erro: {erro}")
            return 2
        print(AVISO + "\n")
        print(montar_orientacao(*valores))
        print("\n" + LIMITACOES)
        return 0
    print(USO)
    return 2
