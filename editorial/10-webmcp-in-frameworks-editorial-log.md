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
