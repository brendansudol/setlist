#!/usr/bin/env python3
"""Build dannys-song/index.html from the data in this file.

    python3 dannys-song/build.py

Standard library only. Every chord shape is checked against the note names it
should produce before any HTML is written, so a mistyped fret stops the build.

The lesson is three video files bought from the instructor's site. They are
not on this site and the page cannot play them, so every time on the page is
plain text: which video, and how far in. Each time here is a (video, seconds)
pair. There is no capo, so fret numbers are ordinary fret numbers.
"""
from html import escape
from pathlib import Path

VIDEOS = {
    0: dict(name="Play-through", file="01_dannys_song_playthru.mp4", length=260,
            what="The whole arrangement, played and sung."),
    1: dict(name="Part 1", file="02_dannys_song_part_1_lesson.mp4", length=881,
            what="Verses and choruses 1 and 2: the Travis-picked part, bar by bar."),
    2: dict(name="Part 2", file="03_dannys_song_part_2_lesson.mp4", length=658,
            what="Verses and choruses 3 and 4: the strummed version, then the outro."),
}


def mmss(t):
    return f"{t // 60}:{t % 60:02d}"


# ---------------------------------------------------------------- music data

NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
OPEN = [4, 9, 2, 7, 11, 4]  # pitch classes of strings 6 to 1, standard tuning
STRING = ["low E", "A", "D", "G", "B", "high E"]
FINGER = {"T": "Thumb", 1: "Index", 2: "Middle", 3: "Ring", 4: "Pinky"}
X = None  # a string that is not part of the shape

FAMILIES = {
    "open": "Open chord",
    "barre": "Barre chord",
    "slash": "D over a moving bass",
}

# frets and fingers run from string 6 (low E) to string 1 (high E).
# barre = (finger, first string index, last string index, fret)
# expect = the notes that should sound, low string to high
# tones = every note the chord name allows; bass = the lowest note
# used = where the shape appears, as shown on its card
# at = (video, seconds) where the lesson first deals with it
CHORDS = [
    dict(id="d", name="D", fam="open", at=(1, 11), used="Intro, verse, chorus and outro",
         frets=[X, X, 0, 2, 3, 2], fingers=[X, X, X, 1, 3, 2],
         expect="D A D F#", tones="D F# A", bass="D",
         where="Ordinary open D",
         tip="The home chord, and the one the picking pattern is taught on. "
             "It only has four strings, so the thumb works the D and G "
             "strings and the fingers take the top two. The instructor "
             "often lands on it a moment before its bar begins."),
    dict(id="c", name="C", fam="open", at=(1, 103), used="Verse, chorus and outro",
         frets=[X, 3, 2, 0, 1, 0], fingers=[X, 3, 2, X, 1, X],
         expect="C E G C E", tones="C E G", bass="C",
         where="Ordinary open C",
         tip="Two beats of it after D. The thumb drops to the A and D "
             "strings and each finger moves over one string. In the strummed "
             "version the second bass note is the low E string at fret 3, so "
             "the ring finger hops across to it."),
    dict(id="bm", name="Bm", fam="barre", at=(1, 150), used="Verse, chorus and outro",
         frets=[X, 2, 4, 4, 3, 2], fingers=[X, 1, 3, 4, 2, 1], barre=(1, 1, 5, 2),
         expect="B F# B D F#", tones="B D F#", bass="B",
         where="Barre at fret 2, root on the A string",
         tip="The only barre chord in the song, held for a whole bar in the "
             "verse. The thumb alternates between the A and D strings."),
    dict(id="e", name="E", fam="open", at=(1, 175), used="Verse, chorus and outro",
         frets=[0, 2, 2, 1, 0, 0], fingers=[X, 2, 3, 1, X, X],
         expect="E B E G# B E", tones="E G# B", bass="E",
         where="Ordinary open E",
         tip="A whole bar in the verse. The thumb alternates between the low "
             "E string and the D string. In the strummed version the second "
             "bass note is a hammer-on on the A string, from open to fret 2."),
    dict(id="a", name="A", fam="open", at=(1, 222), used="Verse, chorus and outro",
         frets=[X, 0, 2, 2, 2, 0], fingers=[X, X, 1, 2, 3, X],
         expect="A E A C# E", tones="A C# E", bass="A",
         where="Ordinary open A",
         tip="The bar that leads back to D. The lesson has a note on the B "
             "string at fret 3 over it in places, which the instructor gets "
             "by forming the D chord early. At the end of each chorus it is "
             "struck once and left to ring before the bass run."),
    dict(id="g", name="G", fam="open", at=(1, 413), used="Chorus",
         frets=[3, 2, 0, 0, 0, 3], fingers=[2, 1, X, X, X, 3],
         expect="G B D G B G", tones="G B D", bass="G",
         where="Ordinary open G",
         tip="Starts each line of the chorus, for two beats. In the strummed "
             "version the A string is hammered on from open to fret 2 as the "
             "second bass note."),
    dict(id="d-csharp", name="D/C#", fam="slash", at=(1, 469), used="Chorus",
         frets=[X, 4, 0, 2, 3, 2], fingers=[X, 4, X, 1, 3, 2],
         expect="C# D A D F#", tones="D F# A C#", bass="C#",
         where="D with the A string fretted at fret 4",
         tip="One beat. Keep the D chord and add the A string at fret 4. The "
             "instructor says you can let the top string go open if that "
             "helps you reach it. The finger shown for the bass note is a "
             "guess; use whichever reaches."),
    dict(id="d-a", name="D/A", fam="slash", at=(1, 485), used="Chorus",
         frets=[X, 0, 0, 2, 3, 2], fingers=[X, X, X, 1, 3, 2],
         expect="A D A D F#", tones="D F# A", bass="A",
         where="D with the open A string as its bass note",
         tip="One beat, at the end of the walk down. It is the plain D "
             "shape; only the thumb changes, starting on the open A string."),
]
C = {ch["id"]: ch for ch in CHORDS}

# One entry per chord change: (chord id, beats). Four beats to the bar.
INTRO = [("d", 4)]
VERSE = [("d", 2), ("c", 2), ("bm", 4), ("e", 4), ("a", 4)]
CHORUS = [("g", 2), ("a", 2), ("d", 1), ("d-csharp", 1), ("bm", 1), ("d-a", 1),
          ("g", 2), ("a", 2), ("d", 1), ("d-csharp", 1), ("bm", 2),
          ("g", 2), ("a", 2), ("d", 2), ("c", 2),
          ("bm", 2), ("e", 2), ("a", 4)]
OUTRO = [("d", 2), ("c", 2), ("bm", 4), ("e", 2), ("a", 2), ("d", 4)]
SECTIONS = [("intro", INTRO), ("verse", VERSE), ("chorus", CHORUS), ("outro", OUTRO)]

# One beat of the Travis pattern on D, in sixteenth notes: (string, who plays it).
# T = thumb, i = index, m = middle. The intro is this beat four times.
PICK_BEAT = [(4, "T"), (2, "i"), (3, "T"), (1, "m")]

# The two strumming shapes the lesson treats as interchangeable, one bar each,
# in sixteenth notes ("1 e & a 2 e & a ..."). T = thumb on a bass string,
# D = brush down, U = flick up, N = pick the G string (or flick up instead),
# . = nothing
STRUM_SPARSE = "T.D.TNDU" * 2
STRUM_BUSY = "T.DUTNDU" * 2

# The contents of each video, as (seconds, what happens)
CONTENTS = {
    0: [(0, "The whole song, picked for the first half and strummed for the second.")],
    1: [
        (11, "The intro: one bar of the pattern on D."),
        (60, "Bars 2 and 3: D to C, then Bm. Which finger takes which string."),
        (175, "Bar 4, E, and bar 5, A."),
        (266, "Bars 6 and 7: the second line, with a brush strum on D."),
        (344, "Bars 8 and 9, and the way into the chorus."),
        (409, "Chorus, bars 10 and 11: G to A, then the walk down from D."),
        (530, "Bars 12 and 13: the thumb changes strings."),
        (636, "Bars 14 and 15: G to A, then D to C."),
        (727, "Bars 16 and 17: Bm, E, the ringing A and the bass run."),
        (823, "Playing the whole song this way, and why part 2 exists."),
    ],
    2: [
        (14, "Verse 3, bars 18 and 19: the strum on D, C and Bm."),
        (128, "The two strum shapes, and why either will do."),
        (183, "Bars 20 and 21: E with a hammer-on, A and the bass run."),
        (281, "Chorus 3, bars 26 and 27: G with a hammer-on, A, the walk down."),
        (391, "Bars 30 to 33: the rest of the chorus."),
        (508, "How the song ends: verse chords once, then the outro."),
        (544, "The outro played, then broken down."),
    ],
}


# -------------------------------------------------------------------- checks

def sounding(ch):
    return [NOTES[(OPEN[i] + f) % 12] for i, f in enumerate(ch["frets"]) if f is not None]


def bass_of(ch):
    """(string index, fret) of the lowest string in the shape."""
    for i, f in enumerate(ch["frets"]):
        if f is not None:
            return i, f
    raise ValueError(ch["name"])


def check():
    assert len({ch["id"] for ch in CHORDS}) == len(CHORDS), "duplicate chord id"
    for ch in CHORDS:
        n = f"{ch['name']} ({ch['id']})"
        notes = sounding(ch)
        assert notes == ch["expect"].split(), f"{n}: got {notes}, expected {ch['expect']}"
        assert set(notes) <= set(ch["tones"].split()), f"{n}: note outside the chord: {notes}"
        assert notes[0] == ch["bass"], f"{n}: bass is {notes[0]}, expected {ch['bass']}"
        assert ch["fam"] in FAMILIES, f"{n}: unknown family"
        video, t = ch["at"]
        assert video in VIDEOS and 0 <= t < VIDEOS[video]["length"], f"{n}: timestamp outside the video"
        for i, (f, fg) in enumerate(zip(ch["frets"], ch["fingers"])):
            if f:
                assert fg in FINGER, f"{n}: string {6 - i} is fretted but has no finger"
            else:
                assert fg is None, f"{n}: string {6 - i} has a finger but no fret"
        if "barre" in ch:
            fg, a, b, fret = ch["barre"]
            assert all(ch["frets"][i] is not None and ch["frets"][i] >= fret
                       for i in range(a, b + 1)), f"{n}: barre crosses a string outside the shape"
            assert ch["frets"][a] == fret and ch["frets"][b] == fret, f"{n}: barre ends"
            assert all(ch["fingers"][i] == fg for i in range(a, b + 1)
                       if ch["frets"][i] == fret), f"{n}: barre finger mismatch"
    for name, seq in SECTIONS:
        beat = 0
        for cid, beats in seq:
            assert cid in C, f"unknown chord in the {name}: {cid}"
            assert beats in (1, 2, 4), f"{name}: chords last one beat, two beats or a bar"
            assert beats < 4 or beat % 4 == 0, f"{name}: a whole-bar chord starts on beat 1"
            assert beats != 2 or beat % 2 == 0, f"{name}: a two-beat chord starts on beat 1 or 3"
            beat += beats
        assert beat % 4 == 0, f"the {name} does not end on a bar line"
    used = {cid for _, seq in SECTIONS for cid, _ in seq}
    assert used == set(C), f"chords never used: {set(C) - used}"
    assert len(PICK_BEAT) == 4 and all(1 <= string <= 6 for string, _ in PICK_BEAT)
    for pattern in (STRUM_SPARSE, STRUM_BUSY):
        assert len(pattern) == 16 and set(pattern) <= set("TDUN."), "a strumming bar is sixteen slots"
    for video, entries in CONTENTS.items():
        times = [t for t, _ in entries]
        assert times == sorted(times) and times[-1] < VIDEOS[video]["length"], "contents out of order"


# ------------------------------------------------------------------ diagrams

CLOCK = ('<svg class="clock" viewBox="0 0 12 12" aria-hidden="true"><circle cx="6" cy="6" r="4.6"/>'
         '<path d="M6 3.4V6l1.8 1.2"/></svg>')


def when(at, label=None):
    """A moment in one of the lesson videos, as text. The videos are not on the
    site, so this is not a link: it tells the reader where to look in their copy."""
    video, t = at
    assert video in VIDEOS and 0 <= t < VIDEOS[video]["length"], f"timestamp outside the video: {at}"
    text = label or f'{VIDEOS[video]["name"]} at'
    return f'<span class="when">{CLOCK}<span>{escape(text)} <b>{mmss(t)}</b></span></span>'


def chordbox(ch):
    frets, fingers = ch["frets"], ch["fingers"]
    fretted = [f for f in frets if f]
    start = 1 if max(fretted) <= 4 else min(fretted)
    assert max(fretted) - start + 1 <= 4, f"{ch['name']}: does not fit in four frets"

    def sx(i):
        return 34 + 20 * i

    def ry(fret):
        return 44 + 32 * (fret - start + 1) - 16

    desc = []
    for i, f in enumerate(frets):
        if f is None:
            continue
        desc.append(f"string {6 - i} " + ("open" if f == 0 else f"fret {f}"))
    label = f"{ch['name']} chord diagram: " + ", ".join(desc)

    o = [f'<svg class="chordbox" viewBox="0 0 150 200" role="img" aria-label="{escape(label)}">']
    for k in range(5):
        y = 44 + 32 * k
        cls = "nut" if (k == 0 and start == 1) else "fret"
        o.append(f'<line class="{cls}" x1="34" y1="{y}" x2="134" y2="{y}"/>')
    widths = [2.2, 1.9, 1.6, 1.3, 1.1, 1.0]
    for i in range(6):
        cls = "string" + (" string-off" if frets[i] is None else "")
        o.append(f'<line class="{cls}" x1="{sx(i)}" y1="44" x2="{sx(i)}" y2="172" stroke-width="{widths[i]}"/>')
    if start > 1:
        o.append(f'<text class="startfret" x="22" y="64.0">{start}fr</text>')
    for i, f in enumerate(frets):
        if f is None:
            o.append(f'<text class="mk" x="{sx(i)}" y="35">×</text>')
        elif f == 0:
            o.append(f'<circle class="openring" cx="{sx(i)}" cy="30" r="4.5"/>')
    covered = set()
    if "barre" in ch:
        fg, a, b, fret = ch["barre"]
        y = ry(fret)
        o.append(f'<rect class="dot" x="{sx(a) - 8.5}" y="{y - 8.5}" width="{sx(b) - sx(a) + 17}" height="17" rx="8.5"/>')
        covered = {i for i in range(a, b + 1) if frets[i] == fret}
        held = sorted(covered)
        nx = sx(held[len(held) // 2]) if len(held) % 2 else (sx(held[len(held) // 2 - 1]) + sx(held[len(held) // 2])) / 2
        o.append(f'<text class="fn" x="{nx}" y="{y + 3.8}">{fg}</text>')
    for i, f in enumerate(frets):
        if not f or i in covered:
            continue
        y = ry(f)
        if fingers[i] == "T":
            o.append(f'<circle class="dot-t" cx="{sx(i)}" cy="{y}" r="8.5"/>')
            o.append(f'<text class="fn ft" x="{sx(i)}" y="{y + 3.8}">T</text>')
        else:
            o.append(f'<circle class="dot" cx="{sx(i)}" cy="{y}" r="8.5"/>')
            o.append(f'<text class="fn" x="{sx(i)}" y="{y + 3.8}">{fingers[i]}</text>')
    for i, f in enumerate(frets):
        if f is not None:
            o.append(f'<text class="nn" x="{sx(i)}" y="191">{NOTES[(OPEN[i] + f) % 12]}</text>')
    o.append("</svg>")
    return "".join(o)


def finger_rows(ch):
    groups = {}
    for i, (f, fg) in enumerate(zip(ch["frets"], ch["fingers"])):
        if f:
            groups.setdefault((fg, f), []).append(i)
    rows = []
    for (fg, f), strings in groups.items():
        barre = ch.get("barre")
        if barre and barre[0] == fg and barre[3] == f and barre[2] - barre[1] >= 2:
            where = f"barre, {STRING[barre[1]]} to {STRING[barre[2]]}"
        else:
            where = ", ".join(STRING[i] for i in strings)
        rows.append((FINGER[fg], where, f))
    opens = [STRING[i] for i, f in enumerate(ch["frets"]) if f == 0]
    if opens:
        rows.append(("Open", ", ".join(opens), 0))
    return "".join(f"<tr><td>{a}</td><td>{b}</td><td class='num'>{c}</td></tr>" for a, b, c in rows)


def card(ch):
    cid = ch["id"]
    return f'''
<article class="chord fam-{ch["fam"]}" id="chord-{cid}">
  <header>
    <h3>{ch["name"]}</h3>
    <p class="meta"><span class="tag">{FAMILIES[ch["fam"]]}</span><span>{escape(ch["used"])}</span></p>
    <p class="where">{escape(ch["where"])}</p>
  </header>
  <div class="chord-body">
    {chordbox(ch)}
    <table class="fingers">
      <thead><tr><th scope="col">Finger</th><th scope="col">String</th><th scope="col" class="num">Fret</th></tr></thead>
      <tbody>{finger_rows(ch)}</tbody>
    </table>
  </div>
  <p class="tip">{escape(ch["tip"])}</p>
  <footer>
    {when(ch["at"])}
    <label class="got" for="got-{cid}"><input type="checkbox" id="got-{cid}" data-got="{cid}"> I can play this</label>
  </footer>
</article>'''


def chips(seq):
    """A section as boxes: a narrow box is two beats, a wide one a whole bar.
    Two chords that last one beat each share a narrow box."""
    units, beat, i = [], 0, 0
    while i < len(seq):
        cid, beats = seq[i]
        if beats == 1:
            assert seq[i + 1][1] == 1, "one-beat chords come in pairs"
            units.append((beat, [cid, seq[i + 1][0]], 2))
            i += 2
        else:
            units.append((beat, [cid], beats))
            i += 1
        beat += units[-1][2]
    items = []
    for start, ids, beats in units:
        label = f"bar {start // 4 + 1}" if start % 4 == 0 else "beat 3"
        first = C[ids[0]]
        # a shared box jumps to the less familiar of its two chords
        target = next((C[i] for i in ids if C[i]["fam"] == "slash"), first)
        cls = f'fam-{target["fam"]}' + (" whole" if beats == 4 else "")
        if len(ids) == 2:
            name = (f'<span class="nm two">{first["name"]}<i></i>{C[ids[1]]["name"]}</span>')
        else:
            name = f'<span class="nm">{first["name"]}</span>'
        items.append(f'<li class="{cls}"><a href="#chord-{target["id"]}">'
                     f'<span class="bar">{label}</span>{name}</a></li>')
    return f'<ol class="loop">{"".join(items)}</ol>'


def pickgrid():
    """One bar of the Travis pattern on D: which string is plucked on each
    sixteenth note, and by which finger. No frets: the fretting hand holds D."""
    rows = [1, 2, 3, 4]
    names = {1: "high E", 2: "B", 3: "G", 4: "D"}
    counts = "1e&a2e&a3e&a4e&a"
    x0, step = 66, 18.6
    ys = {string: 24 + 20 * k for k, string in enumerate(rows)}
    label = ("One bar of the picking pattern on a D chord, in sixteenth notes. Each beat: "
             + ", ".join(f"{'thumb' if who == 'T' else 'index' if who == 'i' else 'middle'} on the {names[string]} string"
                         for string, who in PICK_BEAT) + ".")
    o = [f'<svg class="pick" viewBox="0 0 360 124" role="img" aria-label="{escape(label, quote=True)}">']
    for b in (1, 2, 3):
        x = x0 + step * 4 * b - step / 2
        o.append(f'<line class="beatline" x1="{x:.1f}" y1="12" x2="{x:.1f}" y2="116"/>')
    for string in rows:
        y = ys[string]
        o.append(f'<line class="string" x1="{x0 - 12}" y1="{y}" x2="{x0 + step * 15 + 12:.1f}" y2="{y}" stroke-width="1.2"/>')
        o.append(f'<text class="slab" x="{x0 - 18}" y="{y + 3.3}">{names[string]}</text>')
    for i in range(16):
        string, who = PICK_BEAT[i % 4]
        x, y = x0 + step * i, ys[string]
        if who == "T":
            o.append(f'<circle class="thumbdot" cx="{x:.1f}" cy="{y}" r="7.5"/>')
            o.append(f'<text class="thumblet" x="{x:.1f}" y="{y + 3.4}">T</text>')
        else:
            o.append(f'<circle class="fingerdot" cx="{x:.1f}" cy="{y}" r="7.5"/>')
            o.append(f'<text class="fingerlet" x="{x:.1f}" y="{y + 3.4}">{who}</text>')
        cls = "count count-beat" if counts[i].isdigit() else "count"
        o.append(f'<text class="{cls}" x="{x:.1f}" y="112">{escape(counts[i])}</text>')
    o.append("</svg>")
    return "".join(o)


def strum(pattern, chords, label):
    """One bar of the strumming hand as symbols, one slot per sixteenth note.
    See the legend next to STRUM_SPARSE for the letters. `chords` is a list
    of (slot, name) for the names written above the bar."""
    counts = "1e&a2e&a3e&a4e&a"
    x0, step = 26, 20.6
    o = [f'<svg class="groove" viewBox="0 0 360 96" role="img" aria-label="{escape(label, quote=True)}">']
    for b in (1, 2, 3):
        x = x0 + step * 4 * b - step / 2
        o.append(f'<line class="{"barline" if b == 2 else "beatline"}" x1="{x:.1f}" y1="22" x2="{x:.1f}" y2="90"/>')
    for slot, name in chords:
        o.append(f'<text class="groove-ch" x="{x0 + step * slot - 6:.1f}" y="15">{escape(name)}</text>')
    for i, (g, count) in enumerate(zip(pattern, counts)):
        x = x0 + step * i
        if g == "T":
            o.append(f'<circle class="thumbdot" cx="{x:.1f}" cy="46" r="7.5"/>')
            o.append(f'<text class="thumblet" x="{x:.1f}" y="49.4">T</text>')
        elif g == "D":
            o.append(f'<path class="stroke stroke-wide" d="M{x:.1f} 28V64M{x - 5.5:.1f} 58.5L{x:.1f} 64L{x + 5.5:.1f} 58.5"/>')
        elif g == "U":
            o.append(f'<path class="stroke" d="M{x:.1f} 60V34M{x - 4.5:.1f} 38.5L{x:.1f} 34L{x + 4.5:.1f} 38.5"/>')
        elif g == "N":
            o.append(f'<circle class="notedot" cx="{x:.1f}" cy="46" r="3.6"/>')
        cls = "count count-beat" if count.isdigit() else "count"
        o.append(f'<text class="{cls}" x="{x:.1f}" y="84">{escape(count)}</text>')
    o.append("</svg>")
    return "".join(o)


STRUM_KEY = (
    '<ul class="key">'
    '<li><svg class="key-ico" viewBox="0 0 24 24" aria-hidden="true"><circle class="thumbdot" cx="12" cy="12" r="8.5"/>'
    '<text class="thumblet" x="12" y="15.4">T</text></svg><span><b>Thumb</b> on one of the chord\'s two bass strings.</span></li>'
    '<li><svg class="key-ico" viewBox="0 0 24 24" aria-hidden="true"><path class="stroke stroke-wide" d="M12 3V21M7 16L12 21L17 16"/></svg>'
    '<span><b>Down:</b> a light brush with the backs of the fingernails.</span></li>'
    '<li><svg class="key-ico" viewBox="0 0 24 24" aria-hidden="true"><path class="stroke" d="M12 20V5M8 9L12 5L16 9"/></svg>'
    '<span><b>Up:</b> a flick with the index finger that catches the top string or two.</span></li>'
    '<li><svg class="key-ico" viewBox="0 0 24 24" aria-hidden="true"><circle class="notedot" cx="12" cy="12" r="4"/></svg>'
    '<span><b>A picked note</b> on the G string. The instructor says an up strum does just as well.</span></li>'
    '</ul>'
)


# ---------------------------------------------------------------------- page

CSS = r"""
:root {
  /* Layout: one reading column for a phone propped by the guitar. Chrome stays grey;
     the only colour is the three shape families, used the same way everywhere. */
  --bg: #eef1f4;
  --surface: #ffffff;
  --ink: #16202b;
  --muted: #566472;
  --line: #d3dae1;
  --open: #0c7a64;    /* open chords: D, C, E, A, G */
  --barre: #2459c4;   /* the one barre chord: Bm */
  --slash: #96560a;   /* D over a moving bass note: D/C#, D/A */
  --on-dot: #ffffff;
  --font-display: "Bricolage Grotesque", "Avenir Next", "Segoe UI", sans-serif;
  --font-body: "Atkinson Hyperlegible", "Helvetica Neue", Arial, sans-serif;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    color-scheme: dark;
    --bg: #10161d; --surface: #19212b; --ink: #e9eef3; --muted: #9aa8b6; --line: #2d3946;
    --open: #5ad0b3; --barre: #86adff; --slash: #f0b566; --on-dot: #10161d;
  }
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --bg: #10161d; --surface: #19212b; --ink: #e9eef3; --muted: #9aa8b6; --line: #2d3946;
  --open: #5ad0b3; --barre: #86adff; --slash: #f0b566; --on-dot: #10161d;
}
.fam-open  { --fam: var(--open); }
.fam-barre { --fam: var(--barre); }
.fam-slash { --fam: var(--slash); }

* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body {
  margin: 0; background: var(--bg); color: var(--ink);
  font: 400 16px/1.5 var(--font-body);
}
main { max-width: 760px; margin: 0 auto; padding: 28px 16px 56px; display: grid; gap: 44px; }
h1, h2, h3 { font-family: var(--font-display); text-wrap: balance; margin: 0; line-height: 1.1; }
h1 { font-size: clamp(2rem, 8vw, 3rem); font-weight: 800; letter-spacing: -0.02em; }
h2 { font-size: 1.5rem; font-weight: 700; letter-spacing: -0.01em; scroll-margin-top: 12px; }
p { margin: 0; max-width: 62ch; }
a { color: inherit; }
a:focus-visible, input:focus-visible { outline: 3px solid var(--barre); outline-offset: 2px; border-radius: 4px; }
section { display: grid; gap: 16px; }
.lede { font-size: 1.0625rem; color: var(--muted); }
.eyebrow { font-size: .8125rem; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); font-weight: 700; }
header.top { display: grid; gap: 12px; }

.facts { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1px; margin: 4px 0 0; background: var(--line); border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }
.facts div { background: var(--surface); padding: 10px 12px; }
.facts dt { font-size: .75rem; letter-spacing: .06em; text-transform: uppercase; color: var(--muted); font-weight: 700; }
.facts dd { margin: 2px 0 0; font-size: .9375rem; }

/* the chord map */
.part { display: grid; gap: 10px; }
.part-head { display: flex; flex-wrap: wrap; gap: 6px 12px; align-items: center; justify-content: space-between; }
.part-head h3 { font-size: 1.125rem; font-weight: 700; }
.loop { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; }
@media (min-width: 620px) { .loop { grid-template-columns: repeat(8, 1fr); } }
.loop a { display: grid; gap: 2px; padding: 8px 6px 10px 8px; text-decoration: none; background: var(--surface); border: 1px solid var(--line); border-bottom: 5px solid var(--fam); border-radius: 6px; }
.loop .bar { font-size: .6875rem; letter-spacing: .06em; color: var(--muted); font-variant-numeric: tabular-nums; }
.loop .nm { font: 700 1.125rem/1.1 var(--font-display); }
.loop .whole { grid-column: span 2; }  /* a chord that lasts the whole bar */
.loop .two { font-size: .9375rem; display: flex; flex-wrap: wrap; align-items: baseline; gap: 0 5px; }  /* two chords, a beat each */
.loop .two i { width: 3px; height: 3px; border-radius: 50%; background: var(--muted); align-self: center; }
.note { font-size: .9375rem; color: var(--muted); }

/* shape families */
.families { list-style: none; margin: 0; padding: 0; display: grid; gap: 10px; }
.families li { display: grid; grid-template-columns: 14px 1fr; gap: 10px; align-items: start; }
.families .sw { width: 14px; height: 14px; border-radius: 50%; background: var(--fam); margin-top: 5px; }
.families strong { font-family: var(--font-display); }
.readme { border-left: 3px solid var(--line); padding-left: 12px; color: var(--muted); font-size: .9375rem; }
.readme b { color: var(--ink); }

/* chord cards */
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(288px, 1fr)); gap: 14px; }
.chord { background: var(--surface); border: 1px solid var(--line); border-top: 6px solid var(--fam); border-radius: 8px; padding: 14px; display: grid; gap: 12px; align-content: start; scroll-margin-top: 12px; }
.chord header { display: grid; grid-template-columns: auto 1fr; column-gap: 12px; row-gap: 2px; align-items: baseline; }
.chord h3 { font-size: 2rem; font-weight: 800; }
.meta { display: flex; flex-wrap: wrap; gap: 4px 8px; align-items: center; font-size: .8125rem; color: var(--muted); }
.tag { color: var(--fam); font-weight: 700; border: 1.5px solid var(--fam); border-radius: 99px; padding: 0 8px; line-height: 1.5; white-space: nowrap; }
.where { grid-column: 1 / -1; font-size: .9375rem; }
.chord-body { display: flex; flex-wrap: wrap; gap: 12px; align-items: flex-start; }
.chordbox { width: 150px; height: auto; flex: 0 0 150px; display: block; }
.fingers { flex: 1 1 120px; border-collapse: collapse; font-size: .875rem; font-variant-numeric: tabular-nums; }
.fingers th { text-align: left; font-size: .6875rem; text-transform: uppercase; letter-spacing: .06em; color: var(--muted); font-weight: 700; padding: 0 6px 4px 0; }
.fingers td { padding: 5px 6px 5px 0; border-top: 1px solid var(--line); }
.fingers .num { text-align: right; padding-right: 0; font-weight: 700; }
.tip { font-size: .9375rem; color: var(--muted); }
.chord footer { display: flex; flex-wrap: wrap; gap: 10px 14px; align-items: center; justify-content: space-between; }
.when { display: inline-flex; align-items: center; gap: 7px; min-height: 34px; padding: 4px 13px 4px 10px; border: 1px solid var(--line); border-radius: 99px; background: var(--surface); color: var(--ink); font-size: .875rem; }
.when .clock { width: 12px; height: 12px; flex: none; fill: none; stroke: var(--muted); stroke-width: 1.3; stroke-linecap: round; }
.when b { font-variant-numeric: tabular-nums; }
.got { display: inline-flex; align-items: center; gap: 7px; min-height: 40px; font-size: .875rem; color: var(--muted); cursor: pointer; }
.got input { width: 20px; height: 20px; accent-color: var(--fam); margin: 0; }
.progress { font-size: .9375rem; color: var(--muted); }

/* diagrams */
svg text { font-family: var(--font-body); }
.string { stroke: var(--ink); }
.string-off { opacity: .28; }
.fret { stroke: var(--ink); stroke-width: 1; opacity: .38; }
.nut { stroke: var(--ink); stroke-width: 4; stroke-linecap: square; }
.dot { fill: var(--fam); }
.dot-t { fill: var(--surface); stroke: var(--fam); stroke-width: 2.5; }
.fn { fill: var(--on-dot); font-size: 10.5px; font-weight: 700; text-anchor: middle; }
.ft { fill: var(--ink); }
.startfret { fill: var(--ink); font-size: 11px; font-weight: 700; text-anchor: end; }
.nutlab { fill: var(--muted); font-size: 8.5px; text-anchor: middle; letter-spacing: .04em; }
.mk { fill: var(--muted); font-size: 13px; text-anchor: middle; }
.openring { fill: none; stroke: var(--ink); stroke-width: 1.6; }
.nn { fill: var(--muted); font-size: 10.5px; text-anchor: middle; }

/* figures: the picking pattern and the two strums */
figure { margin: 0; display: grid; gap: 10px; }
figcaption { font-size: .875rem; color: var(--muted); max-width: 62ch; }
.panel { background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 14px 10px; }
.groove, .pick { display: block; width: 100%; max-width: 560px; height: auto; margin: 0 auto; }
.pick .string { opacity: .35; }
.stroke { fill: none; stroke: var(--ink); stroke-width: 1.7; stroke-linecap: round; stroke-linejoin: round; opacity: .6; }
.stroke-wide { stroke-width: 3.2; opacity: 1; }
.thumbdot, .notedot { fill: var(--ink); }
.thumblet { fill: var(--bg); font-size: 9.5px; font-weight: 700; text-anchor: middle; }
.fingerdot { fill: var(--surface); stroke: var(--ink); stroke-width: 1.6; }
.fingerlet { fill: var(--ink); font-size: 10px; font-weight: 700; font-style: italic; text-anchor: middle; }
.count { fill: var(--muted); font-size: 10px; text-anchor: middle; }
.count-beat { fill: var(--ink); font-size: 11.5px; font-weight: 700; }
.groove-ch { fill: var(--ink); font-family: var(--font-display); font-size: 13px; font-weight: 700; }
.beatline { stroke: var(--ink); opacity: .1; }
.barline { stroke: var(--ink); opacity: .22; }
.slab { fill: var(--muted); font-size: 9px; text-anchor: end; }
.key { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 8px 16px; font-size: .9375rem; }
.key li { display: grid; grid-template-columns: 24px 1fr; gap: 10px; align-items: start; }
.key-ico { width: 24px; height: 24px; display: block; }
.bass { border-collapse: collapse; font-size: .9375rem; }
.bass th { text-align: left; font-size: .6875rem; text-transform: uppercase; letter-spacing: .06em; color: var(--muted); font-weight: 700; padding: 0 18px 4px 0; }
.bass td { padding: 6px 18px 6px 0; border-top: 1px solid var(--line); vertical-align: top; }
.videos { list-style: none; margin: 0; padding: 0; display: grid; gap: 1px; background: var(--line); border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }
.videos li { background: var(--surface); padding: 10px 12px; display: grid; gap: 2px; }
.videos b { font-family: var(--font-display); }
.videos span { font-size: .9375rem; color: var(--muted); }
.videos code { font-size: .8125rem; color: var(--muted); overflow-wrap: anywhere; }
.contents { display: grid; gap: 8px; }
.contents h3 { font-size: 1.125rem; font-weight: 700; }
.contents h3 span { font: 400 .9375rem/1 var(--font-body); color: var(--muted); margin-left: 6px; font-variant-numeric: tabular-nums; }
.chapters .row { display: grid; grid-template-columns: 3.4em 1fr; gap: 8px; }
.chapters .row .t { font-weight: 700; text-decoration: none; }
.linkrow { display: flex; flex-wrap: wrap; gap: 8px; }

.points { margin: 0; padding-left: 1.2em; display: grid; gap: 8px; max-width: 62ch; }


/* chapter list */
.chapters { list-style: none; margin: 0; padding: 0; border-top: 1px solid var(--line); }
.chapters li { display: grid; gap: 2px; padding: 10px 0; border-bottom: 1px solid var(--line); }
.chapters a { display: grid; grid-template-columns: 3.4em 1fr; gap: 8px; text-decoration: none; font-weight: 700; }
.chapters .t { font-variant-numeric: tabular-nums; text-decoration: underline; text-underline-offset: 3px; }
.chapters .what { padding-left: calc(3.4em + 8px); color: var(--muted); font-size: .9375rem; }
.steps { margin: 0; padding-left: 1.9em; display: grid; gap: 8px; max-width: 62ch; }
.source { font-size: .875rem; color: var(--muted); border-top: 1px solid var(--line); padding-top: 16px; display: grid; gap: 8px; }
@media (prefers-reduced-motion: no-preference) { html { scroll-behavior: smooth; } }
"""

JS = r"""
(function () {
  var boxes = Array.prototype.slice.call(document.querySelectorAll('input[data-got]'));
  var out = document.getElementById('progress');
  var KEY = 'dannys-song-shapes';
  var saved = {};
  try { saved = JSON.parse(localStorage.getItem(KEY) || '{}') || {}; } catch (e) { saved = {}; }
  function render() {
    var n = boxes.filter(function (b) { return b.checked; }).length;
    out.textContent = n === 0 ? 'Tick each shape off as you get it clean.'
      : n === boxes.length ? 'All ' + n + ' shapes ticked off. Time to set the thumb going under them.'
      : n + ' of ' + boxes.length + ' shapes ticked off.';
  }
  boxes.forEach(function (b) {
    b.checked = !!saved[b.getAttribute('data-got')];
    b.addEventListener('change', function () {
      saved[b.getAttribute('data-got')] = b.checked;
      try { localStorage.setItem(KEY, JSON.stringify(saved)); } catch (e) {}
      render();
    });
  });
  render();
})();
"""

NUMBER_WORDS = {8: "eight", 3: "three"}


def contents(video):
    v = VIDEOS[video]
    rows = "".join(
        f'<li><span class="row"><span class="t">{mmss(t)}</span><span>{escape(what)}</span></span></li>'
        for t, what in CONTENTS[video])
    return (f'<div class="contents"><h3>{v["name"]}<span>{mmss(v["length"])}</span></h3>'
            f'<ol class="chapters">{rows}</ol></div>')


def page():
    n = len(CHORDS)
    cards = "".join(card(ch) for ch in CHORDS)
    videos = "".join(
        f'<li><b>{v["name"]} <span>· {mmss(v["length"])}</span></b><span>{escape(v["what"])}</span><code>{v["file"]}</code></li>'
        for v in VIDEOS.values())
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Danny's Song Lesson Notes</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&amp;family=Bricolage+Grotesque:opsz,wght@12..96,600..800&amp;display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<main>

<header class="top">
  <p class="eyebrow">Guitar lesson notes</p>
  <h1>Danny's Song: a Travis pick, a strum, {NUMBER_WORDS[n]} shapes</h1>
  <p><a href="practice/index.html">Play and loop the 38-bar guitar tab →</a></p>
  <p class="lede">The guitar part to the Loggins &amp; Messina song as Jerry's Guitar Bar teaches it: Travis picking for the first two verses and choruses, an optional strummed version for the last two, and the chords under both. The lesson is a paid download, so this page cannot play it. Every time is written out for you to find in your own copy.</p>
  <dl class="facts">
    <div><dt>Key</dt><dd>D, in standard tuning. The lesson names the key but not the tuning; the chord shapes are the ordinary open ones.</dd></div>
    <div><dt>Capo</dt><dd>None</dd></div>
    <div><dt>Tempo</dt><dd>71 beats a minute, from the lesson's tab</dd></div>
    <div><dt>Counted in</dt><dd>Sixteenth notes: “1 e &amp; a”, four to the beat</dd></div>
  </dl>
</header>

<section aria-labelledby="h-videos">
  <h2 id="h-videos">The three videos</h2>
  <p>Times on this page name one of these and how far in to go. The file names are the ones in the lesson download.</p>
  <ul class="videos">{videos}</ul>
</section>

<section aria-labelledby="h-map">
  <h2 id="h-map">How the song is built</h2>
  <p>Four beats to the bar. A narrow box is two beats and a wide box is a whole bar. A box with two names has two chords, one beat each. Tap a box to jump to its shape; a box with two names goes to the less familiar one.</p>
  <div class="part">
    <div class="part-head"><h3>Intro</h3>{when((1, 11))}</div>
    {chips(INTRO)}
    <p class="note">One bar of the picking pattern on D.</p>
  </div>
  <div class="part">
    <div class="part-head"><h3>Verse</h3>{when((1, 60))}</div>
    {chips(VERSE)}
    <p class="note">These four bars are played twice to make a verse, eight bars in all.</p>
  </div>
  <div class="part">
    <div class="part-head"><h3>Chorus</h3>{when((1, 409))}</div>
    {chips(CHORUS)}
    <p class="note">Eight bars. In bar 2 the bass walks down under the D chord, a beat at a time: the open D string, then the A string at fret 4, at fret 2 and open. The instructor says to make sure you can hear it. Bar 4 starts the same walk and stops on Bm. The last bar is an A struck once and left to ring, then three bass notes climbing the A string back to D.</p>
  </div>
  <div class="part">
    <div class="part-head"><h3>Outro</h3>{when((2, 544))}</div>
    {chips(OUTRO)}
    <p class="note">The verse line, shortened so that E and A share a bar, with a firm last strum on D. The lesson's chord sheet gives E and A a bar each here; this follows the tab and what the instructor plays.</p>
  </div>
</section>

<section aria-labelledby="h-order">
  <h2 id="h-order">The whole song, in order</h2>
  <ol class="steps">
    <li>Intro.</li>
    <li>Verse 1 and chorus 1, picked.</li>
    <li>Verse 2 and chorus 2, picked the same way.</li>
    <li>Verse 3 and chorus 3, strummed.</li>
    <li>Verse 4 and chorus 4, strummed the same way.</li>
    <li>The four verse bars once more, with no singing.</li>
    <li>Outro.</li>
  </ol>
  <p class="note">The strummed half is the instructor's own idea, for variety. He says the guitar on the record keeps picking all the way through while other instruments join in, and that playing all four verses the picked way is just as good.</p>
  <div class="linkrow">{when((1, 823), "Picking it all: part 1 at")} {when((2, 508), "The ending: part 2 at")}</div>
</section>

<section aria-labelledby="h-pick">
  <h2 id="h-pick">The Travis pick</h2>
  <p>The first half of the song is one small pattern, kept going while the chords change under it. The thumb plays two strings in turn, steadily, and a finger plays in each gap.</p>
  <figure>
    <div class="panel">{pickgrid()}</div>
    <figcaption>The intro: one bar on a D chord. <b>T</b> is the thumb, which goes D string, G string, D string, G string without a break. <b>i</b> is the index finger on the B string and <b>m</b> the middle finger on the high E string. The instructor calls the strings out by number: 4, 2, 3, 1.</figcaption>
  </figure>
  <ul class="points">
    <li>Get the thumb even first. The instructor wants it to go like a metronome.</li>
    <li>D only has four strings, so the thumb takes the D and G strings and the fingers take the top two. On every other chord the thumb drops down a string or two and the fingers move over to follow it.</li>
    <li>The thumb's first string is the chord's root: the A string for C, Bm and A, the low E string for E and G.</li>
    <li>Changes come a touch early. The last note before a new chord is often an open string, and he tends to land on D before its bar begins.</li>
    <li>Some bars open with the bass note and a light brush down with the backs of the fingernails in place of the first two picked notes. It happens on D in the second line of the verse, and on G and D in the chorus.</li>
    <li>In the third bar of the chorus the thumb swaps its second string, going to the G string on both G and A.</li>
    <li>The top string picked is not always the same from one pass to the next. The instructor says it does not matter: any pattern you have already played on those chords will work.</li>
  </ul>
  <div class="linkrow">{when((1, 25), "The thumb: part 1 at")} {when((1, 85), "Which finger: part 1 at")} {when((1, 283), "The brush: part 1 at")} {when((1, 542), "The thumb swaps: part 1 at")} {when((1, 775), "The ringing A: part 1 at")}</div>
</section>

<section aria-labelledby="h-strum">
  <h2 id="h-strum">The strum</h2>
  <p>From verse 3 the chords stay the same and only the playing hand changes: the thumb still plays bass notes, and the fingers brush the strings instead of picking them. The lesson uses two shapes and treats them as interchangeable. The instructor's words are not to worry about exactly what the tab says on any of these bars.</p>
  {STRUM_KEY}
  <div class="part">
    <div class="part-head"><h3>The sparser one</h3>{when((2, 32))}</div>
    <figure>
      <div class="panel">{strum(STRUM_SPARSE, [(0, "D"), (8, "C")], "One bar, D then C: thumb, down, thumb, picked note, down, up, on each chord.")}</div>
      <figcaption>A bar of D then C. On each chord: thumb, brush down, thumb on the other bass string, a picked note, down, up.</figcaption>
    </figure>
  </div>
  <div class="part">
    <div class="part-head"><h3>The busier one</h3>{when((2, 103))}</div>
    <figure>
      <div class="panel">{strum(STRUM_BUSY, [(0, "Bm")], "One bar of B minor: thumb, down, up, thumb, picked note, down, up, twice.")}</div>
      <figcaption>A bar of Bm. The same thing with an extra up after the first brush.</figcaption>
    </figure>
  </div>
  <div class="part">
    <div class="part-head"><h3>Where the thumb goes</h3>{when((2, 128), "The two shapes: part 2 at")}</div>
    <p>Each chord has two bass notes, one for each thumb stroke in the figures above.</p>
    <table class="bass">
      <thead><tr><th scope="col">Chord</th><th scope="col">First</th><th scope="col">Second</th></tr></thead>
      <tbody>
        <tr><td>D</td><td>D string</td><td>A string, open. For D/C# it is the A string at fret 4.</td></tr>
        <tr><td>C</td><td>A string</td><td>Low E string at fret 3. The ring finger moves across.</td></tr>
        <tr><td>Bm</td><td>A string</td><td>D string</td></tr>
        <tr><td>E, G</td><td>Low E string</td><td>A string, hammered on from open to fret 2</td></tr>
        <tr><td>A</td><td>A string</td><td>D string in the verse, the open low E string in the chorus</td></tr>
      </tbody>
    </table>
    <p class="note">Each A bar ends with the same climb up the A string as before, frets 2 and 4. After the first line of a verse it leads to D. At the end of the verse it leads to G instead, and the instructor says it still works.</p>
    <div class="linkrow">{when((2, 183), "The hammer-on: part 2 at")} {when((2, 200), "A and the bass run: part 2 at")}</div>
  </div>
</section>

<section aria-labelledby="h-fam">
  <h2 id="h-fam">Three kinds of shape cover all {NUMBER_WORDS[n]}</h2>
  <ul class="families">
    <li class="fam-open"><span class="sw"></span><span><strong>Open chords.</strong> D, C, E, A and G. The lesson assumes you know them.</span></li>
    <li class="fam-barre"><span class="sw"></span><span><strong>Barre chord.</strong> Bm, at fret 2.</span></li>
    <li class="fam-slash"><span class="sw"></span><span><strong>D over a moving bass.</strong> D/C# and D/A are the D chord with a different string under the thumb. They only last a beat each.</span></li>
  </ul>
  <p class="readme"><b>Reading the diagrams:</b> the left line is the low E string and the right line is the high E. The thick line at the top is the nut. Numbers are fingers, 1 for index through 4 for pinky, and a bar across several strings is one finger laid flat. <b>×</b> marks a string that is not part of the shape and a ring marks an open string. The letters underneath are the notes that sound. Frets and strings come from the lesson's tab and what the instructor says. He does not say which finger goes where on these chords, so the finger numbers are the usual fingering.</p>
</section>

<section aria-labelledby="h-shapes">
  <h2 id="h-shapes">The shapes, in the order the song reaches them</h2>
  <p class="progress" id="progress" aria-live="polite">Tick each shape off as you get it clean.</p>
  <div class="cards">{cards}</div>
</section>

<section aria-labelledby="h-practice">
  <h2 id="h-practice">A practice order</h2>
  <ol class="steps">
    <li>Hold D and play the thumb alone, D string then G string, until it is even.</li>
    <li>Add the fingers in the gaps: B string, then high E string. That bar is the intro.</li>
    <li>Take the pattern through the verse chords, letting the thumb move to each chord's root.</li>
    <li>Learn the walk down in the chorus slowly: D, D/C#, Bm, D/A, one beat each.</li>
    <li>Follow part 1 bar by bar for the small changes, then play verse and chorus with the play-through.</li>
    <li>If you want the strummed half, start with thumb and a brush down on each chord, then add the rest.</li>
  </ol>
</section>

<section aria-labelledby="h-video">
  <h2 id="h-video">Find it in the videos</h2>
  {contents(0)}
  {contents(1)}
  {contents(2)}
</section>

<footer class="source">
  <p>Source: the Danny's Song lesson from <a href="https://www.jerrysguitarbar.com">Jerry's Guitar Bar</a>, a paid download of three videos, a tab and a chord sheet. None of those files are on this site, and the tab and the words of the song are not copied here.</p>
  <p>The diagrams were drawn for these notes and are not frames from the videos.</p>
</footer>

</main>
<script>{JS}</script>
</body>
</html>
'''


if __name__ == "__main__":
    check()
    out = Path(__file__).resolve().parent / "index.html"
    html = page()
    out.write_text(html, encoding="utf-8")
    print(f"checked {len(CHORDS)} shapes, wrote {out.name} ({len(html.encode('utf-8'))} bytes)")
