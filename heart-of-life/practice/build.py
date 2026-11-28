#!/usr/bin/env python3
"""Build the standalone practice sheet from the three Heart of Life lessons."""
import json
import sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from practice.notation import ASSETS, HALF, PLAY_ICON, QUARTER, STOP_ICON, STRINGS, WHOLE, bar_button, timeline
from score import LESSON, PASSAGES, TAB

BPM = 88
PASSAGE_NOTES = (
    'Pinch the bass and B strings together on 1. On 2 and 4, tap the bass with your thumb while your index flicks down across the G string. Add the pinky on count 3 of bars 2 and 4.',
    'Keep the thumb moving as before. In bar 10, the melody climbs from the B string onto high e. In bar 12, it starts on G and comes back to B. Aim each flick at the melody note stacked above the x.',
    'At fret 5, listen for C♯–D–E over A, then F♯–E–D over D. Let the two-bar G fill answer those phrases. On the third pass, shorten the G and move to D/F♯. Let the last D pinch ring for a full bar.',
    'Leave A and G open. Move just the fretted notes on D and B, keeping one shape for each bar. The highest pair is D-string fret 16 and B-string fret 15. Retrace the shapes and let the low A7 ring to finish.',
)
DRILLS = ((1, 2, 'D with the pinky'), (3, 4, 'Bm with the pinky'),
          (9, 12, 'Both melody changes'), (19, 20, 'Two-bar G fill'),
          (34, 42, 'Outro climb'), (43, 50, 'Outro descent'))


def prepare_bar(bar):
    assert sum(step.ticks for step in bar.steps) == WHOLE, bar.chord
    events = timeline(bar, None)
    taps = []
    for step, event in zip(bar.steps, events):
        assert len(dict(step.notes)) == len(step.notes)
        assert all(s in STRINGS and (f == "x" or 0 <= f <= 24) for s, f in step.notes)
        if step.tech == "mute":
            assert len(event["notes"]) == 1 and step.notes[0][1] == "x"
            taps.append(event["at"])
        if event["at"] == 0 or step.tech == "mute":
            event["cut"] = True
    assert taps == ([] if len(events) == 1 else [QUARTER, 3 * QUARTER])
    return events


def page():
    scores, passages, options = [], [], []
    for (name, bars, video, seconds, link_text), note in zip(PASSAGES, PASSAGE_NOTES, strict=True):
        first = len(scores) + 1
        buttons = []
        for bar in bars:
            events = prepare_bar(bar)
            buttons.append(bar_button(len(scores), bar, events))
            scores.append(events)
        last = len(scores)
        label = f"Bars {first}–{last}"
        selected = " selected" if first == 1 else ""
        options.append(f'<option value="{first}-{last}" data-anchor="section-{first}"{selected}>{escape(name)}</option>')
        timestamp = f'{seconds // 60}:{seconds % 60:02d}'
        passages.append(f'''<section class="passage" aria-labelledby="section-{first}">
  <div class="passage-head"><h2 id="section-{first}">{escape(name)}</h2><span>{label}</span></div>
  <p class="passage-note note">{escape(note)} <a href="https://youtu.be/{video}?t={seconds}">{link_text} ({timestamp})</a></p>
  <div class="tab">{''.join(buttons)}</div>
</section>''')
    total = len(scores)
    drills = []
    for a, b, name in DRILLS:
        assert 1 <= a <= b <= total
        drills.append(f'<option value="{a}-{b}">{name} · {a}–{b}</option>')
    score = json.dumps(dict(beat=HALF, bars=scores, ringBars=total, sustainBeats=2), separators=(",", ":"))
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Heart of Life · Interactive guitar tab</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&amp;family=Bricolage+Grotesque:opsz,wght@12..96,600..800&amp;display=swap" rel="stylesheet">
<style>{(ASSETS / "sheet.css").read_text(encoding="utf-8")}
.tab {{ grid-template-columns: repeat(4, minmax(0, 1fr)); }}
.passage-head span {{ white-space: nowrap; }}
.passage-note {{ padding: 4px 2px 16px; max-width: 76ch; }}
.range, .range select {{ min-width: 0; max-width: 100%; }}
.top .tuning {{ grid-column: 1; justify-self: start; }}
@media (max-width: 960px) {{ .tab {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
@media (max-width: 580px) {{ .tab {{ grid-template-columns: 1fr; }} }}
@media print {{ .tuning {{ display: none; }} }}
</style>
</head>
<body><main>
<header class="top">
  <p class="eyebrow"><a href="../../index.html">Setlist</a> · <a href="../index.html">Chord shapes &amp; fingering</a></p>
  <h1>The Heart of Life</h1>
  <p class="lede">John Mayer · Fingerstyle guitar tab from the Six String Fingerpicking lessons</p>
  <p class="meta">{total} practice bars · No capo · Cut time · Half note = {BPM}</p>
  <label class="range tuning">Playback tuning <select id="tuning"><option value="0">Standard · lesson</option><option value="-1">Half-step down · recording</option></select></label>
</header>
<div class="practice" role="region" aria-label="Interactive tablature">
  <p class="note hint">Choose a loop or tap a single bar. Play starts with four clicks. Count “1 &amp; 2 &amp; 3 &amp; 4 &amp;” across the tab. The click lands on 1 and 3, and each <strong>x</strong> marks a thumb tap on 2 or 4.</p>
  <div class="controls" role="group" aria-label="Play the tab">
    <button type="button" class="pbtn go" id="go" aria-pressed="false">{PLAY_ICON}{STOP_ICON}<span id="go-text">Play</span></button>
    <label class="tempo"><span>Tempo</span><input type="range" id="tempo" min="40" max="130" step="1" value="{BPM}"><output id="tempo-out" for="tempo">{BPM} bpm</output></label>
    <label class="range">Loop <select id="loop"><option value="1-{total}">All four sections</option>{''.join(options)}<optgroup label="Short drills">{''.join(drills)}</optgroup></select></label>
    <label class="click"><input type="checkbox" id="click" checked>Click</label>
    <span class="position" id="position"></span>
  </div>
  {''.join(passages)}
</div>
<footer class="source">
  <p>These loops follow the instructor’s three lessons. To go from the last chorus into the outro, play G to D/F♯ one extra time, then enter on open A7. <a href="https://youtu.be/Tx6E2w73VcU?t=27">Watch the transition (0:27)</a></p>
  <p><a href="{LESSON}">Six String Fingerpicking lesson videos</a> · <a href="{TAB}">Instructor’s published tab</a></p>
</footer>
</main>
<script id="score-data" type="application/json">{score}</script>
<script>{(ASSETS / "player.js").read_text(encoding="utf-8")}</script>
</body></html>
'''


if __name__ == "__main__":
    out = Path(__file__).with_name("index.html")
    out.write_text(page(), encoding="utf-8")
    print(f"Checked {sum(len(p[1]) for p in PASSAGES)} practice bars and wrote {out.name}.")
