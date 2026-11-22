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

Every page is plain HTML with inline CSS, inline SVG and a few lines of inline
JavaScript, and the generated HTML is committed, so the site needs no build
step to deploy. `your-song` and `all-the-small-things` each have their own
`build.py` (standard library only); run it to regenerate that folder's
`index.html`. The two scripts are separate copies that share most of their
code. The generator for `heart-of-life` was not kept, so that page is edited
by hand.

`all-the-small-things` also has a docked video player: tapping a timestamp
plays that moment of the lesson at the top of the page, using YouTube's
embedded player. It is a trial on that one page; on the other two the
timestamps open YouTube. See
[its write-up](all-the-small-things/README.md#the-docked-player).

## Adding a song

1. Follow the pipeline in [your-song/README.md](your-song/README.md#process).
2. Copy `your-song/build.py` into a new folder, replace the data at the top,
   and run it. Write a `README.md` next to it.
3. Add the song to the list in `index.html` and to the table above.

## Hosting

GitHub Pages serves the `main` branch from the repository root. Pushing to
`main` updates the site.

## Credit

The lessons belong to their instructors; each page links back to its source
video. The pages contain no video frames, lyrics or TAB. Diagrams are original
drawings.
