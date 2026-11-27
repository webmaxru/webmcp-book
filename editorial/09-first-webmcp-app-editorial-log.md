# Editorial log: Chapter 9, "Your First WebMCP App, End to End"

Manuscript: `manuscript/09-first-webmcp-app.md`
Figures: `figures/src/figure-9-1.svg` (start-up decision flow), `figure-9-2.svg` (hub: the six ways to reach the tools, replacing the old card grid), `figure-9-3.svg` (trial timeline), hand-written SVG per the APM figure kit, rendered to `manuscript/resources/images/`
Demo: `chapters/09-first-webmcp-app/` in webmaxru/webmcp-book-demos. Changed: `app.js` (Listing 9.4, batch rollback), `tests/run-tests.mjs` (new rollback test, `init` option for `openPage`), README status block. Suite: 22 checks with `CHAPTER_MD` (21 without), Chromium 156.0.8078.4, Playwright 1.64.1. Result: see the README status block and the validation file.
Validation: VALIDATION.md (37 rows)
Length: 8,364 words (Oct 15) → 9,222 words (`wc -w`, listings included). Growth: the rollback section and table row, the issue #361 and PR #348 notes in the Test Agent section, "Pin versions", "Share the application service", the Chrome 156 Stable sentence.

Materials read before writing: his voice profile and the Book 2 voice report, .agents/skills/personal-author-voice/SKILL.md, professional-writing-editor/references/slop-patterns.md, Book 2's introduction, his recent article.

## Pass 1: voice draft (personal-author-voice)

Register: technical walkthrough (setup, code, tests), with short exploratory passages where the chapter weighs options (polyfill or not, what the trial means).

- "I" only for real authorial acts: the re-run of the suite, "I didn't run the two extensions", and two verified facts about Maxim: he co-authors the Chrome best-practices and build-tools pages (bylines verified 2 Nov 2026), and he has written about service workers since 2017 (his own blog corpus, his voice profile). The service-worker line frames progressive enhancement and makes no claim beyond that.
- Repertoire used where it fits: "Let's put the pieces back together", "Let's start with the tool you already have open", "Have a look at the AbortController", "Some important things to notice here", "Please note:", "of course", "Bottomline:" closing the Fjord Table section, one ":)" (the DevTools pane: "your bug and not the agent's choice"), rhetorical questions that open a real distinction ("Is that worth a 27 KB download for every visitor?", "But what if search_availability registers and book_table is then refused?").
- Long sentences split, spoken rhythm, em dashes 2.2 per 1k words.

## Pass 2: substantive edit (professional-writing-editor)

- Structure kept. The new material went where a reader needs it: the batch rollback inside "Wiring it up" (it explains a listing change), the serialization caveat inside the Test Agent section (it explains the `parse()` fallback), "Pin versions" right after the three booking tests.
- Callouts, listing labels and figure syntax converted to house form. Listing labels now carry the demo path.
- Slop pass: no filler openers, no stacked triads added, no "worth noting", no summary closers inside sections. "not X, but Y" constructions: 0. Semicolons in prose: 0 (the old text had several, split into sentences).
- One phrase I first drafted ("in my experience with any new web platform feature") was removed: it claimed experience the sources don't document. Replaced with the plain statement.
- Checklist item 4 now includes the all-or-nothing test, and the summary has a bullet on registering tools as a set.

## Pass 3: voice recheck + fidelity check

Scripted check against the Oct 15 text: every inline code token, number and URL of the old prose is still present. Code blocks: 11 of 12 byte-identical to the old ones and to the demo files. Listing 9.4 changed on purpose (see below) and matches `app.js` byte for byte (the suite's listing test checks it).

Corrections and additions (per the validation notes and primary sources, see the validation file):
1. Spec draft date 15 Oct → 27 Oct 2026 (IDL unchanged).
2. Chrome 156 is Stable (20 Oct 2026), WebMCP still off by default. New footnote ch09-22.
3. Listing 9.4 + demo: keep the AbortController, `tools.abort()` on any registration failure (Chrome best practices, 30 Oct: "Register tools all at once"). New test and new Table 9.2 row.
4. "Share the application service" cited for the thin-wrapper design (ch09-23).
5. Test Agent: PR #348 (Tool interface, open) and issue #361 (serialization, spec author: "The WPT assertions are wrong, and so is Chrome.") (ch09-24, ch09-25).
6. "Pin versions" from build-tools (ch09-26).
7. Prompt API footnote re-dated (last updated 21 Oct 2026). npm 6.0.3 re-checked as latest on 2 Nov.
8. Chromestatus status re-dated to 2 Nov. Still-in-flux box names the declarative removal (8 Oct) and points to Appendix A for open PRs.
9. Test count 21 → 22. Footnotes "read 14 October 2026" → "retrieved November 2026" where re-read.

Removals: none of the technical content.

Figures: 9.2 was a card grid in the first edition. It's now a hub: the page with its two tools in the middle, six ways to reach them around it, colour-coded browser tooling (teal) versus agents (amber). 9.1 adds the new rollback branch (magenta). 9.3 keeps the facts of the old timeline and marks Chrome 156 Stable.

## Pass: serious technical prose (22 November 2026)

Register override: professional developer book. Blog scaffolding and named fictional people reduced. Protected spans unchanged.

- Point: A first WebMCP app is the page, a start-up decision, and thin tools over the same functions, with a scripted way to call them and a token when the page leaves localhost.
- What changed (voice/register), with one before/after pair if you changed the opening:
  - Before: “Now let’s put the pieces back together and take one small app all the way: … On the way we’ll answer the practical questions every team asks on its first day with WebMCP. How do I switch it on? … how do I call my tools …”
  - After: “This chapter puts the pieces back together and takes one small app all the way: … It answers the practical questions every team asks on its first day with WebMCP. How do you switch it on? … how do you call your tools …”
  - Also dropped “Please note:”, “of course” on the feature-detection line, “Have a look at the AbortController”, “Let’s start with the tool you already have open”, “Some important things to notice here”, “so let me state it plainly”, “so let's look at them separately”, and both smileys’ worth of “:)” on the DevTools pane. The service-worker sentence no longer carries a biography.
- Generalized: “I’ve been writing about service workers since 2017, and this part feels very familiar” was removed. The analogy stays: a service worker is an enhancement of a page that has to work without it. The 2017 history and “feels very familiar” are not restated as facts.
- Kept on purpose: “I didn’t run the two extensions for this chapter”; “which I co-author”; “another page I co-author”; the Prompt API limit (`"downloadable"`, the suite does not download the model). “every team asks” is the chapter’s existing wording. “Bottomline:” at the close stays because it sits inside a baseline quote span.
- Flags (gaps, unsupported claims, likely factual problems). Write "None" if none.
  - “the practical questions every team asks” is an unsupported universal. It was already in the chapter. Left as written.
  - The closing “Bottomline:” was a blog label. A later check showed it was not a real quotation (the baseline span crossed a fence). The label is gone. The sentence is unchanged: the API calls fit on one screen, and the surrounding work is what makes the app.

## Pass: waitForToolsUntil (27 November 2026)

Chapter 9 adds one sentence after the all-or-nothing rollback. Listing 9.4 was not edited and was not re-run. Sources and the listing ledger: `editorial/fidelity-ledger-wait-for-tools-until.md`.
