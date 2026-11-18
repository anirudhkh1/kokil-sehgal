# kokilsehgal.com

Portfolio site for Kokil Sehgal, brand and web designer. It's a plain static site
(HTML, CSS and a little JavaScript) with no framework and no build step, hosted on Vercel.

## Folder structure

```
public/                  ← everything here is the live website
  index.html             ← all page content (text, links, FAQ, SEO tags)
  404.html               ← "page not found" page
  css/styles.css         ← all styling (colors are variables at the top)
  js/main.js             ← scroll fade-in, FAQ, contact form, footer year
  fonts/                 ← self-hosted Newsreader + Instrument Sans
  images/                ← optimised WebP photos (generated, don't edit by hand)
  og-image.jpg           ← preview image when the link is shared (generated)
  favicon.*, icon-*.png, apple-touch-icon.png   ← icons (generated)
  robots.txt, sitemap.xml, site.webmanifest
source/                  ← originals, NOT deployed
  images/                ← full-size photos
  og-image.html          ← template for og-image.jpg
  icon.html              ← template for the KS icons
  legacy/                ← the old single-file export, for reference only
scripts/build_assets.py  ← regenerates images/, icons and og-image.jpg
vercel.json              ← tells Vercel to serve public/, adds cache + security headers
```

## Editing content

Open `public/index.html` and change the text directly. Each section is marked with
a comment (`<!-- Services -->`, `<!-- Work -->`, and so on).

- **FAQ:** each question is a `<details>` block. If you change a question or answer,
  also update the matching entry in the `FAQPage` JSON-LD near the top of the file,
  so Google sees the same text.
- **Contact details:** the email address appears in `index.html` and `js/main.js` (`EMAIL`).

## Changing or adding photos

1. Put the new full-size image in `source/images/` with the same file name
   (`kokil-hero.png`, `kokil-about.png`, `work-*.png`). Photos are cropped to
   4:5 (hero), 1:1 (about) and 4:3 (work).
2. Run:
   ```
   pip install Pillow
   python scripts/build_assets.py
   ```
   This writes resized WebP files to `public/images/` and rebuilds the icons and
   `og-image.jpg` (that step needs Chrome or Edge installed).

To add a new project to "Selected work", add its image to `IMAGES` in
`scripts/build_assets.py`, run the script, then copy one of the `<article class="project">`
blocks in `index.html`.

## Client previews

Redesign previews for prospective clients live in `public/preview/`, one
self-contained HTML file per client (the exported file, unchanged):

```
public/preview/dmi.html   →  https://kokilsehgal.com/preview/dmi
```

To add one: export the page as a single HTML file, save it as
`public/preview/<client-name>.html` (lowercase, hyphens, no spaces), then commit and push.
To take one down: delete the file, then commit and push.

If the export is a folder (`index.html` plus `images/`), combine it into one file first:

```
python scripts/build_preview.py <source-folder> <client-name>
```

Every page under `/preview/` is sent with `X-Robots-Tag: noindex` (see `vercel.json`),
so Google won't list these pages. Never add them to `sitemap.xml` or link to them from
the homepage. Anyone with the link can still open it.

## Preview locally

```
cd public
python -m http.server 8000
```
Then open http://localhost:8000.

## Deploying to Vercel

1. Push this folder to a GitHub repository.
2. In Vercel: **Add New → Project**, import the repo. Leave Framework Preset as
   **Other**, with no build command; `vercel.json` already points Vercel at `public/`.
3. Add the domain `kokilsehgal.com` under **Settings → Domains**, and set
   `www.kokilsehgal.com` to redirect to it (the canonical URL has no `www`).

Or use the CLI from this folder: `npx vercel` (preview) / `npx vercel --prod`.

## After launch

- Add the site in [Google Search Console](https://search.google.com/search-console)
  and submit `https://kokilsehgal.com/sitemap.xml`.
- Check the share preview with the [LinkedIn Post Inspector](https://www.linkedin.com/post-inspector/).
- When you edit content, update `<lastmod>` in `public/sitemap.xml`.
