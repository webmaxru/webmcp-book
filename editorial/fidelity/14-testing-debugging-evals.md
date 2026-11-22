# Fidelity check: Chapter 14, Testing, Debugging and Evals

Date: 22 November 2026. Register pass only. Compared with `python3 /tmp/check_fidelity.py manuscript/14-testing-debugging-evals.md`.

## Protected spans

Checker: `OK 14-testing-debugging-evals.md fences=9 tables=4 figures=2 footnotes=34 quotes=72`.

Counted in the file after editing: 9 fenced blocks, 4 tables (14.1 through 14.4, including separator rows and the italic captions left untouched), 2 figure lines (`![Figure 14.1`, `![Figure 14.2`), 34 footnote definitions, all prefixed `ch14-`. All 72 baseline quote strings are present in the raw file. Listing labels and paths were not edited. The H1 was not edited. No callout was added or removed. The epigraph was not edited.

One edit was reverted. Changing “Please note: the issue reports the same behaviour in Chrome 158.0.8119.0” made the checker report a missing quote. That span starts at the ASCII quotes in François Beaufort’s “a tool that returns "hi" should resolve to '"hi"'” and continues into the next paragraph. The original “Please note” wording was restored. The checker then printed OK.

## Numbers, dates, and quotes confirmed still present

Read in the prose and confirmed unchanged: the 27 October 2026 draft, re-read on 2 November 2026, Chrome for Testing 156.0.8078.4, Stable on 20 October, 21 checks passed, `chrome-devtools-mcp` 1.12.0 as of 2 November 2026 and 1.11.0 released 15 October, about 80 milliseconds for the four unit tests, WPT on 2 November 2026 with a `declarative/` folder of 25 HTML test files and an `imperative/` folder of 51 (49 when first counted, on 15 October), the 14 October 2026 run of five cases against `gpt-6-sol` (first two cases five of five, the 17:00 case zero of five, then 15 of 15 after the case moved to 17:30), Edge 149, the abort after 100 milliseconds, `book_table`’s range of 1 to 12, and issue #361’s dates (reported 23 October, reply 26 October).

Quotes read and found unchanged, including the epigraph “When testing systems that use generative AI, you must account for probabilistic outcomes that don't match your expectations.”, “Full support from security for requiring and validating these schemas in the spec”, “The WPT assertions are wrong, and so is Chrome. A tool that returns "hi" should resolve to '"hi"'.”, “If an agent can't figure out which tool to call for a request like, "I'd like a small pizza,"”, and “There’s no 17:00 table for five on Saturday 28 November.”

## Generalized

“For me, this is the most important test in the file” was deleted. The following sentence still says the browser passes the callback whatever object the agent sent and does not check it against `inputSchema`. “Most important” was not restated.

“(I’m a member of that group myself.)” was deleted. The sentence still says normative pull requests require joining the W3C Web Machine Learning Community Group and agreeing to its contributor license agreement.

## Flags

“Most first bugs with WebMCP are not logic bugs at all” was already in the chapter and was left as written. The next sentences name registration failures (the feature check, a double registration, the wrong view, a schema that is not what was meant). There is no count behind “most”.

“Turn the most common bad inputs into new eval cases” was left. The sentence before it is about a high `INVALID_ARGUMENT` rate on one tool, so “most common” there means the inputs that measurement already showed, not a claim about WebMCP in general.

The author’s CG membership is no longer disclosed next to the contribution rule.
