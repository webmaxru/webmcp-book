# The electronic edition

This folder builds the web edition of *Tools, Not Clicks: Building Agent-Ready Websites with WebMCP* (working title), published at **https://vibeprogrammer.github.io/webmcp-book/**.

It follows the build of Maxim Salnikov's earlier book, [github-agentic-workflows-book](https://github.com/webmaxru/github-agentic-workflows-book): a Python generator, the same "Reader" design (`assets/style.css` and `assets/app.js` are copied from it unchanged; `assets/book.css` adds what this book needs), and a GitHub Actions workflow that publishes to the `gh-pages` branch.

## The manuscript is never edited

`outline/outline.md` and the chapter files under `chapters/` stay publication-ready Markdown. The build only reads them:

- The front page is the book outline. Parts and chapters are read from the "Chapter outline" section of `outline/outline.md`.
- A chapter is published once a Markdown file whose first heading is `# Chapter N: …` exists in a folder under `chapters/`. Every other chapter, and the appendices, are shown as **To be published**. Adding a chapter means adding its folder; nothing here needs to change.
- Rendering happens in memory: footnotes become linked notes, `**Listing N.N — …**` captions become code figures with syntax highlighting, `![…](images/…)` plus its `*Figure N.N — …*` caption becomes a figure (images are copied next to the page), and `> **Still in flux: …**` blockquotes become callouts.

## Build locally

```bash
python -m pip install -r site/requirements.txt
python site/generate.py          # writes site/_site/ (git-ignored)
python -m http.server -d site/_site 8000
```

## Publish

Every push to `main` that touches `chapters/`, `outline/` or `site/` runs `.github/workflows/deploy-pages.yml`, which builds the site and force-pushes it to the `gh-pages` branch. GitHub Pages serves that branch.

## Calls to action

Both links are set at the top of `generate.py` and come from the earlier book's generator:

- Publishers: contact Maxim Salnikov, https://www.linkedin.com/in/webmax/
- Newsletter: the isainative Substack, https://isainative.substack.com/subscribe

## Pages

- `index.html`: cover, both calls to action, and the outline with each chapter's status
- `chapters/<folder>.html`: one page per published chapter, with sidebar, "On this page", notes and prev/next
- `outline.html`: the full outline document; `outline/WebMCP_Book_Outline.pdf`
- `book.html`: all published chapters on one page (for printing)
