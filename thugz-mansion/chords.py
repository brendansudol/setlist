"""Chord diagrams and practice notes for the voicings in the tab."""
from pathlib import Path

from practice.chordbox import chordbox
from practice.notation import ASSETS
from score import AM7, BM7, CAPO, CMAJ7, F7_C, G, LESSON, SOURCE

STRINGS = ("low E", "A", "D", "G", "B", "high e")
FINGERS = ("", "Index", "Middle", "Ring", "Pinky")


def shape(name, slug, voicing, fingers, first_barred, tip):
    frets = [None if fret == "." else int(fret) for fret in voicing]
    assert len(frets) == len(fingers) == 6
    chord = dict(name=name, frets=frets, fingers=fingers)
    rows = []
    for finger in range(1, 5):
        held = [i for i, assigned in enumerate(fingers) if assigned == finger]
        if not held:
            continue
        string = held[0]
        fret = frets[string]
        assert fret and all(frets[i] == fret for i in held)
        if finger == 1 and first_barred is not None:
            assert string == first_barred and min(frets[string:]) == fret
            chord["barre"] = (finger, string, 5, fret)
            where = f"Barre {STRINGS[string]} through high e"
        else:
            assert len(held) == 1
            where = STRINGS[string]
        rows.append(f'<tr><th scope="row">{FINGERS[finger]}</th><td>{where}</td><td>{fret}</td></tr>')
    assert all(bool(fret) == bool(finger) for fret, finger in zip(frets, fingers))
    diagram = chordbox(chord, ("E", "A", "D", "G", "B", "e"))
    return f'''<article class="grip" id="{slug}">
  <h3>{name}</h3>
  <div class="grip-body">{diagram}
    <table><thead><tr><th scope="col">Finger</th><th scope="col">String</th><th scope="col">Fret</th></tr></thead>
    <tbody>{''.join(rows)}</tbody></table>
  </div>
  <p>{tip}</p>
</article>'''


def loop_bar(n):
    return f'<a href="index.html#bar-{n}">Loop bar {n}</a>'


def guide():
    am = shape("Am7", "am7", AM7, (0, 0, 3, 0, 2, 0), None,
               "Leave A, G and high e open. Using middle and ring here keeps your index free for the next chord.")
    bm = shape("Bm7", "bm7", BM7, (0, 1, 3, 1, 2, 1), 1,
               "Slide the two Am7 fingers up two frets on the same strings. Lay your index across fret 2 to take over the strings that were open.")
    c = shape("Cmaj7", "cmaj7", CMAJ7, (0, 1, 3, 2, 4, 1), 1,
              "From Bm7, move your index and ring one fret higher on the same strings. Move middle to G4 and add pinky on B5.")
    f = shape("F7/C", "f7-c", F7_C, (0, 1, 1, 3, 2, 4), 1,
              "Start the strum on A3, the C bass in this shape. In picked bar 8, start on D3 instead. Your other three fingers make the same F7 sound above it.")
    g = shape("G", "g", G, (1, 3, 4, 2, 1, 1), 0,
              "For strumming, play all six. Pick them one at a time first. Check that the B and high e ring clearly under the index barre.")

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Thugz Mansion · Chord shapes and fingering</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&amp;family=Bricolage+Grotesque:opsz,wght@12..96,600..800&amp;display=swap" rel="stylesheet">
<style>{(ASSETS / "sheet.css").read_text(encoding="utf-8")}
{Path(__file__).with_name("chords.css").read_text(encoding="utf-8")}</style>
</head>
<body>
<main>
<header class="top">
  <p class="eyebrow"><a href="../index.html">Setlist</a> · <a href="index.html">Thugz Mansion tab player</a></p>
  <h1>Thugz Mansion <span>Chord shapes &amp; fingering</span></h1>
  <p class="lede">Put the capo on fret {CAPO} and count from there. Fret 1 is the first fret beyond the capo. The names here describe your hand shapes.</p>
</header>

<section aria-labelledby="progression">
  <div class="section-head"><h2 id="progression">The four-bar progression</h2><a href="index.html#section-9">Loop the strumming pattern</a></div>
  <div class="map">
    <div><span>First bar</span><a href="#g">G</a><small>Four beats</small></div>
    <div><span>Second bar</span><a href="#bm7">Bm7</a><small>Four beats</small></div>
    <div><span>Third bar</span><div><a href="#am7">Am7</a> → <a href="#bm7">Bm7</a> → <a href="#cmaj7">Cmaj7</a></div><small>One beat · one beat · two beats</small></div>
    <div><span>Fourth bar</span><div><a href="#am7">Am7</a> → <a href="#bm7">Bm7</a> → <a href="#f7-c">F7/C</a></div><small>One beat · one beat · two beats</small></div>
  </div>
</section>

<section aria-labelledby="first-change">
  <h2 id="first-change">Start with Am7 → Bm7</h2>
  <p>Play just the A, D, G and B strings at first. These are the four notes you pick together in bar 7. Once the change feels easy, add the high e for the strummed version.</p>
  <p class="key">Read each box from low E on the left to high e on the right. Finger numbers run from 1 (index) to 4 (pinky). A long bar means one finger covers several strings. ○ is open and × means skip.</p>
  <div class="pair">{am}{bm}</div>
  <p class="drill">Set the player to 50 bpm. Pick Am7 on beat 1 and Bm7 on beat 2. Give each string a chance to ring before adding Cmaj7 on beat 3. {loop_bar(7)}</p>
</section>

<section aria-labelledby="endings">
  <h2 id="endings">Two endings at fret 3</h2>
  <p>Make Cmaj7, then keep the index barre in place. Move middle, ring and pinky each one string toward high e, keeping their frets. You now have F7/C. In the song, approach each ending from Bm7.</p>
  <div class="pair">{c}{f}</div>
  <p class="drill">Strum once per change. In bar 11, hold Cmaj7 for beats 3 and 4. In bar 12, give those beats to F7/C. {loop_bar(11)} · {loop_bar(12)}</p>
</section>

<section aria-labelledby="opening">
  <h2 id="opening">The opening G</h2>
  <div class="pair">{g}
    <article class="picked"><h3>The picked G in bar 5</h3>
      <p>Start with index on low E3 for the bass. Keep the index across fret 3, put ring on D5 and middle on G4, then pluck D, G and B together. The barre supplies B3.</p>
      <p>The A string stays quiet here, so your pinky is free. Add it on B4 for the little lift while D5 and G4 stay in place. {loop_bar(5)}</p>
      <p><strong>Picking hand</strong> Use thumb, index and middle for D–G–B. For the four-note A–D–G–B grips in bar 7, add your ring finger and assign one finger per string from low to high.</p>
    </article>
  </div>
</section>

<section aria-labelledby="fills">
  <div class="section-head"><h2 id="fills">Put the fills back into the intro</h2><a href="{LESSON}&amp;t=301s">Watch the second half · 5:01</a></div>
  <ol class="fills">
    <li><strong>Open-string pull-offs</strong><p>In bar 1, pick B1 with your index fretting it, then pull off to open B. Do the same from fret 2 on G and D with your middle finger. Finish by sliding your index on A from fret 1 into fret 2 of the next bar. {loop_bar(1)}</p></li>
    <li><strong>The two-string pull-off</strong><p>In bar 2, release the Bm7 grip and lay your index across B and high e at fret 3. Hammer from B3 to B5 with your ring finger. Flatten ring over both strings at fret 5, pick them together, then pull back to the index at fret 3. {loop_bar(2)}</p></li>
    <li><strong>Move the pair together</strong><p>At the end of bar 3, put index on G2 and middle on B3. Pick both, slide together to G4 and B5, then back to G2 and B3. Keep the same two fingers touching the strings throughout. {loop_bar(3)}</p></li>
    <li><strong>Slide into the F7 fragment</strong><p>In bar 4, place ring on G4, middle on B3 and pinky on high e4. Slide all three up one fret. You’ve landed on the top three notes of the F7/C diagram. Release for the open-string pull-offs. {loop_bar(4)}</p></li>
  </ol>
</section>
<footer class="source"><p>The voicings follow Daniel Chavez’s arrangement. The finger assignments and drills are suggestions for moving between those voicings. <a href="{SOURCE}">DC Guitar tab</a> · <a href="{LESSON}">Video lesson</a></p></footer>
</main>
</body>
</html>
'''
