# Scopa_Game

Il classico gioco di carte napoletano: **Scopa**. Umano contro computer (IA).

Scritto in Python con la **sola libreria standard** — nessuna dipendenza
esterna. La GUI usa Tkinter (incluso in Python).

## File

| File | Contenuto |
|------|-----------|
| `scopa_game.py` | Motore di gioco: carte, mazzo, regole, punteggio, IA |
| `scopa_gui.py`  | Interfaccia grafica Tkinter |
| `test_scopa.py` | Certificazione automatica (21 test) |

## Avvio

Gioca con la finestra grafica:

```
python3 scopa_gui.py
```

Simulazione da terminale (motore):

```
python3 scopa_game.py
```

## Testing software

```
python3 test_scopa.py
```

Verifica mazzo da 40 carte uniche, regole di cattura (presa diretta e a
somma), scopa, punteggio ufficiale e 100 partite complete IA contro IA.

## Regole implementate

- Mazzo da 40 carte (Bastoni, Coppe, Denari, Spade — valori 1-10).
- 4 carte sul tavolo, 3 in mano per giocatore; si ridistribuisce fino a
  esaurire il mazzo.
- Cattura: priorita alla presa diretta; in mancanza, cattura a somma.
- **Scopa** quando si svuota il tavolo (non sull'ultima giocata).
- A fine partita le carte sul tavolo vanno all'ultimo che ha preso.
- Punteggio: Carte, Denari, Settebello, Primiera, piu un punto per scopa.
- Match al meglio degli **11 punti** (punteggio cumulativo nella GUI).

## Licenza e Copyright

© Lorenzo De Marco (Lorenzo DM) 2026
Rilasciato sotto la licenza [AGPLv3](https://www.gnu.org/licenses/agpl-3.0.html#license-text) 