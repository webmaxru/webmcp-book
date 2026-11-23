# Editorial log: Tool interface, Chrome 160

23 November 2026. Branch `spec/tool-interface-chrome160`, based on `editorial/serious-tech-prose`.

## Pass 1: specification

Read pull request #348 (merged 19 November 2026), the merged `index.bs`, and the published draft dated 23 November 2026. Read pull request #375 in full (open, explainer only). Chrome 160.0.8173.0 is taken from François Beaufort’s webmcp-extension pull request #105 and from the author’s summary. The stable date 5 January 2027 is the Chromium milestone schedule. No Chrome 160 probe was run. Chromium 156 observations were left as Chromium 156 observations.

## Pass 2: consistency

Searched the manuscript for `RegisteredTool`, `#348`, and `tool.window`. Teaching text now uses `Tool` and `source`, with `source ?? window` where a listing must run before Chrome 160 is stable. Appendix E is the migration. Appendix F is only #375. `Book.txt` lists both. Listing numbers are E.1 and F.1. Figure 5.2’s third column says `Tool` and `source, origin`.

## Register

Same register as the editorial branch: direct technical prose, no new anecdotes, no new certainty about untested browser behaviour. “I have not observed” stays where the chapter already had it.

Detail, including the listing ledger, is in `editorial/fidelity-ledger-tool-interface.md`.

## Review pass

A second reading against `index.bs`, the published draft, pull requests #348 and #375, and extension pull request #105 (merged 23 November 2026) corrected the `source` read: `??` replaces a `null` `source`, so the listings test `!== undefined` and skip a null result. Listing 17.3 now treats a reflected schema as a non-null value. The chapter 15 status line is the 23 November draft. Chromium Dash records canary 160.0.8173.0 for the commit linked from pull request #105.
