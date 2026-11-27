# Editorial log — Appendix A: API Quick Reference

the editor, 2 November 2026. Old: 3,981 words (Oct 15 text in book/manuscript). New: about 5,260 words (IDL listing unchanged; growth is the new Section A.9, the #361 box and the two-sided opt-in paragraph).

## Pass 1 — voice draft
- Intro rewritten in first person as the author ("the page I keep open while I write tool code"), with the validation stamp split into two short paragraphs: what was checked (27 Oct draft, identical IDL) and how it was tested (Chromium 156.0.8078.4, 25/25 re-run 2 Nov).
- Reference sentences kept terse (it is a reference appendix), but semicolon chains split into short sentences, "Please note:", "To be precise:", "I treat the two names as one family" added where Maxim's voice fits without padding.
- No anecdotes added. The only first-person claims are the author's own testing and judgement.

## Pass 2 — substantive edit (professional-writing-editor)
- Structure: A.1–A.8 kept (they map 1:1 to chapters). New A.9 "Proposals that would change this page" (Table A.9) so readers know which open PRs would invalidate which table. Summary moved to A.10 and extended by two bullets.
- Added a "Still in flux: which column is right" box under Table A.5 for issue #361 (editor ruling 26 Oct).
- A.6 gained one paragraph naming the spec's new two-sided opt-in section, replacing the first edition's implicit reliance on the old TODO.
- Listing labels converted to the house format (`**Listing A.1** `path` — title`).
- Slop check: no triads added, no "it's worth noting", no summary-style section endings except the Summary section itself.

## Pass 3 — voice recheck + fidelity check
Every number, API name, URL and claim of the Oct 15 text was kept, corrected or deliberately updated:
- Corrected: spec date 15 Oct → 27 Oct 2026 (IDL unchanged), editor count 3 → 4, issues #224/#234 status date 15 Oct → 2 Nov (still open), Table A.7 caption date.
- Added with sources: Chrome 153 (unregister without cancel), Chrome 155 (JSON-string input deprecated), Chrome 156 (`debugging`, no `window.ontool*`), `executeTool()` null on navigation, #361 ruling, PR #326 two-sided opt-in, PR #334 hints text, PR #350 explainer fix, Chrome 156 stable / 157 date, open PRs #348/#254/#204/#355/#358.
- Kept verbatim: Listing A.1 (byte-identical to the 27 Oct IDL index after normalising whitespace), Listing A.2, Tables A.1–A.8 cells (wording-only edits to remove semicolons), every error message string quoted from Chromium.
- Removed: nothing technical. The phrase "Chromium 156’s trial still ships it" became "Chromium 156 still ships it behind the same flag" (more precise).
- Self-checks: 0 placeholders, 0 semicolons in prose/tables/footnotes, 0 raw HTML, footnotes all defined and used, listings byte-identical to demo files.

## Pass: serious technical prose (22 November 2026)

Register override: professional developer book. Blog scaffolding and named fictional people reduced. Protected spans unchanged.

- Point: Reference appendix. The IDL, tables, and tested behaviour were left alone. Only sentences that were blog scaffolding or taste-based first person changed.
- What changed (voice/register), with one before/after pair if you changed the opening: Before: “This is the page I keep open while I write tool code, and I hope it earns the same place on your second screen. It collects the whole WebMCP surface in one spot.” After: “This appendix collects the whole WebMCP surface in one spot.” Also removed “The good news first:”, “Please note:” before the in-flight-call limit, and the filler “please” before “don’t parse them.”
- Generalized: None.
- Kept on purpose: “I re-ran all 25”, “I tested all of them”, “I treat the two names as one family”, and “I list them because”. Footnote checks (“I compared”, “I couldn’t check”) were not edited. No Lars, Kari, or Jonas in this file.
- Flags (gaps, unsupported claims, likely factual problems). Write "None" if none. The fidelity checker reports one missing quote on this file, and it reported the same quote before this pass. The baseline string jumps from the A.4 heading to “Runs a tool” by skipping the `executeTool` code fence. The fence is still in the file. It was not restored by deleting the fence. Separately, this appendix treats pull request #254 (`outputSchema`) as merged on 2 November 2026. Chapter 15’s charter paragraph and summary, and Appendix D’s still-in-flux note, still call #254 an open pull request. Not corrected here.

## Pass: waitForToolsUntil (27 November 2026)

Appendix A’s IDL is the 24 November 2026 index, including `waitForToolsUntil`. New Section A.3. Old sections A.3–A.10 are now A.4–A.11. The method throws. Those throws were not in the Chromium 156 probes. Sources and the listing ledger: `editorial/fidelity-ledger-wait-for-tools-until.md`.
