#!/usr/bin/env python3
"""Build a standalone interactive practice sheet from B-RoM's 69-bar score."""
import json
from html import escape
from pathlib import Path

from score import BARS, EIGHTH, PRE_INTRO, QUARTER, SECTIONS, TRIPLET, WHOLE

def yt(t):
    return f"https://www.youtube.com/watch?v=U9BqvaBOR8Y&t={t}s"


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

# Playing notes for the original seven-bar pre-intro.
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
LINES = [("Bars 1 to 3", 193), ("Bars 4 to 6", 201), ("Bar 7", 208), ("Main lick", 211)]

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
COUNT = ["1", "&", "2", "&", "3", "&", "4", "&"]
COUNT_SPOKEN = ["beat 1", "the and of 1", "beat 2", "the and of 2",
                "beat 3", "the and of 3", "beat 4", "the and of 4"]


def note_name(midi):
    return f"{NOTE_NAMES[midi % 12]}{midi // 12 - 1}"


def sounding(string, fret):
    return STRINGS[string][2] + fret


TECHNIQUES = {
    "hammer": "hammer on", "pull": "pull off", "bend": "bend up a half step",
    "slide": "slide from the previous fret", "slide in": "slide in from below",
    "vibrato": "vibrato",
}


def check():
    assert len(BARS) == 69 and len(BAR_NOTES) == len(PRE_INTRO)
    assert [n for a, b, _ in SECTIONS for n in range(a, b + 1)] == list(range(1, len(BARS) + 1))
    before = {}
    for n, bar in enumerate(BARS, 1):
        assert sum(st.ticks for st in bar.steps) == WHOLE, f"bar {n}: wrong duration"
        assert all(0 < at < WHOLE and name for at, name in bar.changes)
        for st in bar.steps:
            assert st.ticks > 0 and (not st.tech or st.tech in TECHNIQUES)
            assert st.pick in ("", "down", "up")
            assert st.notes or not (st.tech or st.pick), f"bar {n}: marking on a rest"
            frets = {s: f for s, f, _ in st.notes}
            assert len(frets) == len(st.notes), f"bar {n}: two notes on one string"
            for string, fret, written in st.notes:
                assert string in STRINGS and 0 <= fret <= 24
                assert note_name(sounding(string, fret) + 12) == written, f"bar {n}: {written} at {string}/{fret}"
            if st.tech in ("hammer", "pull", "slide"):
                string, fret, _ = st.notes[0]
                assert string in before and before[string] != fret, f"bar {n}: disconnected slur"
                if st.tech != "slide":
                    assert (fret > before[string]) == (st.tech == "hammer")
            before = frets


W, H = 270, 161
X0, X_END = 30, 261
Y0, GAP = 52, 15
COUNT_Y = 155


def y_of(string):
    return Y0 + (string - 1) * GAP


def num(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def timeline(bar, previous):
    # Guarantee space for two-digit frets even in the thirty-second-note slide.
    widths = [max(20, st.ticks * (X_END - X0) / WHOLE) for st in bar.steps]
    scale = (X_END - X0) / sum(widths)
    events, at, x = [], 0, X0
    for st, width in zip(bar.steps, widths):
        end = x + width * scale
        event = dict(at=at, dur=st.ticks, x=round(x, 2), endX=round(end, 2),
                     notes=[[s, sounding(s, f)] for s, f, _ in st.notes])
        if st.tech:
            event["tech"] = st.tech
        if st.tech == "slide":
            string, fret, _ = st.notes[0]
            event["slideOffset"] = next(f - fret for s, f, _ in previous.notes if s == string)
        events.append(event)
        at, x, previous = at + st.ticks, end, st
    return events


def x_at(events, tick):
    for e in events:
        if e["at"] <= tick < e["at"] + e["dur"]:
            return e["x"] + (e["endX"] - e["x"]) * (tick - e["at"]) / e["dur"]
    return X_END


def bar_svg(i, bar, events):
    o = [f'<svg viewBox="0 0 {W} {H}" aria-hidden="true" focusable="false">']
    for beat in range(4):
        x = num(x_at(events, beat * QUARTER))
        o.append(f'<line class="guide" x1="{x}" y1="43" x2="{x}" y2="144"/>')
    for s, (label, _, _) in STRINGS.items():
        y = y_of(s)
        o.append(f'<line class="sl" x1="1" y1="{y}" x2="{W - 1}" y2="{y}"/>'
                 f'<g class="slab"><rect x="3" y="{y-5}" width="12" height="10"/>'
                 f'<text x="9" y="{y+3}">{label}</text></g>')
    for x in (1, W - 1):
        o.append(f'<line class="bl" x1="{x}" y1="{Y0}" x2="{x}" y2="{y_of(6)}"/>')
    o.append(f'<text class="bn" x="4" y="19">{i + 1:02}</text>')
    for tick, chord in ((0, bar.chord), *bar.changes):
        if chord:
            o.append(f'<text class="ch" x="{num(x_at(events, tick))}" y="19">{escape(chord)}</text>')

    for j, (st, e) in enumerate(zip(bar.steps, events)):
        x, end = e["x"], e["endX"]
        o.append(f'<g class="step" data-step="{j}">')
        for string, fret, _ in st.notes:
            y = y_of(string)
            o.append(f'<rect class="pill" x="{num(x-8)}" y="{num(y-6.5)}" width="{num(end-x-2)}" height="13" rx="6.5"/>'
                     f'<text class="fr" x="{num(x)}" y="{num(y+4.3)}">{fret}</text>')
        if not st.notes:
            label = "4-beat rest" if st.ticks == WHOLE else "rest"
            o.append(f'<rect class="rest-tail" x="{num(x-8)}" y="83" width="{num(end-x-3)}" height="13" rx="6"/>'
                     f'<text class="rest-label" x="{num((x+end)/2-9)}" y="92.5">{label}</text>')
        if st.tech in ("hammer", "pull"):
            y = y_of(st.notes[0][0]) - 8
            x1, x2 = events[j-1]["x"] + 1, x - 1
            mid = (x1 + x2) / 2
            o.append(f'<path class="slur" d="M{num(x1)} {y} Q{num(mid)} {y-9} {num(x2)} {y}"/>'
                     f'<text class="tech" x="{num(mid)}" y="{y-6}">{st.tech[0].upper()}</text>')
        elif st.tech:
            if st.tech == "slide":
                fret = st.notes[0][1]
                arrow = "↗" if e["slideOffset"] < 0 else "↘"
                mark = f'{fret + e["slideOffset"]}{arrow}{fret}'
            else:
                mark = {"slide in": "sl. ↗", "vibrato": "vib.", "bend": "½ bend"}[st.tech]
            o.append(f'<text class="tech" x="{num(x)}" y="35">{mark}</text>')
        if st.pick:
            path = "M-3 3v-6h6v6" if st.pick == "down" else "M-3 -3l3 6 3-6"
            o.append(f'<path class="pick" transform="translate({num(x)} 139)" d="{path}"/>')
        o.append('</g>')

    hits = {e["at"] for e in events if e["notes"]}
    counts = [(k * EIGHTH, label) for k, label in enumerate(COUNT)]
    for st, e in zip(bar.steps, events):
        if st.ticks == TRIPLET and e["at"] % QUARTER == 0:
            at = e["at"]
            counts.remove((at + EIGHTH, "&"))
            counts.extend([(at + TRIPLET, "trip"), (at + 2 * TRIPLET, "let")])
    for tick, label in sorted(counts):
        cls = "cnt hit" if tick in hits else "cnt"
        o.append(f'<text class="{cls}" x="{num(x_at(events,tick))}" y="{COUNT_Y}">{escape(label)}</text>')
    o.append(f'<line class="cursor" x1="{X0}" y1="42" x2="{X0}" y2="132"/></svg>')
    return "".join(o)


def count_spoken(at):
    if at % EIGHTH == 0:
        return COUNT_SPOKEN[at // EIGHTH]
    beat, offset = divmod(at, QUARTER)
    if offset in (TRIPLET, 2 * TRIPLET):
        return f"triplet {offset // TRIPLET + 1} of beat {beat + 1}"
    return f"a thirty-second after beat {beat + 1}"


def bar_button(i, bar, events):
    parts = [f"Bar {i+1}. " + (bar.chord + "." if bar.chord else "")]
    for tick, chord in bar.changes:
        parts.append(f"{chord} on {count_spoken(tick)}.")
    for st, e in zip(bar.steps, events):
        notes = " with ".join(f"{STRINGS[s][1]} string {'open' if f == 0 else f'fret {f}'}"
                              for s, f, _ in st.notes)
        markings = [TECHNIQUES[st.tech]] if st.tech else []
        if st.pick:
            markings.append(st.pick + "stroke")
        parts.append(", ".join([count_spoken(e["at"]).capitalize(), notes or "rest", *markings]) + ".")
    return (f'<button type="button" class="bar" data-bar="{i}" aria-pressed="false" '
            f'aria-label="Loop bar {i+1}" aria-describedby="bar-words-{i}">{bar_svg(i, bar, events)}'
            f'<span class="sr" id="bar-words-{i}">{escape(" ".join(parts))}</span></button>')


PLAY_ICON = '<svg class="ico ico-play" viewBox="0 0 12 12" aria-hidden="true"><path d="M2 1l9 5-9 5z"/></svg>'
STOP_ICON = '<svg class="ico ico-stop" viewBox="0 0 12 12" aria-hidden="true"><rect x="1.5" y="1.5" width="9" height="9" rx="1.5"/></svg>'

CSS = r"""
:root {
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
main { max-width: 1024px; margin: 0 auto; padding: 24px 16px 56px; display: grid; gap: 36px; }
h1, h2 { font-family: var(--font-display); text-wrap: balance; margin: 0; line-height: 1.1; }
h1 { font-size: clamp(1.75rem, 7vw, 2.5rem); font-weight: 800; letter-spacing: -0.02em; }
h2 { font-size: 1.375rem; font-weight: 700; letter-spacing: -0.01em; }
p { margin: 0; max-width: 62ch; }
a { color: inherit; }
:is(a, button, input, select, summary):focus-visible { outline: 3px solid var(--open); outline-offset: 2px; border-radius: 4px; }
section { display: grid; gap: 14px; }
header.top { display: grid; gap: 10px; }
.eyebrow { font-size: .8125rem; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); font-weight: 700; }
.lede { font-size: 1.0625rem; color: var(--muted); }
.note { font-size: .9375rem; color: var(--muted); }
.sr { position: absolute; width: 1px; height: 1px; overflow: hidden; clip-path: inset(50%); white-space: nowrap; }

.passage { display: block; min-width: 0; padding: 14px; background: var(--surface); border: 1px solid var(--line); border-radius: 10px; }
.passage-head { display: flex; align-items: baseline; justify-content: space-between; gap: 12px; padding: 0 2px 12px; margin-bottom: 6px; border-bottom: 1px solid var(--line); }
.passage-head h2 { font-size: 1.15rem; }
.passage-head span, .meta { color: var(--muted); font-size: .875rem; font-variant-numeric: tabular-nums; }
.tab { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); row-gap: 10px; }
.bar { position: relative; display: block; width: 100%; margin: 0; padding: 0; border: 0; border-radius: 6px; background: none; color: inherit; font: inherit; cursor: pointer; -webkit-tap-highlight-color: transparent; transition: opacity .15s; }
.bar svg { display: block; width: 100%; height: auto; }
.bar.out { opacity: .62; }          /* outside the part being looped */
.bar.now, .bar[aria-pressed="true"], .bar:hover { background: var(--wash); }
.bar[aria-pressed="true"] { box-shadow: inset 0 0 0 1.5px var(--open); }
svg text { font-family: var(--font-body); }
.sl { stroke: var(--ink); stroke-width: 1; opacity: .3; }
.bl { stroke: var(--ink); stroke-width: 1.2; opacity: .55; }
.guide { stroke: var(--ink); stroke-width: 1; opacity: .07; }
.bn { fill: var(--muted); font-size: 11px; font-variant-numeric: tabular-nums; }
.ch { fill: var(--open); font-family: var(--font-display); font-size: 15px; font-weight: 800; }
.pill { fill: var(--pill); }
.fr { fill: var(--ink); font-size: 13px; font-weight: 700; text-anchor: middle; font-variant-numeric: tabular-nums; }
.step.on .pill { fill: var(--open); }
.step.on .fr { fill: var(--on-dot); }
.slur { fill: none; stroke: var(--ink); stroke-width: 1.3; stroke-linecap: round; }
.tech { fill: var(--ink); font-size: 8px; font-weight: 700; text-anchor: middle; paint-order: stroke; stroke: var(--surface); stroke-width: 3px; }
.cnt { fill: var(--muted); font-size: 9.5px; text-anchor: middle; }
.cnt.hit { fill: var(--ink); font-weight: 700; opacity: 1; }
.cursor { stroke: var(--open); stroke-width: 2; stroke-linecap: round; opacity: 0; }
.bar.now .cursor { opacity: .9; }
.slab rect { fill: var(--surface); }
.slab text { fill: var(--muted); font-size: 8px; font-weight: 700; text-anchor: middle; }
.pick { stroke: var(--muted); stroke-width: 1.3; fill: none; }
.rest-tail { fill: var(--surface); stroke: var(--line); stroke-dasharray: 3 2; }
.rest-label { fill: var(--muted); font-size: 8.5px; text-anchor: middle; }
.step.on .rest-tail { stroke: var(--open); }
.step.on .rest-label { fill: var(--open); }

.practice { display: grid; gap: 16px; }
.controls { position: sticky; top: 6px; z-index: 2; display: flex; flex-wrap: wrap; align-items: center; gap: 8px 16px; padding: 8px 12px; background: var(--surface); border: 1px solid var(--line); border-radius: 12px; box-shadow: 0 4px 14px rgb(0 0 0 / .10); }
.pbtn { flex: none; display: inline-flex; align-items: center; justify-content: center; gap: 7px; min-width: 44px; min-height: 40px; padding: 0 13px; border: 1px solid var(--line); border-radius: 99px; background: transparent; color: var(--ink); font: 700 .8125rem/1 var(--font-body); font-variant-numeric: tabular-nums; cursor: pointer; -webkit-tap-highlight-color: transparent; }
.pbtn[aria-pressed="true"] { background: var(--ink); border-color: var(--ink); color: var(--bg); }
.go { min-width: 92px; min-height: 44px; background: var(--ink); border-color: var(--ink); color: var(--bg); font-size: .9375rem; }
.ico { width: 11px; height: 11px; fill: currentColor; flex: none; }
.go .ico-stop, .go[aria-pressed="true"] .ico-play { display: none; }
.go[aria-pressed="true"] .ico-stop { display: block; }
.tempo { flex: 1 1 190px; display: flex; align-items: center; gap: 8px; min-height: 40px; font-size: .8125rem; font-weight: 700; color: var(--muted); }
.tempo input { flex: 1 1 0; min-width: 0; accent-color: var(--open); }
.tempo output { min-width: 4.6em; color: var(--ink); font-variant-numeric: tabular-nums; }
.range { display: inline-flex; align-items: center; gap: 6px; color: var(--muted); font-size: .8125rem; font-weight: 700; }
.range select { min-height: 38px; max-width: 100%; border: 1px solid var(--line); border-radius: 6px; padding: 0 6px; background: var(--surface); color: var(--ink); font: inherit; }
.position { color: var(--muted); min-width: 6em; font-size: .8125rem; font-variant-numeric: tabular-nums; text-align: right; }
details { color: var(--muted); font-size: .9375rem; }
summary { color: var(--ink); font-weight: 700; cursor: pointer; width: fit-content; }
details[open] summary { margin-bottom: 10px; }
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
@media (max-width: 820px) {
  .tab { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .position { min-width: 0; }
}
@media (max-width: 580px) {
  main { padding: 18px 12px 38px; gap: 22px; }
  .tab { grid-template-columns: 1fr; }
  .controls { display: grid; grid-template-columns: auto minmax(0, 1fr) auto; gap: 4px 8px; }
  .tempo { grid-column: span 2; }
  .range { grid-column: span 2; justify-self: start; }
  .position { display: none; }
  .passage { padding: 11px; }
}
@media print {
  body { background: #fff; }
  .controls, .linkrow, .hint { display: none; }
  .bar.out { opacity: 1; }
  .tab { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .bar { break-inside: avoid; }
  .passage-head { break-after: avoid; }
}
"""


def page():
    timelines = [timeline(bar, BARS[i-1].steps[-1] if i else None) for i, bar in enumerate(BARS)]
    passages, options = [], []
    for start, end, title in SECTIONS:
        bars = "\n".join(bar_button(i, BARS[i], timelines[i]) for i in range(start-1, end))
        passages.append(f'<section class="passage" aria-labelledby="section-{start}"><div class="passage-head">'
                        f'<h2 id="section-{start}">{title}</h2><span>Bars {start}–{end}</span></div>'
                        f'<div class="tab">{bars}</div></section>')
        options.append(f'<option value="{start}-{end}" data-anchor="section-{start}">{title} · {start}–{end}</option>')
    notes = "".join(
        f'<li><span class="n">Bar {i+1}</span><span class="c">{bar.chord}</span><span>{escape(text)}</span></li>'
        for i, (bar, text) in enumerate(zip(PRE_INTRO, BAR_NOTES)))
    links = "".join(
        f'<a class="watch" href="{yt(t).replace("&", "&amp;")}">{PLAY_ICON}<span>{label} at <b>{mmss(t)}</b></span></a>'
        for label, t in LINES)
    js = Path(__file__).with_name("player.js").read_text(encoding="utf-8")
    payload = json.dumps(dict(beat=QUARTER, preIntroBars=len(PRE_INTRO), bars=timelines), separators=(",", ":"))
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Gild the Lily · Interactive guitar tab</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&amp;family=Bricolage+Grotesque:opsz,wght@12..96,600..800&amp;display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<main>
<header class="top">
  <p class="eyebrow"><a href="../index.html">Chord guide</a> &middot; Guitar practice sheet</p>
  <h1>Gild the Lily</h1>
  <p class="lede">Billy Strings &middot; <i>Intro &amp; more</i>, arranged and tabbed by B-RoM</p>
  <p class="meta">{len(BARS)} bars &middot; Standard tuning &middot; 4/4</p>
</header>

<div class="practice" role="region" aria-label="Interactive tablature">
  <p class="note hint">Choose a passage or tap a bar to loop it. Tap the same bar again for the full score. Play starts with a four-beat count-in.</p>
  <div class="controls" role="group" aria-label="Play the tab">
    <button type="button" class="pbtn go" id="go" aria-pressed="false">{PLAY_ICON}{STOP_ICON}<span id="go-text">Play</span></button>
    <label class="tempo"><span>Tempo</span><input type="range" id="tempo" min="40" max="130" step="1" value="72"><output id="tempo-out" for="tempo">72 bpm</output></label>
    <label class="range">Loop <select id="loop"><option value="1-{len(BARS)}">All {len(BARS)} bars</option>
      <optgroup label="Passages">{"".join(options)}</optgroup>
      <optgroup label="Pre-intro phrases"><option value="1-3">Bars 1–3</option><option value="4-7">Bars 4–7</option></optgroup>
    </select></label>
    <label class="click"><input type="checkbox" id="click" checked>Click</label>
    <span class="position" id="position"></span>
  </div>
  {"".join(passages)}
</div>

<section aria-labelledby="h-read">
  <h2 id="h-read">Reading the tab</h2>
  <dl class="facts">
    <div><dt>Strings &amp; frets</dt><dd>High E is on top. Numbers are frets. Play stacked numbers together.</dd></div>
    <div><dt>Timing</dt><dd>The tails show duration. Dashed tails are rests. Count eighths below the staff and three equal notes on beat 3 of bar 38.</dd></div>
    <div><dt>Picking</dt><dd>Π is a downstroke and V is an upstroke. H means hammer-on and P means pull-off.</dd></div>
    <div><dt>Expression</dt><dd>An arrow shows a slide. Vib. means vibrato. For a ½ bend, raise the pitch one semitone.</dd></div>
  </dl>
  <p class="note">In bar 39, play fret 12 on the G string for a thirty-second note, then slide to fret 9 for a dotted sixteenth. Land on fret 7 on the “and” of beat 2.</p>
  <details><summary>Playing notes for the pre-intro</summary><ol class="bars">{notes}</ol>
    <p class="note">The chord names above bars 1–7 are inferred from the notes. Chord changes from bar 8 onward follow the score.</p>
  </details>
</section>

<section aria-labelledby="h-watch">
  <h2 id="h-watch">See it played</h2>
  <p>B-RoM’s video lesson shows the pre-intro and the start of the main lick.</p>
  <div class="linkrow">{links}</div>
</section>
<footer class="source">
  <p>Tab from B-RoM’s five-page guitar arrangement of <i>Gild the Lily</i> by Billy Strings. The player synthesizes the written guitar part. Chord names over rests show the harmony.</p>
</footer>
</main>
<script id="score-data" type="application/json">{payload}</script>
<script>{js}</script>
</body>
</html>
'''


if __name__ == "__main__":
    check()
    out = Path(__file__).with_name("index.html")
    out.write_text(page(), encoding="utf-8")
    print(f"Checked {len(BARS)} bars and wrote {out.name}.")
