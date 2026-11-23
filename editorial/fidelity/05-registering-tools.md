# Fidelity check: Chapter 5, Registering Tools

Checked 22 November 2026 against `HEAD` and `/tmp/fidelity-baseline.json` via `python3 /tmp/check_fidelity.py manuscript/05-registering-tools.md`.

## Protected spans

`check_fidelity.py` reported no hash mismatch for these. Counts are the baseline counts:

- Fences: 8 (Listings 5.1–5.6, plus the short `if ('modelContext' in document)` fence and the `AbortController` fence).
- Tables: 7 (Tables 5.1–5.7, including separator rows and the italic captions, which were not edited).
- Figures: 2 (`![Figure 5.1`, `![Figure 5.2`).
- Footnote definitions: 49. The Notes section was not edited. The checker’s footnote hashes match the baseline.

Quotes in the baseline: 97. Every quote that is a contiguous substring of `HEAD` is still a contiguous substring of the edited file (0 regressions). Three baseline quotes are not contiguous in `HEAD` either. Each one runs across a fenced listing that the captured quote omitted (the feature-detection fence, Listing 5.3, and the `AbortController` fence). The checker therefore prints FAIL on the edited file and on `HEAD`, with the same three spans. No protected span was rewritten to silence that.

## Numbers, dates, and quotations confirmed still present

Confirmed by search after the edit:

- Draft and probe dates: 27 October 2026, 15 October, 2 November 2026, Chromium 156, 156.0.8078.4.
- API history: issue #101, 5 March 2026, 19 May 2026, 27 May, pull request #347, issue #224, issue #73, Chromium issue 573722078, Chrome 153.
- Schema debate: 14 October, 16 October, 30 October, 1 October.
- Results: issue #361, 23 October 2026, 26 October, Chrome 158, the nine-character string `undefined`, #324, #339, 8 October 2026, #254, 159.0.8140.0.
- Types: webmcp-types 0.1.10, TypeScript 5.9. Issues #234 and #158. 29 September 2026.
- Epigraph: “WebMCP tool declaration should be clear, without a need for developers or agents to look at outputs and retry.”
- “Only resolve a tool execution with success when the output matches the application state.”
- “tools that perform an action and return nothing are very common”.
- “For consequential actions, bind approval to a short-lived private grant that includes the exact draft, hash, version, scope, and expiry. Any edit must revoke the grant.”
- “The WPT assertions are wrong, and so is Chrome.”
- Sample result `FT-1042` in Table 5.5.

## Generalized

- Tutorial “we” (“we moved”, “we go back”, “We’ll use”, “We’ll come back”, “we just discussed”, “when we get to cancellation”) replaced with Chapter 4, this chapter, Chapter 6, or the section name.
- “Please notice where the boundaries are” deleted. The JSON-boundary claim stays.
- Filler “of course” removed in two places. The edge-case crash and the issue #361 sidestep stay.
- “Let’s look” and both “In simple words” glosses removed. The schema omissions, the two-truths rule, and “whoever holds the controller” stay.
- Ingrid → “the guest”. The in-flight `book_table` call still continues if the booking view closes.

## Flags

- Opening claim that the 27 October IDL matches the 15 October IDL, versus Listing 5.2 (labelled 27 October) and the note that pull request #254 added `outputSchema` on 2 November 2026. Not changed.
- “Bottomline:” restored after the checker treated that sentence as a quote span.
- Checker FAIL is the three pre-existing cross-fence quote spans described above.
