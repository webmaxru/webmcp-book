# Fidelity check: Chapter 13, Privacy, Consent and the Human in the Loop

Date: 22 November 2026. Register pass only. Compared with `python3 /tmp/check_fidelity.py manuscript/13-privacy-consent-human-in-the-loop.md`.

## Protected spans

Checker: `OK 13-privacy-consent-human-in-the-loop.md fences=5 tables=0 figures=2 footnotes=33 quotes=75`.

Counted in the file after editing: 5 fenced blocks (listings 13.1 through 13.5, including the WebIDL fence), 2 figure lines (`![Figure 13.1`, `![Figure 13.2`), 0 tables, 33 footnote definitions (`[^ch13-1]` through `[^ch13-29]` and `[^ch13-40]` through `[^ch13-43]`). All 75 baseline quote strings are present in the raw file. Listing labels and paths were not edited. The H1 was not edited. No callout was added or removed. The epigraph was not edited.

## Numbers, dates, and quotes confirmed still present

Read in the prose and confirmed unchanged: the 27 October 2026 draft, re-read on 2 November 2026, Chromium 156.0.8078.4, sixteen tests, the 800 ms arming delay, order `TH-100200` at 7,297 NOK, the “7,297 kr” question in the consent section, `shipTo: 'Oslo 0150'`, `payWith: 'Visa ending 4242'`, exactly four keys, `SESSION_ENDED`, `CART_EMPTY`, issue #288’s report of 2 September 2026, the 700 ms hold mentioned in that thread, and Chrome’s 30 October wording for commit points and plan binding.

Quotes read and found unchanged, including the epigraph “A responsible agent should keep the human-in-the-loop and implement requests for confirmation as needed.”, “enable human-in-the-loop workflows”, “bind approval to a short-lived private grant that includes the exact draft, hash, version, scope, and expiry. Any edit must revoke the grant.”, “isn’t a boundary, it’s a description of one host’s current implementation”, and the agent line “I’ve opened the order for you to confirm”.

## Generalized

“It’s also the most direct answer I know to the TAG’s ‘web for agents’ worry” became “It is also a direct answer to the TAG’s ‘web for agents’ worry.” The curly quotes around “web for agents” are unchanged. “Most direct” was not kept.

“Personally for me, this is the right trade-off for money” became “I recommend this trade-off for money”. The clause after the colon is unchanged: a person said yes, so the order happens, and the agent gets a truthful result instead of a cancellation that did not cancel anything.

## Flags

None. The commit-point sentence is now marked as the author’s recommendation. It does not say the specification requires the order to finish after the click.
