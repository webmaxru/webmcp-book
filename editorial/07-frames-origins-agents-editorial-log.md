# Editorial log: Chapter 7, "Frames, Origins and Page-Embedded Agents"

Manuscript: `manuscript/07-frames-origins-agents.md`
Figures: `figures/src/figure-7-1.svg`, `figure-7-2.svg` rendered to `manuscript/resources/images/figure-7-1.png`, `figure-7-2.png`
Demo: `chapters/07-frames-origins-agents/` (no code change. Suite re-run 2 Nov 2026 on Chromium 156.0.8078.4: 30 passed, 0 failed)
Validation: VALIDATION.md (45 rows)
Length: 7,953 words (Oct 15) → 9,128 words. Growth is new material: the merged §6.3.4 “Interaction with the Same-Origin Policy” section, the #227 `ModelContextClient` proposal, PR #348 (`Tool` interface) and #349, the post-TPAC second-permissions-policy discussion (#236), the `*` in `exposedTo` comment (#317), Chrome’s content-script note and Kenneth Christiansen’s #74 comment. About 1,200 words.

Materials read before writing: his voice profile, professional-writing-editor/references/slop-patterns.md, the RAAE editorial log and introduction (Book 2), his recent article. the validation notes and the spec draft of 27 October 2026 for every technical claim.

## How the passes ran (honest note)

Same as Chapter 6: one combined rewrite, section by section, with the voice profile and slop list open, then the mechanical checks below on the final file. Not three separate drafts.

## Voice

- Register: technical walkthrough, exploratory in the design note (“is this really a general communication primitive?”) and the API-direction section.
- “I” for the tests and opinions (“My view, for what it’s worth”, “I bet you have seen that happen”), “let’s” for the walkthrough, one “:)” where Archibald’s idea and the #227 worker proposal meet.
- No biographical claims in this chapter.

## Substantive edit

- Fixed an internal inconsistency: the intro said 29 tests, the demo section said 30. The suite has 30 (11 syntax, 1 mock, 17 Chromium, 1 extension). Both now say 30.
- The old “Still in flux: the security section is a TODO” box became a real subsection, “What the specification now says about it”, quoting the merged §6.3.4 (rationale, two-sided opt-in, residual risks). The old anchor `#violation-same-origin-boundaries` no longer exists, the footnote now points to `#interaction-with-same-origin-policy`. The PR #326 quote was replaced by the merged spec wording.
- New subsection “Where the consumer API may be heading” presents #227’s proposal as a proposal, with what would and wouldn’t change for the listings.
- Extensions: added Chrome’s own statement that extensions can use WebMCP through content scripts, and Kenneth Christiansen’s 20 Oct comment that his extension injects into the main world. I report the mismatch with my isolated-world test without inventing an explanation, and say what I didn’t test (origin-trial pages).
- Summary updated: PR #326 removed from the open list, a bullet on §6.3.4 added, #348 added.
- Table 7.3 header re-dated to the 27 October draft, semicolons in its cells replaced by commas.

## Line edit and mechanical checks

- Semicolons in prose: 0. Placeholders: 0 (the old “TODO” wording about the earlier draft rephrased so the file contains no placeholder token). Raw HTML: none.
- Listings: 10 labels in the required format. 7.1–7.3 and 7.5–7.10 byte-identical to the demo files, 7.4 is an IDL excerpt.
- Footnotes: `[^ch07-1]` … `[^ch07-31]`, all defined and referenced (new: ch07-31 for #348/#349. ch07-17 now cites the merged PR #326, ch07-19 the new spec section).
- Quotes re-checked against sources fetched on 2 Nov. One paraphrase of Benjamin VanderSloot’s #236 comment taken out of quotation marks because the original has a typo I did not want to reproduce or silently fix.

## Figures

- 7.1: Ledgerly’s frame tree with the browser agent above it, the widget iframe inside, and the three gates as labelled boxes (embedder, provider, consumer), plus a key line pointing to §6.3.4.
- 7.2: a numbered sequence across User, Ledgerly agent, Browser and Supportly frame, from the user’s request to `SUP-1043`, with the cancel path as a footnote line.

## Demo

- No code change (the IDL and the algorithms the demo exercises are unchanged since 15 Oct).
- README status lines updated to 2 Nov 2026, 30 checks.
- `npm install --no-save playwright@1.64.1`, `node tests/run-tests.mjs`: 30/30. `node_modules` deleted afterwards.
