#!/usr/bin/env python3
"""Build the standalone Danny's Song tab and its two-voice playback timeline."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from practice.notation import ASSETS, PLAY_ICON, STOP_ICON, QUARTER, WHOLE, bar_button, timeline
from score import BARS, BPM, SECTIONS, SONG_ORDER

# Rests in the upper staff while the bass keeps playing. Barline releases
# are handled separately so a printed tie can continue from the preceding bar.
UPPER_RESTS = {10: (8,), 11: (8, 12), 12: (8,), 13: (6, 8), 14: (8,), 16: (8,),
               18: (8,), 22: (8,), 26: (8,), 27: (8,), 28: (8,), 29: (8,),
               30: (8,), 31: (8,), 32: (8,), 34: (8,), 36: (8,)}


def bass_attack(number, slot, step):
    if number <= 16:
        return slot % 2 == 0
    if number in (17, 33):
        return True
    if step.tech == "hammer":
        return True
    # Quarter-note bass in the strummed passages, with a few eighth-note walks.
    return slot % 4 == 0 or (number in (21, 25) and slot == 14) or (number == 37 and slot == 10)


def prepare_score():
    assert len(BARS) == 38 and set(SONG_ORDER) == set(range(1, 39))
    assert [i for a, b, _ in SECTIONS for i in range(a, b+1)] == list(range(1, 39))
    active = {}  # string -> (fret, "bass" or "upper")
    timelines = []
    for number, bar in enumerate(BARS, 1):
        assert sum(step.ticks for step in bar.steps) == WHOLE, number
        events = timeline(bar, None, width=382, strummed=True)
        for step, event in zip(bar.steps, events):
            slot = event["at"] // 6
            frets = dict(step.notes)
            for string, fret in step.ties:
                assert slot == 0 and string in active and active[string][0] == fret, number
            bass = max(frets) if frets and bass_attack(number, slot, step) else None
            voices = {s: "bass" if s == bass else "upper" for s in frets}
            if step.tech == "hammer":
                assert bass in active and active[bass][0] < frets[bass], number
            replaced = set(voices.values())
            if slot in UPPER_RESTS.get(number, ()):
                replaced.add("upper")
            if slot == 0:
                release = set(range(1, 7)) - dict(step.ties).keys()
            else:
                release = {s for s, (_, voice) in active.items() if voice in replaced}
            release.update(frets)
            for s in release:
                active.pop(s, None)
            active.update({s: (fret, voices[s]) for s, fret in frets.items()})
            event["release"] = sorted(release)
        timelines.append(events)
    return timelines


def page():
    timelines = prepare_score()
    passages, options = [], []
    for first, last, name in SECTIONS:
        label = f"Bar {first}" if first == last else f"Bars {first}–{last}"
        buttons = ''.join(bar_button(i, BARS[i], timelines[i], sixteenths=True)
                          for i in range(first - 1, last))
        if first == last == 1:
            buttons += ('<aside class="pick-tip"><strong>The picking hand</strong>'
                        '<p>Count “1 e &amp; a”. Play D with your thumb, B with your index, '
                        'G with your thumb, then high e with your middle. Repeat on each beat.</p></aside>')
        passages.append(f'<section class="passage" aria-labelledby="section-{first}">'
                        f'<div class="passage-head"><h2 id="section-{first}">{name}</h2>'
                        f'<span>{label}</span></div><div class="tab">{buttons}</div></section>')
        options.append(f'<option value="{first}-{last}" data-anchor="section-{first}">{name} · {label.lower()}</option>')

    payload = json.dumps(dict(beat=QUARTER, bars=timelines, order=[i-1 for i in SONG_ORDER],
                              sustainBeats=5), separators=(",", ":"))
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Danny’s Song · Interactive guitar tab</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&amp;family=Bricolage+Grotesque:opsz,wght@12..96,600..800&amp;display=swap" rel="stylesheet">
<style>{(ASSETS / "sheet.css").read_text(encoding="utf-8")}
.tab {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
.passage-head span {{ white-space: nowrap; }}
.range {{ max-width: 100%; min-width: 0; }}
.range select {{ min-width: 0; }}
.pick-tip {{ align-self: center; padding: 12px 16px; max-width: 40ch; font-size: .95rem; }}
.pick-tip p {{ margin-top: 4px; }}
@media (max-width: 680px) {{ .tab {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>
<main>
<header class="top">
  <p class="eyebrow"><a href="../../index.html">Setlist</a> · <a href="../index.html">Danny’s Song chord guide</a></p>
  <h1>Danny’s Song</h1>
  <p class="lede">Loggins &amp; Messina · Guitar transcription by Jerry’s Guitar Bar</p>
  <p class="meta">38 bars · Standard tuning · No capo · 4/4 · {BPM} bpm</p>
</header>
<div class="practice" role="region" aria-label="Interactive tablature">
  <p class="note hint">Choose a section or tap a bar to loop it. Tap that bar again to return to the whole song. Play starts with four count-in clicks.</p>
  <div class="controls" role="group" aria-label="Play the tab">
    <button type="button" class="pbtn go" id="go" aria-pressed="false">{PLAY_ICON}{STOP_ICON}<span id="go-text">Play</span></button>
    <label class="tempo"><span>Tempo</span><input type="range" id="tempo" min="40" max="130" step="1" value="{BPM}"><output id="tempo-out" for="tempo">{BPM} bpm</output></label>
    <label class="range">Loop <select id="loop"><option value="1-38">Whole song · with repeats</option>{''.join(options)}</select></label>
    <label class="click"><input type="checkbox" id="click" checked>Click</label>
    <span class="position" id="position"></span>
  </div>
  {''.join(passages)}
</div>
<section aria-labelledby="playing">
  <h2 id="playing">Playing the arrangement</h2>
  <dl class="facts">
    <div><dt>Bass and melody</dt><dd>Listen for the alternating bass beneath the picked melody. In the strummed verse, the bass keeps time while the upper strings supply the offbeats.</dd></div>
    <div><dt>Tied notes</dt><dd>Let a fret in parentheses keep ringing across the barline. The final D is struck on beat 4 of bar 37 and held through bar 38.</dd></div>
    <div><dt>Strumming</dt><dd>Follow the bass with light brushes across the stacked frets. Π and V suggest downstrokes and upstrokes. H marks a hammer-on.</dd></div>
  </dl>
  <p class="note">Whole-song playback follows the lesson form. Play the intro once, bars 2–17 twice, and bars 18–33 twice. Return to 18–21 for the instrumental verse, then finish with 34–38. The numbers above the tab match the PDF.</p>
</section>
<footer class="source"><p>Tab from the Jerry’s Guitar Bar lesson for <i>Danny’s Song</i>. <a href="../index.html">Chord shapes, picking patterns and lesson timestamps</a></p></footer>
</main>
<script id="score-data" type="application/json">{payload}</script>
<script>{(ASSETS / "player.js").read_text(encoding="utf-8")}</script>
</body>
</html>
'''


if __name__ == "__main__":
    out = Path(__file__).with_name("index.html")
    out.write_text(page(), encoding="utf-8")
    print(f"Checked {len(BARS)} bars and wrote {out.name}.")
