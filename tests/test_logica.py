import unittest
from itertools import product

from citizen_assist.assistente import (
    EntradaInvalida,
    decidir,
    interpretar_resposta,
    interpretar_vetor,
    modo_interativo,
    montar_orientacao,
)
from citizen_assist.logica import (
    MAXTERMOS,
    MINTERMOS,
    canonica_pos,
    canonica_sop,
    forma_nand,
    regra_original,
    simplificada,
)

ESPERADO = {
    0: 0, 1: 1, 2: 0, 3: 1, 4: 0, 5: 1, 6: 1, 7: 1,
    8: 1, 9: 1, 10: 1, 11: 1, 12: 1, 13: 1, 14: 1, 15: 1,
}


class TestEquivalencia(unittest.TestCase):
    def test_todas_as_16_combinacoes(self):
        for a, b, c, d in product((0, 1), repeat=4):
            m = 8 * a + 4 * b + 2 * c + d
            with self.subTest(m=m):
                esperado = ESPERADO[m]
                self.assertEqual(regra_original(a, b, c, d), esperado)
                self.assertEqual(canonica_sop(a, b, c, d), esperado)
                self.assertEqual(canonica_pos(a, b, c, d), esperado)
                self.assertEqual(simplificada(a, b, c, d), esperado)
                self.assertEqual(forma_nand(a, b, c, d), esperado)
                self.assertEqual(decidir(a, b, c, d), esperado)

    def test_mintermos_e_maxtermos(self):
        self.assertEqual(set(MINTERMOS) | set(MAXTERMOS), set(range(16)))
        self.assertFalse(set(MINTERMOS) & set(MAXTERMOS))
        self.assertEqual(set(MINTERMOS), {m for m, s in ESPERADO.items() if s == 1})


class TestEntradas(unittest.TestCase):
    def test_respostas_validas(self):
        for texto in ("s", "S", "sim", "SIM ", "1"):
            self.assertEqual(interpretar_resposta(texto), 1)
        for texto in ("n", "N", "não", "nao", "NÃO", "0"):
            self.assertEqual(interpretar_resposta(texto), 0)

    def test_respostas_invalidas(self):
        for texto in ("", "talvez", "2", "sim não", "-1", "x"):
            with self.assertRaises(EntradaInvalida):
                interpretar_resposta(texto)

    def test_vetor(self):
        self.assertEqual(interpretar_vetor("1011"), (1, 0, 1, 1))
        self.assertEqual(interpretar_vetor("1, 0, 1, 1"), (1, 0, 1, 1))
        for texto in ("101", "10110", "1021", "abcd", ""):
            with self.assertRaises(EntradaInvalida):
                interpretar_vetor(texto)

    def test_decidir_fora_de_0_1(self):
        with self.assertRaises(EntradaInvalida):
            decidir(2, 0, 0, 0)


class TestInterface(unittest.TestCase):
    def rodar(self, respostas):
        fila = list(respostas)
        saida = []
        codigo = modo_interativo(entrada=lambda _: fila.pop(0), saida=saida.append)
        return codigo, "\n".join(saida)

    def test_fluxo_isento(self):
        codigo, texto = self.rodar(["n", "s", "s", "n"])
        self.assertEqual(codigo, 0)
        self.assertIn("S=1", texto)
        self.assertIn("2.3.2", texto)

    def test_fluxo_nao_isento(self):
        codigo, texto = self.rodar(["n", "s", "n", "n"])
        self.assertEqual(codigo, 0)
        self.assertIn("S=0", texto)

    def test_resposta_invalida_repete(self):
        codigo, texto = self.rodar(["talvez", "n", "n", "n", "n"])
        self.assertEqual(codigo, 0)
        self.assertIn("não reconhecida", texto)

    def test_tres_erros_encerra(self):
        codigo, texto = self.rodar(["x", "y?", "z"])
        self.assertEqual(codigo, 2)
        self.assertIn("Limite de tentativas", texto)

    def test_aviso_inconsistencia(self):
        self.assertIn("Confira a resposta da pergunta C", montar_orientacao(0, 0, 0, 1))

    def test_aviso_canal_nao_oficial(self):
        _, texto = self.rodar(["n", "n", "n", "n"])
        self.assertIn("Não é canal oficial", texto)


if __name__ == "__main__":
    unittest.main()
