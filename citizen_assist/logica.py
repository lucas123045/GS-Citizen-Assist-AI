from itertools import product

VARIAVEIS = ("A", "B", "C", "D")

MINTERMOS = (1, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)
MAXTERMOS = (0, 2, 4)

EXPRESSAO_CANONICA_SOP = "S = Σm(1,3,5,6,7,8,9,10,11,12,13,14,15)"
EXPRESSAO_CANONICA_POS = "S = ΠM(0,2,4) = (A+B+C+D)(A+B+C'+D)(A+B'+C+D)"
EXPRESSAO_SIMPLIFICADA = "S = A + B·C + D"
EXPRESSAO_NAND = "S = (A' · (B·C)' · D')'"


def regra_original(a, b, c, d):
    criterio_1 = a == 1
    criterio_2 = b == 1 and c == 1
    criterio_3 = d == 1
    if criterio_1 or criterio_2 or criterio_3:
        return 1
    return 0


def literal(x, bit):
    return x if bit else 1 - x


def canonica_sop(a, b, c, d):
    for m in MINTERMOS:
        termo = (literal(a, m >> 3 & 1) & literal(b, m >> 2 & 1)
                 & literal(c, m >> 1 & 1) & literal(d, m & 1))
        if termo:
            return 1
    return 0


def canonica_pos(a, b, c, d):
    nb = 1 - b
    nc = 1 - c
    m0 = a | b | c | d
    m2 = a | b | nc | d
    m4 = a | nb | c | d
    return m0 & m2 & m4


def simplificada(a, b, c, d):
    return a | (b & c) | d


def nand(*entradas):
    r = 1
    for x in entradas:
        r &= x
    return 1 - r


def forma_nand(a, b, c, d):
    return nand(nand(a, a), nand(b, c), nand(d, d))


def termos_ativos(a, b, c, d):
    ativos = []
    if a:
        ativos.append("A")
    if b and c:
        ativos.append("B·C")
    if d:
        ativos.append("D")
    return ativos


def tabela_verdade():
    for i, (a, b, c, d) in enumerate(product((0, 1), repeat=4)):
        yield i, a, b, c, d, regra_original(a, b, c, d)
