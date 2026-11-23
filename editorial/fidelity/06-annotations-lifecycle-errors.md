# Fidelity check: Chapter 6, Annotations, Lifecycle and Errors

Checked 22 November 2026. `python3 /tmp/check_fidelity.py manuscript/06-annotations-lifecycle-errors.md` printed:

`OK 06-annotations-lifecycle-errors.md fences=8 tables=2 figures=3 footnotes=41 quotes=132`

## Protected spans

- Fences: 8 (Listings 6.1–6.8). Not edited.
- Tables: 2 (Tables 6.1 and 6.2), including separator rows and captions. Not edited.
- Figures: 3 (`![Figure 6.1`, `![Figure 6.2`, `![Figure 6.3`). Not edited.
- Footnote definitions: 41. The Notes section was not edited. The checker’s hashes match the baseline.
- Quotes: 132 baseline quotes, all still present. No quote that is in `HEAD` was dropped.

## Numbers, dates, and quotations confirmed still present

Confirmed by search after the edit:

- Draft and test dates: 27 October 2026, 15 October, 2 November 2026, Chromium 156.0.8078.4, 14 and 15 October, stable Chrome 156 since 20 October 2026, “I haven’t tested 157 or later”.
- Hints: July 2026 move, issue #291, 30 September 2026, 20 October, September 2026, Chrome 156.
- Lifecycle: issue #332, 1 October 2026, issue #47 (November 2025), August 2026, 300 ms of simulated work.
- Cancellation: issue #344, 14 October 2026, the 30 ms race, Chrome 152, Chrome 153, `PAGE_DEADLINE_MS` 8000, 120 ms, nine seconds, stock check 600 ms, cancel after 100 ms.
- Errors and sync: issue #361, 26 October, commit b206dae, issue #299 closed 25 September 2026, issues #312 and #328.
- Suite: 73 checks, 31 scenarios.
- Epigraph: “`AbortError` means the caller stopped waiting, not that nothing happened.”
- “Enforcement belongs in your application logic, beyond `readOnlyHint` or `untrustedContentHint`.”
- Beaufort: “The WPT assertions are wrong, and so is Chrome.” and “I don’t think `undefined` should reject,”.
- Tests and co-authorship kept: “I ran it first”, “I tested both descriptions”, “I couldn’t produce the documented `null`”, “in my tests”, “I reproduced the race”, “I found no primary source”, “I co-authored with André Cipriani Bandarra”, “another one I co-authored”.

## Generalized

- Opening “Let’s” / “we leave” / “we built” replaced with the examples leaving the restaurant for the shop, and with “Chapter 3 built”.
- “I left three loose ends” / “I never explained” replaced with Chapter 5 leaving those ends.
- “The good news for this chapter” removed. The unchanged-API-surface claim stays.
- “Please note” removed. The early-156 build limit and “I haven’t tested 157 or later” stay.
- “So, in simple words” removed. “Annotations are information you give the agent. They are not protection.” stays.
- “For a purchase I can live with that cost” removed. Not replaced with a claim that a second prompt is acceptable. The safety claim stays: the page’s own confirmation is still the only arrangement that stays safe whichever browser and agent the user has.
- “One more detail worth noticing”, “it is worth stating”, “that brings us”, and “We will meet that one again” removed. The snapshot, the retry rule, the next section, and the later rejection stay.

## Flags

- The author’s willingness to accept two confirmations on a purchase was dropped and not turned into a general recommendation.
- A quoted spec note still says “the lifetime of an specific invocation.” Left inside the quotation.
