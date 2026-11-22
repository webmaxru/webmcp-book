# Editorial log: 16-product-and-business-implications.md

the editor, v2 rewrite, 2 November 2026. Voice target: Maxim’s his voice profile and the personal-author-voice skill (first person “I”, occasional “Let’s”, short sentences, visible reasoning, curly quotes, no semicolons in prose, few em dashes, no invented anecdotes).

## Pass 1: structure and facts
- Rewrote the chapter in full from the v1 text and the validation file. Kept the v1 section order and the Trailhead thread (Kari, Jonas, the Monday meeting) because Chapters 15 and 17 rely on it.
- Rebuilt “One plan, two surfaces” on the rewritten compare-mcp page (27 Oct 2026). The v1 quotes are gone from that page, the new ones (call center / in-store expert, “Manage core logic with MCP”, “Build a contextual UI with WebMCP”) replace them.
- Added Chrome’s new guidance from best-practices and build-tools (30 Oct 2026, both co-authored by Maxim): start from journeys with the most added value, all-or-nothing registration with rollback, sharing the application service, version pinning, the telemetry loop.
- Added the late-October standards signals that bear on business decisions: Grigorik’s Shopify statement and his “unspecified and incomplete” remark about `SubmitEvent.agentInvoked` (webmcp #365), the EU Consumer Rights Directive question (cited by GitHub handle), the #236 discussion of a second permissions policy, the new elicitation proposal on #165.
- Listing 16.4 (`register-tools.ts`) now registers all or nothing. The demo got a rollback test and `registerTrailheadTools` is exposed on `window.__trailhead` for it.
- Converted listing captions to the house form (`**Listing N.M** \`path\` — title`), table captions to bold, figure captions to the em-dash form, “Still in flux” boxes to `**Still in flux:**` blockquotes.

## Pass 2: voice
- Switched to first person where Maxim would speak from experience (“I’d start”, “I tested”), with “Let’s” at two section openings. Kept Kari and Jonas as the characters who make decisions.
- Broke long sentences, removed every semicolon from prose, cut em dashes to 14 in body text (captions and listing labels need theirs).
- Replaced hedged generic phrasing (“it is important to note”, “in today’s landscape” types) with direct statements, checked against slop-patterns.
- Trimmed the summary from eight bullets to seven, merged the measurement and registration points. Tightened a few sentences (lawyer aside, the “one sentence” line).

## Pass 3: proof and checks
- Every quote re-checked against the editor's source notes and the issue comments. One near-miss fixed: a draft footnote gave a full name for the GitHub user frmoretto, which I could not confirm, so the note now cites the handle only.
- Footnotes ch16-1 to ch16-28 all defined and all cited. Dates updated to the 27 October draft and the October page updates.
- Grep: no TODO/TBD/FIXME/XXX/[insert/[[/lorem/“coming soon”/“to be published”. Zero semicolons in prose.
- Listings are embedded byte for byte from `demos-new/chapters/16-product-and-business-implications/src/` and checked by the demo’s listing test.
- Length: about 8,000 words with listings and notes, against 7,144 in v1. The growth is the new Chrome guidance and the October standards material. I cut elsewhere where repetition allowed.

## v2.1.0 (4 November 2026)

- The GitHub user frmoretto wrote to the author and gave his name, Francesco Marinoni Moretto, and his GitHub profile shows the same name. He is now named in the text (“Francesco Marinoni Moretto (GitHub: frmoretto)” on first mention, “Marinoni Moretto” after that) and in notes ch16-26 and ch17-35. This replaces the handle-only note above.
- New section “WebMCP and protocol checkout (UCP)” after “WebMCP and backend MCP in one plan”, from his suggestion. Every fact was checked against primary sources on 4 November 2026 (live `/.well-known/ucp` fetches on three stores, the UCP 2026-08-25 specification, Shopify’s changelog and Checkout WebMCP documentation). His map is cited as a secondary source. Where the specifications are silent, the text says so. VALIDATION.md rows 21–29. No semicolons in the new prose.

## Pass: serious technical prose (22 November 2026)

Register override: professional developer book. Blog scaffolding and named fictional people reduced. Protected spans unchanged.

- Point: WebMCP converts visits a site already has, and Trailhead’s product team still has to choose journeys, measurement, ownership, and the split with backend MCP. The Monday planning frame stays. The named characters do not.
- What changed (voice/register), with one before/after pair if you changed the opening:
  - Before: “Trailhead’s product team meets on Monday mornings in a room above the warehouse in Lillestrøm. This Monday, Kari, who runs product, has written exactly one question on the whiteboard.”
  - After: “Trailhead’s product team meets on Monday mornings. This Monday the product lead has written exactly one question on the whiteboard.”
  - Heading renamed to “The product question”. “Let’s be precise” and “Please note” removed. The two claims that followed (presence, and the unsettled `agentInvoked`) stay.
  - “the clearest way I know” is now “explains the split … in two lines”, so the superlative is not stated as fact. Both Chrome sentences stay.
  - “The Chrome guide I mentioned earlier” is now “The Chrome guide cited earlier”. The co-author credit (“André Cipriani Bandarra and I co-authored”) stays.
  - “Personally for me, this is the cheapest seat at the table you will ever get” is now “Sending findings back is a low-cost way to influence the standard.”
  - “These are the questions I would ask” is now “I recommend these questions, in roughly this order.”
- Generalized: Kari to “the product lead”, Jonas to “the front-end lead”. Warehouse in Lillestrøm and “Kari is impressed” dropped. “take upstairs” is now “a plan to take to the rest of the company.” “I hear this comparison in almost every planning conversation about agents” is now the prescribed sentence “Planning discussions about agents often start from an SEO analogy.”
- Kept on purpose: the whiteboard question, the other product questions, the branch, four tool calls instead of forty clicks, 4,000 NOK, Monday, the measurement wrapper, attribution, origin-trial caution, and every quote, table, figure, listing, and footnote. “I” for the co-authored guide, “In my tests”, “the simplest approach I can defend”, “I am not a lawyer”, “I fetched”, and “the three profiles I fetched”. “The good news” / “The bad news” stay because each states a real limit (measurable calls, no caller identity).
- Flags: The “almost every planning conversation” frequency is generalized. Do not read “often” as a measured rate. “Cheapest seat … you will ever get” is no longer stated. “Low-cost” is the remaining cost claim, and it is the author’s judgment, not a measured price.
