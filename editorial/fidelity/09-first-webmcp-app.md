# Fidelity: Chapter 9, Your First WebMCP App, End to End

Checked 22 November 2026 against `python3 /tmp/check_fidelity.py` (OK) and against the strings listed below.

## Protected spans

Verified with the same extractors as `check_fidelity.py` (hashes match the baseline):

- Fences: 14
- Tables: 3 spans. Two are Tables 9.1 and 9.2. The third is the single source line in Listing 9.3 that begins `|| !Number.isInteger` (the checker treats a line whose first non-space character is `|` as a table). That line was not edited.
- Figures: 3 (`![Figure 9.1`, `![Figure 9.2`, `![Figure 9.3`)
- Footnotes: 25

The single H1 was not renamed. Listing labels, figure lines, table lines, and footnote definitions were not edited.

## Checker

`OK 09-first-webmcp-app.md fences=14 tables=3 figures=3 footnotes=25 quotes=76`

## Strings confirmed still present

- Builds and dates: Chromium 159.0.8154.6, 18 November run, Chrome trial extended to 162, Edge trial 30 March 2027, `@w3c/webmcp-polyfill` 0.1.1.
- First person kept: “I didn’t run the two extensions for this chapter”, “which I co-author”, “another page I co-author”.
- Quotations left intact beside the edits: “as they appear to the AI agent”, “data from the page, not instructions.”, “Share the application service”, “Pin versions:”.
- The Prompt API limit stays: `availability()` reported `"downloadable"`, and the suite does not download the model.

## Generalized

- Removed “I’ve been writing about service workers since 2017, and this part feels very familiar”. Kept the analogy only: “A service worker is also an enhancement of a page that has to work without it.” The 2017 history is not restated.

## Flags

- “the practical questions every team asks on its first day with WebMCP” is an unsupported universal. It was already in the chapter and was left as written.
- The closing “Bottomline:” remains. It sits inside a baseline quote span. Editing it failed the checker, so it was restored.
- “page's” in “A page's tools” is a pre-existing ASCII apostrophe in a sentence whose only edit was dropping “so let's look at them separately.”
