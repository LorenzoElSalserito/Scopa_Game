"""Motore di gioco per la Scopa (gioco di carte napoletano).

Usa solo la libreria standard di Python (random, itertools): nessuna
dipendenza esterna. Questo modulo contiene la logica completa del gioco,
il punteggio ufficiale e l'intelligenza artificiale.
"""

import random
import itertools

# --- Costanti del gioco -----------------------------------------------------

SEMI = ('Bastoni', 'Coppe', 'Denari', 'Spade')
VALORI = tuple(range(1, 11))  # da Asso (1) a Re (10)

# Valore di ogni carta ai fini della Primiera.
PRIMIERA = {1: 16, 2: 12, 3: 13, 4: 14, 5: 15,
            6: 18, 7: 21, 8: 10, 9: 10, 10: 10}

# Nomi delle figure.
NOMI_FIGURE = {1: 'Asso', 8: 'Fante', 9: 'Cavallo', 10: 'Re'}


# --- Carta ------------------------------------------------------------------

class Carta(object):
    """Una singola carta del mazzo napoletano."""

    __slots__ = ('valore', 'seme')

    def __init__(self, valore, seme):
        if valore not in VALORI:
            raise ValueError('valore carta non valido: %r' % (valore,))
        if seme not in SEMI:
            raise ValueError('seme carta non valido: %r' % (seme,))
        self.valore = valore
        self.seme = seme

    @property
    def nome(self):
        return NOMI_FIGURE.get(self.valore, str(self.valore))

    @property
    def primiera(self):
        return PRIMIERA[self.valore]

    @property
    def e_denari(self):
        return self.seme == 'Denari'

    @property
    def e_settebello(self):
        return self.valore == 7 and self.seme == 'Denari'

    def __eq__(self, altro):
        return (isinstance(altro, Carta) and
                altro.valore == self.valore and altro.seme == self.seme)

    def __ne__(self, altro):
        return not self.__eq__(altro)

    def __hash__(self):
        return hash((self.valore, self.seme))

    def __repr__(self):
        return 'Carta(%d, %r)' % (self.valore, self.seme)

    def __str__(self):
        return '%s di %s' % (self.nome, self.seme)


# --- Mazzo ------------------------------------------------------------------

class Mazzo(object):
    """Mazzo da 40 carte."""

    def __init__(self):
        self.carte = [Carta(v, s) for s in SEMI for v in VALORI]

    def mischia(self):
        random.shuffle(self.carte)

    def pesca(self, numero):
        """Toglie e restituisce `numero` carte dalla cima del mazzo."""
        if numero > len(self.carte):
            raise ValueError('carte insufficienti nel mazzo')
        pescate = self.carte[:numero]
        self.carte = self.carte[numero:]
        return pescate

    def __len__(self):
        return len(self.carte)


# --- Regole di cattura ------------------------------------------------------

def trova_catture(carta, tavolo):
    """Restituisce le possibili prese giocando `carta` sul `tavolo`.

    Ritorna una lista di tuple di Carta. Regola ufficiale: se esiste
    almeno una presa diretta (una carta singola di pari valore) le
    combinazioni a somma non sono ammesse.
    """
    singole = [(c,) for c in tavolo if c.valore == carta.valore]
    if singole:
        return singole
    catture = []
    for r in range(2, len(tavolo) + 1):
        for combo in itertools.combinations(tavolo, r):
            if sum(c.valore for c in combo) == carta.valore:
                catture.append(combo)
    return catture


# --- Giocatore --------------------------------------------------------------

class Giocatore(object):
    """Stato di un giocatore: carte in mano, carte prese, scope fatte."""

    def __init__(self, nome, ai=False):
        self.nome = nome
        self.ai = ai
        self.mano = []
        self.prese = []
        self.scope = 0

    def reset(self):
        self.mano = []
        self.prese = []
        self.scope = 0


# --- Gioco ------------------------------------------------------------------

class GiocoScopa(object):
    """Una partita di Scopa a 2 giocatori (umano contro IA).

    L'indice 0 e' il giocatore umano, l'indice 1 e' il computer.
    """

    def __init__(self, nome_umano='Giocatore', nome_ai='Computer', seed=None):
        if seed is not None:
            random.seed(seed)
        self.giocatori = [Giocatore(nome_umano, ai=False),
                          Giocatore(nome_ai, ai=True)]
        self.mazzo = Mazzo()
        self.mazzo.mischia()
        self.tavolo = []
        self.turno = 0
        self.ultimo_a_prendere = None
        self.finita = False
        self.log = []
        self._distribuisci_iniziale()

    # -- preparazione --------------------------------------------------------

    def _distribuisci_iniziale(self):
        self.tavolo = self.mazzo.pesca(4)
        for g in self.giocatori:
            g.mano = self.mazzo.pesca(3)

    @property
    def giocatore_corrente(self):
        return self.giocatori[self.turno]

    def opzioni_cattura(self, carta):
        """Prese possibili per `carta` con il tavolo attuale."""
        return trova_catture(carta, self.tavolo)

    # -- svolgimento ---------------------------------------------------------

    def gioca(self, carta, cattura=None):
        """Gioca `carta` per il giocatore di turno.

        `cattura` e' una sequenza di Carta da prendere; se None viene
        scelta automaticamente la prima opzione disponibile. Restituisce
        un dizionario che descrive la mossa.
        """
        if self.finita:
            raise RuntimeError('partita gia terminata')
        g = self.giocatore_corrente
        if carta not in g.mano:
            raise ValueError('la carta non e nella mano del giocatore')

        opzioni = trova_catture(carta, self.tavolo)
        if opzioni and cattura is not None:
            cattura = tuple(cattura)
            insiemi = [set(o) for o in opzioni]
            if set(cattura) not in insiemi:
                raise ValueError('presa non valida per la carta giocata')

        g.mano.remove(carta)
        e_ultima_giocata = (len(self.mazzo) == 0 and
                            sum(len(x.mano) for x in self.giocatori) == 0)

        info = {'giocatore': g, 'carta': carta, 'catturate': [],
                'scopa': False, 'a_terra': False}

        if opzioni:
            if cattura is None:
                cattura = opzioni[0]
            for c in cattura:
                self.tavolo.remove(c)
            g.prese.extend(list(cattura))
            g.prese.append(carta)
            self.ultimo_a_prendere = g
            info['catturate'] = list(cattura)
            if not self.tavolo and not e_ultima_giocata:
                g.scope += 1
                info['scopa'] = True
        else:
            self.tavolo.append(carta)
            info['a_terra'] = True

        self.log.append(info)
        self._avanza()
        return info

    def _avanza(self):
        self.turno = 1 - self.turno
        if all(len(g.mano) == 0 for g in self.giocatori):
            if len(self.mazzo) > 0:
                for g in self.giocatori:
                    g.mano = self.mazzo.pesca(3)
            else:
                self._termina()

    def _termina(self):
        # Le carte rimaste sul tavolo vanno all'ultimo che ha preso.
        if self.tavolo and self.ultimo_a_prendere is not None:
            self.ultimo_a_prendere.prese.extend(self.tavolo)
            self.tavolo = []
        self.finita = True

    # -- punteggio -----------------------------------------------------------

    @staticmethod
    def _primiera_totale(carte):
        migliore = {}
        for c in carte:
            if c.primiera > migliore.get(c.seme, 0):
                migliore[c.seme] = c.primiera
        return sum(migliore.values())

    def risultato(self):
        """Calcola il punteggio finale. Restituisce una lista di dizionari,
        uno per giocatore, con voci e punti totali."""
        if not self.finita:
            raise RuntimeError('partita non ancora terminata')

        det = []
        for g in self.giocatori:
            det.append({
                'giocatore': g,
                'carte': len(g.prese),
                'denari': sum(1 for c in g.prese if c.e_denari),
                'settebello': any(c.e_settebello for c in g.prese),
                'primiera': self._primiera_totale(g.prese),
                'scope': g.scope,
                'punti': 0,
                'voci': [],
            })
        a, b = det

        def assegna(chiave, etichetta):
            if a[chiave] > b[chiave]:
                a['punti'] += 1
                a['voci'].append(etichetta)
            elif b[chiave] > a[chiave]:
                b['punti'] += 1
                b['voci'].append(etichetta)

        assegna('carte', 'Carte')
        assegna('denari', 'Denari')
        assegna('primiera', 'Primiera')

        for d in det:
            if d['settebello']:
                d['punti'] += 1
                d['voci'].append('Settebello')
            if d['scope']:
                d['punti'] += d['scope']
                d['voci'].append('Scope x%d' % d['scope'])

        return det

    # -- intelligenza artificiale -------------------------------------------

    @staticmethod
    def _valore_carta(c):
        """Quanto e' "preziosa" una carta da non sprecare scartandola."""
        v = c.primiera / 21.0
        if c.e_denari:
            v += 2.0
        if c.valore == 7:
            v += 1.5
        if c.e_settebello:
            v += 20.0
        return v

    @staticmethod
    def _valuta_presa(catturate, scopa):
        s = 0.0
        for c in catturate:
            s += 1.0 + c.primiera / 21.0
            if c.e_denari:
                s += 2.0
            if c.valore == 7:
                s += 3.0
            if c.e_settebello:
                s += 12.0
        if scopa:
            s += 14.0
        return s

    def mossa_ai(self):
        """Sceglie la mossa per il giocatore IA di turno.

        Restituisce la tupla (carta, cattura) da passare a `gioca`.
        """
        g = self.giocatore_corrente
        if not g.ai:
            raise RuntimeError('non e il turno della IA')

        prese = []
        for carta in g.mano:
            for o in trova_catture(carta, self.tavolo):
                scopa = len(o) == len(self.tavolo)
                prese.append((self._valuta_presa(o, scopa), carta, o))
        if prese:
            prese.sort(key=lambda x: x[0], reverse=True)
            return prese[0][1], prese[0][2]

        # Nessuna presa possibile: scarta minimizzando il rischio.
        migliore = None
        somma_tavolo = sum(c.valore for c in self.tavolo)
        for carta in g.mano:
            somma = somma_tavolo + carta.valore
            # se la somma del tavolo resta <= 10 l'avversario puo' fare scopa
            penalita = 8.0 if (self.tavolo and somma <= 10) else 0.0
            punteggio = -(penalita + self._valore_carta(carta))
            if migliore is None or punteggio > migliore[0]:
                migliore = (punteggio, carta)
        return migliore[1], None


# --- Simulazione da riga di comando ----------------------------------------

def _simula_partita(seed=None, verbose=False):
    """Gioca una partita completa (IA contro scelte casuali) e ritorna il
    risultato. Serve per la certificazione automatica del motore."""
    g = GiocoScopa(seed=seed)
    while not g.finita:
        gc = g.giocatore_corrente
        if gc.ai:
            carta, cattura = g.mossa_ai()
        else:
            carta = random.choice(gc.mano)
            opzioni = g.opzioni_cattura(carta)
            cattura = opzioni[0] if opzioni else None
        info = g.gioca(carta, cattura)
        if verbose:
            if info['a_terra']:
                print('%s: gioca %s (a terra)'
                      % (info['giocatore'].nome, info['carta']))
            else:
                print('%s: gioca %s, prende %s%s'
                      % (info['giocatore'].nome, info['carta'],
                         ', '.join(str(c) for c in info['catturate']),
                         '  SCOPA!' if info['scopa'] else ''))
    return g, g.risultato()


if __name__ == '__main__':
    gioco, dettaglio = _simula_partita(seed=1, verbose=True)
    print('\n--- Risultato finale ---')
    for d in dettaglio:
        print('%-10s %2d punti  [%s]'
              % (d['giocatore'].nome, d['punti'],
                 ', '.join(d['voci']) or 'nessuna voce'))
    totale = sum(d['carte'] for d in dettaglio)
    print('Carte totali raccolte: %d (atteso 40)' % totale)
    assert totale == 40, 'errore: le carte non tornano'
    print('Motore di gioco: OK')
