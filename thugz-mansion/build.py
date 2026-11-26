#!/usr/bin/env python3
"""Build the standalone Thugz Mansion practice sheet."""
import json
import sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from practice.notation import ASSETS, PLAY_ICON, STOP_ICON, QUARTER, WHOLE, bar_button, timeline
from score import BPM, CAPO, LESSON, PASSAGES, SOURCE


def watch(seconds, label):
    return f'<a href="{LESSON}&amp;t={seconds}s">{escape(label)} · {seconds // 60}:{seconds % 60:02}</a>'


def validate(bar, previous):
    assert sum(step.ticks for step in bar.steps) == WHOLE
    for step in bar.steps:
        notes = dict(step.notes)
        assert len(notes) == len(step.notes)
        assert all(1 <= string <= 6 for string in notes)
        if step.tech == "mute":
            assert set(notes.values()) == {"x"}
        else:
            assert all(isinstance(f, int) and 0 <= f <= 24 for f in notes.values())
        if step.tech in ("hammer", "pull", "slide"):
            before = dict(previous.notes)
            deltas = {fret - before[string] for string, fret in notes.items()}
            assert len(deltas) == 1 and 0 not in deltas
            if step.tech != "slide":
                assert (deltas.pop() > 0) == (step.tech == "hammer")
        previous = step


def page():
    options, passages, bars = [], [], []
    for name, seconds, measures in PASSAGES:
        first = len(bars) + 1
        header_id = f"section-{first}"
        buttons = []
        previous = None
        for bar in measures:
            validate(bar, previous)
            events = timeline(bar, previous, capo=CAPO, width=374, strummed=True)
            # Release the previous voicing when the fretting hand changes shape.
            boundaries = {0, *(tick for tick, _ in bar.changes)}
            for event in events:
                if event["at"] in boundaries:
                    event["cut"] = True
            buttons.append(bar_button(len(bars), bar, events, sixteenths=True))
            bars.append(events)
            previous = bar.steps[-1]
        last = len(bars)
        selected = " selected" if first == 1 else ""
        options.append(f'<option value="{first}-{last}" data-anchor="{header_id}"{selected}>{name}</option>')
        links = watch(seconds, "Lesson")
        if first == 1:
            links += " · " + watch(301, "Second half")
        passages.append(f'''<section class="passage" aria-labelledby="{header_id}">
  <div class="passage-head"><h2 id="{header_id}">{name}</h2><span>Bars {first}–{last}</span></div>
  <div class="tab">{''.join(buttons)}</div>
  <p class="lesson">{links}</p>
</section>''')

    payload = json.dumps(dict(beat=QUARTER, ringBars=len(PASSAGES[0][2]) + len(PASSAGES[1][2]), bars=bars),
                         separators=(",", ":"))
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Thugz Mansion · Interactive guitar tab</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&amp;family=Bricolage+Grotesque:opsz,wght@12..96,600..800&amp;display=swap" rel="stylesheet">
<style>{(ASSETS / "sheet.css").read_text(encoding="utf-8")}
.tab {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
.passage-head span {{ white-space: nowrap; }}
.lesson {{ margin-top: 8px; color: var(--muted); font-size: .875rem; }}
.lesson a {{ display: inline-block; padding: 5px 2px; text-underline-offset: .2em; }}
@media (max-width: 680px) {{ .tab {{ grid-template-columns: 1fr; }} }}
@media print {{ .lesson {{ display: none; }} }}
</style>
</head>
<body>
<main>
<header class="top">
  <p class="eyebrow"><a href="../index.html">Setlist</a> &middot; Guitar practice sheet</p>
  <h1>Thugz Mansion</h1>
  <p class="lede">Tupac Shakur &middot; Guitar arrangement by Daniel Chavez</p>
  <p class="meta">Standard tuning &middot; Capo {CAPO} &middot; 4/4 &middot; {BPM} bpm</p>
</header>
<div class="practice" role="region" aria-label="Interactive tablature">
  <p class="note hint">Start with the intro, then choose one of the three verse/chorus patterns. Tap a bar to loop it. Tap it again to play through all four patterns.</p>
  <div class="controls" role="group" aria-label="Play the tab">
    <button type="button" class="pbtn go" id="go" aria-pressed="false">{PLAY_ICON}{STOP_ICON}<span id="go-text">Play</span></button>
    <label class="tempo"><span>Tempo</span><input type="range" id="tempo" min="40" max="130" step="1" value="{BPM}"><output id="tempo-out" for="tempo">{BPM} bpm</output></label>
    <label class="range">Loop <select id="loop"><option value="1-{len(bars)}">All four patterns</option>{''.join(options)}</select></label>
    <label class="click"><input type="checkbox" id="click" checked>Click</label>
    <span class="position" id="position"></span>
  </div>
  {''.join(passages)}
</div>
<section aria-labelledby="reading">
  <h2 id="reading">Playing the tab</h2>
  <dl class="facts">
    <div><dt>Capo 1</dt><dd>Count frets from the capo. A 0 means an open string with the capo on. The G shape sounds A♭.</dd></div>
    <div><dt>Fingerpicking</dt><dd>Pluck stacked frets together. H is a hammer-on, P is a pull-off, and an arrow connects the frets of a slide.</dd></div>
    <div><dt>Strumming</dt><dd>Π marks a downstroke and V an upstroke. At an x, damp the strings for a short percussive hit.</dd></div>
    <div><dt>Counting</dt><dd>Play gives you four clicks to count in. Count each beat “1 e &amp; a” to place the quick fills and muted strokes.</dd></div>
  </dl>
</section>
<footer class="source">
  <p>Frets, voicings and strum directions follow Daniel Chavez’s tab. The player places them on a steady sixteenth-note grid for practice. <a href="{SOURCE}">Original DC Guitar tab</a> · <a href="{LESSON}">Video lesson</a></p>
</footer>
</main>
<script id="score-data" type="application/json">{payload}</script>
<script>{(ASSETS / "player.js").read_text(encoding="utf-8")}</script>
</body>
</html>
'''


if __name__ == "__main__":
    Path(__file__).with_name("index.html").write_text(page(), encoding="utf-8")
