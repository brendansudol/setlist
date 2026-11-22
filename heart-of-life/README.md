# The Heart of Life: how this page was made

**Live page:** https://brendansudol.github.io/setlist/heart-of-life/

[`index.html`](index.html) is a one-file explainer for the six chord shapes in the
intro and verse of "The Heart of Life", worked out from a YouTube guitar lesson.
Tapping any timestamp plays that moment of the lesson in a YouTube player that
stays on screen. This file records where the content came from, how the page
was produced, and what you would need to do the same for another lesson.

## Source

| | |
|---|---|
| Video | [The Heart of Life (John Mayer) Guitar Lesson](https://youtu.be/dgEQvqHTQbw) |
| Channel | Six String Fingerpicking |
| Length | 12:26 |
| Covers | Intro and verse only. The rest of the song is not in this video. |
| Tuning | Standard, no capo. The instructor notes the recording is a half step lower. |

## Who made it

The page was produced by Claude (Anthropic's AI model) in a single working
session, starting from a link to the video. A later session packaged it into
this repository without changing the page.

## The prompt

The exact wording of the opening request was not saved, so it is not quoted
here. What survives is the handoff note written at the end of that session;
the rest of this document is built from it.

A request along these lines asks for the same thing. It is a reconstruction,
not the original:

> Here is a guitar lesson video: `<YouTube URL>`. Make me a phone-friendly page
> that explains the chord shapes it teaches: the progression, a diagram for
> each shape with the fingers, strings and frets, and how the picking pattern
> fits on top. Link each shape to the moment it appears in the video. Don't
> copy frames, lyrics or TAB.

## Process

1. **Get the facts about the video.** Fetching the YouTube URL directly was
   rate limited, so the video was opened in a browser instead. Title, channel
   and length were read from `window.ytInitialPlayerResponse`. Chapters and the
   transcript came from the "Show transcript" panel, because the caption-track
   URL returned nothing.
2. **Confirm every shape by eye.** The transcript gives the frets the
   instructor says out loud. Each one was then checked against the picture:
   pause, set `video.currentTime`, force 1080p, apply a CSS
   `transform: scale(3)` to the `<video>` element with `transform-origin` on
   the fretting hand, and screenshot the player.
3. **Generate the diagrams from data.** A Python script held the shapes as
   data and wrote every diagram as inline SVG: the chord boxes, the
   hand-travel chart and the picking grid. Before writing any HTML it asserted
   each string and fret against the note name it should produce, so a
   mistyped fret would stop the build.
4. **Check the layout.** The page was rendered once at 390px wide, in light
   and dark mode, in headless Chrome.

## What was captured

**Loop (8 bars):** D, D, Bm, Bm, F#m, G, D/F#, A

**Shapes.** Frets are listed from string 6 (low E) to string 1 (high E).
`x` is a string the picking pattern skips.

| Chord | 6 | 5 | 4 | 3 | 2 | 1 | Family | Video |
|---|---|---|---|---|---|---|---|---|
| D | 10 | x | 12 | 11 | 10 | x | Major, thumb over | [1:41](https://youtu.be/dgEQvqHTQbw?t=101) |
| Bm | 7 | x | 9 | 7 | 7 | x | Minor, thumb over | [2:00](https://youtu.be/dgEQvqHTQbw?t=120) |
| F#m | 2 | x | 4 | 2 | 2 | x | Minor, thumb over | [2:17](https://youtu.be/dgEQvqHTQbw?t=137) |
| G | 3 | x | 5 | 4 | 3 | x | Major, thumb over | [2:24](https://youtu.be/dgEQvqHTQbw?t=144) |
| D/F# | 2 | x | 0 | 2 | 3 | 2 | Open | [2:30](https://youtu.be/dgEQvqHTQbw?t=150) |
| A | x | 0 | 2 | 2 | 2 | x | Open | [2:38](https://youtu.be/dgEQvqHTQbw?t=158) |

The thumb frets the low E string on every chord except A.

**Pinky notes in the second bar.** D adds the B string at fret 12
([5:05](https://youtu.be/dgEQvqHTQbw?t=305)). Bm adds the B string at fret 10
([6:06](https://youtu.be/dgEQvqHTQbw?t=366)).

**One bar of picking**

| Beat | What happens |
|---|---|
| 1 | Pinch: bass string and B string together |
| 2 | Thumb taps the bass string while the index flicks down on the G string |
| 2& | B string |
| 3 | Bass string |
| 3& | D string |
| 4 | Tap and G string again |

**Other timestamps:** picking pattern
[3:11](https://youtu.be/dgEQvqHTQbw?t=191), picking on the A chord
[7:50](https://youtu.be/dgEQvqHTQbw?t=470), full loop
[8:28](https://youtu.be/dgEQvqHTQbw?t=508), melody
[8:45](https://youtu.be/dgEQvqHTQbw?t=525).

## Rules the page follows

- **No video frames.** The diagrams are original drawings. Every shape
  deep-links to its moment in the video (`youtu.be/ID?t=SECONDS`) so the real
  hand position is one tap away.
- **No lyrics, and no note-by-note melody or TAB.** The melody section is
  pointed to, not transcribed.
- **Fingering is labelled honestly.** Frets and strings come from the lesson.
  Finger numbers are the standard fingering for each shape, and the page says
  so.

The page was first published with a fourth rule, no embedded player, because
its first host blocked remote images and iframes. GitHub Pages does not, and
that rule has been dropped; see the next section. The page is still one file
and still contains no footage.

## The docked player

Added after the page was first published. The player was tried on
[All The Small Things](../all-the-small-things/README.md#the-docked-player)
first, and the request that brought it here was:

> yes, push it live and can we also incorporate for the other songs too

It is the same player, and that write-up describes how it behaves at each
window width, the speed and loop buttons, and the fallback to plain links.
What is specific to this page:

- **It was added by editing `index.html`,** because this page has no
  generator. A one-off script pasted in the player's styles, markup and
  script from the All The Small Things generator and gave each timestamp
  link its time and a name (`data-t` and `data-part`). The script was not
  kept.
- **23 timestamps play in the page:** the six cards, the two pinky notes, the
  four links under the picking section, the seven chapters and the four
  shortcuts.
- **The shortcuts** beside the video on a wider window are Chords (1:08),
  Pattern (3:11), Pinky notes (5:05) and Melody (8:45).
- **Checked** in a desktop browser at 1152 by 630, 900 by 700 and 375 by 812:
  a tap plays the right moment of the right video, the shortcuts, speed and
  loop work, a bar tapped in the loop lands in view, and closing the video
  leaves the page where it was. It was not tested on a real phone.

## Design

- Phone-first, single column, meant to be read with the phone propped up next
  to the guitar.
- Colour means one thing only: which of the three hand-shape families a chord
  belongs to (major with thumb over, minor with thumb over, open). Everything
  else is grey.
- The "I can play this" checkboxes are saved in the browser's `localStorage`,
  wrapped in `try`/`catch` so the page still works where storage is blocked.
  Nothing is sent anywhere.
- Until a timestamp is tapped, the only outside request is Google Fonts
  (Atkinson Hyperlegible and Bricolage Grotesque), with system fonts as the
  fallback. The first tap loads YouTube's player.

## What is not in this repository

- **The generator script.** It was not kept after the session. `index.html`
  is the generator's output, so edits now happen directly in that file, and
  the note-name assertions from step 3 no longer run.
- **The transcript and the screenshots** used to confirm the shapes. They were
  working material only.

## Doing this for another lesson

The same pipeline applies:

1. Transcript first, for the frets the instructor says out loud.
2. Frames to confirm each shape, using the zoom technique in step 2.
3. Put the shapes in a data structure, generate the diagrams, and assert every
   string and fret against its note name.
4. Render at phone width in light and dark mode before publishing.

Then add a folder next to this one with its own `index.html` and `README.md`,
and add the song to the list in the top-level [`index.html`](../index.html).
