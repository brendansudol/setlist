#!/usr/bin/env python3
"""Gild the Lily, the pre-intro: seven bars of tab redrawn as a practice sheet.

The notes were read off the tab that B-RoM's lesson shows on screen from 3:13
to 3:31. This script holds them as data, checks them, draws every bar as SVG
and writes index.html next to itself, with a small player that plucks the
notes at any tempo and loops any bar. Standard library only.

Run:  python3 gild-the-lily/pre-intro/build.py
"""
import json
from html import escape
from pathlib import Path

VIDEO = {
    "id": "U9BqvaBOR8Y",
    "title": 'How to play "Gild The Lily" - Billy Strings - Guitar Lesson with Tab',
    "by": "B-RoM",
    "length": 367,
}
START, END = 193, 211          # 3:13 to 3:31, the stretch this page covers
LESSON_BPM = 100               # a rough reading of how fast the lesson's cursor moves


def yt(t):
    return f"https://www.youtube.com/watch?v={VIDEO['id']}&t={t}s"


def mmss(t):
    return f"{t // 60}:{t % 60:02d}"


# Strings are numbered the way guitarists number them: 1 is the high E.
# (letter drawn at the start of a row, spoken name, MIDI note of the open string)
STRINGS = {
    1: ("e", "high E", 64),
    2: ("B", "B", 59),
    3: ("G", "G", 55),
    4: ("D", "D", 50),
    5: ("A", "A", 45),
    6: ("E", "low E", 40),
}

# ---------------------------------------------------------------------------
# The seven bars. Time is counted in eighth notes, eight to the bar.
#
# A bar is a list of steps, in order. A step is
#     (how many eighths it lasts, [(string, fret, note on the staff), ...])
# with an optional third item: "h" if the step is hammered on from the note
# before it, "p" if it is pulled off. Those notes are not picked.
#
# "note on the staff" is what the lesson's notation shows above the tab. It was
# read separately from the fret numbers, and check() makes sure the two agree.
# Guitar music is written an octave above where it sounds.
# ---------------------------------------------------------------------------
BARS = [
    dict(chord="D", at=193, steps=[
        (2, [(1, 2, "F#5"), (4, 0, "D4")]),
        (2, [(3, 2, "A4")]),
        (1, [(1, 2, "F#5"), (4, 0, "D4")]),
        (3, [(1, 3, "G5")], "h"),
    ]),
    dict(chord="Am", at=193, steps=[
        (2, [(2, 1, "C5"), (5, 0, "A3")]),
        (2, [(4, 2, "E4")]),
        (1, [(2, 1, "C5")]),
        (1, [(3, 2, "A4")]),
        (2, [(4, 2, "E4")]),
    ]),
    dict(chord="G", at=193, steps=[
        (1, [(3, 2, "A4"), (6, 3, "G3")]),
        (1, [(3, 4, "B4")]),
        (2, [(6, 3, "G3")]),
        (1, [(3, 4, "B4")]),
        (2, [(3, 2, "A4")], "p"),
        (1, [(3, 2, "A4")]),
    ]),
    dict(chord="D", at=201, steps=[
        (2, [(4, 0, "D4")]),
        (2, [(4, 0, "D4")]),
        (4, [(3, 2, "A4"), (4, 0, "D4")]),
    ]),
    dict(chord="D", at=201, steps=[
        (2, [(4, 0, "D4")]),
        (2, [(4, 0, "D4")]),
        (1, [(1, 2, "F#5"), (4, 0, "D4")]),
        (3, [(1, 3, "G5")], "h"),
    ]),
    dict(chord="Am", at=201, steps=[
        (4, [(2, 1, "C5"), (5, 0, "A3")]),
        (4, [(2, 1, "C5")]),
    ]),
    dict(chord="D", at=208, steps=[
        (8, [(4, 4, "F#4"), (5, 5, "D4")]),
    ]),
]

# What to say about each bar, in the order of BARS.
BAR_NOTES = [
    "The open D string under an open D shape. On beat 3, pick fret 2 of the high E and hammer on to fret 3, then let it ring through beat 4.",
    "The open A string under an Am shape. Every fretted note in the bar is already under your fingers if you hold the chord.",
    "The bass moves to fret 3 of the low E. Over it the G string goes 2, 4, then 4 pulled off to 2, and 2 once more on the last half beat.",
    "Two open D strings, a beat each, then the open D with fret 2 of the G string, held for two beats.",
    "Two open D strings again, then the ending of bar 1: fret 2 of the high E hammered on to fret 3.",
    "The open A string with fret 1 of the B string, then fret 1 of the B string alone. Two beats each.",
    "Two notes together, held for the whole bar: fret 5 of the A string and fret 4 of the D string. That is D with F# above it.",
]

# Where each line of the lesson's tab comes up on screen.
LINES = [("Bars 1 to 3", 193), ("Bars 4 to 6", 201), ("Bar 7", 208)]

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
COUNT = ["1", "&", "2", "&", "3", "&", "4", "&"]
COUNT_SPOKEN = ["beat 1", "the and of 1", "beat 2", "the and of 2",
                "beat 3", "the and of 3", "beat 4", "the and of 4"]


def note_name(midi):
    return f"{NOTE_NAMES[midi % 12]}{midi // 12 - 1}"


def sounding(string, fret):
    return STRINGS[string][2] + fret


def unpack(step):
    dur, notes = step[0], step[1]
    return dur, notes, (step[2] if len(step) > 2 else None)


def check():
    assert len(BARS) == len(BAR_NOTES) == 7
    for n, bar in enumerate(BARS, 1):
        slot, before, lowest = 0, {}, None
        for step in bar["steps"]:
            dur, notes, tech = unpack(step)
            assert dur >= 1 and notes, f"bar {n}: an empty step"
            assert len({s for s, _, _ in notes}) == len(notes), f"bar {n}: two notes on one string"
            for string, fret, written in notes:
                assert string in STRINGS and 0 <= fret <= 12, f"bar {n}: no such note"
                # the staff and the tab were read separately and have to agree
                assert note_name(sounding(string, fret) + 12) == written, (
                    f"bar {n}: string {string} fret {fret} is written "
                    f"{note_name(sounding(string, fret) + 12)}, not {written}")
                pitch = sounding(string, fret)
                lowest = pitch if lowest is None else min(lowest, pitch)
            if tech:
                assert tech in ("h", "p") and len(notes) == 1, f"bar {n}: a slur joins single notes"
                string, fret, _ = notes[0]
                assert string in before, f"bar {n}: nothing to slur from on string {string}"
                assert (fret > before[string]) == (tech == "h") and fret != before[string], (
                    f"bar {n}: a hammer-on goes up and a pull-off comes down")
            before = {s: f for s, f, _ in notes}
            slot += dur
        assert slot == 8, f"bar {n} is {slot} eighths long, not 8"
        # the lowest note of every bar is the root of the chord it is labelled with
        assert NOTE_NAMES[lowest % 12] == bar["chord"].rstrip("m"), f"bar {n}: bass is not {bar['chord']}"
        assert START <= bar["at"] < END
    assert [t for _, t in LINES] == sorted({bar["at"] for bar in BARS})
    assert 0 <= START < END < VIDEO["length"]


# ---------------------------------------------------------------------------
# Drawing. One SVG per bar, all the same size, so the bars can sit four to a
# row on a wide window and two to a row on a phone.
# ---------------------------------------------------------------------------
W, H = 190, 154
X0, STEP = 27, 19.5            # x of the first eighth, and the gap to the next
Y0, GAP = 50, 15               # y of the high E string, and the gap to the next
PILL_H, PILL_LEAD = 13, 7      # the tail behind each number; the number sits 7 in
COUNT_Y = 147


def x_of(slot):
    return X0 + slot * STEP


def y_of(string):
    return Y0 + (string - 1) * GAP


def num(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def bar_svg(i, bar):
    o = [f'<svg viewBox="0 0 {W} {H}" aria-hidden="true" focusable="false">']
    for beat in range(4):                       # faint guides down from each beat
        x = num(x_of(beat * 2))
        o.append(f'<line class="guide" x1="{x}" y1="{Y0 - 8}" x2="{x}" y2="{COUNT_Y - 10}"/>')
    for s in STRINGS:
        o.append(f'<line class="sl" x1="0" y1="{y_of(s)}" x2="{W}" y2="{y_of(s)}"/>')
    for x in (0.6, W - 0.6):
        o.append(f'<line class="bl" x1="{x}" y1="{Y0}" x2="{x}" y2="{y_of(6)}"/>')
    o.append('<g class="slab">' + "".join(
        f'<rect x="4" y="{y_of(s) - 5}" width="10" height="10"/><text x="9" y="{y_of(s) + 3}">{STRINGS[s][0]}</text>'
        for s in STRINGS) + '</g>')
    o.append(f'<text class="bn" x="3" y="20">{i + 1}</text>'
             f'<text class="ch" x="15" y="20">{escape(bar["chord"])}</text>')

    slot, starts, prev_slot = 0, set(), 0
    for j, step in enumerate(bar["steps"]):
        dur, notes, tech = unpack(step)
        x = x_of(slot)
        starts.add(slot)
        if tech:                                # the arc from the note before
            y = y_of(notes[0][0]) - PILL_H / 2 - 1.5
            x1, x2 = x_of(prev_slot) + 1, x - 1
            mid = (x1 + x2) / 2
            o.append(f'<path class="slur" d="M{num(x1)} {num(y)} Q{num(mid)} {num(y - 9)} {num(x2)} {num(y)}"/>'
                     f'<text class="tech" x="{num(mid)}" y="{num(y - 7)}">{tech.upper()}</text>')
        g = [f'<g class="step" data-step="{j}">']
        for string, fret, _ in notes:
            y = y_of(string)
            g.append(f'<rect class="pill" x="{num(x - PILL_LEAD)}" y="{num(y - PILL_H / 2)}" '
                     f'width="{num(dur * STEP - 3)}" height="{PILL_H}" rx="{num(PILL_H / 2)}"/>'
                     f'<text class="fr" x="{num(x)}" y="{num(y + 4.3)}">{fret}</text>')
        g.append('</g>')
        o.append("".join(g))
        prev_slot, slot = slot, slot + dur

    for k, label in enumerate(COUNT):
        cls = "cnt hit" if k in starts else "cnt"
        o.append(f'<text class="{cls}" x="{num(x_of(k))}" y="{COUNT_Y}">{escape(label)}</text>')
    o.append(f'<line class="cursor" x1="{X0}" y1="{Y0 - 9}" x2="{X0}" y2="{y_of(6) + 9}"/>')
    o.append('</svg>')
    return "".join(o)


def bar_words(i, bar):
    """The bar in words, for anyone who is not looking at the drawing."""
    parts, slot = [], 0
    for step in bar["steps"]:
        dur, notes, tech = unpack(step)
        what = " with ".join(
            f"{STRINGS[s][1]} string {'open' if f == 0 else f'fret {f}'}" for s, f, _ in notes)
        how = {"h": "hammer on to ", "p": "pull off to ", None: ""}[tech]
        parts.append(f"{COUNT_SPOKEN[slot].capitalize()}: {how}{what}.")
        slot += dur
    return f"Bar {i + 1}, {bar['chord']}. " + " ".join(parts)


def bar_button(i, bar):
    return (f'<button type="button" class="bar" data-bar="{i}" aria-pressed="false" '
            f'aria-label="Loop bar {i + 1}" aria-describedby="bar-words-{i}">{bar_svg(i, bar)}'
            f'<span class="sr" id="bar-words-{i}">{escape(bar_words(i, bar))}</span></button>')


def player_data():
    bars = []
    for bar in BARS:
        steps, slot = [], 0
        for step in bar["steps"]:
            dur, notes, tech = unpack(step)
            steps.append({"slot": slot, "dur": dur, "soft": bool(tech),
                          "notes": [[s, sounding(s, f)] for s, f, _ in notes]})
            slot += dur
        bars.append(steps)
    return {"x0": X0, "step": STEP, "bars": bars}


PLAY_ICON = '<svg class="ico ico-play" viewBox="0 0 12 12" aria-hidden="true"><path d="M2 1l9 5-9 5z"/></svg>'
STOP_ICON = '<svg class="ico ico-stop" viewBox="0 0 12 12" aria-hidden="true"><rect x="1.5" y="1.5" width="9" height="9" rx="1.5"/></svg>'

CSS = r"""
:root {
  /* Same paper, ink and type as the other pages. Green is the colour those pages give
     open chords, and every chord here is one; it also marks the note being played. */
  --bg: #eef1f4;
  --surface: #ffffff;
  --ink: #16202b;
  --muted: #566472;
  --line: #d3dae1;
  --open: #0c7a64;
  --on-dot: #ffffff;
  --pill: #e3e8ed;
  --wash: rgb(12 122 100 / .07);
  --font-display: "Bricolage Grotesque", "Avenir Next", "Segoe UI", sans-serif;
  --font-body: "Atkinson Hyperlegible", "Helvetica Neue", Arial, sans-serif;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    color-scheme: dark;
    --bg: #10161d; --surface: #19212b; --ink: #e9eef3; --muted: #9aa8b6; --line: #2d3946;
    --open: #5ad0b3; --on-dot: #10161d; --pill: #2b3643; --wash: rgb(90 208 179 / .09);
  }
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --bg: #10161d; --surface: #19212b; --ink: #e9eef3; --muted: #9aa8b6; --line: #2d3946;
  --open: #5ad0b3; --on-dot: #10161d; --pill: #2b3643; --wash: rgb(90 208 179 / .09);
}

* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body { margin: 0; background: var(--bg); color: var(--ink); font: 400 16px/1.5 var(--font-body); }
main { max-width: 920px; margin: 0 auto; padding: 24px 16px 56px; display: grid; gap: 36px; }
h1, h2 { font-family: var(--font-display); text-wrap: balance; margin: 0; line-height: 1.1; }
h1 { font-size: clamp(1.75rem, 7vw, 2.5rem); font-weight: 800; letter-spacing: -0.02em; }
h2 { font-size: 1.375rem; font-weight: 700; letter-spacing: -0.01em; }
p { margin: 0; max-width: 62ch; }
a { color: inherit; }
a:focus-visible, button:focus-visible, input:focus-visible { outline: 3px solid var(--open); outline-offset: 2px; border-radius: 4px; }
section { display: grid; gap: 14px; }
header.top { display: grid; gap: 10px; }
.eyebrow { font-size: .8125rem; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); font-weight: 700; }
.lede { font-size: 1.0625rem; color: var(--muted); }
.note { font-size: .9375rem; color: var(--muted); }
.sr { position: absolute; width: 1px; height: 1px; overflow: hidden; clip-path: inset(50%); white-space: nowrap; }

/* the tab: two bars to a row on a phone, four on anything wider */
.sheet { background: var(--surface); border: 1px solid var(--line); border-radius: 10px; padding: 12px 6px 10px; }
.tab { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); row-gap: 8px; }
.bar { position: relative; display: block; width: 100%; margin: 0; padding: 0; border: 0; border-radius: 6px; background: none; color: inherit; font: inherit; cursor: pointer; -webkit-tap-highlight-color: transparent; transition: opacity .15s; }
.bar svg { display: block; width: 100%; height: auto; }
.bar.out { opacity: .32; }          /* outside the part being looped */
.bar.now { background: var(--wash); }
svg text { font-family: var(--font-body); }
.sl { stroke: var(--ink); stroke-width: 1; opacity: .3; }
.bl { stroke: var(--ink); stroke-width: 1.2; opacity: .55; }
.guide { stroke: var(--ink); stroke-width: 1; opacity: .07; }
.bn { fill: var(--muted); font-size: 9px; font-variant-numeric: tabular-nums; }
.ch { fill: var(--open); font-family: var(--font-display); font-size: 15px; font-weight: 800; }
.pill { fill: var(--pill); }
.fr { fill: var(--ink); font-size: 12.5px; font-weight: 700; text-anchor: middle; font-variant-numeric: tabular-nums; }
.step.on .pill { fill: var(--open); }
.step.on .fr { fill: var(--on-dot); }
.slur { fill: none; stroke: var(--ink); stroke-width: 1.3; stroke-linecap: round; }
.tech { fill: var(--ink); font-size: 8px; font-weight: 700; text-anchor: middle; paint-order: stroke; stroke: var(--surface); stroke-width: 3px; }
.cnt { fill: var(--muted); font-size: 9.5px; text-anchor: middle; opacity: .55; }
.cnt.hit { fill: var(--ink); font-weight: 700; opacity: 1; }
.cursor { stroke: var(--open); stroke-width: 2; stroke-linecap: round; opacity: 0; }
.bar.now .cursor { opacity: .9; }
/* string names: only on the bar that starts a row */
.slab { display: none; }
.slab rect { fill: var(--surface); }
.slab text { fill: var(--muted); font-size: 8px; font-weight: 700; text-anchor: middle; }
.tab > :nth-child(2n+1) .slab { display: inline; }
.next { display: grid; align-content: center; gap: 2px; margin: 10px 6px; padding: 10px 12px; border: 1.5px dashed var(--line); border-radius: 8px; text-decoration: none; font-size: .875rem; color: var(--muted); }
.next b { font-family: var(--font-display); font-size: 1rem; color: var(--ink); }
.next:hover { border-color: var(--ink); }
@media (min-width: 720px) {
  .sheet { padding: 16px 12px 12px; }
  .tab { grid-template-columns: repeat(4, minmax(0, 1fr)); row-gap: 14px; }
  .tab > :nth-child(2n+1) .slab { display: none; }
  .tab > :nth-child(4n+1) .slab { display: inline; }
}

/* the player's controls stay at the bottom of the window while the tab is on screen */
.practice { gap: 10px; }
.controls { position: sticky; bottom: 8px; z-index: 2; display: flex; flex-wrap: wrap; align-items: center; gap: 8px 10px; padding: 8px 10px; background: var(--surface); border: 1px solid var(--line); border-radius: 14px; box-shadow: 0 6px 20px rgb(0 0 0 / .12); }
.pbtn { flex: none; display: inline-flex; align-items: center; justify-content: center; gap: 7px; min-width: 44px; min-height: 40px; padding: 0 13px; border: 1px solid var(--line); border-radius: 99px; background: transparent; color: var(--ink); font: 700 .8125rem/1 var(--font-body); font-variant-numeric: tabular-nums; cursor: pointer; -webkit-tap-highlight-color: transparent; }
.pbtn[aria-pressed="true"] { background: var(--ink); border-color: var(--ink); color: var(--bg); }
.go { min-width: 92px; min-height: 44px; background: var(--ink); border-color: var(--ink); color: var(--bg); font-size: .9375rem; }
.ico { width: 11px; height: 11px; fill: currentColor; flex: none; }
.go .ico-stop, .go[aria-pressed="true"] .ico-play { display: none; }
.go[aria-pressed="true"] .ico-stop { display: block; }
.tempo { flex: 1 1 190px; display: flex; align-items: center; gap: 8px; min-height: 40px; font-size: .8125rem; font-weight: 700; color: var(--muted); }
.tempo input { flex: 1 1 0; min-width: 0; accent-color: var(--open); }
.tempo output { min-width: 4.6em; color: var(--ink); font-variant-numeric: tabular-nums; }
.ranges { display: flex; gap: 6px; }
.click { display: inline-flex; align-items: center; gap: 6px; min-height: 40px; font-size: .8125rem; font-weight: 700; color: var(--muted); cursor: pointer; }
.click input { width: 18px; height: 18px; margin: 0; accent-color: var(--open); }

.facts { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1px; margin: 0; background: var(--line); border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }
.facts div { background: var(--surface); padding: 10px 12px; }
.facts dt { font-size: .75rem; letter-spacing: .06em; text-transform: uppercase; color: var(--muted); font-weight: 700; }
.facts dd { margin: 2px 0 0; font-size: .9375rem; }
.bars { list-style: none; margin: 0; padding: 0; display: grid; gap: 0; border-top: 1px solid var(--line); max-width: 68ch; }
.bars li { display: grid; grid-template-columns: 2.6em 3em 1fr; gap: 8px; align-items: baseline; padding: 10px 0; border-bottom: 1px solid var(--line); font-size: .9375rem; }
.bars .n { color: var(--muted); font-variant-numeric: tabular-nums; }
.bars .c { font: 800 1.0625rem/1.2 var(--font-display); color: var(--open); }
.linkrow { display: flex; flex-wrap: wrap; gap: 8px; }
.watch { display: inline-flex; align-items: center; gap: 7px; min-height: 40px; padding: 6px 14px 6px 12px; border-radius: 99px; background: var(--ink); color: var(--bg); text-decoration: none; font-size: .875rem; }
.watch b { font-variant-numeric: tabular-nums; }
.source { font-size: .875rem; color: var(--muted); border-top: 1px solid var(--line); padding-top: 16px; display: grid; gap: 8px; }
@media print {
  body { background: #fff; }
  .controls, .linkrow, .next, .hint { display: none; }
  .sheet { border: 0; padding: 0; }
}
"""

# The player. It plucks a simple synthesised string (Karplus-Strong) for every
# note, a step at a time, a little ahead of the clock, so a change of tempo is
# heard on the very next note.
JS = r"""
(function () {
  var DATA = __DATA__;
  var AC = window.AudioContext || window.webkitAudioContext;
  var bars = [].slice.call(document.querySelectorAll('.bar'));
  var go = document.getElementById('go'), goText = document.getElementById('go-text');
  var tempo = document.getElementById('tempo'), tempoOut = document.getElementById('tempo-out');
  var clickBox = document.getElementById('click');
  var rangeBtns = [].slice.call(document.querySelectorAll('[data-from]'));
  var LAST = DATA.bars.length - 1;

  var ctx = null, master = null, bufs = {};
  var playing = false, timer = 0, raf = 0;
  var range = [0, LAST];
  var next = null;        // the step to schedule next: {bar, step, time}
  var queue = [];         // steps already scheduled: {t0, t1, bar, slot, dur, el, on}
  var ringing = {};       // string number -> the note sounding on it

  function eighth() { return 30 / Number(tempo.value); }

  function buffer(midi) {
    if (bufs[midi]) return bufs[midi];
    var sr = ctx.sampleRate, f = 440 * Math.pow(2, (midi - 69) / 12);
    var n = Math.max(2, Math.round(sr / f - 0.5)), len = Math.floor(sr * 3.2);
    var b = ctx.createBuffer(1, len, sr), d = b.getChannelData(0), i, prev = 0;
    for (i = 0; i < n; i++) { prev = d[i] = 0.55 * (Math.random() * 2 - 1) + 0.45 * prev; }
    d[n] = 0.5 * d[0];
    for (i = n + 1; i < len; i++) { d[i] = 0.998 * 0.5 * (d[i - n] + d[i - n - 1]); }
    var fade = Math.floor(sr * 0.15);
    for (i = 0; i < fade; i++) { d[len - 1 - i] *= i / fade; }
    bufs[midi] = b;
    return b;
  }

  function pluck(string, midi, t, soft) {
    var old = ringing[string];
    if (old) { old.gain.gain.setTargetAtTime(0, t, 0.012); old.src.stop(t + 0.25); }
    var src = ctx.createBufferSource(), gain = ctx.createGain();
    src.buffer = buffer(midi);
    gain.gain.value = soft ? 0.5 : 0.85;
    src.connect(gain); gain.connect(master);
    src.start(t, soft ? 0.012 : 0);       // a hammer-on or pull-off has no pick attack
    ringing[string] = { src: src, gain: gain };
  }

  function tick(t, first) {
    var osc = ctx.createOscillator(), gain = ctx.createGain();
    osc.frequency.value = first ? 1568 : 1047;
    gain.gain.setValueAtTime(0.0001, t);
    gain.gain.exponentialRampToValueAtTime(first ? 0.5 : 0.32, t + 0.002);
    gain.gain.exponentialRampToValueAtTime(0.0001, t + 0.06);
    osc.connect(gain); gain.connect(master);
    osc.start(t); osc.stop(t + 0.08);
  }

  function pump() {
    var horizon = ctx.currentTime + 0.18;
    while (playing && next.time < horizon) {
      var steps = DATA.bars[next.bar], st = steps[next.step], e = eighth(), k;
      for (k = 0; k < st.notes.length; k++) pluck(st.notes[k][0], st.notes[k][1], next.time, st.soft);
      if (clickBox.checked) {
        for (k = st.slot; k < st.slot + st.dur; k++) if (k % 2 === 0) tick(next.time + (k - st.slot) * e, k === 0);
      }
      queue.push({ t0: next.time, t1: next.time + st.dur * e, bar: next.bar, slot: st.slot, dur: st.dur,
                   el: bars[next.bar].querySelectorAll('.step')[next.step], on: false });
      next.time += st.dur * e;
      if (++next.step >= steps.length) { next.step = 0; next.bar = next.bar >= range[1] ? range[0] : next.bar + 1; }
    }
  }

  function draw() {
    var now = ctx.currentTime, i, q, cur = null;
    for (i = queue.length - 1; i >= 0; i--) {
      if (now >= queue[i].t1) { queue[i].el.classList.remove('on'); queue.splice(i, 1); }
    }
    for (i = 0; i < queue.length; i++) {
      q = queue[i];
      if (now >= q.t0) { cur = q; if (!q.on) { q.on = true; q.el.classList.add('on'); } }
    }
    bars.forEach(function (b, n) { b.classList.toggle('now', !!cur && cur.bar === n); });
    if (cur) {
      var x = DATA.x0 + (cur.slot + cur.dur * (now - cur.t0) / (cur.t1 - cur.t0)) * DATA.step;
      var line = bars[cur.bar].querySelector('.cursor');
      line.setAttribute('x1', x.toFixed(1)); line.setAttribute('x2', x.toFixed(1));
    }
    if (playing) raf = requestAnimationFrame(draw);
  }

  function start() {
    if (!AC) return;
    if (!ctx) {
      ctx = new AC();
      master = ctx.createGain(); master.gain.value = 0.5; master.connect(ctx.destination);
    }
    ctx.resume();
    playing = true;
    go.setAttribute('aria-pressed', 'true'); goText.textContent = 'Stop';
    var t = ctx.currentTime + 0.12, e = eighth();
    for (var i = 0; i < 4; i++) tick(t + i * 2 * e, i === 0);      // one bar counted in
    next = { bar: range[0], step: 0, time: t + 8 * e };
    timer = setInterval(pump, 25); pump();
    raf = requestAnimationFrame(draw);
  }

  function stop() {
    playing = false;
    clearInterval(timer); cancelAnimationFrame(raf);
    go.setAttribute('aria-pressed', 'false'); goText.textContent = 'Play';
    if (ctx) {
      var t = ctx.currentTime;
      Object.keys(ringing).forEach(function (s) {
        ringing[s].gain.gain.cancelScheduledValues(t);
        ringing[s].gain.gain.setTargetAtTime(0, t, 0.03);
        try { ringing[s].src.stop(t + 0.3); } catch (err) {}
      });
      // notes and clicks already handed to the clock for the next instant are cut with the rest
      master.gain.cancelScheduledValues(t);
      master.gain.setTargetAtTime(0, t, 0.02);
      var old = master;
      master = ctx.createGain(); master.gain.value = 0.5; master.connect(ctx.destination);
      setTimeout(function () { old.disconnect(); }, 400);
    }
    ringing = {};
    queue.forEach(function (q) { q.el.classList.remove('on'); });
    queue = [];
    bars.forEach(function (b) { b.classList.remove('now'); });
  }

  function setRange(a, b) {
    range = [a, b];
    var whole = a === 0 && b === LAST;
    bars.forEach(function (el, n) {
      el.classList.toggle('out', n < a || n > b);
      el.setAttribute('aria-pressed', String(!whole && a === b && n === a));
    });
    rangeBtns.forEach(function (btn) {
      btn.setAttribute('aria-pressed', String(Number(btn.dataset.from) === a && Number(btn.dataset.to) === b));
    });
    if (playing) { stop(); start(); }
  }

  go.addEventListener('click', function () { if (playing) stop(); else start(); });
  tempo.addEventListener('input', function () { tempoOut.textContent = tempo.value + ' bpm'; });
  rangeBtns.forEach(function (btn) {
    btn.addEventListener('click', function () { setRange(Number(btn.dataset.from), Number(btn.dataset.to)); });
  });
  bars.forEach(function (el, n) {
    el.addEventListener('click', function () {
      if (range[0] === n && range[1] === n) setRange(0, LAST); else setRange(n, n);
    });
  });
  document.addEventListener('keydown', function (e) {
    if (e.key !== ' ' || e.metaKey || e.ctrlKey || e.altKey) return;
    var t = e.target.tagName;
    if (t === 'BUTTON' || t === 'INPUT' || t === 'A' || t === 'TEXTAREA') return;
    e.preventDefault();
    if (playing) stop(); else start();
  });
  document.addEventListener('visibilitychange', function () { if (document.hidden && playing) stop(); });
  if (!AC) { go.disabled = true; goText.textContent = 'No sound here'; }
})();
"""


def page():
    bars = "".join(bar_button(i, bar) for i, bar in enumerate(BARS))
    notes = "".join(
        f'<li><span class="n">Bar {i + 1}</span><span class="c">{escape(bar["chord"])}</span><span>{escape(text)}</span></li>'
        for i, (bar, text) in enumerate(zip(BARS, BAR_NOTES)))
    links = "".join(
        f'<a class="watch" href="{yt(t)}">{PLAY_ICON}<span>{escape(label)} at <b>{mmss(t)}</b></span></a>'
        for label, t in LINES)
    chords = ", ".join(bar["chord"] for bar in BARS)
    js = JS.replace("__DATA__", json.dumps(player_data(), separators=(",", ":")))
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Gild the Lily: the pre-intro</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&amp;family=Bricolage+Grotesque:opsz,wght@12..96,600..800&amp;display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<main>

<header class="top">
  <p class="eyebrow"><a href="../">Gild the Lily</a> &middot; practice sheet</p>
  <h1>The pre-intro, all seven bars</h1>
  <p class="lede">The slow figure that comes before the main lick, redrawn from the tab on screen in B-RoM's lesson between {mmss(START)} and {mmss(END)}. One bar per chord: {chords}.</p>
</header>

<section class="practice" aria-labelledby="h-tab">
  <h2 id="h-tab" class="sr">The tab</h2>
  <div class="sheet">
    <div class="tab">
      {bars}
      <a class="next" href="{yt(END)}"><b>Next: the main lick</b><span>The lesson's tab carries on from {mmss(END)}.</span></a>
    </div>
  </div>
  <div class="controls" role="group" aria-label="Play the tab">
    <button type="button" class="pbtn go" id="go" aria-pressed="false">{PLAY_ICON}{STOP_ICON}<span id="go-text">Play</span></button>
    <label class="tempo"><span>Tempo</span><input type="range" id="tempo" min="40" max="130" step="1" value="72"><output id="tempo-out" for="tempo">72 bpm</output></label>
    <div class="ranges" role="group" aria-label="What to loop">
      <button type="button" class="pbtn" data-from="0" data-to="6" aria-pressed="true">All</button>
      <button type="button" class="pbtn" data-from="0" data-to="2" aria-pressed="false">1&ndash;3</button>
      <button type="button" class="pbtn" data-from="3" data-to="6" aria-pressed="false">4&ndash;7</button>
    </div>
    <label class="click"><input type="checkbox" id="click" checked>Click</label>
  </div>
  <p class="note hint">Play counts one bar in, then loops until you stop it. Tap a bar to loop just that bar, and tap it again for the whole thing. The lesson plays this at roughly {LESSON_BPM} bpm; start slower. No sound on an iPhone usually means the silent switch is on.</p>
</section>

<section aria-labelledby="h-read">
  <h2 id="h-read">How to read it</h2>
  <dl class="facts">
    <div><dt>Lines</dt><dd>Six strings, high E at the top, low E at the bottom</dd></div>
    <div><dt>Numbers</dt><dd>Frets. 0 is the open string.</dd></div>
    <div><dt>Grey tails</dt><dd>How long each note lasts. Let it ring to the end of its tail.</dd></div>
    <div><dt>H and P</dt><dd>Hammer-on and pull-off. The second note is not picked.</dd></div>
    <div><dt>Underneath</dt><dd>The count, in eighths. Bold where a note starts.</dd></div>
    <div><dt>Tuning</dt><dd>Standard. The staff above the lesson's tab agrees with these frets.</dd></div>
  </dl>
</section>

<section aria-labelledby="h-bars">
  <h2 id="h-bars">Bar by bar</h2>
  <p>It follows the chords of the verse, a bar each, so most of it is a chord shape held down and picked one string at a time.</p>
  <ol class="bars">{notes}</ol>
  <p class="note">The chord names and the shapes are a reading of the notes. The lesson's tab does not name a chord over these bars; in every one the lowest note is the root of the chord given here.</p>
</section>

<section aria-labelledby="h-watch">
  <h2 id="h-watch">See it played</h2>
  <p>The lesson shows its tab a line at a time, with a cursor moving through it.</p>
  <div class="linkrow">{links}</div>
</section>

<footer class="source">
  <p>Source: <a href="{yt(START)}">{escape(VIDEO["title"])}</a> by {escape(VIDEO["by"])} on YouTube, {mmss(START)} to {mmss(END)}. The notes are the lesson's. The drawing, the count, the chord names and the bar-by-bar notes were made for this page.</p>
  <p>The sound is a synthesised pluck made in the browser, not a recording, and the {LESSON_BPM} bpm figure is an estimate from the speed of the lesson's cursor.</p>
</footer>

</main>
<script>{js}</script>
</body>
</html>
'''


if __name__ == "__main__":
    check()
    out = Path(__file__).resolve().parent / "index.html"
    html = page()
    out.write_text(html, encoding="utf-8")
    print(f"checked {len(BARS)} bars, wrote {out.name} ({len(html.encode('utf-8'))} bytes)")
