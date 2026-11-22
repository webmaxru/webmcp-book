# Fidelity: Chapter 7, Frames, Origins and Page-Embedded Agents

Checked 22 November 2026 against `python3 /tmp/check_fidelity.py` and against the strings listed below in the edited file.

## Protected spans

Verified with the same extractors as `check_fidelity.py` (hashes match the baseline):

- Fences: 10
- Tables: 3
- Figures: 2 (`![Figure 7.1`, `![Figure 7.2`)
- Footnotes: 31 (`[^ch07-1]` through `[^ch07-31]`)

The single H1, the epigraph, listing labels, and callout labels were not renamed.

## Checker

`check_fidelity.py` prints FAIL with three missing quote strings. The same three are missing from unmodified `HEAD:manuscript/07-frames-origins-agents.md` (baseline indexes 6, 8 and 53). Each runs across a fenced listing, so the string is not contiguous in the file:

- Listing 7.1, from the `allow="tools"` heading through “In an `allow` attribute”
- Listing 7.2, from the tag-manager sentence through the header discussion
- Listing 7.6 through the Table 7.3 introduction

Fences, tables, figures and footnotes match. No fence was edited to chase those strings.

## Strings confirmed still present

- Versions and counts: Chromium 156.0.8078.4, 30 tests, 15 October 2026, 2 November 2026, draft 27 October 2026.
- Limits kept in the first person: “I haven’t tested 157 or later”, “Where Chromium and the draft disagree, I say so”, “so I tested it”, “I recommend reading it in full”, “My answer here is the tool’s owner”, “My view, for what it’s worth”.
- Quotations left intact beside the edits: “does not run JavaScript on the page.”, “general way to call functions in other environments”.

## Generalized

- Removed “(I bet you have seen that happen)”. Did not replace it with a claim that readers have seen tag managers add iframes. The sentence still says a marketing team’s tag manager can add iframes.

## Flags

- “by the way” and “Please note one data point that doesn’t match” remain. Each is inside a baseline quote span that is a contiguous substring. Editing them makes `check_fidelity.py` report a new missing quote. Restored.
- The three pre-existing missing quotes are unchanged from HEAD.
