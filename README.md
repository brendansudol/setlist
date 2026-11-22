# Setlist

Guitar lesson notes, one page per song. Each page turns a lesson video into
chord diagrams, a map of where the fretting hand goes, and links to the moment
each shape appears in the video.

**Live site:** https://brendansudol.github.io/setlist/

## Songs

| Song | Page | How it was made |
|---|---|---|
| The Heart of Life (John Mayer), intro and verse | [heart-of-life/](https://brendansudol.github.io/setlist/heart-of-life/) | [heart-of-life/README.md](heart-of-life/README.md) |
| Your Song (Elton John), intro and verse | [your-song/](https://brendansudol.github.io/setlist/your-song/) | [your-song/README.md](your-song/README.md) |
| All The Small Things (Blink-182), intro to chorus | [all-the-small-things/](https://brendansudol.github.io/setlist/all-the-small-things/) | [all-the-small-things/README.md](all-the-small-things/README.md) |

## Layout

```
index.html              the song list (site home page)
heart-of-life/
  index.html            the explainer page, one self-contained file
  README.md             source, prompt, process and data for that page
your-song/
  index.html            the explainer page, generated
  build.py              the data and the generator for that page
  README.md             source, prompt, process and data for that page
all-the-small-things/
  index.html            the explainer page, generated
  build.py              the data and the generator for that page
  README.md             source, prompt, process and data for that page
.nojekyll               tells GitHub Pages to serve the files as they are
```

Every page is plain HTML with inline CSS, inline SVG and inline JavaScript,
and the generated HTML is committed, so the site needs no build
step to deploy. `your-song` and `all-the-small-things` each have their own
`build.py` (standard library only); run it to regenerate that folder's
`index.html`. The two scripts are separate copies that share most of their
code. The generator for `heart-of-life` was not kept, so that page is edited
by hand.

Every song page has a docked video player: tapping a timestamp plays that
moment of the lesson in YouTube's embedded player, which stays on screen
(across the top on a phone, in the right margin on a wide window). It is
described in
[the All The Small Things write-up](all-the-small-things/README.md#the-docked-player),
where it was built first. The player's styles, markup and script are the same
text in both `build.py` files and in `heart-of-life/index.html`, so a change
to it has to be made in all three.

## Adding a song

1. Follow the pipeline in [your-song/README.md](your-song/README.md#process).
2. Copy `your-song/build.py` into a new folder, replace the data at the top
   (including `VIDEO_ID` and `PARTS`, which the video player uses), and run
   it. Write a `README.md` next to it.
3. Add the song to the list in `index.html` and to the table above.

## Hosting

GitHub Pages serves the `main` branch from the repository root. Pushing to
`main` updates the site.

## Credit

The lessons belong to their instructors; each page links back to its source
video. The pages contain no video frames, lyrics or TAB; the video is played
by YouTube's own embedded player. Diagrams are original drawings.
