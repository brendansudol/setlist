# Setlist

Guitar lesson notes, one page per song. Each page turns a lesson video into
chord diagrams, a map of where the fretting hand goes, and links to the moment
each shape appears in the video.

**Live site:** https://brendansudol.github.io/setlist/

## Songs

| Song | Page | How it was made |
|---|---|---|
| The Heart of Life (John Mayer), intro and verse | [heart-of-life/](https://brendansudol.github.io/setlist/heart-of-life/) | [heart-of-life/README.md](heart-of-life/README.md) |

## Layout

```
index.html              the song list (site home page)
heart-of-life/
  index.html            the explainer page, one self-contained file
  README.md             source, prompt, process and data for that page
.nojekyll               tells GitHub Pages to serve the files as they are
```

There is no build step. Every page is plain HTML with inline CSS, inline SVG
and a few lines of inline JavaScript.

## Adding a song

1. Follow the pipeline in
   [heart-of-life/README.md](heart-of-life/README.md#doing-this-for-another-lesson).
2. Put the result in a new folder with its own `index.html` and `README.md`.
3. Add the song to the list in `index.html` and to the table above.

## Hosting

GitHub Pages serves the `main` branch from the repository root. Pushing to
`main` updates the site.

## Credit

The lessons belong to their instructors; each page links back to its source
video. The pages contain no video frames, lyrics or TAB. Diagrams are original
drawings.
