"""Shared guitar-tab notation, SVG rendering and score timing."""
from dataclasses import dataclass
from html import escape
from pathlib import Path

WHOLE, HALF, QUARTER, EIGHTH = 96, 48, 24, 12
TRIPLET = 8  # three eighth-note triplets in one quarter


@dataclass(frozen=True)
class Step:
    ticks: int
    notes: tuple = ()
    tech: str = ""
    pick: str = ""


def hit(ticks, *notes, tech="", pick=""):
    return Step(ticks, notes, tech, pick)


@dataclass(frozen=True)
class Bar:
    chord: str
    steps: tuple
    # Additional chord changes, measured in ticks from the start of this bar.
    changes: tuple = ()

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
    "vibrato": "vibrato", "mute": "muted stroke",
}


W, H = 270, 161
X0 = 30
Y0, GAP = 52, 15
COUNT_Y = 155


def y_of(string):
    return Y0 + (string - 1) * GAP


def num(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def timeline(bar, previous, *, capo=0, width=W, strummed=False):
    # Guarantee space for two-digit frets even in the thirty-second-note slide.
    span = width - 9 - X0
    widths = [max(20, st.ticks * span / WHOLE) for st in bar.steps]
    scale = span / sum(widths)
    events, at, x = [], 0, X0
    for st, step_width in zip(bar.steps, widths):
        end = x + step_width * scale
        event = dict(at=at, dur=st.ticks, x=round(x, 2), endX=round(end, 2),
                     notes=[[s, sounding(s, f) + capo] for s, f, *_ in st.notes if f != "x"])
        if st.tech:
            event["tech"] = st.tech
        if st.tech == "slide":
            string, fret, *_ = st.notes[0]
            event["slideOffset"] = next(f - fret for s, f, *_ in previous.notes if s == string)
        if strummed and st.pick and len(event["notes"]) > 1:
            event["strum"] = st.pick
            event["notes"].sort(reverse=st.pick == "down")
        events.append(event)
        at, x, previous = at + st.ticks, end, st
    return events


def x_at(events, tick):
    for e in events:
        if e["at"] <= tick < e["at"] + e["dur"]:
            return e["x"] + (e["endX"] - e["x"]) * (tick - e["at"]) / e["dur"]
    return events[-1]["endX"]


def bar_svg(i, bar, events, sixteenths):
    width = round(events[-1]["endX"]) + 9
    o = [f'<svg viewBox="0 0 {width} {H}" aria-hidden="true" focusable="false">']
    for beat in range(4):
        x = num(x_at(events, beat * QUARTER))
        o.append(f'<line class="guide" x1="{x}" y1="43" x2="{x}" y2="144"/>')
    for s, (label, _, _) in STRINGS.items():
        y = y_of(s)
        o.append(f'<line class="sl" x1="1" y1="{y}" x2="{width - 1}" y2="{y}"/>'
                 f'<g class="slab"><rect x="3" y="{y-5}" width="12" height="10"/>'
                 f'<text x="9" y="{y+3}">{label}</text></g>')
    for x in (1, width - 1):
        o.append(f'<line class="bl" x1="{x}" y1="{Y0}" x2="{x}" y2="{y_of(6)}"/>')
    o.append(f'<text class="bn" x="4" y="19">{i + 1:02}</text>')
    for tick, chord in ((0, bar.chord), *bar.changes):
        if chord:
            o.append(f'<text class="ch" x="{num(x_at(events, tick))}" y="19">{escape(chord)}</text>')

    for j, (st, e) in enumerate(zip(bar.steps, events)):
        x, end = e["x"], e["endX"]
        o.append(f'<g class="step" data-step="{j}">')
        for string, fret, *_ in st.notes:
            y = y_of(string)
            o.append(f'<rect class="pill" x="{num(x-8)}" y="{num(y-6.5)}" width="{num(end-x-2)}" height="13" rx="6.5"/>'
                     f'<text class="fr" x="{num(x)}" y="{num(y+4.3)}">{fret}</text>')
        if not st.notes:
            label = "4-beat rest" if st.ticks == WHOLE else "rest"
            o.append(f'<rect class="rest-tail" x="{num(x-8)}" y="83" width="{num(end-x-3)}" height="13" rx="6"/>'
                     f'<text class="rest-label" x="{num((x+end)/2-9)}" y="92.5">{label}</text>')
        if st.tech in ("hammer", "pull"):
            x1, x2 = events[j-1]["x"] + 1, x - 1
            mid = (x1 + x2) / 2
            for string, *_ in st.notes:
                y = y_of(string) - 8
                o.append(f'<path class="slur" d="M{num(x1)} {y} Q{num(mid)} {y-9} {num(x2)} {y}"/>'
                         f'<text class="tech" x="{num(mid)}" y="{y-6}">{st.tech[0].upper()}</text>')
        elif st.tech and st.tech != "mute":
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

    hits = {e["at"] for e in events if e["notes"] or e.get("tech") == "mute"}
    counts = [(k * EIGHTH, label) for k, label in enumerate(COUNT)]
    if sixteenths:
        counts.extend((at, "e" if at % QUARTER == 6 else "a") for at in range(6, WHOLE, EIGHTH))
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
    if offset in (6, 18):
        return f"the {'e' if offset == 6 else 'a'} of beat {beat + 1}"
    return f"a thirty-second after beat {beat + 1}"


def describe_fret(fret):
    if fret == "x":
        return "muted"
    return "open" if fret == 0 else f"fret {fret}"


def bar_button(i, bar, events, *, sixteenths=False):
    parts = [f"Bar {i+1}. " + (bar.chord + "." if bar.chord else "")]
    for tick, chord in bar.changes:
        parts.append(f"{chord} on {count_spoken(tick)}.")
    for st, e in zip(bar.steps, events):
        notes = " with ".join(f"{STRINGS[s][1]} string {describe_fret(f)}"
                              for s, f, *_ in st.notes)
        markings = [TECHNIQUES[st.tech]] if st.tech else []
        if st.pick:
            markings.append(st.pick + "stroke")
        parts.append(", ".join([count_spoken(e["at"]).capitalize(), notes or "rest", *markings]) + ".")
    return (f'<button type="button" class="bar" data-bar="{i}" aria-pressed="false" '
            f'aria-label="Loop bar {i+1}" aria-describedby="bar-words-{i}">{bar_svg(i, bar, events, sixteenths)}'
            f'<span class="sr" id="bar-words-{i}">{escape(" ".join(parts))}</span></button>')


PLAY_ICON = '<svg class="ico ico-play" viewBox="0 0 12 12" aria-hidden="true"><path d="M2 1l9 5-9 5z"/></svg>'
STOP_ICON = '<svg class="ico ico-stop" viewBox="0 0 12 12" aria-hidden="true"><rect x="1.5" y="1.5" width="9" height="9" rx="1.5"/></svg>'


ASSETS = Path(__file__).resolve().parent
