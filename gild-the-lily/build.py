#!/usr/bin/env python3
"""Build gild-the-lily/index.html from the data in this file.

    python3 gild-the-lily/build.py

Standard library only. Every chord shape is checked against the note names it
should produce before any HTML is written, so a mistyped fret stops the build.

The lesson is two videos, so every timestamp here is a (part, seconds) pair.
There is no capo in this lesson, so fret numbers are ordinary fret numbers.
"""
from html import escape
from pathlib import Path
import json

# The lesson's two videos. Part 1 is the one the player starts with.
VIDEOS = {
    1: dict(id="YZlwvVruMcA", length=439, title="How To Play - Gild The Lily by Billy Strings"),
    2: dict(id="BMW2yXYQM6Q", length=676, title="How To Play - Gild The Lily by Billy Strings (Part 2)"),
}
VIDEO_ID = VIDEOS[1]["id"]


def yt(part, t):
    return f"https://youtu.be/{VIDEOS[part]['id']}?t={t}"


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
    "barre": "Barre at fret 2",
    "small": "Three-note version",
}

# frets and fingers run from string 6 (low E) to string 1 (high E).
# barre = (finger, first string index, last string index, fret)
# expect = the notes that should sound, low string to high
# tones = every note the chord name allows; bass = the lowest note
# at = (part of the lesson, seconds) where the shape is shown
CHORDS = [
    dict(id="d", name="D", fam="open", at=(2, 190),
         frets=[X, X, 0, 2, 3, 2], fingers=[X, X, X, 1, 3, 2],
         expect="D A D F#", tones="D F# A", bass="D",
         where="Ordinary open D",
         tip="The home chord: every section passes through it. The lesson "
             "spells it out as the open D string, then frets 2, 3 and 2."),
    dict(id="am", name="Am", fam="open", at=(1, 314),
         frets=[X, 0, 2, 2, 1, 0], fingers=[X, X, 2, 3, 1, X],
         expect="A E A C E", tones="A C E", bass="A",
         where="Ordinary open A minor",
         tip="Only in the verse, for two beats between D and G. The lesson "
             "names it without spelling it out, so this shape is read from "
             "the video."),
    dict(id="g", name="G", fam="open", at=(2, 214),
         frets=[3, 2, 0, 0, 0, 3], fingers=[2, 1, X, X, X, 3],
         expect="G B D G B G", tones="G B D", bass="G",
         where="Open G with the middle finger on the bass",
         tip="The instructor frets the low E string with his middle finger "
             "and adds that you can also fret the B string at fret 3. In the "
             "last line of the chorus the bass walks down from here: fret 3, "
             "fret 2, then the open string under Em."),
    dict(id="c", name="C", fam="open", at=(2, 428),
         frets=[X, 3, 2, 0, 1, 0], fingers=[X, 3, 2, X, 1, X],
         expect="C E G C E", tones="C E G", bass="C",
         where="Ordinary open C",
         tip="Two beats of it in the second half of the verse, between two "
             "Ds. It comes back in the bridge, which is where the lesson "
             "spells it out."),
    dict(id="bm", name="Bm", fam="barre", at=(2, 25),
         frets=[X, 2, 4, 4, 3, 2], fingers=[X, 1, 3, 4, 2, 1], barre=(1, 1, 5, 2),
         expect="B F# B D F#", tones="B D F#", bass="B",
         where="Barre at fret 2 with the root on the A string",
         tip="The first chord of the chorus. Index across fret 2 from the A "
             "string down, then frets 4, 4 and 3. If the barre is a struggle, "
             "the three-note version further down is the instructor's "
             "stand-in."),
    dict(id="fsharp7", name="F#7", fam="barre", at=(2, 45),
         frets=[2, 4, 2, 3, 2, 2], fingers=[1, 3, 1, 2, 1, 1], barre=(1, 0, 5, 2),
         expect="F# C# E A# C# F#", tones="F# A# C# E", bass="F#",
         where="Full barre at fret 2: the F shape without the pinky",
         tip="The instructor describes it as the F major shape moved up to "
             "fret 2 with the pinky taken away, which lets the D string sound "
             "at the barre. Second chord of the chorus, and it returns in the "
             "second half of the bridge."),
    dict(id="a", name="A", fam="open", at=(2, 197),
         frets=[X, 0, 2, 2, 2, X], fingers=[X, X, 1, 1, 1, X], barre=(1, 2, 4, 2),
         expect="A E A C#", tones="A C# E", bass="A",
         where="Open A, held with one finger",
         tip="The chorus uses A major where the verse had A minor. The "
             "instructor lays one finger across the D, G and B strings at "
             "fret 2 and says he prefers that to three fingers. He does not "
             "mention the high E string, so the diagram leaves it out."),
    dict(id="em", name="Em", fam="open", at=(2, 225),
         frets=[0, 2, 2, 0, 0, 0], fingers=[X, 2, 3, X, X, X],
         expect="E B E G B E", tones="E G B", bass="E",
         where="Ordinary open E minor",
         tip="The last chord of the chorus, reached by the walk down from G. "
             "The instructor's shortcut is to fret only the A string and "
             "leave the D string open, which makes it Em7 and frees a "
             "finger."),
    dict(id="fsharp-m", name="F#m", fam="barre", at=(2, 400),
         frets=[2, 4, 4, 2, 2, 2], fingers=[1, 3, 4, 1, 1, 1], barre=(1, 0, 5, 2),
         expect="F# C# F# A C# F#", tones="F# A C#", bass="F#",
         where="Full barre at fret 2: the F shape without the middle finger",
         tip="Only in the bridge. The instructor gets it from the F major "
             "shape at fret 2 by lifting the middle finger. His shortcut is "
             "to lift the pinky as well, which makes it F#m7."),
    dict(id="bm-small", name="Bm", fam="small", at=(2, 74),
         frets=[X, 2, X, 2, 3, X], fingers=[X, 1, X, 2, 3, X],
         expect="B A D", tones="B D F# A", bass="B",
         where="Three notes instead of the barre",
         tip="A string at fret 2, skip the D string, then the G string at "
             "fret 2 and the B string at fret 3. Sound only the strings you "
             "are holding and mute the rest: the instructor says open strings "
             "ringing do not suit the song. The three notes are B, A and D, "
             "which strictly makes it a Bm7."),
    dict(id="fsharp7-small", name="F#7", fam="small", at=(2, 110),
         frets=[2, X, 2, 3, X, X], fingers=[1, X, 2, 3, X, X],
         expect="F# E A#", tones="F# A# C# E", bass="F#",
         where="The same small hand, one string lower",
         tip="Move the small Bm hand across so it starts on the low E "
             "string: fret 2, skip the A string, then the D string at fret 2 "
             "and the G string at fret 3. Again, mute everything you are not "
             "holding."),
]
C = {ch["id"]: ch for ch in CHORDS}

# The three-note shapes stand in for these chords wherever they are used.
STANDS_IN_FOR = {"bm-small": "bm", "fsharp7-small": "fsharp7"}

# One entry per chord change: (chord id, beats). Four beats to the bar.
# "walk" is the two beats where the bass steps down from G towards Em.
VERSE = [("d", 2), ("am", 2), ("g", 2), ("d", 2), ("d", 2), ("c", 2), ("d", 4)]
CHORUS = [("bm", 4), ("fsharp7", 4), ("d", 2), ("a", 2), ("bm", 4),
          ("d", 2), ("a", 2), ("bm", 4), ("d", 2), ("a", 2), ("g", 4),
          ("d", 2), ("a", 2), ("g", 2), ("walk", 2), ("em", 4)]
BRIDGE = [("fsharp-m", 2), ("c", 2), ("d", 4),
          ("d", 2), ("fsharp7", 2), ("c", 4), ("d", 4)]
SECTIONS = [("verse", VERSE), ("chorus", CHORUS), ("bridge", BRIDGE)]

# (seconds, the chapter title YouTube shows, what happens in it), per part
CHAPTERS = {
    1: [
        (0, "Introduction", "What the lesson covers."),
        (18, "Guitar intro breakdown", "The intro lick, note by note, in its "
                                       "four passes."),
        (298, "Verse chords and structure", "The verse chords and how long "
                                            "each one lasts, then two play-throughs."),
    ],
    2: [
        (0, "Chorus chords breakdown", "Bm and F#7 as full barres, then the "
                                       "three-note versions."),
        (154, "Additional chorus chords", "D, A, G and Em, spelled out "
                                          "string by string."),
        (270, "Chorus performance", "The chorus played with the counts, "
                                    "then the walk down to Em."),
        (398, "Bridge and song structure", "The order of the whole song, the "
                                           "two new bridge chords, and what follows the bridge."),
        (540, "Final outro notes", "The last verse and chorus, and the "
                                   "longer lick that ends the song."),
    ],
}

# Where the lesson plays each section. The song map's "From" buttons and the
# shortcuts next to the video both come from this.
PARTS = [("Intro lick", (1, 18)), ("Verse", (1, 297)), ("Chorus", (2, 269)),
         ("Bridge", (2, 445)), ("Outro", (2, 584))]


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
        part, t = ch["at"]
        assert part in VIDEOS and 0 <= t < VIDEOS[part]["length"], f"{n}: timestamp outside the video"
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
            assert cid in C or cid == "walk", f"unknown chord in the {name}: {cid}"
            assert beats in (2, 4), f"{name}: chords last two beats or a bar"
            assert beats == 2 or beat % 4 == 0, f"{name}: a whole-bar chord starts on beat 1"
            beat += beats
        assert beat % 4 == 0, f"the {name} does not end on a bar line"
    used = {cid for _, seq in SECTIONS for cid, _ in seq} - {"walk"}
    assert used == set(C) - set(STANDS_IN_FOR), f"chords never used: {set(C) - set(STANDS_IN_FOR) - used}"
    assert all(C[cid]["fam"] == "small" and full in used for cid, full in STANDS_IN_FOR.items())
    for part, chapters in CHAPTERS.items():
        times = [t for t, _, _ in chapters]
        assert times == sorted(times) and times[-1] < VIDEOS[part]["length"], "chapters out of order"
    for name, (part, t) in PARTS:
        assert part in VIDEOS and 0 <= t < VIDEOS[part]["length"], f"{name}: timestamp outside the video"


def used_in(cid):
    cid = STANDS_IN_FOR.get(cid, cid)
    names = [name for name, seq in SECTIONS if any(c == cid for c, _ in seq)]
    text = names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]
    return text[0].upper() + text[1:]


# ------------------------------------------------------------------ diagrams

PLAY = '<svg class="play" viewBox="0 0 12 12" aria-hidden="true"><path d="M3 1.5v9l7.5-4.5z"/></svg>'


def moment(at, name):
    """Attributes for a timestamp link. It is an ordinary YouTube link; the
    script at the bottom of the page plays it in the docked player instead,
    loading the other part of the lesson if it has to, and shows `name` as
    the name of what is playing."""
    part, t = at
    assert part in VIDEOS and 0 <= t < VIDEOS[part]["length"], f"timestamp outside the video: {at}"
    return (f'href="{yt(part, t)}" data-v="{VIDEOS[part]["id"]}" data-t="{t}" '
            f'data-part="{escape(name, quote=True)}"')


def watch(at, label=None, name=None):
    part, t = at
    label = label or f"Part {part} at"
    return (f'<a class="watch" {moment(at, name or label)}>{PLAY}'
            f'<span>{escape(label)} <b>{mmss(t)}</b></span></a>')


def from_part(name):
    """The "Part n from m:ss" button on a section of the song map."""
    at = dict(PARTS)[name]
    return watch(at, f"Part {at[0]} from", name)


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
    {watch(ch["at"], name=ch["name"])}
    <label class="got" for="got-{cid}"><input type="checkbox" id="got-{cid}" data-got="{cid}"> I can play this</label>
  </footer>
</article>'''


def chips(seq):
    """A section as boxes: a narrow box is two beats, a wide one a whole bar."""
    items, beat = [], 0
    for cid, beats in seq:
        label = f"bar {beat // 4 + 1}" if beat % 4 == 0 else "beat 3"
        ch = C["g" if cid == "walk" else cid]
        name = "walk" if cid == "walk" else ch["name"]
        cls = f'fam-{ch["fam"]}' + (" whole" if beats == 4 else "")
        items.append(f'<li class="{cls}"><a href="#chord-{ch["id"]}">'
                     f'<span class="bar">{label}</span><span class="nm">{name}</span></a></li>')
        beat += beats
    return f'<ol class="loop">{"".join(items)}</ol>'


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
  --open: #0c7a64;    /* open chords: D, Am, G, C, A, Em */
  --barre: #2459c4;   /* barre at fret 2: Bm, F#7, F#m */
  --small: #96560a;   /* three-note versions of Bm and F#7 */
  --on-dot: #ffffff;
  --font-display: "Bricolage Grotesque", "Avenir Next", "Segoe UI", sans-serif;
  --font-body: "Atkinson Hyperlegible", "Helvetica Neue", Arial, sans-serif;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    color-scheme: dark;
    --bg: #10161d; --surface: #19212b; --ink: #e9eef3; --muted: #9aa8b6; --line: #2d3946;
    --open: #5ad0b3; --barre: #86adff; --small: #f0b566; --on-dot: #10161d;
  }
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --bg: #10161d; --surface: #19212b; --ink: #e9eef3; --muted: #9aa8b6; --line: #2d3946;
  --open: #5ad0b3; --barre: #86adff; --small: #f0b566; --on-dot: #10161d;
}
.fam-open  { --fam: var(--open); }
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
.loop .whole { grid-column: span 2; }  /* a chord that lasts the whole bar */
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

.linkrow { display: flex; flex-wrap: wrap; gap: 8px; }

.points { margin: 0; padding-left: 1.2em; display: grid; gap: 8px; max-width: 62ch; }


/* chapter list */
.chapters { list-style: none; margin: 0; padding: 0; border-top: 1px solid var(--line); }
.chapters li { display: grid; gap: 2px; padding: 10px 0; border-bottom: 1px solid var(--line); }
.chapters a { display: grid; grid-template-columns: 3.4em 1fr; gap: 8px; text-decoration: none; font-weight: 700; }
.chapters .t { font-variant-numeric: tabular-nums; text-decoration: underline; text-underline-offset: 3px; }
.chapters .what { padding-left: calc(3.4em + 8px); color: var(--muted); font-size: .9375rem; }
.lesson-part { display: grid; gap: 8px; }
.lesson-part h3 { font-size: 1.125rem; font-weight: 700; }
.lesson-part h3 span { font: 400 .9375rem/1 var(--font-body); color: var(--muted); margin-left: 6px; font-variant-numeric: tabular-nums; }
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
      <nav class="player-jumps" aria-label="Jump to a section">{"".join(f'<a {moment(at, name)}>{escape(name)}</a>' for name, at in PARTS)}</nav>
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
""".replace("__VIDEO__", VIDEO_ID).replace(
    "__LABELS__", json.dumps({v["id"]: f"Part {part}" for part, v in VIDEOS.items()}))

JS = r"""
(function () {
  var boxes = Array.prototype.slice.call(document.querySelectorAll('input[data-got]'));
  var out = document.getElementById('progress');
  var KEY = 'gild-the-lily-shapes';
  var saved = {};
  try { saved = JSON.parse(localStorage.getItem(KEY) || '{}') || {}; } catch (e) { saved = {}; }
  function render() {
    var n = boxes.filter(function (b) { return b.checked; }).length;
    out.textContent = n === 0 ? 'Tick each shape off as you get it clean.'
      : n === boxes.length ? 'All ' + n + ' shapes ticked off. Time to play the song through in order.'
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

NUMBER_WORDS = {11: "eleven", 3: "three"}


def chapter_list(part):
    v = VIDEOS[part]
    items = "".join(
        f'<li><a {moment((part, t), title)}><span class="t">{mmss(t)}</span><span class="ct">{escape(title)}</span></a>'
        f'<span class="what">{escape(what)}</span></li>'
        for t, title, what in CHAPTERS[part])
    return (f'<div class="lesson-part"><h3>Part {part}<span>{mmss(v["length"])}</span></h3>'
            f'<ol class="chapters">{items}</ol></div>')


def page():
    n = len(CHORDS)
    cards = "".join(card(ch) for ch in CHORDS)
    v1, v2 = VIDEOS[1], VIDEOS[2]
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Gild the Lily Chord Shapes</title>
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
  <h1>Gild the Lily: {NUMBER_WORDS[n]} chord shapes</h1>
  <p class="lede">The rhythm-guitar side of the Billy Strings song: the chords for the verse, chorus and bridge and the order the sections come in, worked out from William A. Yarbrough's two-part lesson. Tap any time on this page to play that moment of the lesson. The video stays on screen while you read.</p>
  <dl class="facts">
    <div><dt>Tuning</dt><dd>Standard. The lesson does not say so, but the frets it names only make these chords in standard tuning.</dd></div>
    <div><dt>Capo</dt><dd>None</dd></div>
    <div><dt>To learn</dt><dd>Nine chords, plus three-note versions of the two hardest</dd></div>
    <div><dt>Not here</dt><dd>The intro lick. Part 1 teaches it note by note; this page only points to it.</dd></div>
  </dl>
</header>

<section aria-labelledby="h-map">
  <h2 id="h-map">The song map</h2>
  <p>Four beats to the bar. A narrow box is two beats and a wide box is a whole bar. Tap a box to jump to its shape.</p>
  <div class="part">
    <div class="part-head"><h3>Intro lick</h3>{from_part("Intro lick")}</div>
    <p class="note">A single-note lick that comes round four times. The second pass stops early (1:10), the third adds a run (2:46) and the fourth has its own ending (3:22). The lesson gives it fret by fret; this page does not write it out.</p>
  </div>
  <div class="part">
    <div class="part-head"><h3>Verse</h3>{from_part("Verse")}</div>
    {chips(VERSE)}
    <p class="note">Two beats a chord, then D for a whole bar, as the lesson counts it. The four bars are played twice. There are lead lines over the verse on the record; the instructor's advice is to concentrate on the chords, especially if you are the only guitar. One chord chart found online has Am where this lesson plays C; this page follows the lesson.</p>
  </div>
  <div class="part">
    <div class="part-head"><h3>Chorus</h3>{from_part("Chorus")}</div>
    {chips(CHORUS)}
    <p class="note">After the first two chords it is one move four times: D and A for two beats each, then a third chord. That chord is Bm twice, then G twice. The last G is cut to two beats so the bass can walk down the low E string, fret 3 to fret 2 to open, and land on Em. The lesson counts everything from the first D out loud. It does not count the Bm and F#7 at the start, which are drawn here as a bar each.</p>
  </div>
  <div class="part">
    <div class="part-head"><h3>Bridge</h3>{from_part("Bridge")}</div>
    {chips(BRIDGE)}
    <p class="note">Heard once, after the second chorus. The instructor calls it the key change. The first F# chord is minor and the second is the F#7 from the chorus. The first D runs on across the bar line, six beats in all. After the last D there is a rest, then the intro lick. This is the least certain section on the page: the beat counts are partly read from the video, and one chord chart found online gives the chords differently.</p>
  </div>
</section>

<section aria-labelledby="h-order">
  <h2 id="h-order">The whole song, in order</h2>
  <p>This is the order as the instructor describes it in part 2. He talks it through without playing the whole song and hesitates in places, and this page has not checked it against the recording.</p>
  <ol class="steps">
    <li>Intro lick, four passes.</li>
    <li>Verse.</li>
    <li>Chorus. It ends on Em, and a short piece of the intro lick leads back to the top.</li>
    <li>Intro, verse and chorus again.</li>
    <li>Bridge, then a rest.</li>
    <li>Intro lick twice: once straight through, once stopping early.</li>
    <li>A solo over one pass of the verse chords. If you are not improvising, the instructor suggests strumming the verse chords or repeating the tune.</li>
    <li>Verse, as before.</li>
    <li>Chorus, this time with no bridge after it.</li>
    <li>Outro: the intro lick with extra notes on the end.</li>
  </ol>
  <div class="linkrow">{watch((2, 360), "The order: part 2 at", "Song order")} {watch((2, 483), "After the bridge: part 2 at", "After the bridge")} {watch((2, 584), "Outro: part 2 at", "Outro")}</div>
</section>

<section aria-labelledby="h-fam">
  <h2 id="h-fam">Three kinds of shape cover all {NUMBER_WORDS[n]}</h2>
  <ul class="families">
    <li class="fam-open"><span class="sw"></span><span><strong>Open chords.</strong> D, Am, G, C, A and Em. The lesson assumes you know these. Am is the one it never spells out.</span></li>
    <li class="fam-barre"><span class="sw"></span><span><strong>Barre at fret 2.</strong> Bm, F#7 and F#m all keep the index finger across fret 2. F#7 and F#m are each the F major shape with one finger lifted: the pinky for F#7, the middle finger for F#m.</span></li>
    <li class="fam-small"><span class="sw"></span><span><strong>Three-note versions.</strong> The instructor's stand-ins for Bm and F#7 if the full barre is a struggle. It is one small hand shape, moved across one string.</span></li>
  </ul>
  <p class="readme"><b>Reading the diagrams:</b> the left line is the low E string and the right line is the high E. The thick line at the top is the nut. Numbers are fingers, 1 for index through 4 for pinky, and a bar across several strings is one finger laid flat. <b>×</b> marks a string that is not part of the shape and a ring marks an open string. The letters underneath are the notes that sound. Frets and strings are the ones called out in the lesson and checked against the video; Am is read from the video alone. Finger numbers follow the lesson where it names a finger and the usual fingering otherwise.</p>
</section>

<section aria-labelledby="h-shapes">
  <h2 id="h-shapes">The shapes, in the order the song reaches them</h2>
  <p class="progress" id="progress" aria-live="polite">Tick each shape off as you get it clean.</p>
  <div class="cards">{cards}</div>
</section>

<section aria-labelledby="h-points">
  <h2 id="h-points">What the lesson stresses</h2>
  <ul class="points">
    <li>On the three-note shapes, sound only the strings you are holding. The instructor plays them both ways to show the difference.</li>
    <li>Let the index finger do the muting, and keep it as relaxed as you can. He says the index is what stops the unused strings from ringing.</li>
    <li>He often turns a minor chord into a minor seventh by lifting a finger, as with Em7 and F#m7. It is easier to hold and leaves a finger free.</li>
    <li>He rates this an intermediate lesson and does not teach the open chords from scratch.</li>
  </ul>
  <div class="linkrow">{watch((2, 91), "Muting: part 2 at", "Muting the open strings")} {watch((2, 133), "The index finger: part 2 at", "Relaxing the index finger")}</div>
</section>

<section aria-labelledby="h-practice">
  <h2 id="h-practice">A practice order</h2>
  <ol class="steps">
    <li>Loop the verse: D, Am, G, D, then D, C and a full bar of D. Count two beats a chord.</li>
    <li>Get Bm and F#7 clean on their own, as full barres or as the three-note versions, with nothing else ringing.</li>
    <li>Drill D to A to Bm: two beats, two beats, then a bar. Then the same with G in place of Bm.</li>
    <li>Add the end of the chorus: two beats of G, the walk down the low E string, and a bar of Em.</li>
    <li>Add the bridge: F#m, C and D, then F#7, C and D.</li>
    <li>Play the sections in the order listed above, with the intro lick wherever the list calls for it.</li>
  </ol>
</section>

<section aria-labelledby="h-video">
  <h2 id="h-video">Find it in the videos</h2>
  {chapter_list(1)}
  {chapter_list(2)}
</section>

<footer class="source">
  <p>Source: <a href="https://youtu.be/{v1["id"]}">{escape(v1["title"])}</a> and <a href="https://youtu.be/{v2["id"]}">Part 2</a> by William A. Yarbrough on YouTube. Part 1 teaches the intro lick and the verse; part 2 teaches the chorus, the bridge, the order of the song and the outro.</p>
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
