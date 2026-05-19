"""Certificazione automatica del motore di gioco della Scopa.

Esegui con:  python3 test_scopa.py
Usa solo libreria standard (unittest).
"""

import unittest

from scopa_game import (Carta, Mazzo, GiocoScopa, trova_catture,
                        _simula_partita, SEMI, VALORI)


class TestMazzo(unittest.TestCase):

    def test_mazzo_40_carte_uniche(self):
        m = Mazzo()
        self.assertEqual(len(m), 40)
        self.assertEqual(len(set(m.carte)), 40)
        for s in SEMI:
            for v in VALORI:
                self.assertIn(Carta(v, s), m.carte)

    def test_pesca_riduce_il_mazzo(self):
        m = Mazzo()
        pescate = m.pesca(7)
        self.assertEqual(len(pescate), 7)
        self.assertEqual(len(m), 33)

    def test_pesca_eccessiva_solleva_errore(self):
        m = Mazzo()
        self.assertRaises(ValueError, m.pesca, 41)


class TestCarta(unittest.TestCase):

    def test_carta_non_valida(self):
        self.assertRaises(ValueError, Carta, 11, 'Denari')
        self.assertRaises(ValueError, Carta, 5, 'Picche')

    def test_settebello(self):
        self.assertTrue(Carta(7, 'Denari').e_settebello)
        self.assertFalse(Carta(7, 'Spade').e_settebello)

    def test_uguaglianza_e_hash(self):
        self.assertEqual(Carta(3, 'Coppe'), Carta(3, 'Coppe'))
        self.assertNotEqual(Carta(3, 'Coppe'), Carta(3, 'Spade'))
        self.assertEqual(len({Carta(1, 'Oro' if False else 'Spade'),
                              Carta(1, 'Spade')}), 1)


class TestCatture(unittest.TestCase):

    def test_priorita_presa_diretta(self):
        # con un 6 singolo a terra, giocando un 6 non vale la coppia 3+3
        tavolo = [Carta(6, 'Coppe'), Carta(3, 'Spade'), Carta(3, 'Bastoni')]
        opzioni = trova_catture(Carta(6, 'Denari'), tavolo)
        self.assertEqual(opzioni, [(Carta(6, 'Coppe'),)])

    def test_cattura_a_somma(self):
        tavolo = [Carta(2, 'Coppe'), Carta(4, 'Spade'), Carta(5, 'Bastoni')]
        opzioni = trova_catture(Carta(6, 'Denari'), tavolo)
        self.assertEqual(len(opzioni), 1)
        self.assertEqual(set(opzioni[0]),
                         {Carta(2, 'Coppe'), Carta(4, 'Spade')})

    def test_nessuna_cattura(self):
        tavolo = [Carta(8, 'Coppe'), Carta(9, 'Spade')]
        self.assertEqual(trova_catture(Carta(3, 'Denari'), tavolo), [])

    def test_doppia_presa_diretta(self):
        tavolo = [Carta(4, 'Coppe'), Carta(4, 'Spade')]
        opzioni = trova_catture(Carta(4, 'Denari'), tavolo)
        self.assertEqual(len(opzioni), 2)


class TestGioco(unittest.TestCase):

    def test_distribuzione_iniziale(self):
        g = GiocoScopa(seed=1)
        self.assertEqual(len(g.tavolo), 4)
        self.assertEqual(len(g.giocatori[0].mano), 3)
        self.assertEqual(len(g.giocatori[1].mano), 3)
        self.assertEqual(len(g.mazzo), 30)

    def test_scopa(self):
        g = GiocoScopa(seed=1)
        g.tavolo = [Carta(4, 'Coppe')]
        g.giocatori[0].mano = [Carta(4, 'Spade')]
        g.turno = 0
        info = g.gioca(Carta(4, 'Spade'))
        self.assertTrue(info['scopa'])
        self.assertEqual(g.giocatori[0].scope, 1)
        self.assertEqual(g.tavolo, [])

    def test_niente_scopa_sull_ultima_giocata(self):
        g = GiocoScopa(seed=1)
        g.mazzo.carte = []
        g.tavolo = [Carta(4, 'Coppe')]
        g.giocatori[0].mano = [Carta(4, 'Spade')]
        g.giocatori[1].mano = []
        g.turno = 0
        info = g.gioca(Carta(4, 'Spade'))
        self.assertFalse(info['scopa'])
        self.assertEqual(g.giocatori[0].scope, 0)
        self.assertTrue(g.finita)

    def test_carta_a_terra(self):
        g = GiocoScopa(seed=1)
        g.tavolo = [Carta(9, 'Coppe')]
        g.giocatori[0].mano = [Carta(3, 'Spade')]
        g.turno = 0
        info = g.gioca(Carta(3, 'Spade'))
        self.assertTrue(info['a_terra'])
        self.assertIn(Carta(3, 'Spade'), g.tavolo)

    def test_cattura_non_valida_rifiutata(self):
        g = GiocoScopa(seed=1)
        g.tavolo = [Carta(5, 'Coppe')]
        g.giocatori[0].mano = [Carta(5, 'Spade')]
        g.turno = 0
        self.assertRaises(ValueError, g.gioca,
                          Carta(5, 'Spade'), [Carta(9, 'Bastoni')])

    def test_carta_non_in_mano(self):
        g = GiocoScopa(seed=1)
        g.turno = 0
        carta_estranea = Carta(2, 'Bastoni')
        if carta_estranea in g.giocatori[0].mano:
            carta_estranea = Carta(9, 'Spade')
        if carta_estranea not in g.giocatori[0].mano:
            self.assertRaises(ValueError, g.gioca, carta_estranea)


class TestPunteggio(unittest.TestCase):

    def test_primiera(self):
        carte = [Carta(7, 'Denari'), Carta(7, 'Coppe'),
                 Carta(7, 'Spade'), Carta(7, 'Bastoni')]
        self.assertEqual(GiocoScopa._primiera_totale(carte), 84)

    def test_risultato_completo(self):
        g, det = _simula_partita(seed=3)
        self.assertEqual(sum(d['carte'] for d in det), 40)
        # il settebello appartiene a esattamente un giocatore
        self.assertEqual(sum(1 for d in det if d['settebello']), 1)
        for d in det:
            self.assertGreaterEqual(d['punti'], 0)

    def test_certificazione_100_partite(self):
        for seed in range(100):
            g, det = _simula_partita(seed=seed)
            self.assertTrue(g.finita)
            self.assertEqual(sum(d['carte'] for d in det), 40)
            self.assertEqual(len(g.tavolo), 0)
            self.assertEqual(sum(d['denari'] for d in det), 10)


class TestIA(unittest.TestCase):

    def test_ia_preferisce_il_settebello(self):
        g = GiocoScopa(seed=1)
        g.tavolo = [Carta(7, 'Denari'), Carta(2, 'Coppe')]
        g.giocatori[1].mano = [Carta(7, 'Spade'), Carta(2, 'Bastoni')]
        g.turno = 1
        carta, cattura = g.mossa_ai()
        self.assertEqual(carta, Carta(7, 'Spade'))
        self.assertIn(Carta(7, 'Denari'), cattura)

    def test_ia_gioca_sempre_una_carta_valida(self):
        for seed in range(30):
            g = GiocoScopa(seed=seed)
            while not g.finita:
                gc = g.giocatore_corrente
                if gc.ai:
                    carta, cattura = g.mossa_ai()
                    self.assertIn(carta, gc.mano)
                    g.gioca(carta, cattura)
                else:
                    c = gc.mano[0]
                    op = g.opzioni_cattura(c)
                    g.gioca(c, op[0] if op else None)


if __name__ == '__main__':
    print('=== CERTIFICAZIONE MOTORE SCOPA ===')
    unittest.main(verbosity=2, exit=False)
