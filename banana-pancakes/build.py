#!/usr/bin/env python3
"""Build banana-pancakes/index.html from the data in this file.

    python3 banana-pancakes/build.py

Standard library only. Every chord shape is checked against the note names it
should produce before any HTML is written, so a mistyped fret stops the build.

There is no capo in this lesson, so fret numbers are ordinary fret numbers.
"""
from html import escape
from pathlib import Path

VIDEO_ID = "5-rVm6CdCaY"
VIDEO_LENGTH = 1298  # seconds


def yt(t):
    return f"https://youtu.be/{VIDEO_ID}?t={t}"


def mmss(t):
    return f"{t // 60}:{t % 60:02d}"


# ---------------------------------------------------------------- music data

NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
OPEN = [4, 9, 2, 7, 11, 4]  # pitch classes of strings 6 to 1, standard tuning
STRING = ["low E", "A", "D", "G", "B", "high E"]
FINGER = {"T": "Thumb", 1: "Index", 2: "Middle", 3: "Ring", 4: "Pinky"}
X = None  # a string that is not part of the shape

FAMILIES = {
    "ebarre": "Barre, root on the low E",
    "abarre": "Barre, root on the A string",
    "small": "Three-string grip",
}

# frets and fingers run from string 6 (low E) to string 1 (high E).
# barre = (finger, first string index, last string index, fret)
# expect = the notes that should sound, low string to high
# tones = every note the chord name allows; bass = the lowest note
# used = the parts of the song the shape appears in, as shown on its card
CHORDS = [
    dict(id="am7", name="Am7", fam="ebarre", t=305, used="Intro, verse, chorus and bridge",
         frets=[5, 7, 5, 5, 5, 5], fingers=[1, 3, 1, 1, 1, 1], barre=(1, 0, 5, 5),
         expect="A E G C E A", tones="A C E G", bass="A",
         where="Minor barre at fret 5 with the little finger left off",
         tip="The barre has to sound five strings on its own, which is what "
             "makes this one tricky. The instructor rolls his first finger "
             "slightly onto its side, and says some players press the second "
             "finger on top of the barre to help. It is the chord the riff "
             "lands on and the main chord of the chorus and bridge."),
    dict(id="g7", name="G7", fam="ebarre", t=356, used="Intro",
         frets=[3, 5, 3, 4, 3, 3], fingers=[1, 3, 1, 2, 1, 1], barre=(1, 0, 5, 3),
         expect="G D F B D G", tones="G B D F", bass="G",
         where="G barre at fret 3 with the little finger lifted",
         tip="Play the ordinary G barre and lift the little finger, so the D "
             "string sounds at the barre. That note is what makes it G7, so "
             "do not let the third finger mute it. The instructor is fairly "
             "sure the record has G7 after the riff, though Jack Johnson "
             "often plays a plain G."),
    dict(id="d7", name="D7", fam="small", t=497, used="The stabs, verse and bridge",
         frets=[X, 5, 4, 5, X, X], fingers=[X, 2, 1, 3, X, X],
         expect="D F# C", tones="D F# A C", bass="D",
         where="Three strings, with everything else muted",
         tip="Second finger on the A string at fret 5, first finger on the D "
             "string at fret 4, third finger on the G string at fret 5. The "
             "second finger also leans on the low E string to mute it, and "
             "the top two strings are muted. The instructor says this small "
             "grip is what Jack Johnson uses and sounds more like the record "
             "than a full D7."),
    dict(id="g", name="G", fam="ebarre", t=550, used="Verse, chorus and bridge",
         frets=[3, 5, 5, 4, 3, 3], fingers=[1, 3, 4, 2, 1, 1], barre=(1, 0, 5, 3),
         expect="G D G B D G", tones="G B D", bass="G",
         where="Ordinary G barre at fret 3",
         tip="The verse starts here. The record sometimes has G7 in the "
             "verse, but the instructor says Jack Johnson mostly plays a "
             "plain G when he plays it live."),
    dict(id="c7", name="C7", fam="abarre", t=570, used="Verse",
         frets=[X, 3, 5, 3, 5, 3], fingers=[X, 1, 3, 1, 4, 1], barre=(1, 1, 5, 3),
         expect="C G A# E G", tones="C E G A#", bass="C",
         where="C7 barre at fret 3",
         tip="The first finger also mutes the low E string. The instructor "
             "does not really hear the top string on the record, so it "
             "matters least. This is the chord that gets the busier rhythm "
             "at the end of each pass through the verse."),
    dict(id="d7-big", name="D7", fam="abarre", t=1085, used="Bridge",
         frets=[X, 5, 7, 5, 7, 5], fingers=[X, 1, 3, 1, 4, 1], barre=(1, 1, 5, 5),
         expect="D A C F# A", tones="D F# A C", bass="D",
         where="The C7 shape, two frets higher",
         tip="Only in the bridge, where it replaces the small D7. The "
             "instructor says the fuller chord is part of what lifts the "
             "bridge. Under it the thumb alternates between the A string and "
             "the D string."),
    dict(id="bm7", name="Bm7", fam="ebarre", t=1122, used="Bridge",
         frets=[7, 9, 7, 7, 7, 7], fingers=[1, 3, 1, 1, 1, 1], barre=(1, 0, 5, 7),
         expect="B F# A D F# B", tones="B D F# A", bass="B",
         where="The Am7 shape, two frets higher",
         tip="Two bars of it in the bridge. The thumb alternates between the "
             "low E string and the A string."),
    dict(id="em", name="Em", fam="abarre", t=1200, used="Bridge",
         frets=[X, 7, 9, 9, 8, 7], fingers=[X, 1, 3, 4, 2, 1], barre=(1, 1, 5, 7),
         expect="E B E G B", tones="E G B", bass="E",
         where="Minor barre at fret 7, root on the A string",
         tip="Half a bar in the bridge, before the bass note drops."),
    dict(id="em-dsharp", name="Em/D#", fam="abarre", t=1205, used="Bridge",
         frets=[X, 6, 9, 9, 8, X], fingers=[X, 1, 3, 4, 2, X],
         expect="D# B E G", tones="E G B D#", bass="D#",
         where="Em with the bass note one fret lower",
         tip="Keep the Em shape and move the bass note on the A string back "
             "from fret 7 to fret 6. The instructor says it feels as if it "
             "should drop two frets, but it is one, and the bass guitar on "
             "the record does the same. With the first finger reaching back "
             "the top string is hard to hold, so the diagram leaves it out; "
             "the lesson's notation keeps it."),
    dict(id="c", name="C", fam="abarre", t=1212, used="Bridge",
         frets=[X, 3, 5, 5, 5, X], fingers=[X, 1, 3, 3, 3, X], barre=(3, 2, 4, 5),
         expect="C G C E", tones="C E G", bass="C",
         where="C barre at fret 3",
         tip="One bar near the end of the bridge. The lesson's notation "
             "shows the A string and the three strings above it, so the top "
             "string is left out here."),
]
C = {ch["id"]: ch for ch in CHORDS}

# One entry per change: (what is played, beats). Four beats to the bar.
# "riff" is a bar of the riff; "stab" is the two D7 stabs on beats 3 and 4.
INTRO = [("riff", 4), ("am7", 4), ("riff", 4), ("g7", 4)]
VERSE = [("g", 2), ("d7", 2), ("am7", 2), ("c7", 2)]
CHORUS = [("am7", 4), ("riff", 4), ("g", 4), ("riff", 4)]
CHORUS_END = [("am7", 4), ("am7", 4), ("g", 4), ("g", 4)]
BRIDGE = [("am7", 4), ("am7", 4), ("d7-big", 4), ("d7-big", 4),
          ("bm7", 4), ("bm7", 4), ("em", 2), ("em-dsharp", 2), ("c", 4),
          ("g", 4), ("d7", 4), ("g", 4), ("g", 2), ("stab", 2)]
SECTIONS = [("intro", INTRO), ("verse", VERSE), ("chorus", CHORUS),
            ("end of the second chorus", CHORUS_END), ("bridge", BRIDGE)]

# One or two bars of the playing hand in eighth notes ("1 & 2 & 3 & 4 &").
# T = thumb on the chord's bass note, D = fingers flick down across the chord,
# U = first finger brushes up, X = a percussive hit with the playing hand,
# N = one note of the riff (which note is not recorded here),
# C = the chord struck once and left to ring, - = still ringing, . = nothing
VERSE_GROOVE = "T.D.T.D." "T.D.TUDU"
CHORUS_GROOVE = "TUXUTUXU"
RIFF_RHYTHM = "..NNNNNN" "N..C----"

# Where on the neck the single-note parts are played. Zones only: the notes of
# the riff are deliberately not in this file.
# zone = (letter, style, first fret, last fret, first string, last string),
# with strings counted from 0 (high E) to 5 (low E), the way tablature is drawn
RIFF_ZONES = [
    ("A", "zone-a", 3, 7, 4, 5),
    ("B", "zone-b", 5, 7, 3, 4),
]

# (seconds, the chapter title from the video's description, what happens in it)
CHAPTERS = [
    (0, "Guitar Cover", "The whole song, played and sung."),
    (194, "Lesson Welcome", "Why the song is harder than it looks, and why "
                            "he teaches the fingers version."),
    (233, "Riff", "The riff, counted slowly, then Am7 and G7."),
    (397, "Riff Variation", "The one-off change the first time the riff is "
                            "sung over."),
    (497, "Chord Stab", "The three-string D7 and the two stabs."),
    (550, "Verses & Chorus", "The verse chords, the bass-and-chord rhythm "
                             "and the little riff on the last C."),
    (852, "Rhythm", "The chorus groove: thumb, up, hit, up."),
    (976, "Playthrough Verses", "Verse and chorus played through."),
    (1054, "End of Verse 2 + Bridge", "The longer second chorus, then the "
                                      "bridge chords and the alternating bass."),
    (1227, "Song Structure & Details", "The rest of the song's order, and "
                                       "how to simplify it."),
]

# Where the lesson teaches each part. The "From" buttons on the page and the
# shortcuts next to the video both come from this.
PARTS = [("Riff", 233), ("Verse", 550), ("Chorus groove", 852), ("Bridge", 1085),
         ("Song order", 1227)]


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
        assert 0 <= ch["t"] < VIDEO_LENGTH, f"{n}: timestamp outside the video"
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
            assert cid in C or cid in ("riff", "stab"), f"unknown chord in the {name}: {cid}"
            assert beats in (2, 4), f"{name}: chords last two beats or a bar"
            assert beats == 2 or beat % 4 == 0, f"{name}: a whole-bar chord starts on beat 1"
            beat += beats
        assert beat % 4 == 0, f"the {name} does not end on a bar line"
    used = {cid for _, seq in SECTIONS for cid, _ in seq} - {"riff", "stab"}
    assert used == set(C), f"chords never used: {set(C) - used}"
    for pattern in (VERSE_GROOVE, CHORUS_GROOVE, RIFF_RHYTHM):
        assert len(pattern) in (8, 16) and set(pattern) <= set("TDUXNC-."), "a groove is eight or sixteen slots"
    for z in RIFF_ZONES:
        assert 1 <= z[2] <= z[3] <= 8 and 0 <= z[4] <= z[5] <= 5, f"zone {z[0]} is off the drawn neck"
    times = [t for t, _, _ in CHAPTERS]
    assert times == sorted(times) and times[-1] < VIDEO_LENGTH, "chapters out of order"
    assert all(0 <= t < VIDEO_LENGTH for _, t in PARTS), "a part starts outside the video"


# ------------------------------------------------------------------ diagrams

PLAY = '<svg class="play" viewBox="0 0 12 12" aria-hidden="true"><path d="M3 1.5v9l7.5-4.5z"/></svg>'


def moment(t, part):
    """Attributes for a timestamp link. It is an ordinary YouTube link; the
    script at the bottom of the page plays it in the docked player instead,
    and shows `part` as the name of what is playing."""
    assert 0 <= t < VIDEO_LENGTH, f"timestamp outside the video: {t}"
    return f'href="{yt(t)}" data-t="{t}" data-part="{escape(part, quote=True)}"'


def watch(t, label="Watch at", part=None):
    return (f'<a class="watch" {moment(t, part or label)}>{PLAY}'
            f'<span>{escape(label)} <b>{mmss(t)}</b></span></a>')


def from_part(name, label="From"):
    """The "From m:ss" button for a part of the lesson."""
    return watch(dict(PARTS)[name], label, name)


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
    {watch(ch["t"], part=ch["name"])}
    <label class="got" for="got-{cid}"><input type="checkbox" id="got-{cid}" data-got="{cid}"> I can play this</label>
  </footer>
</article>'''


def chips(seq):
    """A section as boxes: a narrow box is two beats, a wide one a whole bar."""
    items, beat = [], 0
    for cid, beats in seq:
        label = f"bar {beat // 4 + 1}" if beat % 4 == 0 else "beat 3"
        if cid == "riff":
            cls, href, name = "fam-none", "#h-riff", "riff"
        else:
            ch = C["d7" if cid == "stab" else cid]
            cls, href = f'fam-{ch["fam"]}', f'#chord-{ch["id"]}'
            name = "D7 ×2" if cid == "stab" else ch["name"]
        if beats == 4:
            cls += " whole"
        items.append(f'<li class="{cls}"><a href="{href}">'
                     f'<span class="bar">{label}</span><span class="nm">{name}</span></a></li>')
        beat += beats
    return f'<ol class="loop">{"".join(items)}</ol>'


def groove(pattern, chords, label):
    """The playing hand as symbols, one slot per eighth note. See the legend
    next to VERSE_GROOVE for the letters. `chords` is a list of (slot, name)
    for the names written above the bar."""
    n = len(pattern)
    counts = "1&2&3&4&" * (n // 8)
    x0, x1 = 26, 338
    step = (x1 - x0) / (n - 1)
    o = [f'<svg class="groove" viewBox="0 0 360 96" role="img" aria-label="{escape(label, quote=True)}">']
    for i in range(2, n, 2):
        x = x0 + step * i - step / 2
        o.append(f'<line class="{"barline" if i % 8 == 0 else "beatline"}" x1="{x:.1f}" y1="22" x2="{x:.1f}" y2="90"/>')
    for slot, name in chords:
        o.append(f'<text class="groove-ch" x="{x0 + step * slot - 6:.1f}" y="15">{escape(name)}</text>')
    for i, (g, count) in enumerate(zip(pattern, counts)):
        x = x0 + step * i
        if g == "T":
            o.append(f'<circle class="thumbdot" cx="{x:.1f}" cy="46" r="8.5"/>')
            o.append(f'<text class="thumblet" x="{x:.1f}" y="49.6">T</text>')
        elif g in "DC":
            o.append(f'<path class="stroke stroke-wide" d="M{x:.1f} 26V66M{x - 6:.1f} 60L{x:.1f} 66L{x + 6:.1f} 60"/>')
            if g == "C":
                run = len(pattern[i + 1:]) - len(pattern[i + 1:].lstrip("-"))
                o.append(f'<path class="ring" d="M{x + 10:.1f} 46H{x0 + step * (i + run) + 6:.1f}"/>')
        elif g == "U":
            o.append(f'<path class="stroke" d="M{x:.1f} 60V34M{x - 4.5:.1f} 38.5L{x:.1f} 34L{x + 4.5:.1f} 38.5"/>')
        elif g == "X":
            o.append(f'<path class="hit" d="M{x - 6:.1f} 40L{x + 6:.1f} 52M{x + 6:.1f} 40L{x - 6:.1f} 52"/>')
        elif g == "N":
            o.append(f'<circle class="notedot" cx="{x:.1f}" cy="46" r="4"/>')
        cls = "count count-beat" if count.isdigit() else "count"
        o.append(f'<text class="{cls}" x="{x:.1f}" y="84">{escape(count)}</text>')
    o.append("</svg>")
    return "".join(o)


def neckmap():
    """The first eight frets, with the zones the single-note parts use. No notes."""
    lo, hi = 1, 8
    x0, x1 = 58, 352
    fw = (x1 - x0) / (hi - lo + 1)
    ys = [34 + 18 * i for i in range(6)]  # high E at the top, as in tablature
    names = ["high E", "B", "G", "D", "A", "low E"]
    widths = [1.0, 1.1, 1.3, 1.6, 1.9, 2.2]

    def fx(f):
        return x0 + fw * (f - lo)

    label = ("Fretboard from the nut to fret 8 with two zones marked. "
             + " ".join(f"Zone {z[0]}: frets {z[2]} to {z[3]}, {names[z[4]]} string to {names[z[5]]} string."
                        for z in RIFF_ZONES)
             + " The open low E string is also marked.")
    o = [f'<svg class="neck" viewBox="0 0 360 150" role="img" aria-label="{escape(label, quote=True)}">']
    o.append(f'<rect class="board" x="{x0}" y="{ys[0] - 8}" width="{x1 - x0}" height="{ys[5] - ys[0] + 16}" rx="3"/>')
    for f in range(lo + 1, hi + 2):
        o.append(f'<line class="fret" x1="{fx(f):.1f}" y1="{ys[0] - 8}" x2="{fx(f):.1f}" y2="{ys[5] + 8}"/>')
    o.append(f'<line class="nut" x1="{x0}" y1="{ys[0] - 8}" x2="{x0}" y2="{ys[5] + 8}"/>')
    for f in range(lo, hi + 1):
        o.append(f'<text class="fnum" x="{fx(f) + fw / 2:.1f}" y="18">{f}</text>')
    for f in (3, 5, 7):
        o.append(f'<circle class="inlay" cx="{fx(f) + fw / 2:.1f}" cy="{(ys[2] + ys[3]) / 2}" r="3"/>')
    for i, y in enumerate(ys):
        o.append(f'<line class="string" x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke-width="{widths[i]}"/>')
        o.append(f'<text class="slab" x="{x0 - 20}" y="{y + 3.3}">{names[i]}</text>')
    o.append(f'<circle class="openring" cx="{x0 - 10}" cy="{ys[5]}" r="4.5"/>')
    for letter, cls, f1, f2, s1, s2 in RIFF_ZONES:
        x, w = fx(f1) + 2, fx(f2 + 1) - fx(f1) - 4
        y, h = ys[s1] - 7, ys[s2] - ys[s1] + 14
        o.append(f'<rect class="{cls}" x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="6"/>')
        bx, by = (x + w - 9, y + 9) if letter == "B" else (x + 9, y + h - 9)
        o.append(f'<circle class="zbadge" cx="{bx:.1f}" cy="{by}" r="7"/>')
        o.append(f'<text class="zlet" x="{bx:.1f}" y="{by + 3.6}">{letter}</text>')
    o.append("</svg>")
    return "".join(o)


GROOVE_KEY = (
    '<ul class="key">'
    '<li><svg class="key-ico" viewBox="0 0 24 24" aria-hidden="true"><circle class="thumbdot" cx="12" cy="12" r="8.5"/>'
    '<text class="thumblet" x="12" y="15.6">T</text></svg><span><b>Thumb</b> on the chord\'s bass note.</span></li>'
    '<li><svg class="key-ico" viewBox="0 0 24 24" aria-hidden="true"><path class="stroke stroke-wide" d="M12 3V21M7 16L12 21L17 16"/></svg>'
    '<span><b>Down:</b> the fingers flick down across the chord.</span></li>'
    '<li><svg class="key-ico" viewBox="0 0 24 24" aria-hidden="true"><path class="stroke" d="M12 20V5M8 9L12 5L16 9"/></svg>'
    '<span><b>Up:</b> the first finger brushes back up.</span></li>'
    '<li><svg class="key-ico" viewBox="0 0 24 24" aria-hidden="true"><path class="hit" d="M6 6L18 18M18 6L6 18"/></svg>'
    '<span><b>Hit:</b> the playing hand lands on the strings. No chord sounds.</span></li>'
    '<li><svg class="key-ico" viewBox="0 0 24 24" aria-hidden="true"><circle class="notedot" cx="12" cy="12" r="4"/></svg>'
    '<span><b>A riff note.</b> The dots show when the notes fall, not which notes they are.</span></li>'
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
  --ebarre: #2459c4;  /* barre with its root on the low E string: Am7, G7, G, Bm7 */
  --abarre: #a52d76;  /* barre with its root on the A string: C7, D7, Em, Em/D#, C */
  --small: #96560a;   /* the three-string D7 */
  --on-dot: #ffffff;
  --font-display: "Bricolage Grotesque", "Avenir Next", "Segoe UI", sans-serif;
  --font-body: "Atkinson Hyperlegible", "Helvetica Neue", Arial, sans-serif;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    color-scheme: dark;
    --bg: #10161d; --surface: #19212b; --ink: #e9eef3; --muted: #9aa8b6; --line: #2d3946;
    --ebarre: #86adff; --abarre: #f090c8; --small: #f0b566; --on-dot: #10161d;
  }
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --bg: #10161d; --surface: #19212b; --ink: #e9eef3; --muted: #9aa8b6; --line: #2d3946;
  --ebarre: #86adff; --abarre: #f090c8; --small: #f0b566; --on-dot: #10161d;
}
.fam-ebarre { --fam: var(--ebarre); }
.fam-abarre { --fam: var(--abarre); }
.fam-small  { --fam: var(--small); }
.fam-none   { --fam: var(--muted); }  /* a bar of the riff in the song map */

* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body {
  margin: 0; background: var(--bg); color: var(--ink);
  font: 400 16px/1.5 var(--font-body);
}
main { max-width: 760px; margin: 0 auto; padding: 28px 16px 56px; display: grid; gap: 44px; }
h1, h2, h3 { font-family: var(--font-display); text-wrap: balance; margin: 0; line-height: 1.1; }
h1 { font-size: clamp(2rem, 8vw, 3rem); font-weight: 800; letter-spacing: -0.02em; }
h2 { font-size: 1.5rem; font-weight: 700; letter-spacing: -0.01em; scroll-margin-top: calc(var(--player-h, 0px) + 12px); /* a section jumped to lands below the open video */ }
p { margin: 0; max-width: 62ch; }
a { color: inherit; }
a:focus-visible, input:focus-visible { outline: 3px solid var(--ebarre); outline-offset: 2px; border-radius: 4px; }
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
.loop .whole { grid-column: span 2; }  /* something that lasts the whole bar */
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
.chord { background: var(--surface); border: 1px solid var(--line); border-top: 6px solid var(--fam); border-radius: 8px; padding: 14px; display: grid; gap: 12px; align-content: start; scroll-margin-top: calc(var(--player-h, 0px) + 12px); /* a box tapped in the song map lands below the open video */ }
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
.watch { display: inline-flex; align-items: center; gap: 7px; min-height: 40px; padding: 6px 14px 6px 12px; border-radius: 99px; background: var(--ink); color: var(--bg); text-decoration: none; font-size: .875rem; }
.watch .play { width: 11px; height: 11px; fill: currentColor; flex: none; }
.watch b { font-variant-numeric: tabular-nums; }
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

/* figures: the grooves and the map of the riff */
figure { margin: 0; display: grid; gap: 10px; }
figcaption { font-size: .875rem; color: var(--muted); max-width: 62ch; }
.panel { background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 14px 10px; }
.groove, .neck { display: block; width: 100%; max-width: 560px; height: auto; margin: 0 auto; }
.stroke { fill: none; stroke: var(--ink); stroke-width: 1.7; stroke-linecap: round; stroke-linejoin: round; opacity: .6; }
.stroke-wide { stroke-width: 3.2; opacity: 1; }
.hit { fill: none; stroke: var(--ink); stroke-width: 2.6; stroke-linecap: round; }
.thumbdot, .notedot { fill: var(--ink); }
.thumblet { fill: var(--bg); font-size: 9.5px; font-weight: 700; text-anchor: middle; }
.ring { fill: none; stroke: var(--ink); stroke-width: 1.4; stroke-dasharray: 2 3.5; stroke-linecap: round; opacity: .55; }
.count { fill: var(--muted); font-size: 10px; text-anchor: middle; }
.count-beat { fill: var(--ink); font-size: 11.5px; font-weight: 700; }
.groove-ch { fill: var(--ink); font-family: var(--font-display); font-size: 13px; font-weight: 700; }
.beatline { stroke: var(--ink); opacity: .1; }
.barline { stroke: var(--ink); opacity: .4; }
.key { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 8px 16px; font-size: .9375rem; }
.key li { display: grid; grid-template-columns: 24px 1fr; gap: 10px; align-items: start; }
.key-ico { width: 24px; height: 24px; display: block; }
.neck .board { fill: var(--ink); opacity: .05; }
.neck .string { opacity: .45; }
.neck .nut { stroke-width: 4; }
.inlay { fill: var(--ink); opacity: .2; }
.fnum { fill: var(--muted); font-size: 9px; text-anchor: middle; font-variant-numeric: tabular-nums; }
.slab { fill: var(--muted); font-size: 9px; text-anchor: end; }
.zone-a { fill: var(--ink); opacity: .13; }
.zone-b { fill: none; stroke: var(--ink); stroke-width: 1.8; stroke-dasharray: 5 3.5; }
.zbadge { fill: var(--ink); }
.zlet { fill: var(--bg); font-size: 9.5px; font-weight: 700; text-anchor: middle; }
.bass { border-collapse: collapse; font-size: .9375rem; }
.bass th { text-align: left; font-size: .6875rem; text-transform: uppercase; letter-spacing: .06em; color: var(--muted); font-weight: 700; padding: 0 18px 4px 0; }
.bass td { padding: 6px 18px 6px 0; border-top: 1px solid var(--line); }
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

/* The lesson video. Hidden until a timestamp is tapped; after that it stays on screen
   while the page scrolls, so the video and a diagram are visible together. Where it
   sits depends on the width of the window:
     under 700px   a band across the top: the video, then a row of controls
     from 700px    the same band, with the controls beside the video
     from 1100px   a box in the right margin; the reading column slides left to make
                   room, and the page keeps the whole height of the window
   The script moves the page itself when the video opens and closes, so the browser's
   own scroll anchoring is turned off to stop the two corrections adding up. */
html, body { overflow-anchor: none; }
.player { position: sticky; top: 0; z-index: 5; background: var(--surface); border-bottom: 1px solid var(--line); box-shadow: 0 4px 16px rgb(0 0 0 / .14); }
.player[hidden] { display: none; }
.player-in { max-width: 760px; margin: 0 auto; }
.player-frame { position: relative; width: min(100%, calc(42vh * 16 / 9)); aspect-ratio: 16 / 9; margin: 0 auto; background: #000; }
.player-frame iframe { position: absolute; inset: 0; width: 100%; height: 100%; border: 0; }
.player-msg { position: absolute; inset: 0; z-index: 1; display: grid; place-content: center; justify-items: center; gap: 8px; padding: 16px; text-align: center; background: #000; color: #fff; font-size: .9375rem; }
.player-msg[hidden] { display: none; }
.player-msg a { color: #fff; font-weight: 700; }
.player-bar { display: flex; align-items: center; gap: 8px; padding: 6px 8px 6px 14px; }
.player-title { flex: 1 1 0; min-width: 0; font-weight: 700; font-size: .9375rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.pbtn { flex: none; min-width: 44px; min-height: 40px; padding: 0 12px; border: 1px solid var(--line); border-radius: 99px; background: transparent; color: var(--ink); font: 700 .8125rem/1 var(--font-body); font-variant-numeric: tabular-nums; cursor: pointer; -webkit-tap-highlight-color: transparent; }
.pbtn[aria-pressed="true"] { background: var(--ink); border-color: var(--ink); color: var(--bg); }
.pbtn:disabled { opacity: .45; cursor: default; }
.pbtn:focus-visible { outline: 3px solid var(--ebarre); outline-offset: 2px; }
.pbtn-x { width: 40px; min-width: 40px; padding: 0; }
.pbtn-x svg { display: block; width: 12px; height: 12px; margin: 0 auto; }
.player-jumps { display: none; }  /* section shortcuts: only where there is room for them */

@media (min-width: 700px) {
  /* The controls sit beside the video, so the band is only as tall as the video. */
  .player-in { display: grid; grid-template-columns: auto minmax(0, 1fr); padding: 0 16px; }
  .player-frame { width: min(54vw, calc(42vh * 16 / 9)); margin: 0; }
  .player-bar { display: grid; grid-template-columns: auto auto minmax(0, 1fr) auto; grid-template-rows: auto 1fr auto; gap: 10px 8px; padding: 12px 0 12px 20px; }
  .player-title { grid-column: 1 / 4; grid-row: 1; font: 700 1.25rem/1.15 var(--font-display); white-space: normal; }
  .pbtn-x { grid-column: 4; grid-row: 1; align-self: start; }
  .player-jumps { grid-column: 1 / -1; grid-row: 2; align-self: start; display: flex; flex-wrap: wrap; gap: 6px; }
  .player-jumps a { display: inline-flex; align-items: center; min-height: 32px; padding: 0 11px; border: 1px solid var(--line); border-radius: 99px; color: var(--muted); font-size: .8125rem; font-weight: 700; text-decoration: none; }
  .player-jumps a:hover { color: var(--ink); border-color: var(--ink); }
  #player-speed { grid-column: 1; grid-row: 3; }
  #player-loop { grid-column: 2; grid-row: 3; }
}
@media (min-width: 700px) and (min-height: 600px) { .player-frame { width: min(54vw, calc(34vh * 16 / 9)); } }  /* on a tall window, leave more room for the cards */

@media (min-width: 1100px) {
  /* The video leaves the reading column for a box on the right. --rail is its width:
     whatever the window has left over once the column has its full 760px, between
     340px and 600px, and never so tall that the controls under it leave the screen.
     --col is the column's width and --edge the margin left on each side of the pair. */
  :root {
    --rail: min(clamp(340px, calc(100vw - 784px), 600px), calc((100vh - 220px) * 16 / 9));
    --col: min(760px, calc(100vw - var(--rail) - 24px));
    --edge: calc((100vw - var(--col) - var(--rail) - 8px) / 2);
  }
  :root.dock-open main { max-width: var(--col); margin-left: var(--edge); margin-right: 0; }
  .player { position: fixed; top: 16px; right: var(--edge); width: var(--rail); max-height: calc(100vh - 32px); overflow: hidden auto; border: 1px solid var(--line); border-radius: 12px; box-shadow: 0 8px 28px rgb(0 0 0 / .2); }
  .player-in { display: block; max-width: none; padding: 0; }
  .player-frame { width: 100%; }
  .player-bar { padding: 14px 12px 14px 16px; }
}
@media print { .player { display: none; } }
"""

PLAYER = f'''
<aside class="player" id="player" aria-label="Lesson video" hidden>
  <div class="player-in">
    <div class="player-frame">
      <div id="player-video"></div>
      <div class="player-msg" id="player-msg" hidden><span id="player-msg-text"></span><a id="player-msg-link" href="https://youtu.be/{VIDEO_ID}">Open this part on YouTube</a></div>
    </div>
    <div class="player-bar">
      <p class="player-title" id="player-title" aria-live="polite"></p>
      <nav class="player-jumps" aria-label="Jump to a section">{"".join(f'<a {moment(t, name)}>{escape(name)}</a>' for name, t in PARTS)}</nav>
      <button type="button" class="pbtn" id="player-speed">1×</button>
      <button type="button" class="pbtn" id="player-loop" aria-pressed="false" disabled>Loop from here</button>
      <button type="button" class="pbtn pbtn-x" id="player-close" aria-label="Close the video"><svg viewBox="0 0 12 12" aria-hidden="true"><path d="M2 2l8 8M10 2l-8 8" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg></button>
    </div>
  </div>
</aside>
'''

PLAYER_JS = r"""
(function () {
  // Timestamp links are ordinary YouTube links. This turns a tap on one into "play
  // that moment in the video docked on this page". Nothing is requested from YouTube
  // until the first tap, and if the player cannot load the links go back to being links.
  var VIDEO = '__VIDEO__';   // the page's lesson video
  var LABELS = __LABELS__;   // {video id: "Part 1", ...} on a page whose lesson is split across videos
  var dock = document.getElementById('player');
  // Opened from disk there is no referrer and YouTube refuses to embed, so do nothing.
  if (!dock || location.protocol === 'file:' || !Element.prototype.closest) return;
  var root = document.documentElement;
  var page = document.querySelector('main');
  var titleEl = document.getElementById('player-title');
  var msgEl = document.getElementById('player-msg');
  var msgText = document.getElementById('player-msg-text');
  var msgLink = document.getElementById('player-msg-link');
  var speedBtn = document.getElementById('player-speed');
  var loopBtn = document.getElementById('player-loop');
  var closeBtn = document.getElementById('player-close');
  var RATES = [1, 0.75, 0.5];
  var player = null, ready = false, loading = false, dead = false;
  var want = 0, wantVid = VIDEO, curVid = null, switching = false;
  var rate = 1, loopA = null, loopB = null, loopTimer = null, slowTimer = null;
  var calm = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);

  function mmss(t) {
    t = Math.max(0, Math.floor(t));
    var s = t % 60;
    return Math.floor(t / 60) + ':' + (s < 10 ? '0' : '') + s;
  }
  function now() {
    try { return player.getCurrentTime() || 0; } catch (e) { return want; }
  }
  // The dock is a band across the top that pushes the page down or, in a wide
  // window, a box fixed in the right margin that covers nothing at the top.
  function bandHeight() {
    if (dock.hidden || getComputedStyle(dock).position !== 'sticky') return 0;
    return dock.getBoundingClientRect().height;
  }
  function measure() { root.style.setProperty('--player-h', Math.round(bandHeight()) + 'px'); }
  function scrollByY(dy, smooth) {
    if (!dy) return;
    try { window.scrollBy({ top: dy, left: 0, behavior: smooth && !calm ? 'smooth' : 'instant' }); }
    catch (e) { window.scrollBy(0, dy); }
  }
  // Something in the page that is on screen now, to hold steady while the layout changes.
  function probe() {
    var r = page.getBoundingClientRect();
    var x = r.left + Math.min(120, r.width / 2);
    for (var y = bandHeight() + 16; y < window.innerHeight; y += 40) {
      var el = document.elementFromPoint(x, y);
      if (el && el !== page && page.contains(el) && el.getBoundingClientRect().height < window.innerHeight) return el;
    }
    return page;
  }
  // Change the layout, then scroll so that `ref` is where it was on screen before.
  function hold(ref, change) {
    var before = ref.getBoundingClientRect().top;
    change();
    measure();
    scrollByY(ref.getBoundingClientRect().top - before, false);
  }
  function say(text) {
    msgText.textContent = text;
    msgLink.href = 'https://youtu.be/' + wantVid + '?t=' + Math.floor(want);
    msgEl.hidden = false;
  }
  function hush() { msgEl.hidden = true; }

  function openDock(origin) {
    // A tap inside the dock itself (a section shortcut) has no card to bring into view.
    var anchor = origin && !dock.contains(origin) ? (origin.closest('.chord, .part, .addon') || origin) : null;
    if (dock.hidden) {
      hold(anchor || probe(), function () {  // the page is rearranged: keep it where it was
        dock.hidden = false;
        root.classList.add('dock-open');
      });
    }
    if (anchor) {
      var under = anchor.getBoundingClientRect().top - (bandHeight() + 8);
      if (under < 0) scrollByY(under, true);  // bring the tapped card out from under the dock
    }
  }
  function closeDock() {
    loopOff();
    if (ready) { try { player.pauseVideo(); } catch (e) {} }
    hold(probe(), function () {
      dock.hidden = true;
      root.classList.remove('dock-open');
    });
  }

  function play(t, part, vid) {
    want = t;
    wantVid = vid || VIDEO;
    titleEl.textContent = (part ? part + ' · ' : '') + (LABELS[wantVid] ? LABELS[wantVid] + ', ' : '') + mmss(t);
    loopOff();
    if (ready) show();
    else if (!loading) load();
  }
  // Play `want` in `wantVid`, loading that video first if a different one is in the player.
  function show() {
    if (wantVid !== curVid) {
      curVid = wantVid;
      switching = true;  // a newly loaded video may reset the speed: put it back once it plays
      player.loadVideoById({ videoId: wantVid, startSeconds: want });
    } else {
      player.seekTo(want, true);
      player.playVideo();
    }
  }
  function load() {
    loading = true;
    say('Loading the video…');
    window.onYouTubeIframeAPIReady = build;
    var s = document.createElement('script');
    s.src = 'https://www.youtube.com/iframe_api';
    s.onerror = giveUp;
    document.head.appendChild(s);
    slowTimer = setTimeout(function () {
      if (!ready && !dead) say('The video is taking a while to load.');
    }, 10000);
  }
  function build() {
    curVid = wantVid;
    player = new YT.Player('player-video', {
      host: 'https://www.youtube-nocookie.com',
      videoId: curVid,
      playerVars: { start: Math.floor(want), autoplay: 1, playsinline: 1, rel: 0 },
      events: {
        onReady: function () {
          ready = true;
          clearTimeout(slowTimer);
          hush();
          loopBtn.disabled = false;
          if (rate !== 1) player.setPlaybackRate(rate);
          show();
        },
        onError: giveUp,
        onStateChange: function (e) {
          if (e.data !== 1 || !switching) return;
          switching = false;
          if (player.getPlaybackRate() !== rate) player.setPlaybackRate(rate);
        },
        onPlaybackRateChange: function (e) { if (!switching) { rate = e.data; paintSpeed(); } }
      }
    });
  }
  function giveUp() {
    dead = true;  // from here on the timestamps open YouTube, as they do without this script
    loopOff();
    loopBtn.disabled = true;
    clearTimeout(slowTimer);
    say('The video could not be played here.');
  }

  function paintSpeed() {
    speedBtn.textContent = rate + '×';
    speedBtn.setAttribute('aria-label', 'Playback speed ' + rate + '×. Tap to change.');
  }
  speedBtn.addEventListener('click', function () {
    rate = RATES[(RATES.indexOf(rate) + 1) % RATES.length];
    paintSpeed();
    if (ready) player.setPlaybackRate(rate);
  });

  // One button, three presses: mark the start, mark the end (the loop begins), stop.
  function paintLoop() {
    var on = loopB !== null;
    loopBtn.setAttribute('aria-pressed', on ? 'true' : 'false');
    if (on) {
      loopBtn.textContent = mmss(loopA) + '–' + mmss(loopB);
      loopBtn.setAttribute('aria-label', 'Looping ' + mmss(loopA) + ' to ' + mmss(loopB) + '. Tap to stop.');
    } else {
      loopBtn.textContent = loopA !== null ? 'Loop to here' : 'Loop from here';
      loopBtn.removeAttribute('aria-label');
    }
  }
  function loopOff() {
    loopA = loopB = null;
    clearInterval(loopTimer);
    loopTimer = null;
    paintLoop();
  }
  function loopTick() {
    if (!ready || loopB === null) return;
    var t = now(), ended = false;
    try { ended = player.getPlayerState() === 0; } catch (e) {}
    if (ended || t >= loopB || t < loopA - 1) {
      player.seekTo(loopA, true);
      if (ended) player.playVideo();
    }
  }
  loopBtn.addEventListener('click', function () {
    if (!ready) return;
    var t = now();
    if (loopB !== null) { loopOff(); return; }
    if (loopA === null) { loopA = t; paintLoop(); return; }
    if (t < loopA) { loopB = loopA; loopA = t; } else { loopB = t; }
    if (loopB - loopA < 2) loopB = loopA + 2;
    paintLoop();
    player.seekTo(loopA, true);
    player.playVideo();
    loopTimer = setInterval(loopTick, 200);
  });

  document.addEventListener('click', function (e) {
    if (dead || e.defaultPrevented || e.button || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    var a = e.target.closest('a[data-t]');
    if (!a) return;
    e.preventDefault();
    openDock(a);
    play(parseFloat(a.getAttribute('data-t')), a.getAttribute('data-part'), a.getAttribute('data-v'));
  });
  closeBtn.addEventListener('click', closeDock);
  window.addEventListener('resize', function () { if (!dock.hidden) measure(); });
  paintSpeed();
  paintLoop();
})();
""".replace("__VIDEO__", VIDEO_ID).replace("__LABELS__", "{}")

JS = r"""
(function () {
  var boxes = Array.prototype.slice.call(document.querySelectorAll('input[data-got]'));
  var out = document.getElementById('progress');
  var KEY = 'banana-pancakes-shapes';
  var saved = {};
  try { saved = JSON.parse(localStorage.getItem(KEY) || '{}') || {}; } catch (e) { saved = {}; }
  function render() {
    var n = boxes.filter(function (b) { return b.checked; }).length;
    out.textContent = n === 0 ? 'Tick each shape off as you get it clean.'
      : n === boxes.length ? 'All ' + n + ' shapes ticked off. Time to put the grooves under them.'
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

NUMBER_WORDS = {10: "ten", 3: "three"}


def page():
    n = len(CHORDS)
    cards = "".join(card(ch) for ch in CHORDS)
    chapters = "".join(
        f'<li><a {moment(t, title)}><span class="t">{mmss(t)}</span><span class="ct">{escape(title)}</span></a>'
        f'<span class="what">{escape(what)}</span></li>'
        for t, title, what in CHAPTERS)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Banana Pancakes Lesson Notes</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&amp;family=Bricolage+Grotesque:opsz,wght@12..96,600..800&amp;display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
{PLAYER}
<main>

<header class="top">
  <p class="eyebrow">Guitar lesson notes</p>
  <h1>Banana Pancakes: a riff, two grooves, {NUMBER_WORDS[n]} shapes</h1>
  <p class="lede">How Jack Johnson's song is put together, worked out from Justin's 22-minute JustinGuitar lesson: where each chord falls, what the playing hand does, and where the riff sits. Tap any time on this page to play that moment of the lesson. The video stays on screen while you read, and the lesson's own notation and tab are on screen in it.</p>
  <dl class="facts">
    <div><dt>Tuning</dt><dd>Standard. The lesson does not say so, but the frets it shows only make these chords in standard tuning.</dd></div>
    <div><dt>Capo</dt><dd>None</dd></div>
    <div><dt>Played with</dt><dd>Fingers: the thumb on the bass strings and the first finger for the brushes. The instructor says it works the same with a pick.</dd></div>
    <div><dt>Level</dt><dd>Intermediate to upper intermediate, in the instructor's words</dd></div>
  </dl>
</header>

<section aria-labelledby="h-map">
  <h2 id="h-map">How the song is built</h2>
  <p>Four beats to the bar. A narrow box is two beats and a wide box is a whole bar. Tap a chord to jump to its shape, or a riff box to jump to the riff.</p>
  <div class="part">
    <div class="part-head"><h3>Intro</h3>{watch(233, "From", "Intro")}</div>
    {chips(INTRO)}
    <p class="note">The riff runs into Am7, then again into G7. These four bars come round twice: once on their own, and once under the first line of singing. After that, two D7 stabs on beats 3 and 4 lead into the verse.</p>
  </div>
  <div class="part">
    <div class="part-head"><h3>Verse</h3>{from_part("Verse")}</div>
    {chips(VERSE)}
    <p class="note">Two beats a chord, round and round. The lesson does not say how many times. On the last pass the C gets a short riff of its own that leads into the chorus.</p>
  </div>
  <div class="part">
    <div class="part-head"><h3>Chorus</h3>{from_part("Chorus groove")}</div>
    {chips(CHORUS)}
    <p class="note">The groove and the riff take turns, a bar each: Am7, riff, G, riff. The first chorus ends by staying on the chord and hitting the two D7 stabs.</p>
  </div>
  <div class="part">
    <div class="part-head"><h3>The end of the second chorus</h3>{watch(1054, "From", "End of the second chorus")}</div>
    {chips(CHORUS_END)}
    <p class="note">The second chorus is longer. Instead of stopping it keeps bouncing between Am7 and G, two bars each, with the groove and no riff, and that carries it into the bridge.</p>
  </div>
  <div class="part">
    <div class="part-head"><h3>Bridge</h3>{from_part("Bridge")}</div>
    {chips(BRIDGE)}
    <p class="note">Bars 1 to 4 are played twice, as the instructor talks it through. The D7 in bars 3 and 4 is the big one; the D7 in bar 10 and the stabs at the end are the small one. In bar 7 the bass drops one fret under the Em. The whole bridge uses the chorus groove, with the thumb swapping between two bass strings.</p>
  </div>
</section>

<section aria-labelledby="h-groove">
  <h2 id="h-groove">The two grooves</h2>
  <p>The instructor's advice is to learn these before the riff, and to keep the playing hand moving and loose. Each slot below is an eighth note, counted “1 &amp; 2 &amp; 3 &amp; 4 &amp;”.</p>
  {GROOVE_KEY}
  <div class="part">
    <div class="part-head"><h3>Verse: bass, chord, bass, chord</h3>{watch(601, "Watch at", "Verse groove")}</div>
    <figure>
      <div class="panel">{groove(VERSE_GROOVE, [(0, "G"), (4, "D7"), (8, "Am7"), (12, "C7")], "Two bars of the verse: thumb then a down flick on each chord, and thumb, up, down, up on the C7.")}</div>
      <figcaption>One pass of the verse. Each chord is a thumbed bass note on the beat and a flick down on the next beat. The C7 is busier: thumb, up, down, up.</figcaption>
    </figure>
    <p class="note">The short, clipped sound comes from the fretting hand. Press the chord as you play it and relax the pressure straight after, without lifting off the strings. The instructor calls it pumping the chord and plays it both ways to show the difference.</p>
    <div class="linkrow">{watch(617, "The pump at", "Pumping the chord")} {watch(653, "The C7 rhythm at", "The C7 rhythm")}</div>
  </div>
  <div class="part">
    <div class="part-head"><h3>Chorus and bridge: thumb, up, hit, up</h3>{from_part("Chorus groove", "Watch at")}</div>
    <figure>
      <div class="panel">{groove(CHORUS_GROOVE, [(0, "Am7")], "One bar of the chorus groove: thumb, up, hit, up, twice.")}</div>
      <figcaption>One bar of the chorus. Thumb, up, hit, up, twice in every bar. The ups are a light brush with the first finger.</figcaption>
    </figure>
    <p class="note">Here the hit comes from the playing hand landing on the strings, not from the fretting hand letting go. He also changes chord a touch early. Practise it slowly until the order is automatic, then work on keeping it relaxed.</p>
    <div class="linkrow">{watch(870, "The hit at", "The hit")} {watch(941, "Changing early at", "Changing chord early")}</div>
  </div>
  <div class="part">
    <div class="part-head"><h3>In the bridge the bass alternates</h3>{watch(1143, "Watch at", "Alternating bass")}</div>
    <p>The groove stays the same, but the two thumb notes in each bar are on different strings. The instructor says Jack Johnson always does this on acoustic, and that it is up to you whether to pick it out.</p>
    <table class="bass">
      <thead><tr><th scope="col">Chord</th><th scope="col">Beat 1</th><th scope="col">Beat 3</th></tr></thead>
      <tbody>
        <tr><td>Am7, Bm7</td><td>low E string</td><td>A string</td></tr>
        <tr><td>D7</td><td>A string</td><td>D string</td></tr>
        <tr><td>Em, then Em/D#</td><td>A string, fret 7</td><td>A string, fret 6</td></tr>
        <tr><td>C</td><td>A string</td><td>A string</td></tr>
      </tbody>
    </table>
  </div>
</section>

<section aria-labelledby="h-riff">
  <h2 id="h-riff">The riff</h2>
  <p>A guide to how the lesson teaches the riff: where on the neck it sits, when its notes fall and how the instructor fingers it. It is not a transcription. The lesson shows the riff in notation and tab on screen, and each button here puts that moment in the player.</p>
  <figure>
    <div class="panel">{neckmap()}</div>
    <figcaption>The first eight frets, drawn the way tablature is, with the high E string at the top. <b>A</b> is where the riff lives: the low E and A strings between frets 3 and 7. The ring marks the open low E string, which the riff also uses. <b>B</b>, the dashed box, is the short riff on the last C of the verse.</figcaption>
  </figure>
  <figure>
    <div class="panel">{groove(RIFF_RHYTHM, [(2, "riff"), (11, "Am7")], "Two bars: six riff notes from beat 2, one more on beat 1 of the next bar, then the chord struck once just after beat 2 and left to ring.")}</div>
    <figcaption>When the notes fall. The riff starts on beat 2 with six eighth notes and lands on a seventh note on beat 1 of the next bar. The chord is then struck once, just after beat 2, and rings to the end of the bar.</figcaption>
  </figure>
  <ul class="points">
    <li>The thumb plays every note of the riff. For the chord the instructor flicks down with the nail of his first finger, to get a crisper sound.</li>
    <li>It moves by sliding. He starts with the third finger on the low E string and uses the first finger on the A string, and says Jack Johnson seems to play all of it with the first finger. Either is fine.</li>
    <li>The first time the riff is sung over, and only then, a few of its notes change. The instructor admits he played that version all the way through for years.</li>
    <li>In the chorus the riff bar starts with one bass note on beat 1, then the same six notes.</li>
    <li>The last C of each verse has a riff of its own, in zone B. He says it outlines a C6 and that he often forgets it when he is singing.</li>
  </ul>
  <div class="linkrow">{from_part("Riff", "The riff at")} {watch(265, "Counted at", "The riff, counted")} {watch(397, "The variation at", "The riff variation")} {watch(780, "The C riff at", "The riff on the last C")}</div>
</section>

<section aria-labelledby="h-order">
  <h2 id="h-order">The whole song, in order</h2>
  <ol class="steps">
    <li>Intro: the riff into Am7, then into G7.</li>
    <li>The same four bars under the first line of singing, with the riff's one-off variation, then two D7 stabs.</li>
    <li>Verse 1. The last C gets its little riff.</li>
    <li>Chorus 1: groove, riff, groove, riff, ending on the D7 stabs.</li>
    <li>Verse 2, the same as verse 1.</li>
    <li>Chorus 2, the same but longer: it keeps bouncing between Am7 and G.</li>
    <li>Bridge.</li>
    <li>Verse 1 again.</li>
    <li>The long chorus again, with a little ad-libbing at the end.</li>
    <li>Finish on a G chord.</li>
  </ol>
  <div class="linkrow">{watch(976, "Verse into chorus, played, at", "Verse into chorus")} {from_part("Song order", "The order, explained at")}</div>
</section>

<section aria-labelledby="h-fam">
  <h2 id="h-fam">Three kinds of shape cover all {NUMBER_WORDS[n]}</h2>
  <ul class="families">
    <li class="fam-ebarre"><span class="sw"></span><span><strong>Barre with its root on the low E string.</strong> G, G7, Am7 and Bm7 are one hand shape with small changes. G7 is G with the little finger lifted, and Bm7 is Am7 two frets higher.</span></li>
    <li class="fam-abarre"><span class="sw"></span><span><strong>Barre with its root on the A string.</strong> C7, the big D7, Em and C. C7 and the big D7 are the same shape two frets apart. Em/D# is Em with its bass note moved.</span></li>
    <li class="fam-small"><span class="sw"></span><span><strong>Three-string grip.</strong> The small D7 used for the stabs and the verse.</span></li>
  </ul>
  <p class="readme"><b>Reading the diagrams:</b> the left line is the low E string and the right line is the high E. No shape here is down at the nut, so every diagram has a label such as <b>5fr</b> at its top left, which is the fret its top row stands for. Numbers are fingers, 1 for index through 4 for pinky, and a bar across several strings is one finger laid flat. <b>×</b> marks a string that is not part of the shape. The letters underneath are the notes that sound. Frets and strings are the ones the lesson says and shows. Finger numbers follow the lesson where it names a finger and the usual fingering otherwise.</p>
</section>

<section aria-labelledby="h-shapes">
  <h2 id="h-shapes">The shapes, in the order the song reaches them</h2>
  <p class="progress" id="progress" aria-live="polite">Tick each shape off as you get it clean.</p>
  <div class="cards">{cards}</div>
</section>

<section aria-labelledby="h-points">
  <h2 id="h-points">What the lesson stresses</h2>
  <ul class="points">
    <li>Stay relaxed. The instructor comes back to this more than anything else: the groove only sits right when the playing hand is loose and keeps moving.</li>
    <li>The two grooves get their short sound in different ways. The verse is the fretting hand letting go; the chorus is the playing hand landing on the strings.</li>
    <li>Learn the chorus groove before you add the riff to it.</li>
    <li>It is fine to simplify at first: get the chords right and keep the strumming very plain.</li>
    <li>If barre chords are still a struggle, he suggests this is not the song to start them on.</li>
  </ul>
  <div class="linkrow">{watch(681, "Staying relaxed at", "Staying relaxed")} {watch(1240, "Simplifying it at", "Simplifying the song")}</div>
</section>

<section aria-labelledby="h-practice">
  <h2 id="h-practice">A practice order</h2>
  <ol class="steps">
    <li>Get Am7 and G7 ringing on every string, one string at a time.</li>
    <li>Play the verse groove on one chord: thumb, flick, thumb, flick, pressing and relaxing the chord.</li>
    <li>Take it through the verse changes, two beats a chord, and add thumb, up, down, up on the C7.</li>
    <li>Play the chorus groove on Am7 alone, slowly: thumb, up, hit, up.</li>
    <li>Move it between Am7 and G, changing a touch early.</li>
    <li>Learn the riff from the lesson and drop it in between the groove bars.</li>
    <li>Add the bridge chords, then the alternating bass under them.</li>
  </ol>
</section>

<section aria-labelledby="h-video">
  <h2 id="h-video">Find it in the video</h2>
  <ol class="chapters">{chapters}</ol>
</section>

<footer class="source">
  <p>Source: <a href="https://youtu.be/{VIDEO_ID}">Banana Pancakes by Jack Johnson | Acoustic Guitar Lesson</a> by JustinGuitar Songs on YouTube. The instructor's own page for the lesson is <a href="https://www.justinguitar.com/yt-banana-pancakes">on justinguitar.com</a>.</p>
  <p>The diagrams were drawn for these notes and are not frames from the video. The lesson's notation and tab are not copied here; follow the timestamps to see them.</p>
</footer>

</main>
<script>{JS}</script>
<script>{PLAYER_JS}</script>
</body>
</html>
'''


if __name__ == "__main__":
    check()
    out = Path(__file__).resolve().parent / "index.html"
    html = page()
    out.write_text(html, encoding="utf-8")
    print(f"checked {len(CHORDS)} shapes, wrote {out.name} ({len(html.encode('utf-8'))} bytes)")
