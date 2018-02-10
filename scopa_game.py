import random


class Mazzo(object):
    def carte(valore, seme):
        valore = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        seme = ['Bastoni', 'Coppa', 'Oro', 'Spada']
        self.carte = []
        carta = Carta(seme, valore)
        self.carte.append(carta)

    def mischia_carte(self):
        self.carte = random.sample(carte, len(carte))
        self.ultima_carta = 0

    def carte_da_giocare(self):
        return self.carte[self.ultima_carta:]

    def carte_giocate(self):
        return self.carte[0:self.ultima_carta]

    def numero_carte_da_giocare(self):
        return len(self.carte_da_giocare())

    def numero_carte_giocate(self):
        return len(self.carte_giocate())

    def _togli_carte(self, numero_carte):
        self.ultima_carta += numero_carte

    def dai_carte(self, numero_carte):
        carte = range(numero_carte)
        carte_date = []
        for c in carte:
            carta = self.ultima_carta + c
            carte_date.append(self.carte[carta])
        self._togli_carte(numero_carte)
        return carte_date


class MazzoGiocatore(object):
    def __init__(self):
        self.carte = set()
        self.scope = set()

    def aggiungi_carte(self, lista_carte):
        for carta in lista_carte:
            self.carte.add(carta)

    def scope(self, carte_mano, carte_tavolo):
        for carte in carte_tavolo:
            if carte[valore] == carte_tavolo[valore] and
            carte in carte_tavolo == 1:
                self.scope.add(carte)
                print('SCOPA!')

    def calcola_punteggio(self):
        punteggio = 0
        for carte[7, seme] in self.carte:
            if self.carte[7, seme] > 2:
                punteggio = punteggio+1
        for carte in self.carte:
            if len(lista_carte) > 20:
                punteggio = punteggio+1
                print('Hai fatto un punto,'
                      'il numero di carte che hai è:' len(lista_carte))
        for carte[valore, 'Oro'] in self.carte:
            if self.carte[valore, 'Oro'] > 5:
                punteggio = punteggio+1
        for carte[7, 'Oro'] in self.carte:
            punteggio = punteggio+1
        for scope in self.scope:
            punteggio = punteggio+scope


class ManoTavolo(object):
    def __init__(self, carte_iniziali):
        """
            carte iniziali è una lista
        """
        self.carte = carte_iniziali

    def aggiungi_carte(self, carte):
        self.carte.append(carte)

    def togli_carte(self, carte):
        for carta in carte:
            self.carte.remove(carta)


class ManoGiocatore(object):
    def __init__(self):
        self.carte_mano = []
        self.carte_mazzo = []

    def prendi_carte_in_mano(self, carte):
        """
            acquisisce le carte dal mazzo
        """
        self.carte_mano = carte

    def prendi_carte_in_mazzo(self, carte):
        """ mette nel proprio mazzo"""
        self.carte_mazzo = carte

    def lancia_carta(self, carta):
        return self.carte.index(carta)

    def scegli_carta(self, carte_mano, carte_tavolo=None):
        """
            sulla base delle proprie carte (self.carte)
            e su quelle presenti sul tavolo
            sceglie la carta da giocare
        """
        for valore in carte_mano[valore, seme]:
            if valore == carte_tavolo[valore, seme]:
                self.carte.index(carta)
            if valore = carte_tavolo[valore] + carte_tavolo[valore]:
                self.carte.index(carta)
            else:
                return self.carte.index(carta) != carte_tavolo


class ManoGiocatoreStupido(ManoGiocatore):
    def scegli_carta(self, carte, carte_tavolo=None):
        carta_random = random.randint(0, len(carte)-1)
        return carte_in_mano[carta_random]


class GiocoCarteNapolatane(object):
    def __init__(self, giocatori,
                 numero_carte_tavolo_inizio,
                 numero_carte_mano_giocatori,
                 numero_carte_mazzo=40):
        """
            giocatori lista di tipo ManoGiocatore
            il tavolo viene inizializzato nel metodo .inizia()
            mazzo di tipo Mazzo
        """
        self.tavolo = None
        self.giocatori = giocatori
        self.mazzo = Mazzo(numero_carte_mazzo)
        self.numero_carte_tavolo_inizio = numero_carte_tavolo_inizio
        self.numero_carte_mano_giocatori = numero_carte_mano_giocatori
        # controllare che il numero dei giocatori sia modulo di 2
        if (len(giocatori) % 2):
            raise Exception('numero giocatori incompatibile')

    def inizia(self):
        if not self.tavolo and self.numero_carte_tavolo_inizio:
            carte_iniziali = self.mazzo.dai_carte(self.numero_carte_tavolo_inizio)
            self.tavolo = ManoTavolo(carte_iniziali)
        else:
            raise Exception('Specificare il numero delle carte '
                            'da giocare sul tavolo, es: 4')
        # dai le carte ai giocatori solo nella prima mano
        for giocatore in self.giocatori:
            carte_dal_mazzo = self.mazzo.dai_carte(self.numero_carte_mano_giocatori)
            giocatore.prendi_carte_in_mano(carte_dal_mazzo)

    def turno(self):
        for giocatore in self.giocatori:
            giocatore.scegli_carta(giocatore)


if __name__ == '__main__':
    g1 = ManoGiocatoreStupido()
    g2 = ManoGiocatoreStupido()
    giocatori = [g1, g2]
    # scopa
    gioco = GiocoCarteNapolatane(giocatori,
                                 numero_carte_tavolo_inizio=4,
                                 numero_carte_mano_giocatori=3,
                                 numero_carte_mazzo=40)
    gioco.inizia()
    print("Il gioco ha inizio")
    lista_carte = [str(i) for i in gioco.tavolo.carte]
    print("Carte sul tavolo: {}".format(' '.join(lista_carte)))
