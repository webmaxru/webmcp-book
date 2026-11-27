# Editorial log: Chapter 10, "WebMCP in Frameworks" (second edition)

Manuscript: `manuscript/10-webmcp-in-frameworks.md`
Figures: `figures/src/figure-10-1.svg`, `figure-10-2.svg` (hand-written SVG, APM palette, rendered with `figures/render.py`), `figure-10-3.png` (test-run screenshot, kept)
Demos: `chapters/10-webmcp-in-frameworks/` (React suite 12/12 mock and 12/12 Chromium 156.0.8078.4 WebMCPTesting, 2 November 2026)
Validation: VALIDATION.md
Length: 8200 words before, 9965 words after (`wc -w`, code included). The chapter grew because three things are new since 15 October 2026: Chrome's 30 October best-practices constraints (batch registration, one application service, commit points, stale state), Chrome's switch of the React package and its new Vue section, and the checkout guard in the demo.

Material read before writing: his voice profile, the Book 2 voice report, `.agents/skills/personal-author-voice/SKILL.md`, `.agents/skills/professional-writing-editor/SKILL.md` with `references/slop-patterns.md`, Book 2 `manuscript/00-introduction.md`, Book 2 `editorial/01-audit-the-agent-environment-editorial-log.md`, his recent article, the validation notes, the house style.

## Pass 1: voice draft

- Register: technical walkthrough (tutorial "we"/"let's" around listings), with Maxim's first person only for authorial judgment and verified facts: "I think it's worth saying why" (a design choice), "I'm one of its co-authors" (the best-practices byline, the author facts / the validation notes §1.10), "I won't print untested code here" (an editorial decision about the Vue section). No invented experiences.
- His repertoire, used sparingly and only where it fits: "Let's have a look at the numbered comments.", "Bottomline:", "Please note:", "of course", parenthetical asides ("(or until the agent gave up)", "(even worse)"), rhetorical questions that are answered at once ("Should you, though?", "Where do the two hooks really differ?").
- Rhythm: short checkpoint sentences after long explanations ("It isn't.", "Your app can."). No ":)" in this chapter, no exclamation marks: the subject (cancellation and orders) didn't call for them.

## Pass 2: substantive edit (professional-writing-editor)

- Structure: "React: the usewebmcp hook" became "React: two hooks", because Chrome's page now points to a different package. The section now says what changed, compares the two hooks on the one point where they really differ (results), and states why Trailhead keeps `usewebmcp`.
- New subsection "The whole set, or none of it" right after the five jobs, because it is a registration rule and belongs with the other registration rules. It carries a Chromium 156 probe instead of an opinion.
- New subsection "A commit point, and a cart that must not move" inside the unregistering section, because it continues the checkout story with the same listing.
- New short "Vue: a composable" section without a listing (no tested Vue demo exists).
- Slop pass: removed reflexive contrasts ("not a failure", "not to the page", "not as the source of truth"), kept the ones that carry an argument (registration signal vs execution signal, `refused` vs `error`). No "moreover/furthermore", no "Here's the thing", no summarising section closers. Zero semicolons in prose (one verbatim quote with a semicolon was split into two quotes).
- Clean-manuscript conversions: listing labels to `**Listing 10.N** \`path\` — title`, callouts to `> **Still in flux:** ...`, footnotes without semicolons.

## Pass 3: voice recheck and fidelity check

Every number, API name, URL and quoted claim of the 15 October text was checked against the validation notes and the primary sources (see the validation file, 32 rows).

Corrections:
- Spec date 15 → 27 October 2026 in every note and the Table 10.3 source line. Section numbers re-checked (unchanged).
- Chrome's React package: `usewebmcp` → `use-webmcp-tool` (page updated 16 October 2026). The old quotes were replaced with the current ones.
- "the two frameworks that Chrome's imperative-API page names" → three (React, Vue, Angular).
- Angular's async-validator note quoted in its corrected 21 October wording.
- "Chromium 156" re-dated: Chrome 156 is Stable since 20 October 2026.
- Test counts: 11 → 12 React tests, run 2 November 2026.

Additions (all sourced): Chrome best practices of 30 October (four quotes), "As of Chrome 153" note, VueUse `useWebMCP`, Angular `debugging` annotation and `webmcp-types` switch (main branch), Angular 22.2.4 as latest, Chrome docs on the events being non-cancelable and `window.on…` handlers unsupported.

Removals: the sentence "Trailhead uses `usewebmcp`, because Chrome's documentation points to it" (no longer true). Nothing else technical was removed.

Kept as first-edition evidence (not re-run on 2 November): the Angular Signal Forms observations (listings unchanged), the MCP-B guide quotes (third-party docs, not re-fetched).

## Pass: serious technical prose (22 November 2026)

Register override: professional developer book. Blog scaffolding and named fictional people reduced. Protected spans unchanged.

- Point: In a framework the WebMCP API stays the same. What changes is which component or injector registers a tool, and when that registration is aborted, without churning `toolchange` or stranding a call that is already running.
- What changed (voice/register), with one before/after pair if you changed the opening:
  - Before: “The good news first: the API doesn’t change in a framework. … So this chapter is about getting the “who” and the “when” right. We tie registration…”
  - After: “The API doesn’t change in a framework. … This chapter gets the “who” and the “when” right. It ties registration…”
  - Removed “Let’s have a look”, “Bottomline:”, “Please note:”, filler “of course”, “I think it’s worth saying why”, and “as we’ll see shortly”. Tutorial “we” (“we look”, “we built”, “we’ll see”) became “this chapter” or a forward reference to the cart page. “I won’t print untested code” became “this chapter doesn’t print untested code”, with the missing Vue demo still the reason.
- Generalized: “the app logic we already have” became “existing application logic”. Same claim. No frequency claim was turned into a fact.
- Kept on purpose: “I’m one of its co-authors” (Chrome best-practices byline). The Chromium 156 probe, the StrictMode `AbortError`, and the `inputSchema: null` failure. Short results that carry a limit (“It isn’t.”, “Your app can.”). No Lars, Kari, or Jonas in this chapter. Code fences, tables, figures, footnotes, listing paths, and the H1 were not edited.
- Flags (gaps, unsupported claims, likely factual problems). Write "None" if none.
  - None.

## Pass: waitForToolsUntil (27 November 2026)

Chapter 10 adds the route-change gap and Listing 10.12 (`on-route-change.js`). `usewebmcp`, VueUse and Angular were not re-read for this method. The Chromium 156 route tests were not re-run. Sources and the listing ledger: `editorial/fidelity-ledger-wait-for-tools-until.md`.

## Follow-up: summary and synchronous throw (27 November 2026)

The chapter summary had told the reader to keep a rollback inside the promise and cited Listing 10.12. Listing 10.12 uses `Promise.allSettled()` and leaves a successful sibling registered. The summary and the route-change section now say that, and point the rollback at Listing 5.7. Listing 10.12 wraps `waitForToolsUntil?.()` in `try`, catches `InvalidStateError` and `NotAllowedError`, and returns the `Promise.allSettled()` promise. It did not return that promise in 3.1.0. `usewebmcp`, VueUse and Angular were not re-read. The Chromium 156 route tests were not re-run. The exact listing text is in `editorial/fidelity-ledger-wait-for-tools-until.md`.
