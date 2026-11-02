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
