"""Practice bars from the three Six String Fingerpicking lessons.

The four small counts in the teacher's pattern fill one cut-time measure.
A backbeat contains both an unpitched thumb tap and a pitched index flick.
"""
from practice.notation import Bar, EIGHTH, QUARTER, WHOLE, hit

# (string, fret); 1 is high e. The thumb moves to string 5 for open A.
D = ((6, 10), (4, 12), (3, 11), (2, 10))
BM = ((6, 7), (4, 9), (3, 7), (2, 7))
FSM = ((6, 2), (4, 4), (3, 2), (2, 2))
G = ((6, 3), (4, 5), (3, 4), (2, 3))
D_FS = ((6, 2), (4, 0), (3, 2), (2, 3))
A_OPEN = ((5, 0), (4, 2), (3, 2), (2, 2))


def tap(duration, bass, flick):
    return hit(duration, (bass[0], "x"), flick, tech="mute")


def groove(name, bass, pinch, flick_two, after_two, after_three, flick_four):
    return Bar(name, (
        hit(QUARTER, bass, pinch), tap(EIGHTH, bass, flick_two), hit(EIGHTH, after_two),
        hit(EIGHTH, bass), hit(EIGHTH, after_three), tap(QUARTER, bass, flick_four),
    ))


def pattern(name, grip):
    bass, fourth, third, second = grip
    return groove(name, bass, second, third, second, fourth, third)


def four_counts(name, bass, upper):
    a, b, c, d = upper
    return Bar(name, (hit(QUARTER, bass, a), tap(QUARTER, bass, b),
                      hit(QUARTER, bass, c), tap(QUARTER, bass, d)))


VERSE_END = (pattern("F#m", FSM), pattern("G", G), pattern("D/F#", D_FS), pattern("A", A_OPEN))
VERSE = (
    pattern("D", D), four_counts("D", D[0], (D[3], D[2], (2, 12), D[2])),
    pattern("Bm", BM), four_counts("Bm", BM[0], (BM[3], BM[2], (2, 10), BM[2])),
    *VERSE_END,
)
MELODY = (
    VERSE[0], four_counts("D", D[0], ((2, 10), (2, 12), (1, 9), (1, 10))),
    VERSE[2], four_counts("Bm", BM[0], ((3, 9), (2, 7), (1, 7), (2, 10))),
    *VERSE_END,
)

# Follow the opening play-through: C#–D–E over A and F#–E–D over D.
CHORUS_A = groove("A", (6, 5), (3, 6), (4, 7), (3, 7), (2, 5), (3, 6))
CHORUS_D = groove("D", (5, 5), (2, 7), (3, 7), (2, 5), (3, 7), (3, 7))
G_SHORT = groove("G", G[0], G[2], G[1], G[3], G[1], G[3])
bass, fourth, third, second = G
G_FILL = (
    Bar("G", (hit(QUARTER, bass, third), tap(EIGHTH, bass, fourth), hit(EIGHTH, second),
              hit(EIGHTH, bass), hit(EIGHTH, fourth), tap(EIGHTH, bass, third), hit(EIGHTH, second))),
    Bar("G", (hit(EIGHTH, bass), hit(EIGHTH, fourth), tap(EIGHTH, bass, third), hit(EIGHTH, second),
              hit(EIGHTH, bass), hit(EIGHTH, fourth), tap(QUARTER, bass, third))),
)
CHORUS_LINE = (CHORUS_A, CHORUS_D, *G_FILL)
CHORUS = (
    *CHORUS_LINE, *CHORUS_LINE,
    CHORUS_A, CHORUS_D, G_SHORT, pattern("D/F#", D_FS), pattern("G", G),
    pattern("D/F#", D_FS), pattern("A", A_OPEN), pattern("D", D),
    Bar("D", (hit(WHOLE, D[0], D[3]),)),
)

# Open A and G continue under the moving D- and B-string pair.
OUTRO_FRETS = ((2, 2), (4, 3), (5, 5), (7, 7), (9, 8), (11, 10), (12, 12), (14, 14), (16, 15))
OUTRO = tuple(pattern("A7", ((5, 0), (4, d), (3, 0), (2, b)))
              for d, b in (*OUTRO_FRETS, *OUTRO_FRETS[-2:0:-1])) + (
    Bar("A7", (hit(WHOLE, (5, 0), (4, 2), (3, 0), (2, 2)),)),
)

LESSON = "https://sixstringfingerpicking.com/songs/the-heart-of-life-guitar-lesson/"
TAB = "https://www.musicnotes.com/sheetmusic/six-string-fingerpicking/the-heart-of-life-accompaniment-only/MN0218635"
INTRO_VIDEO = "dgEQvqHTQbw"
CHORUS_VIDEO = "i7CZnBemDs0"
OUTRO_VIDEO = "Tx6E2w73VcU"

PASSAGES = (
    ("Intro & verse", VERSE, INTRO_VIDEO, 191, "Learn the thumb tap"),
    ("Intro melody variation", MELODY, INTRO_VIDEO, 525, "Add the melody"),
    ("Chorus", CHORUS, CHORUS_VIDEO, 56, "Learn the chorus"),
    ("Outro", OUTRO, OUTRO_VIDEO, 113, "Learn the moving shapes"),
)
