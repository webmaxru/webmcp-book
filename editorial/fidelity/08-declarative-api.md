# Fidelity: Chapter 8, The Declarative API: Forms as Tools

Checked 22 November 2026 against `python3 /tmp/check_fidelity.py` (OK) and against the strings listed below.

## Protected spans

Verified with the same extractors as `check_fidelity.py` (hashes match the baseline):

- Fences: 12
- Tables: 3
- Figures: 2 (`![Figure 8.1`, `![Figure 8.2`)
- Footnotes: 24 (`[^ch08-1]` through `[^ch08-24]`)

The single H1, the epigraph, listing labels, and callout labels were not renamed. Table lines and `*Table ...*` captions were not edited.

## Checker

`OK 08-declarative-api.md fences=12 tables=3 figures=2 footnotes=24 quotes=91`

## Strings confirmed still present

- Dates and builds: removal on 8 October 2026, re-check on 2 November 2026, Chromium 156.0.8078.4, 17 of 17, Stable 156.0.8078.80 on 20 October 2026, Chrome 157 on 3 November, TAG comment 26 October 2026.
- First person kept: “when I re-checked”, “so I tested it”, “than I tested”, “when I removed `toolname`”, “I’m one of its co-authors”, “In my tests”, “I haven’t used it”, “what I observed”, “I didn’t test it”, “I haven’t seen its plans”, “I expected the agent to keep waiting”, “Other limits I found”, “no error my code could catch”, “I re-validated”.
- Quotations left intact beside the edits: “this form is a tool”, “ask to fully work out the declarative version before shipping the imperative one.”, “The WPT assertions are wrong, and so is Chrome.”

## Generalized

- “Personally for me, this is the strongest argument that the declarative idea will come back in some form” became “The TAG comment is one argument that the declarative idea will come back in some form, even though it has left the spec.” “Strongest” is not stated as fact.

## Flags

- Left unchanged, because each sits inside a baseline quote span and editing it failed the checker: “We’ll come back to it below”, “which makes sense if you think about it”, “Useful, of course.”
- No factual claim was corrected.
