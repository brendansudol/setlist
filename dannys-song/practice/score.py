"""Jerry's Guitar Bar tab, in printed measure order.

Each group is one beat of four sixteenth-note slots. E is low E and e is high e.
+ stacks notes, . lets time pass, ~ carries a tied string across the barline,
h is a hammer-on and r is a rolled chord. Integer rows reuse an identical bar.
"""
from practice.notation import Bar, Step

BPM = 71
SECTIONS = (
    (1, 1, "Intro"), (2, 9, "Picked verse"), (10, 17, "Picked chorus"),
    (18, 25, "Strummed verse"), (26, 33, "Strummed chorus"), (34, 38, "Outro"),
)
# Play the printed repeat, then the later verses and instrumental turnaround
# described in the companion lesson. Section and single-bar loops stay local.
SONG_ORDER = (1, *range(2, 18), *range(2, 18), *range(18, 34), *range(18, 34),
              *range(18, 22), *range(34, 39))

# Chord symbols on successive beats. A dash continues the preceding chord.
ROWS = (
    # Intro
    ("D", "D0 B3 G2 e2 | D0 B3 G2 e2 | D0 B3 G2 e2 | D0 B3 G2 e2"),  # 1
    # Picked verse
    ("D - C -", "D0+~e2 B3 G2 e2 | D0 B3 G2 e0 | A3 G0 D2 e0 | A3 G0 D2 e0"),  # 2
    ("Bm", "A2 G4 D4 B3 | A2 G4 D4 e2 | A2 G4 D4 B3 | A2 G4 D4 B0"),  # 3
    ("E", "E0+~B0 G1 D2 e0 | E0 G1 D2 B0 | E0 G1 D2 B0 | E0 G1 D2 B0"),  # 4
    ("A", "A0 G2 D2 B2 | A0 G2 D2 B3 | A0 G2 D2 e0 | A0 G2 D2 B3"),  # 5
    ("D - C -", "D0+~B3 . rG2+B3+e2 . | D0 B3 G2 e0 | A3 G0 D2 e0 | A3 G0 D2 e0"),  # 6
    3,  # 7
    4,  # 8
    ("A", "A0 G2 D2 B2 | A0 G2 D2 B3 | A0 G2 D2 e0 | A0 G2 D2 B2"),  # 9
    # Picked chorus
    ("G - A -", "E3 . rD0+G0+B0+e3 . | E3 B0 D0 G0 | A0 G2 D2 B2 | A0 G2 D2 B3"),  # 10
    ("D D/C# Bm D/A", "D0 . rG2+B3+e2 . | A4 G2 D0 B0 | A2 G4 D4 B3 | A0 G2 D0 B0"),  # 11
    ("G - A -", "E3 B0 G0 e3 | E3 B0 G0 e3 | A0 B2 G2 e0 | A0 B2 G2 e0"),  # 12
    ("D D/C# Bm -", "D0 . G2 B3 | A4 . D0 B3 | A2 G4 D4 B3 | A2 G4 D4 ."),  # 13
    ("G - A -", "E3 . D0 . | E3 B0 D0 G0 | A0 G2 D2 B2 | A0 G2 D2 B3"),  # 14
    ("D - C -", "D0+~B3 . rG2+B3+e2 . | D0 B3 G2 e0 | A3 G0 D2 e0 | A3 G0 D0 B0"),  # 15
    ("Bm - E -", "A2 G4 D4 B3 | A2 G4 D4 . | E0 G1 D2 e0 | E0 G1 D2 ."),  # 16
    ("A", "A0 . D2+G2+B2 . | . . . . | . . A0 . | A2 . A4 ."),  # 17
    # Strummed verse
    ("D - C -", "D0 . G2+B3+e2 . | A0 G2 G2+B3+e2 G2+B3+e2 | A3 . G0+B1+e0 . | E3 G0 G0+B1+e0 G0+B1+e0"),  # 18
    ("Bm", "A2 . G4+B3+e2 G4+B3+e2 | D4 G4 G4+B3+e2 G4+B3+e2 | A2 . G4+B3+e2 G4+B3+e2 | D4 G4 G4+B3+e2 G4+B3+e2"),  # 19
    ("E", "E0 . G1+B0+e0 G1+B0+e0 | A0 hA2 G1+B0+e0 G1+B0+e0 | E0 . G1+B0+e0 G1+B0+e0 | A0 hA2 G1+B0+e0 G1+B0+e0"),  # 20
    ("A", "A0 . G2+B2+e0 G2+B2+e0 | D2 G2 G2+B2+e0 G2+B2+e0 | A0 . G2+B2+e0 G2+B2+e0 | A2 . A4 ."),  # 21
    18,  # 22
    19,  # 23
    20,  # 24
    21,  # 25
    # Strummed chorus
    ("G - A -", "E3 . G0+B0+e3 . | A0 hA2 G0+B0+e3 G0+B0+e3 | A0 . G2+B2+e0 . | E0 G2 G2+B2+e0 G2+B2+e0"),  # 26
    ("D D/C# Bm -", "D0 . G2+B3+e2 . | A4 G2 G2+B3+e2 G2+B3+e2 | A2 . G4+B3+e2 G4+B3+e2 | D4 G4 G4+B3+e2 G4+B3+e2"),  # 27
    26,  # 28
    27,  # 29
    26,  # 30
    18,  # 31
    ("Bm - E -", "A2 . G4+B3+e2 G4+B3+e2 | D4 G4 G4+B3+e2 G4+B3+e2 | E0 . G1+B0+e0 G1+B0+e0 | A0 hA2 G1+B0+e0 G1+B0+e0"),  # 32
    ("A", "A0 . D2+G2+B2+e0 . | . . . . | . . A0 . | A2 . A4 ."),  # 33
    # Outro
    18,  # 34
    ("Bm", "A2 . G4+B3+e2 G4+B3+e2 | D4 G4 G4+B3+e2 G4+B3+e2 | A2 . G4+B3+e2 G4+B3+e2 | E2 G4 G4+B3+e2 G4+B3+e2"),  # 35
    ("E - A -", "E0 . G1+B0+e0 G1+B0+e0 | A0 hA2 G1+B0+e0 G1+B0+e0 | A0 . G2+B2+e0 G2+B2+e0 | E0 G2 G2+B2+e0 G2+B2+e0"),  # 36
    ("D", "D0 . G2+B3+e2 G2+B3+e2 | A0 G2 G2+B3+e2 G2+B3+e2 | D0 . A0 . | D0+G2+B3+e2 . . ."),  # 37
    ("D", "~D0+~G2+~B3+~e2 . . . | . . . . | . . . . | . . . ."),  # 38
)

STRING_NUMBER = {name: n for n, name in enumerate("eBGDAE", 1)}


def read_bar(number, chords, grid):
    beats = [group.split() for group in grid.split("|")]
    assert len(beats) == 4 and all(len(group) == 4 for group in beats), number
    columns = [value for group in beats for value in group]
    starts = [slot for slot, token in enumerate(columns) if token != "."]
    assert starts[0] == 0
    steps = []
    for slot, end in zip(starts, starts[1:] + [16]):
        token = columns[slot]
        tech = "hammer" if token.startswith("h") else ""
        rolled = token.startswith("r")
        if tech or rolled:
            token = token[1:]
        notes, ties = [], []
        for symbol in token.split("+"):
            target = ties if symbol.startswith("~") else notes
            note = symbol.removeprefix("~")
            string, fret = note[0], note[1:]
            assert string in STRING_NUMBER and fret.isdigit() and 0 <= int(fret) <= 24
            target.append((STRING_NUMBER[string], int(fret)))
        assert len({s for s, _ in notes + ties}) == len(notes + ties)
        assert not ties or slot == 0
        stroke = ""
        if rolled or (number >= 18 and len(notes) > 1):
            stroke = "up" if slot % 2 else "down"
        steps.append(Step(6 * (end - slot), tuple(notes), tech, stroke, tuple(ties)))
    names = chords.split()
    changes = tuple((i * 24, chord) for i, chord in enumerate(names) if i and chord != "-")
    return Bar(names[0], tuple(steps), changes)


BARS = []
for number, row in enumerate(ROWS, 1):
    if isinstance(row, int):
        assert 1 <= row < number
        BARS.append(BARS[row - 1])
    else:
        BARS.append(read_bar(number, *row))
