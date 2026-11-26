# Thugz Mansion

[Open the practice sheet](index.html)

Tupac Shakur’s acoustic arrangement, as taught by Daniel Chavez. The four-bar intro also serves as the interlude. Each verse/chorus option covers the same four-bar progression.

| Practice bars | Lesson |
|---|---|
| 1–4 | [Intro / interlude](https://www.youtube.com/watch?v=Fzprg4riZIs&t=14s) · [Second half at 5:01](https://www.youtube.com/watch?v=Fzprg4riZIs&t=301s) |
| 5–8 | [Fingerpicking](https://www.youtube.com/watch?v=Fzprg4riZIs&t=463s) |
| 9–12 | [Strumming](https://www.youtube.com/watch?v=Fzprg4riZIs&t=740s) |
| 13–16 | [Muted strumming](https://www.youtube.com/watch?v=Fzprg4riZIs&t=957s) |

Frets, grips, articulations and stroke directions come from the [DC Guitar tab](https://dc-guitar.com/artists/tupac-shakur/thugz-mansion). Its chord names and fret numbers are relative to a first-fret capo in standard tuning. Playback transposes each string up one semitone. The source lists 88 bpm. Its plain-text tab gives no note durations, so the sheet uses a straight sixteenth-note practice grid.

The intro loops on first load. Select a different passage, tap a bar to isolate it, or select all four patterns to play through the examples in lesson order. Play or Space starts a four-click count-in. Each passage heading also works as a link target, for example [muted strumming](index.html#section-13).

## Rebuilding

Run from the repository root with Python 3.

```sh
python3 -B thugz-mansion/build.py
```

[score.py](score.py) records attacks from low E to high e. A dot skips the string and an x is a muted stroke. The [shared renderer and player](../practice/) are inlined in the generated sheet so it opens directly from disk.
