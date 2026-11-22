# Editorial log: 17-the-road-ahead.md

the editor, v2 rewrite, 2 November 2026. Same voice target as Chapter 16.

## Pass 1: structure and facts
- Re-dated every status to 2 November 2026 and the 27 October draft. Removed the “opened and closed the day before this chapter was written” phrasing for #344 and gave dates instead.
- §6.3.4 is no longer a TODO: PR #326 merged on 27 October. Rewrote that paragraph around the spec’s own words (“only visible to and executable by” same-origin documents, three gates). Updated Table 17.1, the summary and the note.
- Added the #92 required-or-optional schema debate, kenchris’s notes on #254 and #41, Sagar’s `*` comment on #317, Beaufort’s follow-ups on #344 and #332, the new elicitation proposal (#165) and the #204 hand-over, harness feedback on #255, the 30 October #236 discussion, the TAG’s 26 October early comment, and the late-October charter discussion (strategy#576, charter-drafts#901).
- Named people where the source names them and the role matters (François Beaufort, Mark Foltz, Samuel Dallstream, Johann Hofmann, Khushal Sagar, Benjamin VanderSloot, Ilya Grigorik). The TAG comment is attributed to the TAG because the individual author was not confirmed.
- Added a “Asking the user mid-call” row to Table 17.1.
- Checklist: added item 3 (register all or nothing, Chrome’s best practice) and folded version recording from the build-tools guide into the probe item. Now 12 items.
- Listing 17.2 (`adapter.js`) now rolls back a failed batch with `AbortSignal.any`. The demo gained a rollback test, so the suite has 14 checks per mode (was 13), all passing in mock and Chromium 156 modes on 2 November.
- house formats: bold table caption, `**Listing N.M** \`path\` — title` labels, em-dash figure captions, `**Still in flux:**` callouts.

## Pass 2: voice
- First person for the author’s probes and opinions (“I tried it”, “My probe”, “I agree with him”), questions in “Closing the book”, short sentences. Removed every prose semicolon and kept em dashes to 8 in body text.
- Softened none of the facts. Where a status is an estimate (charter refinement end), it is phrased as the W3C team’s estimate.

## Pass 3: proof and checks
- Notes ch17-1 to ch17-38 all defined and cited, dated to 2 November readings. Fixed the v1 note that attributed Chrome’s shipping plan to “the author” of PR #338 (it was Beaufort’s comment). Removed semicolons from notes too.
- Listings embedded byte for byte from `demos-new/chapters/17-the-road-ahead/src/`, checked by the demo’s listing test (passed).
- Grep: no placeholders, no “coming soon”, zero prose semicolons.
- Length: about 8,400 words with listings and notes, against 7,308 in v1, mostly the October developments and one new checklist item.

## After the validation notes were final
- Added PR #348 (`Tool` interface), the §6.2 text from PR #334 that points to the Agentic Web WG, and the #361 serialisation ruling (checklist item 9). Notes ch17-39 to ch17-41.

## Pass: serious technical prose (22 November 2026)

Register override: professional developer book. Blog scaffolding and named fictional people reduced. Protected spans unchanged.

- Point: The chapter is still a map of open WebMCP questions as of 2 November 2026, plus a small adapter so Trailhead’s bets survive the answers. The first-release question stays. The named people do not.
- What changed (voice/register), with one before/after pair if you changed the opening:
  - Before: “Jonas has stopped getting paged about the adapter. Kari has wiped the whiteboard and written a new question: *What are we betting on, and what happens if we lose the bet?* I like that question as an ending for a book about a draft.”
  - After: “the front-end lead has stopped getting paged about the adapter. The product lead’s new question is: *What are we betting on, and what happens if we lose the bet?*” The “I like that question” sentence is gone. The next sentence still says the previous chapters were checked on a particular day and that both the spec and the browser will move.
  - Heading renamed to “The question after the first release”.
  - “I’ve sorted” / “what I would do about it now” is now “It groups the questions into five” and “a practical response now”.
  - “a rule I’d follow anyway” is now “keeping tools thin anyway”. “In production I would use a full validator” is now “In production, use a full validator.”
  - “and I agree with him” removed. Beaufort’s “_still_ confusing” quotation and footnote stay on that sentence.
  - Closing: “Lars” is “a customer”. “I’ve tried to be honest in this chapter about how open they are” is now “this chapter leaves them open.”
- Generalized: Kari and Jonas to “the product lead” and “the front-end lead”. Lars, in the closing only, to “a customer”. The tent, the price slider, and the screenshot after every nudge stay.
- Kept on purpose: origin-trial release, measurement wrapper, paging about the adapter, three weeks after the Monday meeting, the betting question, Figure 17.1’s five groups, the 2 November 2026 state of play, three futures, the checklist, and the three listings. “I” for checks: “the draft I read”, “I tried it”, “My expectation”, “My probe”, “In my tests”. Code fences, Table 17.1, both figures, and all footnotes untouched.
- Flags: The author’s agreement with Beaufort is no longer stated. The quotation remains Beaufort’s. The practical lesson (idempotent consequential tools, check the signal before each irreversible step) is unchanged. “This chapter leaves them open” replaces a personal honesty pledge. It does not close or newly settle any question in the chapter.

## Reconciliation (22 November 2026)

The claim that the demo validates every `run()` result against the printed `outputSchema` now states what the listing shows: the printed schema requires `products`, and Listing 17.2’s `{ status: 'error', code: 'INVALID_ARGUMENT', message }` would not validate against it. The code was not changed. The companion demo’s broader schema is a flag for the author, not a new description of the listing.
