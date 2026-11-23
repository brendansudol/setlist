#!/usr/bin/env python3
"""Build your-song/index.html from the data in this file.

    python3 your-song/build.py

Standard library only. Every chord shape is checked against the note names it
should produce before any HTML is written, so a mistyped fret stops the build.

All fret numbers are counted from the capo, the same way the lesson names the
chords ("as if there were no capo at all").
"""
from html import escape
from pathlib import Path

VIDEO_ID = "o3AstcWl7E8"
VIDEO_LENGTH = 1407  # seconds


def yt(t):
    return f"https://youtu.be/{VIDEO_ID}?t={t}"


def mmss(t):
    return f"{t // 60}:{t % 60:02d}"


# ---------------------------------------------------------------- music data

NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
OPEN = [4, 9, 2, 7, 11, 4]  # pitch classes of strings 6 to 1, standard tuning
STRING = ["low E", "A", "D", "G", "B", "high E"]
FINGER = {"T": "Thumb", 1: "Index", 2: "Middle", 3: "Ring", 4: "Pinky"}
X = None  # a string that is not played in the shape

FAMILIES = {
    "open": "Open chord",
    "bm": "Bm shape",
    "barre": "Fret 2 barre",
    "small": "Small shape",
}

# frets and fingers run from string 6 (low E) to string 1 (high E).
# barre = (finger, first string index, last string index, fret)
# expect = the notes that should sound, low string to high
# tones = every note the chord name allows; bass = the lowest note
CHORDS = [
    dict(id="d", name="D", fam="open", t=71,
         frets=[X, X, 0, 2, 3, 2], fingers=[X, X, X, 1, 3, 2],
         expect="D A D F#", tones="D F# A", bass="D",
         where="Ordinary open D",
         tip="Home base. The intro and both lines of the verse start here, and "
             "the second half of the verse ends here."),
    dict(id="g-over-d", name="G/D", fam="small", t=80,
         frets=[X, X, 0, 4, 3, 3], fingers=[X, X, X, 2, 1, 1], barre=(1, 4, 5, 3),
         expect="D B D G", tones="G B D", bass="D",
         where="A small G shape over the open D string",
         tip="Lay the index flat across the top two strings at fret 3 and put "
             "the middle finger on the G string at fret 4. The open D string "
             "is the bass."),
    dict(id="a-over-d", name="A/D", fam="small", t=95,
         frets=[X, X, 0, 6, 5, 5], fingers=[X, X, X, 2, 1, 1], barre=(1, 4, 5, 5),
         expect="D C# E A", tones="A C# E D", bass="D",
         where="The G/D hand, moved up two frets",
         tip="Nothing changes in the hand. Slide it up two frets and let the "
             "open D string keep ringing underneath."),
    dict(id="gmaj7", name="Gmaj7", fam="small", t=327,
         frets=[3, X, X, X, 3, 2], fingers=[2, X, X, X, 3, 1],
         expect="G D F#", tones="G B D F#", bass="G",
         where="A low G under the top of the D chord",
         tip="The top two strings hold the same frets as D. Only the bass "
             "changes: in the video the middle finger reaches across to the "
             "low E string at fret 3 and the index takes the high E string."),
    dict(id="a-over-csharp", name="A/C#", fam="open", t=374,
         frets=[X, 4, 2, 2, X, 0], fingers=[X, 3, 1, 2, X, X],
         expect="C# E A E", tones="A C# E", bass="C#",
         where="A with C# in the bass",
         tip="The instructor uses his first and second fingers on the D and G "
             "strings and his third on the A string at fret 4, and says to "
             "find your own fingering if that is uncomfortable. The B string "
             "is left out."),
    dict(id="fsharp-m7", name="F#m7", fam="barre", t=423,
         frets=[2, 4, 2, 2, 2, 2], fingers=[1, 3, 1, 1, 1, 1], barre=(1, 0, 5, 2),
         expect="F# C# E A C# F#", tones="F# A C# E", bass="F#",
         where="Index across all six strings at fret 2",
         tip="The ring finger adds fret 4 on the A string. The instructor "
             "notes that this bar only sounds the low E and the top two "
             "strings, so that finger is optional."),
    dict(id="bm", name="Bm", fam="bm", t=479,
         frets=[X, 2, 4, 4, 3, 2], fingers=[X, 1, 3, 4, 2, 1], barre=(1, 1, 5, 2),
         expect="B F# B D F#", tones="B D F#", bass="B",
         where="The usual Bm barre at fret 2",
         tip="This hand stays down for the next two chords. Only the bass "
             "note underneath it changes."),
    dict(id="bm-over-a", name="Bm/A", fam="bm", t=523,
         frets=[X, 0, 4, 4, 3, 2], fingers=[X, X, 3, 4, 2, 1],
         expect="A F# B D F#", tones="B D F# A", bass="A",
         where="Bm with the A string open",
         tip="Lift the index off the A string so it rings open as the bass. "
             "The other three fingers do not move."),
    dict(id="bm-over-gsharp", name="Bm/G#", fam="bm", t=546,
         frets=[4, X, 4, 4, 3, 2], fingers=["T", X, 3, 4, 2, 1],
         expect="G# F# B D F#", tones="B D F# G#", bass="G#",
         where="Bm with the thumb on the low E string",
         tip="The thumb wraps over the top to fret 4. The lesson calls this "
             "chord B minor over A flat, which is the same note as G#, and "
             "says another finger can take the bass if the thumb will not "
             "reach."),
    dict(id="g6", name="G6", fam="small", t=588,
         frets=[3, X, X, X, 0, 0], fingers=["T", X, X, X, X, X],
         expect="G B E", tones="G B D E", bass="G",
         where="Thumb on the low E string, top two strings open",
         tip="The fretting fingers come right off. The thumb holds G at "
             "fret 3 while the open B and high E strings ring."),
    dict(id="a", name="A", fam="open", t=672,
         frets=[X, 0, 2, 2, 2, 0], fingers=[X, X, 1, 2, 3, X],
         expect="A E A C# E", tones="A C# E", bass="A",
         where="Ordinary open A",
         tip="It appears twice in line 2. Both times the B string rises to "
             "fret 3 for a moment, a suspended sound, and comes back."),
    dict(id="fsharp-7", name="F#7", fam="barre", t=698,
         frets=[2, 4, 2, 3, 2, 2], fingers=[1, 3, 1, 2, 1, 1], barre=(1, 0, 5, 2),
         expect="F# C# E A# C# F#", tones="F# A# C# E", bass="F#",
         where="The F#m7 barre plus one finger",
         tip="Keep the barre at fret 2 and add the middle finger on the G "
             "string at fret 3. That one note is the difference between F#m7 "
             "and F#7."),
    dict(id="em", name="Em", fam="bm", t=807,
         frets=[X, 7, 9, 9, 8, 7], fingers=[X, 1, 3, 4, 2, 1], barre=(1, 1, 5, 7),
         expect="E B E G B", tones="E G B", bass="E",
         where="The Bm hand, moved up to fret 7",
         tip="Same shape as Bm, five frets higher. With the capo on fret 2 "
             "this sits at the ninth fret of the guitar, which is how the "
             "instructor describes it."),
    dict(id="g", name="G", fam="open", t=840,
         frets=[3, 2, 0, 0, 3, 3], fingers=[2, 1, X, X, 3, 4],
         expect="G B D G D G", tones="G B D", bass="G",
         where="Full open G",
         tip="The video clearly shows the middle finger on the low E string "
             "at fret 3 and the index at fret 2. The ring and pinky on the "
             "top two strings are harder to see, so those two follow the "
             "usual four-finger G."),
]
C = {ch["id"]: ch for ch in CHORDS}

INTRO = ["d", "g-over-d", "a-over-d", "g-over-d"]
LINE1 = ["d", "gmaj7", "a-over-csharp", "fsharp-m7",
         "bm", "bm-over-a", "bm-over-gsharp", "g6"]
LINE2 = ["d", "a", "fsharp-7", "bm", "d", "em", "g", "a"]

# Single reaches the instructor calls out. Pointers only, not a transcription.
REACHES = [
    ("G/D in the intro", 212,
     "With the shape held down, the pinky stretches up to fret 7 on the high "
     "E string."),
    ("A/D in the intro", 157,
     "The arrangement reaches this chord by sliding the pinky along the G "
     "string from fret 4 to fret 6 rather than moving the whole shape. The "
     "instructor calls it a bit of a stretch."),
    ("A/C#", 398,
     "The pinky hammers fret 5 on the high E string and pulls off. He says "
     "this one is awkward."),
    ("F#7", 715,
     "The pinky slides from fret 5 to fret 7 on the high E string while the "
     "barre stays down."),
    ("D in line 2", 798,
     "A stretch up to fret 5 on the high E string without letting go of D."),
]

CHAPTERS = [
    (0, "Intro", "What the lesson covers."),
    (8, "Demo", "The arrangement played at speed."),
    (50, "Overview", "Tuning, and where the capo goes."),
    (61, "Intro", "The three intro chords, then the intro one bar at a time."),
    (255, "Intro Play Through", "The whole intro, slowly."),
    (266, "Verse (Part 1)", "The first half of the verse, chord by chord. "
                            "Line 2 starts at 10:25."),
    (920, "1st Play Through of Verse", "The first half, slowly."),
    (956, "Verse (Part 2)", "The second half: the same chords with small "
                            "changes, ending on D."),
    (1318, "2nd Play Through of Verse", "The second half, slowly."),
    (1387, "Outro", "Where the rest of the lesson lives."),
]

# Where each part of the chord map starts in the video. The map's "From" buttons and
# the shortcuts next to the video both come from this.
PARTS = [("Intro", 61), ("Verse, line 1", 266), ("Verse, line 2", 625),
         ("Second half of the verse", 956)]


# -------------------------------------------------------------------- checks

def sounding(ch):
    return [NOTES[(OPEN[i] + f) % 12] for i, f in enumerate(ch["frets"]) if f is not None]


def bass_of(ch):
    """(string index, fret) of the lowest played string."""
    for i, f in enumerate(ch["frets"]):
        if f is not None:
            return i, f
    raise ValueError(ch["name"])


def check():
    assert len({ch["id"] for ch in CHORDS}) == len(CHORDS), "duplicate chord id"
    for ch in CHORDS:
        n = ch["name"]
        notes = sounding(ch)
        assert notes == ch["expect"].split(), f"{n}: got {notes}, expected {ch['expect']}"
        assert set(notes) <= set(ch["tones"].split()), f"{n}: note outside the chord: {notes}"
        assert notes[0] == ch["bass"], f"{n}: bass is {notes[0]}, expected {ch['bass']}"
        assert ch["fam"] in FAMILIES, f"{n}: unknown family"
        assert 0 <= ch["t"] < VIDEO_LENGTH, f"{n}: timestamp outside the video"
        assert bass_of(ch)[0] <= 2, f"{n}: bass is not on one of the three low strings"
        for i, (f, fg) in enumerate(zip(ch["frets"], ch["fingers"])):
            if f:
                assert fg in FINGER, f"{n}: string {6 - i} is fretted but has no finger"
            else:
                assert fg is None, f"{n}: string {6 - i} has a finger but no fret"
        if "barre" in ch:
            fg, a, b, fret = ch["barre"]
            assert all(ch["frets"][i] is not None and ch["frets"][i] >= fret
                       for i in range(a, b + 1)), f"{n}: barre crosses an unplayed string"
            assert ch["frets"][a] == fret and ch["frets"][b] == fret, f"{n}: barre ends"
            assert all(ch["fingers"][i] == fg for i in range(a, b + 1)
                       if ch["frets"][i] == fret), f"{n}: barre finger mismatch"
    for seq in (INTRO, LINE1, LINE2):
        for cid in seq:
            assert cid in C, f"unknown chord in a sequence: {cid}"
    used = set(INTRO + LINE1 + LINE2)
    assert used == set(C), f"chords never used: {set(C) - used}"
    for label, t, _ in REACHES:
        assert 0 <= t < VIDEO_LENGTH, label
    times = [t for t, _, _ in CHAPTERS]
    assert times == sorted(times) and times[-1] < VIDEO_LENGTH, "chapters out of order"


def used_in(cid):
    parts = []
    if cid in INTRO:
        parts.append("Intro")
    l1, l2 = cid in LINE1, cid in LINE2
    if l1 and l2:
        parts.append("verse, both lines")
    elif l1:
        parts.append("verse, line 1")
    elif l2:
        parts.append("verse, line 2")
    text = " and ".join(parts)
    return text[0].upper() + text[1:]


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


def from_part(name):
    """The "From m:ss" button on a part of the chord map."""
    return watch(dict(PARTS)[name], "From", name)


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
    label = f"{ch['name']} chord diagram, frets counted from the capo: " + ", ".join(desc)

    o = [f'<svg class="chordbox" viewBox="0 0 150 200" role="img" aria-label="{escape(label)}">']
    for k in range(5):
        y = 44 + 32 * k
        cls = "nut" if (k == 0 and start == 1) else "fret"
        o.append(f'<line class="{cls}" x1="34" y1="{y}" x2="134" y2="{y}"/>')
    widths = [2.2, 1.9, 1.6, 1.3, 1.1, 1.0]
    for i in range(6):
        cls = "string" + (" string-off" if frets[i] is None else "")
        o.append(f'<line class="{cls}" x1="{sx(i)}" y1="44" x2="{sx(i)}" y2="172" stroke-width="{widths[i]}"/>')
    if start == 1:
        o.append('<text class="capolab" x="26" y="47">capo</text>')
    else:
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
        # put the finger number on a string the barre really holds down
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
    <p class="meta"><span class="tag">{FAMILIES[ch["fam"]]}</span><span>{used_in(cid)}</span></p>
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
    items = []
    for n, cid in enumerate(seq, 1):
        ch = C[cid]
        items.append(f'<li class="fam-{ch["fam"]}"><a href="#chord-{cid}">'
                     f'<span class="bar">{n}</span><span class="nm">{ch["name"]}</span></a></li>')
    return f'<ol class="loop">{"".join(items)}</ol>'


def travel():
    x0, x1, n = 60, 336, 10
    fw = (x1 - x0) / n
    rows = []
    y = 70
    for label, seq in (("Line 1", LINE1), ("Line 2", LINE2)):
        y += 14
        rows.append(f'<text class="blocklab" x="2" y="{y}">{label}</text>')
        y += 5
        for k, cid in enumerate(seq, 1):
            ch = C[cid]
            cy = y + 9.5
            fretted = [f for f in ch["frets"] if f]
            lo, hi = min(fretted), max(fretted)
            g = [f'<g class="fam-{ch["fam"]}">',
                 f'<text class="rowlab" x="2" y="{cy + 4}"><tspan class="ord">{k}</tspan> {ch["name"]}</text>',
                 f'<rect class="span" x="{x0 + fw * (lo - 1) + 2:.1f}" y="{cy - 7}" width="{fw * (hi - lo + 1) - 4:.1f}" height="14" rx="7"/>']
            if "T" in ch["fingers"]:
                tf = ch["frets"][ch["fingers"].index("T")]
                tx = x0 + fw * (tf - 0.5)
                g.append(f'<circle class="dot-t" cx="{tx:.1f}" cy="{cy}" r="5.8"/>')
                g.append(f'<text class="fn ft" x="{tx:.1f}" y="{cy + 3}">T</text>')
            if bass_of(ch)[1] == 0:
                g.append(f'<circle class="openring" cx="{x0 - 8}" cy="{cy}" r="3.8"/>')
            g.append("</g>")
            rows.append("".join(g))
            y += 19
        y += 4
    h = y + 4
    o = [f'<svg class="travel" viewBox="0 0 340 {h}" role="img" aria-label="Chart of the frets the hand covers for each of the sixteen verse chords. Fifteen of them sit between the capo and fret 4. Em is the exception, at frets 7 to 9.">',
         f'<rect class="board" x="{x0}" y="14" width="{x1 - x0}" height="36"/>']
    for i in range(6):
        sy = 18 + 5.6 * i
        o.append(f'<line class="string" x1="{x0}" y1="{sy:.1f}" x2="{x1}" y2="{sy:.1f}" stroke-width="{1.6 - 0.14 * i:.2f}"/>')
    o.append(f'<line class="nut" x1="{x0}" y1="14" x2="{x0}" y2="50"/>')
    o.append(f'<text class="capolab mid" x="{x0}" y="9">capo</text>')
    o.append(f'<line class="grid" x1="{x0}" y1="70" x2="{x0}" y2="{h - 4}"/>')
    for f in range(1, n + 1):
        fx = x0 + fw * f
        o.append(f'<line class="fret" x1="{fx:.1f}" y1="14" x2="{fx:.1f}" y2="50"/>')
        o.append(f'<line class="grid" x1="{fx:.1f}" y1="70" x2="{fx:.1f}" y2="{h - 4}"/>')
        o.append(f'<text class="fnum" x="{fx - fw / 2:.1f}" y="64">{f}</text>')
    o.extend(rows)
    o.append("</svg>")
    return "".join(o)


def bassmap():
    row_of = {2: 0, 1: 1, 0: 2}  # D string on top, low E at the bottom
    row_name = ["D", "A", "low E"]

    def cx(i):
        return 72 + i * 36

    o = []
    y = 0
    for label, seq in (("Line 1", LINE1), ("Line 2", LINE2)):
        y += 14
        o.append(f'<text class="blocklab" x="2" y="{y}">{label}</text>')
        hy = y + 18
        for i, cid in enumerate(seq):
            o.append(f'<text class="cn" x="{cx(i)}" y="{hy}">{C[cid]["name"]}</text>')

        def ry(r, hy=hy):
            return hy + 24 + r * 26

        for r in range(3):
            o.append(f'<line class="string" x1="52" y1="{ry(r)}" x2="336" y2="{ry(r)}" stroke-width="{1.2 + 0.4 * r:.1f}"/>')
            o.append(f'<text class="slab" x="46" y="{ry(r) + 4}">{row_name[r]}</text>')
        pts, dots = [], []
        for i, cid in enumerate(seq):
            ch = C[cid]
            si, f = bass_of(ch)
            px, py = cx(i), ry(row_of[si])
            pts.append(f"{px},{py}")
            cls = "bass-open" if f == 0 else "dot"
            num = "fn ft" if f == 0 else "fn"
            dots.append(f'<g class="fam-{ch["fam"]}"><circle class="{cls}" cx="{px}" cy="{py}" r="10"/>'
                        f'<text class="{num}" x="{px}" y="{py + 3.8}">{f}</text></g>')
        o.append(f'<polyline class="walk" points="{" ".join(pts)}"/>')
        o.extend(dots)
        y = ry(2) + 20
    h = y
    walk = ", ".join(f"{C[c]['name']} on {NOTES[(OPEN[bass_of(C[c])[0]] + bass_of(C[c])[1]) % 12]}" for c in LINE1)
    head = (f'<svg class="bassmap" viewBox="0 0 340 {h}" role="img" aria-label="Where the bass note sits '
            f'for each verse chord. Line 1: {escape(walk)}.">')
    return head + "".join(o) + "</svg>"


# ---------------------------------------------------------------------- page

CSS = r"""
:root {
  /* Layout: one reading column for a phone propped by the guitar. Chrome stays grey;
     the only colour is the four hand-shape families, used the same way everywhere. */
  --bg: #eef1f4;
  --surface: #ffffff;
  --ink: #16202b;
  --muted: #566472;
  --line: #d3dae1;
  --open: #0c7a64;    /* open chords: D, A, A/C#, G */
  --bm: #a52d76;      /* the Bm barre shape: Bm, Bm/A, Bm/G#, Em */
  --barre: #2459c4;   /* full barre at fret 2: F#m7, F#7 */
  --small: #96560a;   /* small shapes over a bass note: G/D, A/D, Gmaj7, G6 */
  --on-dot: #ffffff;
  --font-display: "Bricolage Grotesque", "Avenir Next", "Segoe UI", sans-serif;
  --font-body: "Atkinson Hyperlegible", "Helvetica Neue", Arial, sans-serif;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    color-scheme: dark;
    --bg: #10161d; --surface: #19212b; --ink: #e9eef3; --muted: #9aa8b6; --line: #2d3946;
    --open: #5ad0b3; --bm: #f090c8; --barre: #86adff; --small: #f0b566; --on-dot: #10161d;
  }
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --bg: #10161d; --surface: #19212b; --ink: #e9eef3; --muted: #9aa8b6; --line: #2d3946;
  --open: #5ad0b3; --bm: #f090c8; --barre: #86adff; --small: #f0b566; --on-dot: #10161d;
}
.fam-open  { --fam: var(--open); }
.fam-bm    { --fam: var(--bm); }
.fam-barre { --fam: var(--barre); }
.fam-small { --fam: var(--small); }

* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body {
  margin: 0; background: var(--bg); color: var(--ink);
  font: 400 16px/1.5 var(--font-body);
}
main { max-width: 760px; margin: 0 auto; padding: 28px 16px 56px; display: grid; gap: 44px; }
h1, h2, h3 { font-family: var(--font-display); text-wrap: balance; margin: 0; line-height: 1.1; }
h1 { font-size: clamp(2rem, 8vw, 3rem); font-weight: 800; letter-spacing: -0.02em; }
h2 { font-size: 1.5rem; font-weight: 700; letter-spacing: -0.01em; }
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
.chord { background: var(--surface); border: 1px solid var(--line); border-top: 6px solid var(--fam); border-radius: 8px; padding: 14px; display: grid; gap: 12px; align-content: start; scroll-margin-top: calc(var(--player-h, 0px) + 12px); /* a chord tapped in the map lands below the open video */ }
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
.capolab { fill: var(--muted); font-size: 8.5px; text-anchor: end; letter-spacing: .04em; }
.capolab.mid { text-anchor: middle; }
.mk { fill: var(--muted); font-size: 13px; text-anchor: middle; }
.openring { fill: none; stroke: var(--ink); stroke-width: 1.6; }
.nn { fill: var(--muted); font-size: 10.5px; text-anchor: middle; }

figure { margin: 0; display: grid; gap: 10px; }
figcaption { font-size: .875rem; color: var(--muted); max-width: 62ch; }
.panel { background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 14px 12px; }
.travel, .bassmap { display: block; width: 100%; max-width: 560px; height: auto; margin: 0 auto; }
.board { fill: var(--ink); opacity: .07; }
.travel .string { opacity: .5; }
.travel .fret { opacity: .5; }
.travel .nut { stroke-width: 3; }
.grid { stroke: var(--ink); opacity: .1; }
.fnum { fill: var(--muted); font-size: 9.5px; text-anchor: middle; font-variant-numeric: tabular-nums; }
.rowlab { fill: var(--ink); font-size: 10.5px; font-weight: 700; }
.rowlab .ord { fill: var(--muted); font-weight: 400; }
.blocklab { fill: var(--muted); font-size: 9.5px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; }
.span { fill: var(--fam); opacity: .85; }
.travel .dot-t { stroke-width: 2; }
.travel .fn { font-size: 8px; }

.bassmap .string { opacity: .35; }
.cn { fill: var(--ink); font-size: 9.5px; font-weight: 700; text-anchor: middle; }
.slab { fill: var(--muted); font-size: 10.5px; text-anchor: end; }
.walk { fill: none; stroke: var(--ink); stroke-width: 1.4; opacity: .28; stroke-linejoin: round; }
.bass-open { fill: var(--surface); stroke: var(--fam); stroke-width: 2.5; }

.points { margin: 0; padding-left: 1.2em; display: grid; gap: 8px; max-width: 62ch; }

/* reaches */
.reaches { list-style: none; margin: 0; padding: 0; border-top: 1px solid var(--line); }
.reaches li { display: grid; gap: 8px; padding: 12px 0; border-bottom: 1px solid var(--line); justify-items: start; }
.reaches strong { font-family: var(--font-display); font-size: 1.0625rem; }
.reaches p { font-size: .9375rem; color: var(--muted); }

/* chapter list */
.chapters { list-style: none; margin: 0; padding: 0; border-top: 1px solid var(--line); }
.chapters li { display: grid; gap: 2px; padding: 10px 0; border-bottom: 1px solid var(--line); }
.chapters a { display: grid; grid-template-columns: 3.4em 1fr; gap: 8px; text-decoration: none; font-weight: 700; }
.chapters .t { font-variant-numeric: tabular-nums; text-decoration: underline; text-underline-offset: 3px; }
.chapters .what { padding-left: calc(3.4em + 8px); color: var(--muted); font-size: .9375rem; }
.steps { margin: 0; padding-left: 1.4em; display: grid; gap: 8px; max-width: 62ch; }
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
.pbtn:focus-visible { outline: 3px solid var(--barre); outline-offset: 2px; }
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
  var KEY = 'your-song-shapes';
  var saved = {};
  try { saved = JSON.parse(localStorage.getItem(KEY) || '{}') || {}; } catch (e) { saved = {}; }
  function render() {
    var n = boxes.filter(function (b) { return b.checked; }).length;
    out.textContent = n === 0 ? 'Tick each shape off as you get it clean.'
      : n === boxes.length ? 'All ' + n + ' shapes ticked off. Time to add the picking from the video.'
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

NUMBER_WORDS = {14: "fourteen", 4: "four"}


def page():
    n = len(CHORDS)
    cards = "".join(card(ch) for ch in CHORDS)
    reaches = "".join(
        f"<li><strong>{escape(label)}</strong><p>{escape(text)}</p>{watch(t, part=label)}</li>"
        for label, t, text in REACHES)
    chapters = "".join(
        f'<li><a {moment(t, title)}><span class="t">{mmss(t)}</span><span class="ct">{escape(title)}</span></a>'
        f'<span class="what">{escape(what)}</span></li>'
        for t, title, what in CHAPTERS)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Your Song Chord Shapes</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&amp;family=Bricolage+Grotesque:opsz,wght@12..96,600..800&amp;display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
{PLAYER}
<main>

<header class="top">
  <p class="eyebrow">Fingerstyle lesson notes</p>
  <h1>Your Song: {NUMBER_WORDS[n]} chord shapes</h1>
  <p class="lede">Every fretting-hand shape in the intro and verse of a fingerstyle arrangement, worked out from Six String Fingerpicking's 23-minute lesson on the Elton John song. Tap any time on this page to play that moment of the lesson. The video stays on screen while you read.</p>
  <dl class="facts">
    <div><dt>Tuning</dt><dd>Standard</dd></div>
    <div><dt>Capo</dt><dd>Fret 2 in the lesson. The instructor calls it optional and says fret 1 matches the original.</dd></div>
    <div><dt>Fret numbers</dt><dd>Counted from the capo everywhere on this page, the way the lesson names the chords.</dd></div>
    <div><dt>To learn</dt><dd>{n} shapes in {len(FAMILIES)} families</dd></div>
  </dl>
</header>

<section aria-labelledby="h-map">
  <h2 id="h-map">The chord map</h2>
  <p>Chords in the order they are played. Tap one to jump to its shape.</p>
  <div class="part">
    <div class="part-head"><h3>Intro</h3>{from_part("Intro")}</div>
    {chips(INTRO)}
  </div>
  <div class="part">
    <div class="part-head"><h3>Verse, line 1</h3>{from_part("Verse, line 1")}</div>
    {chips(LINE1)}
    <p class="note">The changes come two to a bar: the lesson counts D and Gmaj7 as the first bar, A/C# and F#m7 as the second.</p>
  </div>
  <div class="part">
    <div class="part-head"><h3>Verse, line 2</h3>{from_part("Verse, line 2")}</div>
    {chips(LINE2)}
    <p class="note">At 10:25 the instructor plays line 1 again from the top and carries straight on into line 2.</p>
  </div>
  <div class="part">
    <div class="part-head"><h3>Second half of the verse</h3>{from_part("Second half of the verse")}</div>
    <p class="note">The same sixteen chords with small changes on top. The one difference in the chords is the last one: it lands on D instead of A.</p>
  </div>
</section>

<section aria-labelledby="h-fam">
  <h2 id="h-fam">Four kinds of shape cover all {NUMBER_WORDS[n]}</h2>
  <ul class="families">
    <li class="fam-open"><span class="sw"></span><span><strong>Open chords.</strong> D, A, A/C# and G, down by the capo.</span></li>
    <li class="fam-bm"><span class="sw"></span><span><strong>The Bm barre shape.</strong> Bm at fret 2 and Em at fret 7 are one hand shape. Bm/A and Bm/G# keep that hand and change only the bass note.</span></li>
    <li class="fam-barre"><span class="sw"></span><span><strong>Full barre at fret 2.</strong> F#m7 and F#7, one finger apart.</span></li>
    <li class="fam-small"><span class="sw"></span><span><strong>Small shapes over a bass note.</strong> G/D, A/D, Gmaj7 and G6 are a bass note plus two or three strings on top.</span></li>
  </ul>
  <p class="readme"><b>Reading the diagrams:</b> the left line is the low E string and the right line is the high E. The thick line at the top is the capo; a label such as <b>7fr</b> means the diagram starts higher up, at fret 7 above the capo. <b>T</b> is your thumb, wrapped over the top of the neck. Numbers are fingers, 1 for index through 4 for pinky. <b>×</b> marks a string that is not played in that shape and a ring marks an open string. The letters underneath are the note names as the lesson uses them, as if the capo were the nut; with the capo on fret 2 everything sounds a whole step higher. Frets and strings are the ones called out in the lesson and checked against the video. Finger numbers follow the video where it shows them clearly and the usual fingering otherwise.</p>
</section>

<section aria-labelledby="h-shapes">
  <h2 id="h-shapes">The shapes, in the order they first appear</h2>
  <p class="progress" id="progress" aria-live="polite">Tick each shape off as you get it clean.</p>
  <div class="cards">{cards}</div>
</section>

<section aria-labelledby="h-travel">
  <h2 id="h-travel">How far the hand travels in the verse</h2>
  <figure>
    <div class="panel">{travel()}</div>
    <figcaption>Each bar covers the frets your fingers occupy for that chord, top to bottom in playing order. T is where the thumb frets the low E string, and a ring left of the capo means the bass note is an open string. Almost everything sits within four frets of the capo. The one real move is up to Em and back down to G near the end of line 2.</figcaption>
  </figure>
</section>

<section aria-labelledby="h-bass">
  <h2 id="h-bass">Where the thumb finds the bass note</h2>
  <p>This arrangement has no single picking pattern to loop. Each chord gets its own short figure: the thumb plays the bass note and the fingers carry the tune on the upper strings. Those figures are the lesson itself, so this page does not write them out. What it can show is where each one starts.</p>
  <figure>
    <div class="panel">{bassmap()}</div>
    <figcaption>The number in each dot is the fret of the bass note, counted from the capo, on the string named at the left. A ring with 0 is an open string. In line 1 the bass under the Bm shape steps down one note per chord: B, A, G#, then G.</figcaption>
  </figure>
  <ul class="points">
    <li>The bass only ever uses the three low strings, and D always takes its bass from the open D string.</li>
    <li>Bm, Bm/A and Bm/G# are one held shape. Practise that walking bass on its own before adding anything on top.</li>
    <li>The second half of the verse keeps these bass notes and changes the rhythm in a few places. The video is the place to hear that.</li>
  </ul>
</section>

<section aria-labelledby="h-reach">
  <h2 id="h-reach">Reaches worth drilling</h2>
  <p>A few single notes that the instructor singles out because the hand has to stretch for them while a shape stays down.</p>
  <ul class="reaches">{reaches}</ul>
</section>

<section aria-labelledby="h-order">
  <h2 id="h-order">A practice order</h2>
  <ol class="steps">
    <li>Play D, then G/D, then slide that small shape up two frets for A/D and back. Let the open D string ring the whole time.</li>
    <li>Hold Bm and change only the bass: A string fretted, A string open, then thumb on the low E at fret 4. Let go for G6.</li>
    <li>Hold the barre at fret 2 and switch between F#m7 and F#7 by adding and lifting the middle finger.</li>
    <li>Drill the one big move: D, up to Em at fret 7, back down to G.</li>
    <li>Run line 1 in order with the thumb only, one bass note per chord. Then line 2.</li>
    <li>Add the picking from the video, one chord at a time.</li>
  </ol>
</section>

<section aria-labelledby="h-video">
  <h2 id="h-video">Find it in the video</h2>
  <ol class="chapters">{chapters}</ol>
</section>

<footer class="source">
  <p>Source: <a href="https://youtu.be/{VIDEO_ID}">Your Song by Elton John - Fingerstyle Guitar Lesson</a> by Six String Fingerpicking on YouTube. The video teaches the intro and verse; the instructor links the full lesson and TAB in its description.</p>
  <p>The diagrams were drawn for these notes and are not frames from the video. Follow the timestamps to see the real hand positions.</p>
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
