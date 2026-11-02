# theme/

Everything that decides how the book looks lives here, and only here. The manuscript (`manuscript/`) is plain Markdown with no styling in it, and the build tools (`tools/`) read the theme from this folder. Swapping or restyling the theme never touches a chapter: edit or replace these files, run `python3 tools/build.py`, and every edition picks the change up.

| Folder | Used by | What it is |
| --- | --- | --- |
| `site/` | `tools/build_site.py` | The web edition. `style.css` (light and dark palettes, the chapter spine, the hero, code, callouts, tables, footnotes, mobile layout and print styles), `app.js` (mobile menu, copy buttons, current-section highlight, search), `theme-toggle.js`, `favicon.svg`, `apple-touch-icon.png`, the web fonts in `site/fonts/` (WOFF2 subsets) and the page templates in `site/templates/` (`page.html` for parts, chapters and appendices, `index.html` for the home page, `plain.html` for About, Release history and 404). |
| `print/` | `tools/build_pdf.py` | `print.css`: the 7 × 9.25 in PDF for Leanpub and KDP (trim size, margins, running heads, folios, part and chapter openers, the table of contents, code wrapping). |
| `epub/` | `tools/build_epub.py` | `epub.css`: structure and gentle defaults for reading apps, which override fonts and colours at the reader's request. |
| `fonts/` | `print/print.css` | Literata (text), Bricolage Grotesque (headings) and IBM Plex Mono (code) as TTF, with their SIL Open Font Licences (`OFL-*.txt`). |

The look is derived from the author's APM book (apm.isainative.dev): the indigo and amber palette, the type, and the chapter spine.

## Templates

Templates are plain HTML with `{{name}}` placeholders that `tools/build_site.py` fills in (`{{root}}` is the relative path back to the site root, `{{content}}` the rendered chapter, and so on). A placeholder the build does not know stays empty.

## One thing to keep in step

Each template starts with a one-line inline script that applies the saved light or dark choice before the page paints (no flash of the wrong theme). The web edition's Content-Security-Policy in `staticwebapp.config.json` allows exactly that script by its SHA-256 hash. If you change that line, recompute the hash and update the policy, or the browser will block the script:

```sh
python3 -c "import re,hashlib,base64,pathlib; s=re.search(r'<script>(.*?)</script>', pathlib.Path('theme/site/templates/page.html').read_text(), re.S).group(1); print('sha256-' + base64.b64encode(hashlib.sha256(s.encode()).digest()).decode())"
```
