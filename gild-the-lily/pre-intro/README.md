# Gild the Lily · interactive guitar tab

[Open the practice sheet](index.html) · [Chord guide](../index.html)

The sheet covers bars 1–69 of *Billy Strings – Gild the Lily (Intro & more)*,
arranged and tabbed by B-RoM. It runs directly from the generated HTML.
The first seven bars also appear in [B-RoM’s video lesson](https://www.youtube.com/watch?v=U9BqvaBOR8Y&t=193s).
Their chord labels are inferred. Later chord changes follow the PDF,
including the change on beat 3 of bar 59.

## Practicing

Play or Space starts a four-beat count-in. The tempo slider runs from
40 to 130 bpm and defaults to 72. Click toggles the metronome during
playback. The guitar stays silent for the duration of each written rest.

Choose the whole score, a passage, or either original pre-intro phrase in
the Loop menu. Tap a bar to repeat it and tap it again to return to all 69.
The cursor follows the sounding part and brings each row into view.

The guitar uses Woodshed’s steel-string sound. The fundamental and lower
overtones sustain while the higher overtones fade quickly. The player gives
hammer-ons, pull-offs and slides a softer attack. [Original voice in Woodshed](https://github.com/brendansudol/guitar-woodshed/blob/b7265be/js/audio.js)

## Rebuilding

```sh
python3 -B gild-the-lily/pre-intro/build.py
```

[score.py](score.py) holds the strings, frets, written pitches, picking and
articulations. Durations use 24 ticks per quarter note, which represents
both the triplet in bar 38 and the thirty-second in bar 39 exactly.
[build.py](build.py) checks the measure lengths, pitches and legato
connections, draws the tab, and embeds [player.js](player.js) and the
same score timing in [index.html](index.html). The build uses the Python
standard library. Synthesized slides, bends and vibrato approximate the
printed articulations.

<details>
<summary>History of the original seven-bar version</summary>

## Source

| | |
|---|---|
| Lesson | [How to play "Gild The Lily" - Billy Strings - Guitar Lesson with Tab](https://www.youtube.com/watch?v=U9BqvaBOR8Y&t=193s), 6:07 |
| Channel | B-RoM |
| Stretch used | 3:13 to 3:31, where the lesson shows bars 1 to 7 of its tab |
| Tuning | Standard. Not stated; see "How sure each part is". |

This is a different lesson from the one the main page is built on. The main
page already pointed to it as a place where tab is shown on screen.

## Who made it

Claude (Anthropic's AI model), in one working session, at the request of the
site's owner.

## The prompt

> screenshot and put together the tab for the pre-intro part from 3:13 - 3:31
> here - https://www.youtube.com/watch?v=U9BqvaBOR8Y so i can see it all in one
> digestible place for practicing

The first attempt did exactly that: three lines of tab captured from the video
and joined into one image. On seeing it, the owner asked for something better:

> instead of stitching images together, you could just use the info from the
> images and recreate the tab using a better presentation / web tech as needed

So the frames became working material and the tab was redrawn from what they
show. When the page was working:

> deploy it and push it up live

## This page writes the notes out

No other page on this site does. The main Gild the Lily page maps the intro
lick without giving its notes, and says why. This sheet is the exception, made
because the site's owner asked for it: seven bars, credited to the lesson they
came from and linked to the moment it shows them. The frames are not in this
repository, and the main lick is still not written out.

## Process

1. **Finding the lines.** One frame a second from 3:13 to 3:31 showed that the
   lesson puts up three lines of tab in that stretch: bars 1 to 3 at 3:12,
   bars 4 to 6 at 3:21, and a line starting with bar 7 at 3:28. A cursor
   reaches bar 8, where the main lick begins, at about 3:30.
2. **Clean frames.** Each line was captured at 1080p at a moment when the
   cursor was somewhere else, in two overlapping halves so the numbers were
   large enough to read without doubt.
3. **Reading.** Every bar was read twice: the fret numbers on the tab, and the
   notes and note lengths on the staff above it.
4. **Data, then a generator.** The bars went into `build.py` as data. The
   script checks them, draws each bar as SVG and writes the page, including
   the same data as JSON for the player.
5. **Testing.** Served from a local web server and checked in a browser at
   1024 and 456 pixels wide, and in dark mode at the narrower width. It was
   not tested on a real phone. Playback was run with the
   sound muted and checked by what it scheduled and what the page showed: the
   count-in, the length of every step at 72 beats a minute, the hammer-on
   starting without a pick attack, a single bar looping, bars 4 to 7 looping
   in order, and nothing sounding after Stop.

Two things about capturing frames that were not obvious. The background-tab
technique itself is in
[Your Song's write-up](../../your-song/README.md#getting-frames-from-a-background-tab).

- **The browser tool's capture region is in screenshot pixels, not page
  pixels.** Here a 1440-pixel-wide page came back as a 1543-pixel-wide
  screenshot, so a region sized from the page's own measurements cut off the
  right-hand 7 per cent of the canvas, and the two halves of each line did not
  meet. Drawing the canvas on a bright magenta backdrop and capturing a little
  more than its size let a script find the canvas edge exactly.
- **Asking for a scaled-down screenshot shrinks the saved file too,** not just
  the preview.

## What was captured

Seven bars in 4/4. The notes themselves are in `build.py`, as string, fret and
length for every step.

| Bar | Chord it outlines | In short | Lesson |
|---|---|---|---|
| 1 | D | Open D string under a D shape, with a hammer-on from fret 2 to 3 on the high E | [3:13](https://www.youtube.com/watch?v=U9BqvaBOR8Y&t=193s) |
| 2 | Am | Open A string under an Am shape, picked one string at a time | |
| 3 | G | Fret 3 of the low E, with a 2, 4, pull-off figure on the G string | |
| 4 | D | Open D twice, then D with fret 2 of the G string, held | [3:21](https://www.youtube.com/watch?v=U9BqvaBOR8Y&t=201s) |
| 5 | D | Open D twice, then bar 1's hammer-on again | |
| 6 | Am | Open A with fret 1 of the B string, then that note alone | |
| 7 | D | Fret 5 of the A string and fret 4 of the D string, held for the bar | [3:28](https://www.youtube.com/watch?v=U9BqvaBOR8Y&t=208s) |

## How sure each part is

- **Strings and frets** were read from frames large enough that no number was
  in doubt, and each one agrees with the note written on the staff above it.
- **Note lengths** come from the staff. Every bar adds up to four beats.
- **The hammer-ons and the pull-off** are marked H and P in the lesson's tab.
- **Chord names are a reading, not the lesson's.** Its tab names no chord over
  these bars. In each bar the lowest note is the root of the chord given.
- **"It follows the chords of the verse"** compares this with the main page's
  verse: D, Am, G, D, D, then C or Am, then D. Bar 6 here is A and C, which is
  Am.
- **Tuning is inferred** from the staff and the tab agreeing in standard
  tuning. Whether the instructor uses a capo was not checked.
- **About 100 beats a minute** is an estimate from how long the lesson's
  cursor takes to cross each line.
- **Nobody listened.** The frames have no sound, and the page's playback was
  tested muted. Its pitches were measured instead: each synthesised note is
  within about 3 cents of the note it stands for. Whether the lesson's playing
  matches its own tab was not checked by ear.
- **Fingering** on the page is the plain consequence of the chord shapes. The
  instructor's hands were not studied.

## Checks built into the generator

`build.py` refuses to write the page unless:

- every bar is exactly eight eighth notes long;
- every fret, in standard tuning, gives the note that was read from the staff
  for it, an octave down, as guitar music is written;
- no step puts two notes on one string;
- every hammer-on goes up from a note on the same string, and every pull-off
  comes down;
- the lowest note of every bar is the root of the chord the bar is labelled
  with;
- every timestamp falls inside the stretch of the video the page covers.

## Design

Same paper, ink and type as the other pages. What is specific here:

- **Everything in one place.** Four bars to a row on a wide window, two on a
  phone, with the controls pinned to the bottom of the window for as long as
  the tab is on screen. The string names are drawn only on the bar that
  starts a row.
- **A tail behind every number** shows how long the note lasts, which plain
  tab does not.
- **The count under every bar,** in eighths, bold where a note starts.
- **Green** is the colour the other pages give open chords, and every chord
  here is one. It also marks the note sounding during playback.
- **The eighth cell** of the grid points to where the lesson's tab carries on.

## The player

A few dozen lines of script, no library. Each note is a short plucked-string
sound made in the browser (the Karplus-Strong method: a burst of noise fed
round a delay line), scheduled a fraction of a second ahead of the clock so a
change of tempo is heard on the next note.

- **Play** counts one bar in, then loops until stopped. Space does the same.
- **Tempo** runs from 40 to 130 beats a minute and starts at 72.
- **All, 1-3 and 4-7** choose what loops. Tapping a bar loops that bar alone;
  tapping it again goes back to all seven.
- **Click** turns the metronome off or on.
- A note rings until the same string is played again, as it would on a
  guitar. Hammer-ons and pull-offs sound without a pick attack.
- This page has no docked video player. Its timestamps open YouTube.

</details>
