# Editorial log: `waitForToolsUntil`

27 November 2026. Branch `spec/wait-for-tools-until`, from `main`.

## Pass 1: specification

Read pull request #373 in full (diff, description, three issue comments, merge time). Read `index.bs` on `main` after the merge and the published draft dated 24 November 2026. Read issue #328 (still open), issue #374 (still open) and pull request #375 (still open). Read Chromium commit `dc7d570` from Chromium Dash and from the tree at that revision: the IDL, `model_context.cc` (not part of the commit diff), `GetScriptToolsReadyState`, and `kActorObservationDelayTimeout`.

The author’s summary said a 10-second Chrome timeout marks tools ready. The specification’s timeout removes the promise. Chrome at that commit warns at 10 seconds and the actor observation times out at 10 seconds. The book says both, and does not treat the warning as the specification timer. No Chrome 160 probe was run.

## Pass 2: consistency

Searched the manuscript for `ModelContext`, registration, route changes, #328, Chrome 160 and “three methods”. IDL excerpts that show the registration surface now include `undefined waitForToolsUntil(Promise<any> promise)`. `getTools()` is not described as waiting. Appendix F is not treated as superseded. Appendix E separates 160.0.8173.0 (`Tool`) from 160.0.8185.0 (this method).

## Register

Same serious technical register as `main`. New prose names the mechanism, the draft, the Chromium revision and what was not run. No new test result was invented.

Detail, including the listing ledger, is in `editorial/fidelity-ledger-wait-for-tools-until.md`.

## Review pass

A second reading checked the IDL line, the throw versus reject split, the initial `true`, the deferred `getTools()` wait, the `Promise.all` settlement bug, and the Chrome warning versus the actor timeout. Listing 17.2 passes the batch promise, including the rollback `abort()`, and still returns the names to a caller that awaits it. The printed 2 November probe JSON was left without a `waitForToolsUntil` field.
