# Setlist

Guitar lesson notes, one page per song. Each page turns a lesson video into
chord diagrams, a map of where the fretting hand goes, and links to the moment
each shape appears in the video.

**Live site:** https://brendansudol.github.io/setlist/

## Songs

| Song | Page | How it was made |
|---|---|---|
| The Heart of Life (John Mayer), intro, verse, chorus and outro | [Chord guide](heart-of-life/index.html) · [Interactive tab](heart-of-life/practice/index.html) | [heart-of-life/README.md](heart-of-life/README.md) |
| Your Song (Elton John), intro and verse | [your-song/](https://brendansudol.github.io/setlist/your-song/) | [your-song/README.md](your-song/README.md) |
| All The Small Things (Blink-182), intro to chorus | [all-the-small-things/](https://brendansudol.github.io/setlist/all-the-small-things/) | [all-the-small-things/README.md](all-the-small-things/README.md) |
| Gild the Lily (Billy Strings), verse, chorus and bridge | [gild-the-lily/](https://brendansudol.github.io/setlist/gild-the-lily/) | [gild-the-lily/README.md](gild-the-lily/README.md) |
| Thugz Mansion (Tupac Shakur), intro and three verse/chorus patterns | [Interactive tab](thugz-mansion/index.html) · [Chord shapes and fingering](thugz-mansion/chords.html) | [thugz-mansion/README.md](thugz-mansion/README.md) |
| Banana Pancakes (Jack Johnson), the whole song | [banana-pancakes/](https://brendansudol.github.io/setlist/banana-pancakes/) | [banana-pancakes/README.md](banana-pancakes/README.md) |
| Danny's Song (Loggins & Messina), the whole song | [Chord guide](dannys-song/index.html) · [Interactive tab](dannys-song/practice/index.html) | [dannys-song/README.md](dannys-song/README.md) |

## Layout

```
index.html              the song list (site home page)
heart-of-life/
  index.html            the explainer page, one self-contained file
  README.md             source, prompt, process and data for that page
  practice/             the lesson loops, their generator and the standalone tab player
your-song/
  index.html            the explainer page, generated
  build.py              the data and the generator for that page
  README.md             source, prompt, process and data for that page
all-the-small-things/
  index.html            the explainer page, generated
  build.py              the data and the generator for that page
  README.md             source, prompt, process and data for that page
gild-the-lily/
  index.html            the explainer page, generated
  build.py              the data and the generator for that page
  README.md             source, prompt, process and data for that page
  pre-intro/            the 69-bar B-RoM guitar arrangement and practice player
    index.html          the tab and its player, generated
    build.py            validates the score and generates the standalone sheet
    score.py            the transcribed measures and practice passages
    README.md           source, prompt, process and data for that sheet
thugz-mansion/          Daniel Chavez’s four tab examples and their generator
practice/               notation renderer, styles and audio shared by the tab sheets
banana-pancakes/
  index.html            the explainer page, generated
  build.py              the data and the generator for that page
  README.md             source, prompt, process and data for that page
dannys-song/
  index.html            the explainer page, generated
  build.py              the data and the generator for that page
  README.md             source, prompt, process and data for that page
.nojekyll               tells GitHub Pages to serve the files as they are
```

Every page is plain HTML with inline CSS, inline SVG and inline JavaScript,
and the generated HTML is committed, so the site needs no build
step to deploy. `your-song`, `all-the-small-things`, `gild-the-lily`,
`banana-pancakes` and `dannys-song` each have their own `build.py` (standard
library only); run it to regenerate that folder's `index.html`. The five
scripts are separate copies that share most of their code, and the pages they
make are not meant to look alike: each is built around what its song needs. The generator for `heart-of-life` was not kept, so that page is edited
by hand.

Every page made from a YouTube lesson has a docked video player: tapping a
timestamp plays that moment of the lesson in YouTube's embedded player, which
stays on screen
(across the top on a phone, in the right margin on a wide window). It is
described in
[the All The Small Things write-up](all-the-small-things/README.md#the-docked-player),
where it was built first. The player's styles, markup and script are the same
text in all four `build.py` files and in `heart-of-life/index.html`, so a
change to it has to be made in all five. A lesson can be split across
videos, as Gild the Lily's is: the player loads whichever one a timestamp
belongs to. `dannys-song` is the exception. Its lesson is a paid download of
video files. Its chord guide lists the video timestamps, and its separate
practice sheet synthesizes the guitar part.

## Adding a song

1. Follow the pipeline in [your-song/README.md](your-song/README.md#process).
2. Copy `your-song/build.py` into a new folder, replace the data at the top
   (including `VIDEO_ID` and `PARTS`, which the video player uses), and run
   it. Write a `README.md` next to it. For a lesson in more than one video,
   start from `gild-the-lily/build.py` instead.
3. Add the song to the list in `index.html` and to the table above.

## Hosting

GitHub Pages serves the `main` branch from the repository root. Pushing to
`main` updates the site.

## Credit

The lessons belong to their instructors; each page links back to its source
video. The pages contain no video frames or lyrics, and the video is played
by YouTube's own embedded player. Diagrams are original drawings.
The playable tab sheets cover [Six String Fingerpicking’s Heart of Life lessons](heart-of-life/README.md#interactive-practice-sheet),
[B-RoM’s Gild the Lily arrangement](gild-the-lily/pre-intro/README.md),
[Daniel Chavez’s Thugz Mansion patterns](thugz-mansion/README.md) and
[the Jerry’s Guitar Bar arrangement of Danny’s Song](dannys-song/practice/index.html).
