"""B-RoM's Gild the Lily guitar part, in printed bar order.

Durations use 24 ticks per quarter. Each fret is (string, fret, written pitch).
Guitar notation sounds an octave below the staff. A step without frets is a rest.
"""
from practice.notation import Bar, Step, EIGHTH, HALF, QUARTER, TRIPLET, WHOLE, hit


PRE_INTRO = (
    Bar("D", (
        hit(QUARTER, (1, 2, "F#5"), (4, 0, "D4")),
        hit(QUARTER, (3, 2, "A4")),
        hit(EIGHTH, (1, 2, "F#5"), (4, 0, "D4")),
        hit(3 * EIGHTH, (1, 3, "G5"), tech="hammer"),
    )),
    Bar("Am", (
        hit(QUARTER, (2, 1, "C5"), (5, 0, "A3")),
        hit(QUARTER, (4, 2, "E4")),
        hit(EIGHTH, (2, 1, "C5")),
        hit(EIGHTH, (3, 2, "A4")),
        hit(QUARTER, (4, 2, "E4")),
    )),
    Bar("G", (
        hit(EIGHTH, (3, 2, "A4"), (6, 3, "G3")),
        hit(EIGHTH, (3, 4, "B4")),
        hit(QUARTER, (6, 3, "G3")),
        hit(EIGHTH, (3, 4, "B4")),
        hit(QUARTER, (3, 2, "A4"), tech="pull"),
        hit(EIGHTH, (3, 2, "A4")),
    )),
    Bar("D", (
        hit(QUARTER, (4, 0, "D4")),
        hit(QUARTER, (4, 0, "D4")),
        hit(HALF, (3, 2, "A4"), (4, 0, "D4")),
    )),
    Bar("D", (
        hit(QUARTER, (4, 0, "D4")),
        hit(QUARTER, (4, 0, "D4")),
        hit(EIGHTH, (1, 2, "F#5"), (4, 0, "D4")),
        hit(3 * EIGHTH, (1, 3, "G5"), tech="hammer"),
    )),
    Bar("Am", (hit(HALF, (2, 1, "C5"), (5, 0, "A3")), hit(HALF, (2, 1, "C5")))),
    Bar("D", (hit(WHOLE, (4, 4, "F#4"), (5, 5, "D4")),)),
)


def opening_lick(slide_in=False):
    return Bar("D", (
        Step(QUARTER),
        hit(QUARTER, (1, 10, "D6"), pick="down", tech="slide in" if slide_in else ""),
        hit(EIGHTH, (1, 10, "D6"), pick="down"),
        hit(EIGHTH, (2, 10, "A5"), pick="up"),
        hit(EIGHTH, (2, 8, "G5"), pick="down"),
        hit(EIGHTH, (2, 7, "F#5"), pick="up"),
    ))


def answer(chord):
    return Bar(chord, (
        Step(EIGHTH),
        hit(QUARTER, (3, 7, "D5"), pick="up"),
        hit(QUARTER, (3, 5, "C5"), pick="up"),
        hit(EIGHTH, (4, 7, "A4"), pick="up"),
        hit(EIGHTH, (3, 5, "C5"), pick="down"),
        hit(EIGHTH, (2, 5, "E5"), pick="up"),
    ))


LOW_TURN = Bar("G", (
    Step(EIGHTH),
    hit(EIGHTH, (3, 7, "D5"), pick="up"),
    hit(EIGHTH, (3, 5, "C5"), tech="pull"),
    hit(EIGHTH, (4, 7, "A4"), pick="up"),
    hit(EIGHTH, (4, 5, "G4"), pick="down"),
    hit(EIGHTH, (5, 7, "E4"), pick="up"),
    hit(EIGHTH, (4, 5, "G4"), pick="down"),
    hit(EIGHTH, (5, 7, "E4"), pick="up"),
))
SLIDE_TO_NINE = hit(EIGHTH, (5, 9, "F#4"), tech="slide")
VIBRATO = hit(QUARTER, (3, 7, "D5"), tech="vibrato", pick="up")
LOW_END = Bar("D", (SLIDE_TO_NINE, VIBRATO, Step(HALF), Step(EIGHTH)))
REST_END = Bar("D", (Step(EIGHTH), VIBRATO, Step(HALF), Step(EIGHTH)))
PICKUP = Bar("D", (Step(EIGHTH), VIBRATO, Step(HALF), hit(EIGHTH, (4, 7, "A4"), pick="up")))
ASCENT = Bar("D", (
    hit(EIGHTH, (4, 10, "C5"), tech="slide"),
    hit(EIGHTH, (3, 9, "E5"), pick="up"),
    hit(QUARTER, (3, 11, "F#5"), tech="slide"),
    hit(EIGHTH, (1, 10, "D6"), pick="down"),
    hit(QUARTER, (1, 12, "E6"), pick="up"),
    hit(EIGHTH, (1, 14, "F#6"), pick="up"),
))


def silent(chord):
    return Bar(chord, (Step(WHOLE),))


def bent_fill(low_turn=False):
    twelves = ((1, 12, "E6"), (2, 12, "B5"))
    fourth_beat = ((3, 11, "F#5"),) if low_turn else twelves
    return Bar("D", (
        Step(QUARTER),
        hit(QUARTER, *twelves, tech="bend", pick="down"),
        hit(EIGHTH, *twelves, pick="down"),
        hit(EIGHTH, (2, 10, "A5"), pick="up"),
        hit(EIGHTH, *fourth_beat, pick="down"),
        hit(EIGHTH, (1, 10, "D6"), (2, 10, "A5"), pick="up"),
    ))


D_PAIR = Bar("D", (
    hit(HALF, (1, 10, "D6"), (3, 11, "F#5")),
    hit(HALF, (1, 5, "A5"), (3, 7, "D5")),
))
A_PAIR = Bar("A", (
    hit(HALF, (1, 9, "C#6"), (3, 9, "E5")),
    hit(HALF, (1, 5, "A5"), (3, 6, "C#5")),
))
SEVENS = (hit(WHOLE, (1, 7, "B5"), (3, 7, "D5")),)

BARS = (
    *PRE_INTRO,
    # 8–15
    opening_lick(slide_in=True), answer("Am"), LOW_TURN, LOW_END,
    opening_lick(slide_in=True), answer("C"), REST_END, silent("D"),
    # 16–23
    opening_lick(slide_in=True), answer("Am"), LOW_TURN,
    Bar("D", (
        SLIDE_TO_NINE, VIBRATO,
        hit(EIGHTH, (3, 9, "E5"), pick="up"),
        hit(EIGHTH, (2, 7, "F#5"), pick="down"),
        hit(EIGHTH, (2, 8, "G5"), pick="up"),
        hit(EIGHTH, (2, 10, "A5"), pick="down"),
        hit(EIGHTH, (1, 7, "B5"), pick="up"),
    )),
    opening_lick(), answer("C"), PICKUP, ASCENT,
    # 24–31
    silent("D"), silent("Am"), silent("G"), bent_fill(),
    silent("D"), silent("C"), silent("D"), bent_fill(low_turn=True),
    # 32–39
    silent("D"), silent("Am"), silent("G"), bent_fill(), silent("D"), silent("C"),
    Bar("D", (
        Step(HALF),
        hit(TRIPLET, (1, 9, "C#6"), pick="down"),
        hit(TRIPLET, (1, 10, "D6"), tech="hammer"),
        hit(TRIPLET, (1, 9, "C#6"), tech="pull"),
        hit(EIGHTH, (2, 12, "B5"), pick="down"),
        hit(EIGHTH, (2, 10, "A5"), pick="up"),
    )),
    Bar("", (
        hit(EIGHTH, (2, 12, "B5"), pick="down"),
        hit(EIGHTH, (2, 10, "A5"), pick="up"),
        hit(3, (3, 12, "G5"), pick="down"),       # thirty-second
        hit(9, (3, 9, "E5"), tech="slide"),      # dotted sixteenth
        hit(EIGHTH, (3, 7, "D5"), pick="up"),
        hit(EIGHTH, (3, 9, "E5"), pick="down"),
        hit(EIGHTH, (3, 7, "D5"), pick="up"),
        hit(EIGHTH, (4, 9, "B4"), pick="down"),
        hit(EIGHTH, (4, 7, "A4"), pick="up"),
    )),
    # 40–47
    Bar("Bm", (hit(WHOLE, (4, 9, "B4"), pick="down"),)),
    silent("Bm"), silent("F♯"), silent("F♯"),
    D_PAIR, A_PAIR, Bar("Bm", SEVENS), silent("Bm"),
    # 48–55
    D_PAIR, A_PAIR, Bar("Bm", SEVENS), silent("Bm"), D_PAIR,
    Bar("A", (
        hit(HALF, (1, 7, "B5"), (3, 7, "D5")),
        hit(HALF, (1, 2, "F#5"), (3, 4, "B4")),
    )),
    Bar("G", (hit(WHOLE, (1, 5, "A5"), (3, 0, "G4")),)), silent("G"),
    # 56–61
    D_PAIR, A_PAIR, Bar("G", SEVENS),
    Bar("G", (Step(HALF), Step(HALF)), changes=((HALF, "Gsus2/G♭"),)),
    Bar("Em", (
        Step(3 * EIGHTH),
        hit(EIGHTH, (1, 10, "D6"), pick="up"),
        hit(EIGHTH, (1, 7, "B5"), tech="pull"),
        hit(EIGHTH, (2, 10, "A5"), pick="up"),
        hit(EIGHTH, (2, 7, "F#5"), tech="pull"),
        hit(EIGHTH, (3, 9, "E5"), pick="up"),
    )),
    Bar("Em", (
        hit(EIGHTH, (3, 11, "F#5"), tech="slide"),
        hit(EIGHTH, (3, 9, "E5"), pick="up"),
        hit(EIGHTH, (3, 7, "D5"), pick="down"),
        hit(EIGHTH, (4, 9, "B4"), pick="up"),
        hit(HALF, (4, 7, "A4"), pick="down"),
    )),
    # 62–69
    opening_lick(slide_in=True), answer("Am"), LOW_TURN, LOW_END,
    opening_lick(), answer("C"), PICKUP, ASCENT,
)

# Practice groupings. The PDF numbers the bars without naming sections.
SECTIONS = (
    (1, 7, "Pre-intro"),
    (8, 23, "Intro lick"),
    (24, 39, "Verse fills"),
    (40, 61, "Chorus"),
    (62, 69, "Return to the lick"),
)
