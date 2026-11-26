"""Daniel Chavez's four tab examples. Onsets are sixteenths, shapes run low E to high e."""
from practice.notation import Bar, Step

CAPO, BPM = 1, 88
LESSON = "https://www.youtube.com/watch?v=Fzprg4riZIs"
SOURCE = "https://dc-guitar.com/artists/tupac-shakur/thugz-mansion"

G, BM7, AM7, CMAJ7, F7_C = "355433", ".24232", ".02010", ".35453", ".33545"
AM_PICK, BM_PICK, C_PICK = ".0201.", ".2423.", ".3545."
SLAP = "xxxxxx"


def measure(chord, attacks, changes=()):
    """Each attack is (sixteenth, six-string shape, optional articulation or stroke)."""
    starts = [slot for slot, *_ in attacks]
    assert starts[0] == 0 and starts == sorted(set(starts)) and starts[-1] < 16
    steps = []
    for (slot, shape, *mark), end in zip(attacks, starts[1:] + [16]):
        assert len(shape) == 6 and set(shape) <= set(".x0123456789")
        notes = tuple((6 - i, int(fret) if fret.isdigit() else fret)
                      for i, fret in enumerate(shape) if fret != ".")
        assert notes
        tech = "mute" if "x" in shape else ""
        pick = ""
        if mark and mark[0] in ("up", "down"):
            pick = mark[0]
        elif mark:
            tech = mark[0]
        steps.append(Step(6 * (end - slot), notes, tech, pick))
    return Bar(chord, tuple(steps), tuple((6 * slot, name) for slot, name in changes))


INTRO = (
    measure("G", [
        (0, "3....."), (2, "..543."), (4, SLAP), (6, "...433"),
        (8, "....1."), (9, "....0.", "pull"), (10, "...2.."), (11, "...0..", "pull"),
        (12, "..2..."), (14, "..0...", "pull"), (15, ".1...."),
    ], [(8, "Am")]),
    measure("Bm7", [
        (0, ".2....", "slide"), (2, "..423."), (4, SLAP), (6, "...232"),
        (8, "....3."), (10, "....5.", "hammer"), (12, "....55"), (14, "....33", "pull"),
    ]),
    measure("Am7", [
        (0, AM_PICK), (4, BM_PICK), (8, C_PICK),
        (12, "...23."), (13, "...45.", "slide"), (14, "...23.", "slide"),
    ], [(4, "Bm7"), (8, "Cmaj7")]),
    measure("Am7", [
        (0, AM_PICK), (4, BM_PICK), (8, "...434"), (9, "...545", "slide"),
        (10, "....1."), (11, "....0.", "pull"), (12, "...2.."), (13, "...0..", "pull"),
        (14, "..2..."), (15, "..0...", "pull"),
    ], [(4, "Bm7"), (8, "F7"), (10, "Am")]),
)

PICKED = (
    measure("G", [
        (0, "3....."), (2, "..543."), (4, SLAP), (6, "..543."),
        (10, "..544."), (12, SLAP), (14, "..0..."),
    ]),
    measure("Bm7", [
        (0, ".2...."), (2, "..423."), (4, SLAP), (6, "..423."),
        (10, "..423."), (12, SLAP), (14, "..0..."),
    ]),
    measure("Am7", [
        (0, AM_PICK), (4, BM_PICK), (8, C_PICK), (10, C_PICK), (12, SLAP), (14, "..0..."),
    ], [(4, "Bm7"), (8, "Cmaj7")]),
    measure("Am7", [
        (0, AM_PICK), (4, BM_PICK), (8, "..3545"), (10, "...545"), (12, SLAP), (14, "..0..."),
    ], [(4, "Bm7"), (8, "F7")]),
)

# The stroke line under the chord shapes applies until the next chord change.
FULL_STROKES = (0, 3, 4, 5, 6, 9, 10, 11, 12, 14, 15)
MOVING_STROKES = (0, 3, 4, 8, 9, 10, 11, 12, 14, 15)


def strummed(muted):
    bars = []
    for chord, shape, changes in (
        ("G", G, ()), ("Bm7", BM7, ()),
        ("Am7", AM7, ((4, "Bm7", BM7), (8, "Cmaj7", CMAJ7))),
        ("Am7", AM7, ((4, "Bm7", BM7), (8, "F7/C", F7_C))),
    ):
        dead = {14, 15} if changes else {4, 5, 10, 11, 14, 15}
        shapes = {slot: voicing for slot, _, voicing in changes}
        notes = []
        for slot in MOVING_STROKES if changes else FULL_STROKES:
            shape = shapes.get(slot, shape)
            stroke = "up" if slot % 2 else "down"
            notes.append((slot, "x....." if muted and slot in dead else shape, stroke))
        bars.append(measure(chord, notes, [(slot, name) for slot, name, _ in changes]))
    return tuple(bars)


# Each option is an alternative accompaniment for the same verse/chorus progression.
PASSAGES = (
    ("Intro / interlude", 14, INTRO),
    ("Option 1 · Fingerpicking", 463, PICKED),
    ("Option 2 · Strumming", 740, strummed(False)),
    ("Option 3 · Muted strumming", 957, strummed(True)),
)
