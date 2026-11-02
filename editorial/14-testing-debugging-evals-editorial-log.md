# Editorial log — Chapter 14: Testing, Debugging and Evals

v2 rewrite, 2 November 2026 . Base text: the Oct 15 manuscript as restructured in book/manuscript (10,676 words incl. listings and notes). Result: 12,470 words incl. listings and notes. Growth comes from new, sourced material: Chrome’s evals page, the 30 October build-tools and best-practices guidance (time-travel states, pin versions, share the application service, register tools all at once), issue #92’s October discussion, the #361 serialization ruling, the Chromium main-branch changes for Chrome 158, chrome-devtools-mcp 1.11/1.12 and the Example Agentic Chrome Extension.

## Pass 1 — voice draft
- Full rewrite in Maxim’s voice from his voice profile and the Book 2 practice: first person for judgment (“For me, this is the most important test in the file”, “I haven’t tested that combination”, “I could not test that build here” style honesty), tutorial “let’s/we” (“Let’s build both, in five layers”), rhetorical questions (“So why not test them like any other function?”, “Is running both redundant? Not at all.”), “In simple words”, “Please note”, “Bottomline”, parentheses for asides, one exclamation (“The scripted ‘careful’ agent had passed that same case!”).
- Personal colour only from verified facts: “Chrome’s guide on building tools, a page I co-authored” (byline of the 30 Oct revision) and “I’m a member of that group myself” (the author facts: on the W3C WebML CG participant list). No invented anecdotes.
- Listing labels converted to the house form with repo-relative paths (`chapters/14-testing-debugging-evals/...`). The example bug report moved from an unlabelled blockquote to a `text` code block (house style: blockquotes are callouts only). Callouts normalised to `> **Still in flux:** *Topic.* ...` and `> **Tip:**`.

## Pass 2 — substantive edit (professional-writing-editor)
- Structure kept (five layers, then feedback channels), because it is the chapter’s argument and Figure 14.1 mirrors it. New material placed where a reader needs it: the Chrome evals page at the top of Layer 4, time-travel and pin-versions at the end of Layer 1, the #361/Chromium-158 story under Table 14.1, “register tools all at once” next to the toolsAdded observation, a new “test the failure in the middle of a chain” habit.
- Slop pass: no semicolons in prose (footnote semicolons changed to commas), no “Here’s the thing”/“worth noting”/“seamless”/“robust”, no summarising section endings except the chapter summary. Seven “, not X” contrasts rewritten (16 → 9).
- Table 14.1 retitled and re-dated, two cells extended with the #361 state. Table 14.2 retitled as unchanged through 2 November. Table 14.3 names both Chrome agent extensions.

## Pass 3 — voice recheck + fidelity check
All claims checked (VALIDATION.md 57 rows).
- Kept: all eight listings byte-identical to the demo files (compared programmatically after the rewrite), every number of the Oct text (80 ms, 49→51 is a correction, 5/5, 0/5, 15/15, 17:00/17:30, 100 ms, 1 to 12, seven outcome words, Edge 149, Node 20), every URL and every code-quoted name (a token diff of old vs new found only `1.10.1`, deliberately updated, and `async`, which moved into the code-block bug report).
- Corrected: spec date 15 Oct → 27 Oct 2026 (text and four footnotes), chrome-devtools-mcp 1.10.1 → 1.12.0, WPT imperative files 49 → 51 (+25 declarative), issue #92 status and October comments, imperative-api update date 21 Sep → 16 Oct, DevTools page date (none shown), build-tools byline and 30 Oct update, webmcp-tools latest commit.
- Added with sources: #361 ruling and proposal, Chromium CLs 8546218 and 8510757 with milestone arithmetic (stated as not observed), spec PR #334 hint sentence, chrome-devtools-mcp 1.11.0 release notes, Chrome evals page, best-practices architectural constraints.
- Removed: nothing technical. The old phrase “on 15 October … still open” for #92 became the 2 November state.
- Footnotes renumbered by first appearance (33 notes, all prefixed ch14-).
- Self-check: 0 placeholders, 0 prose semicolons, 0 raw HTML, both image paths exist, no undefined or unused footnotes.
