#!/usr/bin/env python3
"""Build a standalone interactive practice sheet from B-RoM's 69-bar score."""
import json
import sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from practice.notation import (
    ASSETS, PLAY_ICON, STOP_ICON, STRINGS, TECHNIQUES,
    bar_button, note_name, sounding, timeline,
)
from score import BARS, PRE_INTRO, QUARTER, SECTIONS, WHOLE

def yt(t):
    return f"https://www.youtube.com/watch?v=U9BqvaBOR8Y&t={t}s"


def mmss(t):
    return f"{t // 60}:{t % 60:02d}"


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
    js = (ASSETS / "player.js").read_text(encoding="utf-8")
    payload = json.dumps(dict(beat=QUARTER, ringBars=len(PRE_INTRO), bars=timelines), separators=(",", ":"))
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Gild the Lily · Interactive guitar tab</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&amp;family=Bricolage+Grotesque:opsz,wght@12..96,600..800&amp;display=swap" rel="stylesheet">
<style>{(ASSETS / 'sheet.css').read_text(encoding='utf-8')}</style>
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
