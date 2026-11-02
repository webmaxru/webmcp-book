# Releasing

Each release of *Tools, Not Clicks* is a Git tag `vX.Y.Z`. Pushing the tag builds the book from that tag and publishes a GitHub Release with three files, plus their checksums:

- `Tools-Not-Clicks-Maxim-Salnikov-vX.Y.Z.pdf`: the print PDF, 7 × 9.25 in (Leanpub and KDP).
- `Tools-Not-Clicks-Maxim-Salnikov-vX.Y.Z.epub`: EPUB 3, checked with EPUBCheck.
- `Tools-Not-Clicks-HTML-vX.Y.Z.zip`: the web edition, readable offline (open `index.html`).
- `SHA256SUMS.txt`.

The release notes are the version's section of [`CHANGELOG.md`](CHANGELOG.md). After a stable release is published, the workflow asks `deploy-swa` to put that tag on the web edition at https://webmcp.salnikov.no (see [`DEPLOY.md`](DEPLOY.md)). Everything runs on the built-in `GITHUB_TOKEN`; no secrets are needed for the release itself.

## Version numbers

Versions follow Semantic Versioning, read for a book:

- **Major** (`3.0.0`): a new edition. The book is revised as a whole, chapters are added, removed or reordered, or the API it teaches changes in a way that breaks earlier listings.
- **Minor** (`2.1.0`): new material inside the current structure. A new section or appendix, a new figure or listing, a status update (for example a Chrome version that changes what works).
- **Patch** (`2.0.1`): corrections. Typos, broken links, wrong numbers, layout fixes, theme and build fixes that change no text.
- **Pre-release** (`2.1.0-rc.1`): a review copy. Published as a GitHub pre-release, never marked Latest, and not deployed to the web edition.

Version 1.0.0 (15 October 2026) was the first edition. It was never tagged, so it has no GitHub Release; CHANGELOG.md records it as the baseline. Version 2.0.0 is the first tagged release.

## Cut a release

1. On `main`, set `"version"` in [`tools/book.json`](tools/book.json) to the new version. For a release that re-tests the book, also update `"chrome_version"` and `"spec_date"` there: the title and copyright pages print them.
2. In `CHANGELOG.md`, change the version's heading from `## [X.Y.Z] - unreleased` to `## [X.Y.Z] - YYYY-MM-DD` (the release date), and add the compare link at the bottom. The release fails if the date is missing.
3. Check locally (optional; CI does the same on the pull request):

   ```sh
   python3 tools/lint_manuscript.py
   python3 tools/build.py all
   ```

4. Merge to `main`, then tag the merge commit and push the tag:

   ```sh
   git switch main && git pull
   git tag -a vX.Y.Z -m "vX.Y.Z"
   git push origin vX.Y.Z
   ```

5. Watch **Actions → Release**. It checks that the tag matches `tools/book.json`, takes the notes from CHANGELOG.md, runs the lint, builds the three editions, runs EPUBCheck, publishes the release, and starts the web deploy. The release is marked **Latest** only when its tag is the highest stable version.
6. Upload the new PDF and EPUB to Leanpub and KDP (see [README.md](README.md#leanpub) and [README.md](README.md#kindle-direct-publishing-kdp)).

## Rebuild or publish a release by hand

**Actions → Release → Run workflow**, with `tag` set to an existing tag (for example `v2.0.0`). The workflow builds from that tag and replaces the release's files, keeping the release itself. Use it when a build fix must reach an existing release, or when a tag was pushed before the workflow existed.

The release notes always come from `CHANGELOG.md` on the default branch, so a corrected changelog entry can be republished the same way.

## Roll back the web edition

**Actions → deploy-swa → Run workflow**, with `ref` set to an earlier tag. The PDF and EPUB of every version stay on their GitHub Releases.

## Fix a bad release

Don't move a tag that people may have downloaded. Fix the problem on `main`, add a patch entry to CHANGELOG.md, and release `vX.Y.(Z+1)`. To withdraw a release completely, delete it on GitHub (Releases → … → Delete), then delete the tag (`git push origin :refs/tags/vX.Y.Z`).

## What the build reads

The editions are built only from `manuscript/` (the text, `Book.txt` and the images in `manuscript/resources/images/`), `tools/book.json` (title, version, copyright lines, links), `CHANGELOG.md` (the web edition's Release history page) and `theme/` (all styling). `figures/` holds the sources of the figures; render them into `manuscript/resources/images/` before a release.
