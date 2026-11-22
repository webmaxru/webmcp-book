# Editorial log: Chapter 1, The Agentic Web Arrives

Manuscript: `manuscript/01-the-agentic-web-arrives.md`. Old text (15 October 2026): 6,204 words by `wc -w`. New text: 6,320 words. The chapter grew slightly because the author's own stance was added in a few places (see pass 1); repetitive passages were tightened where they existed.

Read before drafting: his voice profile (measured profile of Maxim's pre-2023 posts), the Book 2 voice report (v1 punctuation and v2 voice push shipped; v3 grammar noise and v6 humanizer did not), `.agents/skills/personal-author-voice/SKILL.md`, `.agents/skills/professional-writing-editor/SKILL.md` with `references/slop-patterns.md`, the Book 2 introduction and its editorial log, and his recent article (the latest applied example of his voice). Facts: the validation notes v1 and the primary sources listed in VALIDATION.md.

## Pass 1: voice draft (personal-author-voice)

- **Author presence.** First person only where it is his judgment or his documented background: the service-worker analogy in the opening ("I have written about service workers and offline web apps for years"), the Prompt API aside ("As a PWA person I find this one especially nice: an agent that keeps working offline"), the progressive-enhancement remark, "Personally for me, this is the strongest argument of all", "This is the picture I'd like you to carry through the book". No invented anecdotes, talks, numbers or people. Lars, Trailhead, Fjord Table, Supportly/Ledgerly and the Test Agent stay exactly as they were.
- **Rhythm.** Mixed sentence lengths with short checkpoints ("Another screenshot.", "Probably.", "Better, but not zero across the board"), rhetorical questions ("Is that a confirmation? Or an upsell…"), parentheses for asides, "Let's look", "Let's say", "of course", "Please look at the last row". No ":)" in this chapter.
- **Callouts** converted to the house form `> **Still in flux:** …` (one paragraph each, the old bold titles folded into the first sentence).
- **Headings** kept, except "What this book will and will not cover" → "What this book covers, and what it doesn't" (contraction, his register).

## Pass 2: substantive edit (professional-writing-editor)

- **Point:** browser agents operate websites by actuation, which is fragile and costly; sites have a stake; structured tools (WebMCP) are the alternative, with the human present. Every section checked against it.
- **Slop sweep** (slop-patterns.md): removed "landscape" (Atlas paragraph: "how fast this area moves"), no "robust/seamless/delve/It's worth noting"; one over-signposting sentence in the opening shortened; the long service-worker sentence from pass 1 cut to one line; "countless service worker talks" (unverifiable) replaced by a plain statement; "We have done this kind of work before, every time…" reduced to one clause. Summary bullets kept because the book's chapter template has them, not as a symmetric ending.
- **Semicolons:** zero in prose. One verbatim explainer quote contained a semicolon; it is now quoted as two halves joined by "and", same words.
- **Placeholder lint:** the implementation-status page's literal "coming soon" (Meta Ray-Ban Display) is paraphrased ("on its way, off by default and enabled per device", which is what the page says) so the manuscript lint's "coming soon" rule passes.

## Pass 3: voice recheck and fidelity check

- Voice: contractions kept, author "I" in five places, all supported; "we" for the walkthrough of projects; "you" for the reader. No grammar noise added.
- Fidelity — kept unchanged: every quote, number and date from the old text (Gemini in Chrome Sept 2025 quotes, Atlas Oct 2025 and its retirement, Comet tagline, Claude in Chrome 1,000 users / Dec 2025, Operator → ChatGPT agent July 2025, Prompt API, CUA quotes and 58.1 % / 87 %, Anthropic 123 cases / 29 scenarios / 23.6 % / 11.2 % / 35.7 %, 1,000–1,800 tokens per screenshot, WebArena 14.41 % / 78.24 %, all explainer and Chrome-docs quotes), Tables 1.1 and 1.2, the project descriptions and chapter numbers.
- Corrected per the validation notes: spec date 15 October → 27 October 2026 (text and footnote ch01-2); implementation-status sentence re-dated to 2 November 2026 and extended with the Chrome (149) and Edge (150) origin-trial lines that the page lists; "moving target" callout now says the edition was re-checked in early November 2026; "(retrieved November 2026)" added to the footnotes of the docs pages re-read (ch01-2, ch01-7, ch01-9, ch01-15, ch01-16).
- Removed: nothing technical. The old line "Chrome and Edge are both running origin trials" is kept (still true: Chrome OT 149→162, Edge OT until 30 March 2027).

## Pass: serious technical prose (22 November 2026)

Register override: professional developer book. Blog scaffolding and named fictional people reduced. Protected spans unchanged.

- Point: browser agents already shop by actuation, which is fragile and costly, and the site has a stake in offering structured tools while the user is still in the tab.
- What changed (voice/register), with one before/after pair if you changed the opening:
  - Before: “Lars has a hiking trip in Jotunheimen in three weeks and no tent. On Tuesday evening he opens Trailhead, a Norwegian outdoor-gear store, and instead of clicking through it himself he types into his browser’s assistant panel: [the quoted request]. Then he goes to make tea.”
  - After: “A customer has a hiking trip in Jotunheimen in three weeks and no tent. On Tuesday evening the customer opens Trailhead, a Norwegian outdoor-gear store, and types into the browser’s assistant panel instead of clicking through the store: [the same quoted request].”
  - The return is now “By the time the customer returns, the job is done. The outcome is still uncertain.” Heading renamed to “A worked example: shopping by actuation”. Taste and autobiography removed (service-worker train memory, “I am happy to borrow”, “As a PWA person”, “I sort them”, “of course”, “Let’s say”, “Please look”, “let’s look”, “Personally for me”, “I’d like you to carry”, “trusting mine”, “We build it”). The service-worker comparison stays as a bad-connection analogy. “Another screenshot.” stays.
- Generalized: Lars to “a customer” / “the customer”. Tea errand dropped. “Probably.” became “The outcome is still uncertain.” The author’s ranking “the strongest argument of all” was not kept as a fact. “trusting mine” became a check of the figures printed in the chapter.
- Kept on purpose: Trailhead, Jotunheimen, the shopping quotation, “Moss”, 20 per cent off, the actuation loop, every cited number, date, and quotation, “When I re-checked” (2 November 2026), project names and tool names, Tables 1.1 and 1.2, Figures 1.1–1.3, all footnotes, the H1, and `{sample: true}`. Fjellheim 2 Tent, 3,499 NOK, order TH-100231, Posten, Saturday, the laptop, and the tab are not in this chapter. No in-file reference to the old heading.
- Flags (gaps, unsupported claims, likely factual problems). Write "None" if none.
  - None in the chapter. VALIDATION.md still calls Lars an established fictional example. Left untouched, per the contract.

## Reconciliation (22 November 2026)

“It is also Trailhead’s problem” restored the original move into the four site-side points: “Consider the tent purchase from Trailhead’s side.” No claim added.
