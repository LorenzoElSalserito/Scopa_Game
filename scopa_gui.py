"""Interfaccia grafica professionale (Tkinter) per il gioco della Scopa.

Avvio:  python3 scopa_gui.py

Usa solo la libreria standard di Python (tkinter). Le carte sono
disegnate su Canvas (semi, pip e figure vettoriali): nessuna immagine
esterna, nessuna dipendenza. Il motore di gioco e' in scopa_game.py.
"""

import tkinter as tk
from tkinter import messagebox

from scopa_game import GiocoScopa, NOMI_FIGURE


# --- Palette ----------------------------------------------------------------

PAL = {
    'feltro':        '#0d5a32',
    'feltro_chiaro': '#127a44',
    'feltro_scuro':  '#063d20',
    'bordo_scuro':   '#042614',
    'oro':           '#e3b341',
    'oro_scuro':     '#a07d1c',
    'panna':         '#f4ecd8',
    'testo':         '#f4ecd8',
    'ombra':         '#04341c',
}

# Colore di ogni seme.
COLORI_SEME = {
    'Bastoni': '#2f7d3a',
    'Coppe':   '#c0392b',
    'Denari':  '#c98a00',
    'Spade':   '#2a5d9c',
}

PUNTI_MATCH = 11  # punti per vincere il match


# --- Carta disegnata ---------------------------------------------------------

# Posizione dei pip (frazioni del corpo carta) per i valori numerici 1-7.
LAYOUT_PIP = {
    1: [(.50, .50)],
    2: [(.50, .31), (.50, .69)],
    3: [(.50, .27), (.50, .50), (.50, .73)],
    4: [(.35, .31), (.65, .31), (.35, .69), (.65, .69)],
    5: [(.35, .29), (.65, .29), (.50, .50), (.35, .71), (.65, .71)],
    6: [(.35, .27), (.65, .27), (.35, .50), (.65, .50), (.35, .73), (.65, .73)],
    7: [(.34, .27), (.66, .27), (.30, .50), (.50, .50), (.70, .50),
        (.34, .73), (.66, .73)],
}
SCALA_PIP = {1: 1.95, 2: 1.30, 3: 1.25, 4: 1.12, 5: 1.02, 6: 0.95, 7: 0.82}


class CartaWidget(tk.Canvas):
    """Una carta resa graficamente su Canvas, con ombra, semi e hover.

    `grande=True` -> carta della mano del giocatore (con effetto hover).
    `grande=False` -> carta compatta per tavolo e avversario.
    """

    PER_RIGA = 13  # carte per riga sul tavolo (oltre si va a capo)

    def __init__(self, parent, carta=None, scoperta=True, grande=True):
        self.carta = carta
        self.scoperta = scoperta
        self.grande = grande
        self.evidenza = None       # None | 'cattura' | 'scopa' | 'attiva'
        self.sollevata = False

        self.CW, self.CH = (92, 138) if grande else (60, 90)
        self.K = self.CW / 104.0
        self.MX = 8
        self.LIFT = 12 if grande else 0
        self.Y_BASE = self.LIFT + 3
        self.Y_HOVER = 3
        self.R = max(6, int(12 * self.K))
        self.W = self.CW + 2 * self.MX + 6
        self.H = self.CH + self.Y_BASE + 9

        super().__init__(parent, width=self.W, height=self.H,
                         bg=PAL['feltro'], highlightthickness=0, bd=0)
        self._disegna()

    # -- API -----------------------------------------------------------------

    def imposta(self, evidenza=None, sollevata=False):
        if evidenza == self.evidenza and sollevata == self.sollevata:
            return
        self.evidenza = evidenza
        self.sollevata = sollevata
        self._disegna()

    # -- disegno -------------------------------------------------------------

    @staticmethod
    def _round_rect(cv, x1, y1, x2, y2, r, **kw):
        pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r,
               x2, y2, x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r,
               x1, y1 + r, x1, y1]
        return cv.create_polygon(pts, smooth=True, **kw)

    def _disegna(self):
        self.delete('all')
        y0 = self.Y_HOVER if self.sollevata else self.Y_BASE
        x0 = self.MX
        x1, y1 = x0 + self.CW, y0 + self.CH

        if self.evidenza in ('cattura', 'scopa', 'attiva'):
            glow = {'cattura': PAL['oro'], 'scopa': '#7CFC8A',
                    'attiva': PAL['oro']}[self.evidenza]
            self._round_rect(self, x0 - 5, y0 - 5, x1 + 5, y1 + 5,
                             self.R + 4, fill=glow, outline='')

        self._round_rect(self, x0 + 5, y0 + 6, x1 + 5, y1 + 6, self.R,
                         fill=PAL['ombra'], outline='')

        if self.scoperta and self.carta is not None:
            self._disegna_fronte(x0, y0, x1, y1)
        else:
            self._disegna_retro(x0, y0, x1, y1)

    def _disegna_retro(self, x0, y0, x1, y1):
        self._round_rect(self, x0, y0, x1, y1, self.R,
                         fill='#16386f', outline='#0a1f44', width=2)
        m = max(7, int(10 * self.K))
        self._round_rect(self, x0 + m, y0 + m, x1 - m, y1 - m,
                         max(3, self.R - 5), fill='#1d4a8f',
                         outline=PAL['oro_scuro'], width=1)
        passo = max(12, int(17 * self.K))
        ix0, iy0, ix1, iy1 = x0 + m, y0 + m, x1 - m, y1 - m
        x = ix0 - (iy1 - iy0)
        while x < ix1:
            self.create_line(max(ix0, x), iy0 if x >= ix0 else iy0 + (ix0 - x),
                             min(ix1, x + (iy1 - iy0)),
                             iy1 if x + (iy1 - iy0) <= ix1
                             else iy1 - (x + (iy1 - iy0) - ix1),
                             fill='#2f5fa6')
            self.create_line(min(ix1, ix1 - (x - ix0)), iy0,
                             max(ix0, ix1 - (x - ix0) - (iy1 - iy0)), iy1,
                             fill='#2f5fa6')
            x += passo
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        rr = max(13, int(20 * self.K))
        self.create_oval(cx - rr, cy - rr, cx + rr, cy + rr,
                         fill='#16386f', outline=PAL['oro'], width=2)
        self.create_text(cx, cy, text='S', fill=PAL['oro'],
                         font=('Georgia', max(13, int(20 * self.K)), 'bold'))

    def _disegna_fronte(self, x0, y0, x1, y1):
        carta = self.carta
        col = COLORI_SEME[carta.seme]
        self._round_rect(self, x0, y0, x1, y1, self.R,
                         fill='#fdfaf1', outline=col, width=2)
        self._round_rect(self, x0 + 4, y0 + 4, x1 - 4, y1 - 4,
                         max(3, self.R - 3), fill='', outline=col, width=1)

        co = max(11, int(13 * self.K))
        f_idx = max(9, int(15 * self.K))
        for ax, ay, verso in ((x0 + co, y0 + co, 1), (x1 - co, y1 - co, -1)):
            self.create_text(ax, ay, text=str(carta.valore), fill=col,
                             font=('Georgia', f_idx, 'bold'))
            self._pip(carta.seme, ax, ay + verso * int(15 * self.K), 0.40)

        cx = (x0 + x1) / 2
        cy = (y0 + y1) / 2
        if carta.valore <= 7:
            scala = SCALA_PIP[carta.valore]
            for fx, fy in LAYOUT_PIP[carta.valore]:
                self._pip(carta.seme, x0 + fx * self.CW,
                          y0 + fy * self.CH, scala)
        else:
            self._pip(carta.seme, cx, cy - 7 * self.K, 2.30)
            nome = NOMI_FIGURE.get(carta.valore, '').upper()
            bh = max(13, int(16 * self.K))
            self.create_rectangle(x0 + co, y1 - co - bh, x1 - co, y1 - co,
                                  fill=col, outline='')
            self.create_text(cx, y1 - co - bh / 2, text=nome,
                             fill='#fdfaf1',
                             font=('Georgia', max(7, int(9 * self.K)), 'bold'))

    # -- pip dei semi --------------------------------------------------------

    def _pip(self, seme, cx, cy, s):
        s = s * self.K
        {'Denari': self._pip_denari, 'Coppe': self._pip_coppe,
         'Spade': self._pip_spade, 'Bastoni': self._pip_bastoni}[seme](cx,
                                                                       cy, s)

    def _pip_denari(self, cx, cy, s):
        r = 11 * s
        w = max(1, int(s))
        self.create_oval(cx - r, cy - r, cx + r, cy + r,
                         fill='#b8860b', outline='#8a6508', width=w)
        self.create_oval(cx - r * .74, cy - r * .74, cx + r * .74,
                         cy + r * .74, fill='#f0c419', outline='#d6a900')
        self.create_oval(cx - r * .34, cy - r * .34, cx + r * .34,
                         cy + r * .34, fill='#fff2b0', outline='')
        self.create_arc(cx - r * .58, cy - r * .58, cx + r * .58,
                        cy + r * .58, start=55, extent=70, style=tk.ARC,
                        outline='#fff6cf', width=w)

    def _pip_coppe(self, cx, cy, s):
        w = 9 * s
        h = 8 * s
        top = cy - 10 * s
        lw = max(1, int(s))
        self.create_oval(cx - w, top - 2 * s, cx + w, top + 4 * s,
                         fill='#e9694f', outline='#9c2418', width=lw)
        self.create_arc(cx - w, top, cx + w, top + 2 * h, start=180,
                        extent=180, style=tk.CHORD, fill='#c0392b',
                        outline='#9c2418', width=lw)
        self.create_rectangle(cx - 1.6 * s, top + 2 * h - s,
                              cx + 1.6 * s, top + 2 * h + 6 * s,
                              fill='#9c2418', outline='')
        self.create_oval(cx - w * .72, top + 2 * h + 4 * s, cx + w * .72,
                         top + 2 * h + 9 * s, fill='#c0392b',
                         outline='#9c2418', width=lw)

    def _pip_spade(self, cx, cy, s):
        h = 13 * s
        w = 5.4 * s
        lw = max(1, int(s))
        self.create_polygon(cx, cy - h, cx + w, cy - h * .15,
                            cx, cy + h * .42, cx - w, cy - h * .15,
                            fill='#3f6fb0', outline='#1f3f70', width=lw)
        self.create_line(cx, cy - h * .8, cx, cy + h * .3,
                         fill='#cdddf2', width=lw)
        self.create_rectangle(cx - w * 1.7, cy + h * .40, cx + w * 1.7,
                              cy + h * .58, fill='#2a5d9c',
                              outline='#1f3f70')
        self.create_rectangle(cx - 1.7 * s, cy + h * .58, cx + 1.7 * s,
                              cy + h * .92, fill='#2a5d9c', outline='')
        self.create_oval(cx - 2.6 * s, cy + h * .88, cx + 2.6 * s,
                         cy + h * 1.12, fill='#3f6fb0', outline='#1f3f70')

    def _pip_bastoni(self, cx, cy, s):
        d = 12 * s
        self.create_line(cx - d * .72, cy + d * .72, cx + d * .72,
                         cy - d * .72, fill='#2f7d3a',
                         width=max(3, 6 * s), capstyle=tk.ROUND)
        self.create_line(cx - d * .72, cy + d * .72, cx + d * .72,
                         cy - d * .72, fill='#5bbf67',
                         width=max(1, 2 * s), capstyle=tk.ROUND)
        for fx, fy in ((-.30, .30), (.10, -.10)):
            self.create_oval(cx + fx * d - 2.4 * s, cy + fy * d - 2.4 * s,
                             cx + fx * d + 2.4 * s, cy + fy * d + 2.4 * s,
                             fill='#236b2f', outline='')


# --- Finestra principale -----------------------------------------------------

class ScopaGUI(object):

    def __init__(self, root):
        self.root = root
        root.title('Scopa - Gioco di carte napoletano')
        root.configure(bg=PAL['bordo_scuro'])

        self.gioco = None
        self.match = [0, 0]
        self._attesa = False
        self._msg = ''
        self._ultima_a_terra = None
        self._mano_widgets = []
        self._tavolo_widgets = []

        self._crea_menu()
        self._build()
        self.nuova_partita()
        self._sistema_finestra()

    # -- dimensionamento finestra -------------------------------------------

    def _sistema_finestra(self):
        """Dimensiona la finestra per il caso peggiore (tavolo su 2 righe)
        cosi' la mano del giocatore resta sempre visibile e cliccabile."""
        from scopa_game import Carta, SEMI
        salva = self.gioco.tavolo
        # riga di tavolo piena: riserva la larghezza e l'altezza giuste
        self.gioco.tavolo = [Carta(v, s) for s in SEMI
                             for v in range(1, 11)][:CartaWidget.PER_RIGA]
        self.render()
        self.root.update_idletasks()
        h_max = self.root.winfo_reqheight()
        w_max = self.root.winfo_reqwidth()
        self.gioco.tavolo = salva
        self.render()

        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        w = min(w_max, sw - 40)
        h = min(h_max, sh - 60)
        x = max(0, (sw - w) // 2)
        y = max(0, (sh - h) // 2 - 20)
        self.root.geometry('%dx%d+%d+%d' % (w, h, x, y))
        self.root.minsize(min(w, 760), min(h, 620))

    # -- menu ----------------------------------------------------------------

    def _crea_menu(self):
        barra = tk.Menu(self.root)
        m_partita = tk.Menu(barra, tearoff=0)
        m_partita.add_command(label='Nuova partita', accelerator='Ctrl+N',
                              command=self.nuova_partita)
        m_partita.add_command(label='Nuovo match', command=self.nuovo_match)
        m_partita.add_separator()
        m_partita.add_command(label='Esci', command=self.root.destroy)
        barra.add_cascade(label='Partita', menu=m_partita)

        m_aiuto = tk.Menu(barra, tearoff=0)
        m_aiuto.add_command(label='Regole', command=self._mostra_regole)
        m_aiuto.add_command(label='Informazioni', command=self._mostra_info)
        barra.add_cascade(label='Aiuto', menu=m_aiuto)

        self.root.config(menu=barra)
        self.root.bind('<Control-n>', lambda e: self.nuova_partita())

    # -- costruzione ---------------------------------------------------------

    def _pannello_giocatore(self, parent, titolo):
        f = tk.Frame(parent, bg=PAL['feltro_scuro'], bd=0,
                     highlightthickness=3,
                     highlightbackground=PAL['oro_scuro'],
                     highlightcolor=PAL['oro_scuro'])
        f.pack(side='left', expand=True, fill='x', padx=10)
        intest = tk.Frame(f, bg=PAL['feltro_scuro'])
        intest.pack(fill='x', padx=12, pady=(5, 0))
        nome = tk.Label(intest, text=titolo, bg=PAL['feltro_scuro'],
                        fg=PAL['panna'], font=('Georgia', 12, 'bold'))
        nome.pack(side='left')
        sette = tk.Label(intest, text='', bg=PAL['feltro_scuro'],
                         fg=PAL['oro'], font=('Georgia', 10, 'bold'))
        sette.pack(side='right')
        punti = tk.Label(f, text='0', bg=PAL['feltro_scuro'],
                         fg=PAL['oro'], font=('Georgia', 22, 'bold'))
        punti.pack()
        sub = tk.Label(f, text='', bg=PAL['feltro_scuro'],
                       fg='#bcd6c4', font=('Helvetica', 9))
        sub.pack(pady=(0, 5))
        return {'frame': f, 'nome': nome, 'sette': sette,
                'punti': punti, 'sub': sub}

    def _separatore(self, parent):
        tk.Frame(parent, bg=PAL['oro_scuro'], height=2).pack(fill='x',
                                                             padx=24, pady=1)

    def _build(self):
        cornice = tk.Frame(self.root, bg=PAL['feltro'], bd=0)
        cornice.pack(fill='both', expand=True, padx=6, pady=6)

        tk.Label(cornice, text='S  C  O  P  A',
                 font=('Georgia', 17, 'bold'),
                 bg=PAL['feltro'], fg=PAL['oro']).pack(pady=(7, 0))
        tk.Label(cornice, text='gioco di carte napoletano',
                 font=('Georgia', 8, 'italic'),
                 bg=PAL['feltro'], fg='#bcd6c4').pack()

        pannelli = tk.Frame(cornice, bg=PAL['feltro'])
        pannelli.pack(fill='x', pady=6, padx=14)
        self.pan_umano = self._pannello_giocatore(pannelli, 'Tu')
        self.pan_ai = self._pannello_giocatore(pannelli, 'Computer')

        self._separatore(cornice)

        self.f_ai = tk.Frame(cornice, bg=PAL['feltro'])
        self.f_ai.pack(pady=(5, 2))

        self.f_tavolo_box = tk.Frame(cornice, bg=PAL['feltro_chiaro'],
                                     highlightthickness=2,
                                     highlightbackground=PAL['oro_scuro'])
        self.f_tavolo_box.pack(pady=5, padx=20, fill='x')
        tk.Label(self.f_tavolo_box, text='TAVOLO',
                 font=('Georgia', 8, 'bold'), bg=PAL['feltro_chiaro'],
                 fg='#bcd6c4').pack(pady=(3, 0))
        self.f_tavolo = tk.Frame(self.f_tavolo_box, bg=PAL['feltro_chiaro'])
        self.f_tavolo.pack(pady=(2, 6))

        self.lbl_msg = tk.Label(
            cornice, text='', font=('Georgia', 10),
            bg=PAL['feltro_scuro'], fg=PAL['panna'], wraplength=820,
            pady=7, padx=14)
        self.lbl_msg.pack(fill='x', padx=20, pady=5)

        self.f_mano = tk.Frame(cornice, bg=PAL['feltro'])
        self.f_mano.pack(pady=(2, 4))

        self._separatore(cornice)

        piede = tk.Frame(cornice, bg=PAL['feltro'])
        piede.pack(fill='x', pady=6, padx=20)
        self.lbl_stato = tk.Label(piede, text='', font=('Helvetica', 9),
                                  bg=PAL['feltro'], fg='#bcd6c4')
        self.lbl_stato.pack(side='left')
        self._bottone(piede, 'Esci', self.root.destroy).pack(side='right')
        self._bottone(piede, 'Nuova partita', self.nuova_partita,
                      primario=True).pack(side='right', padx=8)

        tk.Label(cornice, text='Copyright © Lorenzo DM - Licenza AGPLv3',
                 font=('Helvetica', 8), bg=PAL['feltro'],
                 fg='#8fae97').pack(pady=(0, 6))

    def _bottone(self, parent, testo, cmd, primario=False):
        bg = PAL['oro'] if primario else PAL['feltro_scuro']
        fg = '#2a1c08' if primario else PAL['panna']
        act = '#f0c869' if primario else PAL['feltro_chiaro']
        return tk.Button(parent, text=testo, command=cmd,
                         font=('Georgia', 10, 'bold'), bg=bg, fg=fg,
                         activebackground=act, activeforeground=fg,
                         relief='flat', bd=0, padx=16, pady=6,
                         cursor='hand2', highlightthickness=0)

    # -- rendering -----------------------------------------------------------

    def render(self):
        umano, ai = self.gioco.giocatori

        for w in self.f_ai.winfo_children():
            w.destroy()
        if ai.mano:
            for _ in ai.mano:
                CartaWidget(self.f_ai, scoperta=False,
                            grande=False).pack(side='left', padx=3)
        else:
            tk.Label(self.f_ai, text='nessuna carta in mano',
                     bg=PAL['feltro'], fg='#bcd6c4',
                     font=('Helvetica', 9, 'italic')).pack(pady=20)

        for w in self.f_tavolo.winfo_children():
            w.destroy()
        self._tavolo_widgets = []
        if self.gioco.tavolo:
            for i, c in enumerate(self.gioco.tavolo):
                w = CartaWidget(self.f_tavolo, carta=c, grande=False)
                w.grid(row=i // CartaWidget.PER_RIGA,
                       column=i % CartaWidget.PER_RIGA, padx=3, pady=2)
                if c == self._ultima_a_terra:
                    w.imposta(evidenza='attiva')
                self._tavolo_widgets.append((c, w))
        else:
            tk.Label(self.f_tavolo, text='— tavolo vuoto —',
                     bg=PAL['feltro_chiaro'], fg='#bcd6c4',
                     font=('Georgia', 11, 'italic')).pack(pady=44)

        for w in self.f_mano.winfo_children():
            w.destroy()
        self._mano_widgets = []
        attivo = (self.gioco.turno == 0 and not self.gioco.finita
                  and not self._attesa)
        if umano.mano:
            for c in umano.mano:
                w = CartaWidget(self.f_mano, carta=c, grande=True)
                w.pack(side='left', padx=5)
                if attivo:
                    w.bind('<Button-1>', lambda e, cc=c: self._gioca_umano(cc))
                    w.bind('<Enter>', lambda e, cc=c, ww=w:
                           self._hover_on(cc, ww))
                    w.bind('<Leave>', lambda e: self._hover_off())
                self._mano_widgets.append((c, w))
        else:
            tk.Label(self.f_mano, text='nessuna carta in mano',
                     bg=PAL['feltro'], fg='#bcd6c4',
                     font=('Helvetica', 9, 'italic')).pack(pady=30)

        self._aggiorna_info()

    def _aggiorna_info(self):
        umano, ai = self.gioco.giocatori
        for pan, g, mt, attivo in (
                (self.pan_umano, umano, self.match[0], self.gioco.turno == 0),
                (self.pan_ai, ai, self.match[1], self.gioco.turno == 1)):
            pan['punti'].config(text=str(mt))
            pan['sub'].config(text='partita: %d carte  -  %d scope'
                              % (len(g.prese), g.scope))
            ha_sette = any(c.e_settebello for c in g.prese)
            pan['sette'].config(text='7 Denari' if ha_sette else '')
            evid = (PAL['oro'] if (attivo and not self.gioco.finita
                                   and not self._attesa)
                    else PAL['oro_scuro'])
            pan['frame'].config(highlightbackground=evid,
                                highlightcolor=evid)

        if self.gioco.finita:
            stato = 'Partita terminata.'
        elif self._attesa:
            stato = 'Il Computer sta giocando...'
        elif self.gioco.turno == 0:
            stato = 'Tocca a te: passa il mouse e clicca una carta.'
        else:
            stato = 'Turno del Computer.'
        self.lbl_stato.config(
            text='Mazzo: %d carte rimaste     %s'
            % (len(self.gioco.mazzo), stato))
        self.lbl_msg.config(text=self._msg or 'In bocca al lupo!')

    # -- evidenziazione hover -----------------------------------------------

    def _hover_on(self, carta, widget):
        if self.gioco.turno != 0 or self.gioco.finita or self._attesa:
            return
        widget.imposta(evidenza='attiva', sollevata=True)
        opzioni = self.gioco.opzioni_cattura(carta)
        catturabili = set()
        scopa = False
        for o in opzioni:
            catturabili.update(o)
            if len(o) == len(self.gioco.tavolo):
                scopa = True
        for c, w in self._tavolo_widgets:
            if c in catturabili:
                w.imposta(evidenza='scopa' if scopa else 'cattura')

    def _hover_off(self):
        for c, w in self._mano_widgets:
            w.imposta(evidenza=None, sollevata=False)
        for c, w in self._tavolo_widgets:
            w.imposta(evidenza='attiva' if c == self._ultima_a_terra
                      else None)

    # -- ciclo di gioco ------------------------------------------------------

    def nuova_partita(self):
        if max(self.match) >= PUNTI_MATCH:
            self.match = [0, 0]
        self.gioco = GiocoScopa(nome_umano='Tu', nome_ai='Computer')
        self._attesa = False
        self._ultima_a_terra = None
        self._msg = 'Nuova partita. Cattura piu carte, denari e il 7 di Denari!'
        self.render()

    def nuovo_match(self):
        self.match = [0, 0]
        self.nuova_partita()

    def _gioca_umano(self, carta):
        if self.gioco.turno != 0 or self.gioco.finita or self._attesa:
            return
        opzioni = self.gioco.opzioni_cattura(carta)
        if len(opzioni) > 1:
            scelta = self._chiedi_scelta(carta, opzioni)
            if scelta is None:
                return
        elif len(opzioni) == 1:
            scelta = opzioni[0]
        else:
            scelta = None

        info = self.gioco.gioca(carta, scelta)
        self._aggiorna_dopo_mossa(info)

        if self.gioco.finita:
            self.render()
            self._fine_partita()
            return
        self._attesa = True
        self.render()
        self.root.after(950, self._turno_ai)

    def _turno_ai(self):
        if self.gioco.finita:
            self._attesa = False
            self.render()
            self._fine_partita()
            return
        if self.gioco.turno != 1:
            self._attesa = False
            self.render()
            return
        carta, cattura = self.gioco.mossa_ai()
        info = self.gioco.gioca(carta, cattura)
        self._aggiorna_dopo_mossa(info)
        self._attesa = False
        self.render()
        if info['scopa']:
            self._flash_banner()
        if self.gioco.finita:
            self._fine_partita()

    def _aggiorna_dopo_mossa(self, info):
        self._msg = self._descrivi(info)
        self._ultima_a_terra = info['carta'] if info['a_terra'] else None

    # -- dialoghi ------------------------------------------------------------

    def _modale(self, titolo):
        top = tk.Toplevel(self.root)
        top.title(titolo)
        top.configure(bg=PAL['feltro'])
        top.transient(self.root)
        top.resizable(False, False)
        top.grab_set()
        return top

    def _chiedi_scelta(self, carta, opzioni):
        top = self._modale('Scegli la presa')
        tk.Label(top, text='Giochi  %s' % carta, bg=PAL['feltro'],
                 fg=PAL['oro'],
                 font=('Georgia', 13, 'bold')).pack(padx=24, pady=(18, 4))
        tk.Label(top, text='Scegli quali carte raccogliere:',
                 bg=PAL['feltro'], fg=PAL['panna'],
                 font=('Helvetica', 10)).pack(pady=(0, 10))

        scelta = {'v': None}

        def conferma(opz):
            scelta['v'] = opz
            top.destroy()

        for o in opzioni:
            testo = '  +  '.join(str(c) for c in o)
            self._bottone(top, testo, lambda oo=o: conferma(oo),
                          primario=True).pack(padx=24, pady=4, fill='x')
        self._bottone(top, 'Annulla', top.destroy).pack(pady=(10, 18))

        top.update_idletasks()
        self._centra(top)
        self.root.wait_window(top)
        return scelta['v']

    def _centra(self, top):
        self.root.update_idletasks()
        x = (self.root.winfo_rootx()
             + (self.root.winfo_width() - top.winfo_width()) // 2)
        y = (self.root.winfo_rooty()
             + (self.root.winfo_height() - top.winfo_height()) // 3)
        top.geometry('+%d+%d' % (max(0, x), max(0, y)))

    def _flash_banner(self):
        seq = [PAL['oro'], PAL['feltro_scuro'], PAL['oro'],
               PAL['feltro_scuro']]

        def passo(i):
            if i < len(seq):
                self.lbl_msg.config(bg=seq[i])
                self.root.after(160, lambda: passo(i + 1))
        passo(0)

    def _fine_partita(self):
        det = self.gioco.risultato()
        self.match[0] += det[0]['punti']
        self.match[1] += det[1]['punti']
        self.render()

        a, b = det
        righe = ['Risultato della partita', '']
        for d in det:
            righe.append('  %-9s  %2d punti   [%s]'
                          % (d['giocatore'].nome, d['punti'],
                             ', '.join(d['voci']) or 'niente'))
        righe += ['',
                  '  Carte:     Tu %2d   Computer %2d'
                  % (a['carte'], b['carte']),
                  '  Denari:    Tu %2d   Computer %2d'
                  % (a['denari'], b['denari']),
                  '  Primiera:  Tu %2d   Computer %2d'
                  % (a['primiera'], b['primiera']),
                  '  Settebello: %s'
                  % ('Tu' if a['settebello'] else 'Computer'),
                  '',
                  '  MATCH:  Tu %d  -  %d  Computer'
                  % (self.match[0], self.match[1])]

        titolo = 'Fine partita'
        if self.match[0] >= PUNTI_MATCH or self.match[1] >= PUNTI_MATCH:
            if self.match[0] > self.match[1]:
                righe.append('\n  >>> HAI VINTO IL MATCH! <<<')
                titolo = 'Hai vinto!'
            elif self.match[1] > self.match[0]:
                righe.append('\n  Il Computer ha vinto il match.')
                titolo = 'Match perso'
            else:
                righe.append('\n  Match in parita: si prosegue.')
        messagebox.showinfo(titolo, '\n'.join(righe))

    # -- aiuto ---------------------------------------------------------------

    def _mostra_regole(self):
        messagebox.showinfo(
            'Regole della Scopa',
            'OBIETTIVO\n'
            'Catturare carte per fare punti.\n\n'
            'SVOLGIMENTO\n'
            '- 4 carte sul tavolo, 3 in mano a testa.\n'
            '- Al proprio turno si gioca una carta.\n'
            '- Se uguaglia una carta del tavolo la cattura;\n'
            '  altrimenti puo prendere piu carte la cui somma\n'
            '  e pari al suo valore. La presa diretta ha priorita.\n'
            '- Se non prende nulla, resta sul tavolo.\n'
            '- SCOPA: svuotare il tavolo vale 1 punto.\n\n'
            'PUNTEGGIO\n'
            '- Carte: chi ne prende di piu (1 punto).\n'
            '- Denari: chi prende piu Denari (1 punto).\n'
            '- Settebello: chi prende il 7 di Denari (1 punto).\n'
            '- Primiera: miglior combinazione (1 punto).\n'
            '- Ogni scopa: 1 punto.\n\n'
            'Vince il match chi arriva a %d punti.' % PUNTI_MATCH)

    def _mostra_info(self):
        messagebox.showinfo(
            'Informazioni',
            'Scopa - Gioco di carte napoletano\n\n'
            'Interfaccia Tkinter, carte disegnate vettorialmente.\n'
            'Solo libreria standard Python: nessuna dipendenza.\n\n'
            'Avversario controllato da IA euristica.')

    # -- testo ---------------------------------------------------------------

    @staticmethod
    def _descrivi(info):
        chi = info['giocatore'].nome
        if info['a_terra']:
            return '%s gioca %s e la lascia sul tavolo.' % (chi, info['carta'])
        prese = ', '.join(str(c) for c in info['catturate'])
        msg = '%s gioca %s e raccoglie: %s.' % (chi, info['carta'], prese)
        if info['scopa']:
            msg += '          * * *  S C O P A !  * * *'
        return msg


def main():
    root = tk.Tk()
    ScopaGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
