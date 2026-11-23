# Fidelity note — Appendix A

Reviewed 22 November 2026 after the serious-technical-prose pass.

Checker: `FAIL appendix-a-api-reference.md` with one missing quote. The same failure was present before this pass (confirmed by running the checker on the unmodified file). Fences, tables, figures, and footnotes match the baseline. The failure is not a span this pass damaged.

## Protected spans

Counted in the file and confirmed against the checker:

- Fences: 5. Listing A.1 (WebIDL), the three short `registerTool` / `getTools` / `executeTool` samples, and Listing A.2.
- Figures: 0.
- Tables: 9. Tables A.1 through A.9, including separator rows. No table line was edited.
- Footnotes: 30. `[^appa-1]` through `[^appa-29]`, plus `[^appa-output-schema]`. Definitions were not edited.
- Epigraph left as printed: “Tool execution errors are not exposed to the web.”
- H1 not renamed.

The missing baseline quote begins `` ` specifically. `` and continues through the A.4 heading into “Runs a tool…”. In the manuscript that string is interrupted by the `executeTool` code fence. The fence is still there. Removing it would have made the quote contiguous and would have broken the fence hash, so it was left.

## Numbers, dates, and quotes confirmed still present

Checked in the edited file: Draft Community Group Report 27 October 2026, read 2 November 2026, IDL same as the 15 October draft, “all 25” probes re-run, Chromium 156.0.8078.4, Chrome 156 stable since 20 October 2026, Chrome 157 on 3 November 2026, Chrome 153 / 155 / 156 behaviour notes, issues #224, #234, #361, and #92, declarative API removed 8 October 2026, open pull requests as of 15 November 2026, “Tool execution errors are not exposed to the web.”, “The WPT assertions are wrong, and so is Chrome.”, “I re-ran all 25”, “I tested all of them”, “I treat the two names as one family”.

## Generalized

None.

## Flags

Pull request #254 is described here as merged on 2 November 2026 and reflected in Tables A.1 and A.4. Chapter 15’s charter paragraph and summary, and Appendix D’s still-in-flux note, still call #254 open. Not corrected in this appendix.

The checker’s missing quote is a baseline extraction that skipped a code fence. It is not a claim that disappeared from the prose.
