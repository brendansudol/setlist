#!/usr/bin/env python3
"""Build all-the-small-things/index.html from the data in this file.

    python3 all-the-small-things/build.py

Standard library only. Every chord shape is checked against the note names it
should produce before any HTML is written, so a mistyped fret stops the build.

There is no capo in this lesson, so fret numbers are ordinary fret numbers.
"""
from html import escape
from pathlib import Path

VIDEO_ID = "hsBlzBTk9Xc"
VIDEO_LENGTH = 1075  # seconds


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
    "power": "Power-chord shape",
    "cbarre": "C barre shape",
    "open": "Open shape",
    "thumb": "Thumb-over F",
}

# frets and fingers run from string 6 (low E) to string 1 (high E).
# barre = (finger, first string index, last string index, fret)
# expect = the notes that should sound, low string to high
# tones = every note the chord name allows; bass = the lowest note
CHORDS = [
    dict(id="c-barre", name="C", fam="cbarre", t=130,
         frets=[X, 3, 5, 5, 5, X], fingers=[X, 1, 3, 3, 3, X], barre=(3, 2, 4, 5),
         expect="C G C E", tones="C E G", bass="C",
         where="Barre shape with its root on the A string",
         tip="Index on the A string at fret 3, ring finger flattened across "
             "the D, G and B strings at fret 5. The intro strums a full bar "
             "of this in steady eighth notes."),
    dict(id="csus4", name="Csus4", fam="cbarre", t=150,
         frets=[X, 3, 5, 5, 6, X], fingers=[X, 1, 3, 3, 4, X], barre=(3, 2, 3, 5),
         expect="C G C F", tones="C F G", bass="C",
         where="The C barre plus the pinky",
         tip="Keep the C shape down and add the pinky on the B string at "
             "fret 6. One more bar of the same strumming."),
    dict(id="g-shape", name="G", fam="power", t=178,
         frets=[3, 5, 5, 4, X, X], fingers=[1, 3, 4, 2, X, X],
         expect="G D G B", tones="G B D", bass="G",
         where="Power-chord shape at fret 3, plus one finger",
         tip="A G power chord with the middle finger added on the G string "
             "at fret 4. The two quick chords that open the song are this "
             "hand and the F below, hit on the low strings only. The lesson "
             "calls those G5 and F5."),
    dict(id="f-shape", name="F", fam="power", t=222,
         frets=[1, 3, 3, 2, X, X], fingers=[1, 3, 4, 2, X, X],
         expect="F C F A", tones="F A C", bass="F",
         where="The same hand, two frets lower",
         tip="Slide the G shape down two frets without changing it. It "
             "arrives at the very end of the fourth bar and leads back to C."),
    dict(id="c-open", name="C", fam="open", t=303,
         frets=[X, 3, 2, 0, 1, 0], fingers=[X, 3, 2, X, 1, X],
         expect="C E G C E", tones="C E G", bass="C",
         where="Ordinary open C",
         tip="From the verse to the end of the lesson, every C is this one. "
             "The bass note is on the A string."),
    dict(id="g-one", name="G", fam="open", t=323,
         frets=[3, X, 0, 0, 0, X], fingers=[3, X, X, X, X, X],
         expect="G D G B", tones="G B D", bass="G",
         where="One finger on the low E string, the rest open",
         tip="Only the low E string is fretted. Keep the index close to the "
             "B string at fret 1, because the tune touches that note at the "
             "end of the bar. Some bars also use the open high E string."),
    dict(id="fmaj7", name="Fmaj7", fam="thumb", t=351,
         frets=[1, X, 3, 2, 1, 0], fingers=["T", X, 3, 2, 1, X],
         expect="F F A C E", tones="F A C E", bass="F",
         where="Thumb over the top for the bass note",
         tip="The thumb wraps round to fret the low E string at fret 1. The "
             "high E string stays open, which is what makes it Fmaj7. The "
             "instructor says the F is the same every time in the verse."),
    dict(id="g-add", name="G", fam="open", t=756,
         frets=[3, X, 0, 0, 3, X], fingers=[2, X, X, X, 3, X],
         expect="G D G D", tones="G B D", bass="G",
         where="The one-finger G plus the B string at fret 3",
         tip="Used in the pre-chorus and chorus, where the note on the B "
             "string carries the tune. In the chorus the open high E string "
             "is strummed with it."),
    dict(id="f-thumb", name="F", fam="thumb", t=782,
         frets=[1, X, 3, 2, 1, 1], fingers=["T", X, 3, 2, 1, 1], barre=(1, 4, 5, 1),
         expect="F F A C F", tones="F A C", bass="F",
         where="Fmaj7 with the top string fretted too",
         tip="Lay the index across the top two strings at fret 1 and keep "
             "the thumb on the bass. Lifting the index off the high E string "
             "turns it back into Fmaj7, and the pre-chorus does exactly that "
             "at the end of its last bar."),
]
C = {ch["id"]: ch for ch in CHORDS}

INTRO = ["c-barre", "csus4", "g-shape", "f-shape"]  # bar 4 starts on G, ends on F
VERSE = ["c-open", "g-one", "fmaj7", "g-one"]       # four times, sixteen bars
PRE = ["c-open", "c-open", "g-add", "f-thumb"]
CHORUS = PRE                                         # played twice
SECTIONS = [("intro", INTRO), ("verse", VERSE), ("pre-chorus", PRE), ("chorus", CHORUS)]

CHAPTERS = [
    (0, "Performance", "The whole arrangement played through."),
    (96, "Intro", "The two lead-in chords, then the four strummed bars."),
    (284, "1st Verse", "Sixteen bars: the same four chords four times, with "
                       "the tune changing on top."),
    (658, "Six String Fingerpicking Academy", "A break to talk about the "
                                              "instructor's courses."),
    (706, "Pre-Chorus", "Two bars of C, one of G, one of F."),
    (823, "Chorus", "The same four bars with a strummed feel, played twice."),
    (1046, "Outro", "Where the rest of the lesson lives."),
]

# Where each section starts in the video. The song map's "From" buttons and the
# section shortcuts next to the video both come from this.
PARTS = [("Intro", 96), ("Verse", 284), ("Pre-chorus", 706), ("Chorus", 823)]


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
    for _, seq in SECTIONS:
        assert len(seq) == 4, "each section is a four-bar unit"
        for cid in seq:
            assert cid in C, f"unknown chord in a section: {cid}"
    used = {cid for _, seq in SECTIONS for cid in seq}
    assert used == set(C), f"chords never used: {set(C) - used}"
    times = [t for t, _, _ in CHAPTERS]
    assert times == sorted(times) and times[-1] < VIDEO_LENGTH, "chapters out of order"
    assert [name.lower() for name, _ in PARTS] == [name for name, _ in SECTIONS], "PARTS and SECTIONS differ"
    assert all(t in times for _, t in PARTS), "a section does not start where its chapter does"


def used_in(cid):
    names = [name for name, seq in SECTIONS if cid in seq]
    text = names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]
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
    """The "From m:ss" button on a section of the song map."""
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


def chips(seq, names=None):
    items = []
    for n, cid in enumerate(seq, 1):
        ch = C[cid]
        name = (names or {}).get(n, ch["name"])
        items.append(f'<li class="fam-{ch["fam"]}"><a href="#chord-{cid}">'
                     f'<span class="bar">bar {n}</span><span class="nm">{name}</span></a></li>')
    return f'<ol class="loop">{"".join(items)}</ol>'


def travel():
    x0, x1, n = 60, 336, 7
    fw = (x1 - x0) / n
    rows = []
    y = 70
    for label, seq in (("Intro", INTRO), ("Verse", VERSE), ("Pre-chorus and chorus", PRE)):
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
            g.append("</g>")
            rows.append("".join(g))
            y += 19
        y += 4
    h = y + 4
    o = [f'<svg class="travel" viewBox="0 0 340 {h}" role="img" aria-label="Chart of the frets the hand covers in each section. The intro sits at frets 3 to 6 and drops to fret 1 for F. The verse, pre-chorus and chorus all stay within the first three frets.">',
         f'<rect class="board" x="{x0}" y="14" width="{x1 - x0}" height="36"/>']
    for i in range(6):
        sy = 18 + 5.6 * i
        o.append(f'<line class="string" x1="{x0}" y1="{sy:.1f}" x2="{x1}" y2="{sy:.1f}" stroke-width="{1.6 - 0.14 * i:.2f}"/>')
    o.append(f'<line class="nut" x1="{x0}" y1="14" x2="{x0}" y2="50"/>')
    o.append(f'<text class="nutlab" x="{x0}" y="9">nut</text>')
    o.append(f'<line class="grid" x1="{x0}" y1="70" x2="{x0}" y2="{h - 4}"/>')
    for f in range(1, n + 1):
        fx = x0 + fw * f
        o.append(f'<line class="fret" x1="{fx:.1f}" y1="14" x2="{fx:.1f}" y2="50"/>')
        o.append(f'<line class="grid" x1="{fx:.1f}" y1="70" x2="{fx:.1f}" y2="{h - 4}"/>')
        o.append(f'<text class="fnum" x="{fx - fw / 2:.1f}" y="64">{f}</text>')
    o.extend(rows)
    o.append("</svg>")
    return "".join(o)


def pickgrid():
    """One bar of the verse figure: 1, 2, and-of-2, then two tune notes."""
    xs = [64 + 35 * i for i in range(8)]
    rows = [("Top two", 44), ("G", 70), ("D", 96), ("Bass", 122)]
    o = ['<svg class="pick" viewBox="0 0 340 140" role="img" aria-label="One bar of the verse figure. '
         'Beat 1: the bass note. Beat 2: the D string. And of 2: the G string. '
         'Beats 3 and 4: one tune note each, on the B or high E string.">']
    for i, x in enumerate(xs):
        beat = "&" if i % 2 else str(i // 2 + 1)
        o.append(f'<text class="beat{" off" if i % 2 else ""}" x="{x}" y="16">{beat}</text>')
    for name, y in rows:
        o.append(f'<line class="string" x1="48" y1="{y}" x2="334" y2="{y}" stroke-width="{2 if name == "Bass" else 1.2}"/>')
        o.append(f'<text class="slab" x="42" y="{y + 4}">{name}</text>')
    for i, y, cls in ((0, 122, "ev"), (2, 96, "ev"), (3, 70, "ev"), (4, 44, "ev-tune"), (6, 44, "ev-tune")):
        o.append(f'<circle class="{cls}" cx="{xs[i]}" cy="{y}" r="9"/>')
    o.append("</svg>")
    return "".join(o)


LEGEND = (
    '<ul class="legend">'
    '<li><svg class="legend-ico" viewBox="0 0 24 24" aria-hidden="true"><circle class="ev" cx="12" cy="12" r="9"/></svg>'
    '<span>A plucked string. These three are the same in every verse bar.</span></li>'
    '<li><svg class="legend-ico" viewBox="0 0 24 24" aria-hidden="true"><circle class="ev-tune" cx="12" cy="12" r="9"/></svg>'
    '<span>A tune note on the B or high E string. Which string and fret changes from bar to bar.</span></li>'
    '</ul>'
)


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
  --open: #0c7a64;    /* open shapes: open C and the two one-finger Gs */
  --cbarre: #a52d76;  /* C barre shape: C, Csus4 */
  --power: #2459c4;   /* power-chord shape: G, F */
  --thumb: #96560a;   /* thumb-over F: Fmaj7, F */
  --on-dot: #ffffff;
  --font-display: "Bricolage Grotesque", "Avenir Next", "Segoe UI", sans-serif;
  --font-body: "Atkinson Hyperlegible", "Helvetica Neue", Arial, sans-serif;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    color-scheme: dark;
    --bg: #10161d; --surface: #19212b; --ink: #e9eef3; --muted: #9aa8b6; --line: #2d3946;
    --open: #5ad0b3; --cbarre: #f090c8; --power: #86adff; --thumb: #f0b566; --on-dot: #10161d;
  }
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --bg: #10161d; --surface: #19212b; --ink: #e9eef3; --muted: #9aa8b6; --line: #2d3946;
  --open: #5ad0b3; --cbarre: #f090c8; --power: #86adff; --thumb: #f0b566; --on-dot: #10161d;
}
.fam-open   { --fam: var(--open); }
.fam-cbarre    { --fam: var(--cbarre); }
.fam-power  { --fam: var(--power); }
.fam-thumb  { --fam: var(--thumb); }

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
a:focus-visible, input:focus-visible { outline: 3px solid var(--power); outline-offset: 2px; border-radius: 4px; }
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
.chord { background: var(--surface); border: 1px solid var(--line); border-top: 6px solid var(--fam); border-radius: 8px; padding: 14px; display: grid; gap: 12px; align-content: start; scroll-margin-top: calc(var(--player-h, 0px) + 12px); /* a bar tapped in the song map lands below the open video */ }
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

figure { margin: 0; display: grid; gap: 10px; }
figcaption { font-size: .875rem; color: var(--muted); max-width: 62ch; }
.panel { background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 14px 12px; }
.travel, .pick { display: block; width: 100%; max-width: 560px; height: auto; margin: 0 auto; }
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

.slab { fill: var(--muted); font-size: 10.5px; text-anchor: end; }

.pick .string { opacity: .35; }
.beat { fill: var(--ink); font-size: 12px; font-weight: 700; text-anchor: middle; }
.beat.off { fill: var(--muted); font-weight: 400; }
.ev { fill: var(--ink); }
.ev-tune { fill: var(--surface); stroke: var(--ink); stroke-width: 1.8; stroke-dasharray: 3.2 2.4; }
.legend { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 8px 16px; font-size: .9375rem; }
.legend li { display: grid; grid-template-columns: 24px 1fr; gap: 10px; align-items: start; }
.legend-ico { width: 24px; height: 24px; display: block; }
.linkrow { display: flex; flex-wrap: wrap; gap: 8px; }

.points { margin: 0; padding-left: 1.2em; display: grid; gap: 8px; max-width: 62ch; }


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
.pbtn:focus-visible { outline: 3px solid var(--power); outline-offset: 2px; }
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
  var VIDEO = '__VIDEO__';
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
  var want = 0, rate = 1, loopA = null, loopB = null, loopTimer = null, slowTimer = null;
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
    msgLink.href = 'https://youtu.be/' + VIDEO + '?t=' + Math.floor(want);
    msgEl.hidden = false;
  }
  function hush() { msgEl.hidden = true; }

  function openDock(origin) {
    // A tap inside the dock itself (a section shortcut) has no card to bring into view.
    var anchor = origin && !dock.contains(origin) ? (origin.closest('.chord, .part') || origin) : null;
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

  function play(t, part) {
    want = t;
    titleEl.textContent = (part ? part + ' · ' : '') + mmss(t);
    loopOff();
    if (ready) { player.seekTo(t, true); player.playVideo(); }
    else if (!loading) load();
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
    player = new YT.Player('player-video', {
      host: 'https://www.youtube-nocookie.com',
      videoId: VIDEO,
      playerVars: { start: Math.floor(want), autoplay: 1, playsinline: 1, rel: 0 },
      events: {
        onReady: function () {
          ready = true;
          clearTimeout(slowTimer);
          hush();
          loopBtn.disabled = false;
          if (rate !== 1) player.setPlaybackRate(rate);
          player.seekTo(want, true);
          player.playVideo();
        },
        onError: giveUp,
        onPlaybackRateChange: function (e) { rate = e.data; paintSpeed(); }
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
    play(parseFloat(a.getAttribute('data-t')), a.getAttribute('data-part'));
  });
  closeBtn.addEventListener('click', closeDock);
  window.addEventListener('resize', function () { if (!dock.hidden) measure(); });
  paintSpeed();
  paintLoop();
})();
""".replace("__VIDEO__", VIDEO_ID)

JS = r"""
(function () {
  var boxes = Array.prototype.slice.call(document.querySelectorAll('input[data-got]'));
  var out = document.getElementById('progress');
  var KEY = 'all-the-small-things-shapes';
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

NUMBER_WORDS = {9: "nine", 4: "four"}


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
<title>All The Small Things Chord Shapes</title>
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
  <h1>All The Small Things: {NUMBER_WORDS[n]} chord shapes</h1>
  <p class="lede">The fretting-hand shapes for the intro, first verse, pre-chorus and chorus of a fingerstyle arrangement, worked out from Six String Fingerpicking's 18-minute lesson on the Blink-182 song. Tap any time on this page to play that moment of the lesson. The video stays on screen while you read.</p>
  <dl class="facts">
    <div><dt>Tuning</dt><dd>Standard. The lesson does not say so, but the frets it names only make these chords in standard tuning.</dd></div>
    <div><dt>Capo</dt><dd>None</dd></div>
    <div><dt>To learn</dt><dd>{n} shapes in {len(FAMILIES)} families, all of them a C, a G or an F</dd></div>
    <div><dt>Covers</dt><dd>Intro, first verse, pre-chorus and chorus</dd></div>
  </dl>
</header>

<section aria-labelledby="h-map">
  <h2 id="h-map">The song map</h2>
  <p>Every section is a four-bar unit. Tap a bar to jump to its shape.</p>
  <div class="part">
    <div class="part-head"><h3>Intro</h3>{from_part("Intro")}</div>
    {chips(INTRO, {4: "G → F"})}
    <p class="note">Two quick chords lead in before bar 1: the G shape and then the F shape, hit on the low strings only. Bars 1 to 3 are strummed in steady eighth notes. Bar 4 starts on G, drops to muted strums and lands on F at the very end. The four bars are played twice.</p>
  </div>
  <div class="part">
    <div class="part-head"><h3>Verse</h3>{from_part("Verse")}</div>
    {chips(VERSE)}
    <p class="note">Played four times, sixteen bars in all. The chords never change. The tune on top does, from the ninth bar (7:04) and again in the last four (8:49).</p>
  </div>
  <div class="part">
    <div class="part-head"><h3>Pre-chorus</h3>{from_part("Pre-chorus")}</div>
    {chips(PRE)}
    <p class="note">Two bars of C, one of G, one of F. The G and F are fuller than the verse versions.</p>
  </div>
  <div class="part">
    <div class="part-head"><h3>Chorus</h3>{from_part("Chorus")}</div>
    {chips(CHORUS)}
    <p class="note">The same four bars as the pre-chorus, with a strummed feel, played twice. The lesson stops here: the instructor says another verse and a bridge follow, and that he teaches those on his website.</p>
  </div>
</section>

<section aria-labelledby="h-fam">
  <h2 id="h-fam">Four kinds of shape cover all {NUMBER_WORDS[n]}</h2>
  <ul class="families">
    <li class="fam-power"><span class="sw"></span><span><strong>Power-chord shape.</strong> The intro's G at fret 3 and F at fret 1 are one hand, two frets apart.</span></li>
    <li class="fam-cbarre"><span class="sw"></span><span><strong>C barre shape.</strong> The intro's C and Csus4, one pinky apart.</span></li>
    <li class="fam-open"><span class="sw"></span><span><strong>Open shapes.</strong> Open C, and two versions of G with a single finger on the low E string.</span></li>
    <li class="fam-thumb"><span class="sw"></span><span><strong>Thumb-over F.</strong> Fmaj7 and F, both with the thumb fretting the bass note.</span></li>
  </ul>
  <p class="readme"><b>Reading the diagrams:</b> the left line is the low E string and the right line is the high E. The thick line at the top is the nut; a label such as <b>3fr</b> means the diagram starts at fret 3 instead. <b>T</b> is your thumb, wrapped over the top of the neck. Numbers are fingers, 1 for index through 4 for pinky. <b>×</b> marks a string that is not part of the shape and a ring marks an open string. The letters underneath are the notes that sound. Frets and strings are the ones called out in the lesson and checked against the video. Finger numbers follow the video where it shows them clearly and the usual fingering otherwise.</p>
</section>

<section aria-labelledby="h-shapes">
  <h2 id="h-shapes">The shapes, in the order they first appear</h2>
  <p class="progress" id="progress" aria-live="polite">Tick each shape off as you get it clean.</p>
  <div class="cards">{cards}</div>
</section>

<section aria-labelledby="h-travel">
  <h2 id="h-travel">Where the hand sits, section by section</h2>
  <figure>
    <div class="panel">{travel()}</div>
    <figcaption>Each bar covers the frets your fingers occupy for that chord, one row per bar of the four-bar unit. T is where the thumb frets the low E string. The intro is the only part played up the neck. From the verse on, the hand never leaves the first three frets.</figcaption>
  </figure>
</section>

<section aria-labelledby="h-pick">
  <h2 id="h-pick">What the picking hand does in the verse</h2>
  <figure>
    <div class="panel">{pickgrid()}</div>
    <figcaption>One bar of the verse, read left to right. The lesson counts it "one, two and three, four": five notes to the bar.</figcaption>
  </figure>
  {LEGEND}
  <ul class="points">
    <li>The bass note is on the A string under C and on the low E string under G and Fmaj7.</li>
    <li>The first three notes never change, so they are worth getting automatic before adding the tune.</li>
    <li>The two tune notes are what the lesson teaches bar by bar. This page does not write them out; the verse section of the video does.</li>
    <li>The intro is strummed, and the pre-chorus and chorus mix picking with light strums. Those are easier to watch than to read.</li>
    <li>The lesson names strings, not picking-hand fingers, so the diagram does not assign any.</li>
  </ul>
  <div class="linkrow">{watch(303, "Verse figure at", "Verse figure")} {watch(424, "Tune changes at", "Tune changes")} {watch(610, "Verse, slowly, at", "Verse, slowly")}</div>
</section>

<section aria-labelledby="h-order">
  <h2 id="h-order">A practice order</h2>
  <ol class="steps">
    <li>Slide the power-chord shape between G at fret 3 and F at fret 1 until it moves as one hand.</li>
    <li>Hold the C barre and add and lift the pinky for Csus4.</li>
    <li>Strum the intro slowly: a bar each of C, Csus4 and G, then the fourth bar that ends on F.</li>
    <li>Loop the verse chords with the bass note only: C, G, Fmaj7, G. Getting the thumb over for Fmaj7 is the hard part.</li>
    <li>Add the D and G strings after each bass note, then the two tune notes from the video, one bar at a time.</li>
    <li>For the pre-chorus and chorus, swap in the fuller G and F and follow the video for the strumming.</li>
  </ol>
</section>

<section aria-labelledby="h-video">
  <h2 id="h-video">Find it in the video</h2>
  <ol class="chapters">{chapters}</ol>
</section>

<footer class="source">
  <p>Source: <a href="https://youtu.be/{VIDEO_ID}">All The Small Things (Blink 182) - Fingerstyle Guitar Lesson</a> by Six String Fingerpicking on YouTube. The video teaches the intro, first verse, pre-chorus and chorus; the instructor links the full lesson and TAB in its description.</p>
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
