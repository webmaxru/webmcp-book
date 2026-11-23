# Editorial log — Appendix D: Migration Notes

the editor, 2 November 2026. Old: 2,659 words. New: about 3,660 words (new Section D.6 with Table D.3 and a Still-in-flux box, the D.4 rollback paragraph).

## Pass 1 — voice draft
- Intro and section openers rewritten in Maxim's voice: a rhetorical question in D.2 ("Guess which failure is the dangerous one? The quiet one."), "To be fair to `provideContext()`", "In simple words", first person for the author's own testing ("I re-ran all 20 checks").
- No anecdotes, no invented history.

## Pass 2 — substantive edit
- New D.6 "From the first edition to now (October to November 2026)": the plan asked for a migration section if the API changed. It didn't (IDL identical), so the section says so plainly and lists what did change around the API, with what to do in code (Table D.3), plus the open proposals that could force the next migration.
- Listing D.4 improved to follow Chrome's 30 October "register tools all at once" guidance (rollback on failure); the text explains the change from the first edition.
- Listing labels converted to house format. Checklist renumbered to 10 items. Summary moved to D.8.
- Slop check: no triads, no summarising section endings except the Summary.

## Pass 3 — voice recheck + fidelity
- Kept: every date and PR/commit in Table D.1, all five listings' behaviour (D.3, D.5 unchanged code; D.4 extended), all quotes (PR #205 wording, README epigraph re-verified on 2 Nov).
- Corrected: "15 October 2026 draft" → 27 October (three places), test count 20 → 21, Imperative API page date 21 Sep → 16 Oct, epigraph date October → November.
- Added: #361, #204 status, React/Vue package pointers, spec anchor change, best-practices guidance, Chrome release dates, open PRs.
- Removed: nothing.
- Self-checks: 0 placeholders (note: footnote appd-12 quotes the historical identifier `unregisterTool("add-todo")` from the 2025 explainer, lowercase inside code; flag if the build lint is case-insensitive), 0 semicolons in prose, 0 raw HTML, listings byte-identical.

## Pass: serious technical prose (22 November 2026)

Register override: professional developer book. Blog scaffolding and named fictional people reduced. Protected spans unchanged.

- Point: Migration facts, tables, and code stayed. Three blog lines were rewritten into the claim they were announcing.
- What changed (voice/register), with one before/after pair if you changed the opening: Before: “In simple words, it can only ever remove its own tools.” After: “It can only ever remove its own tools.” “Guess which failure is the dangerous one? The quiet one.” became “The quiet failure is the dangerous one.” “I have good news: you don’t need to port anything” became “you don’t need to port anything.” The comparison that follows (“I compared the two IDL indexes”) stayed.
- Generalized: None.
- Kept on purpose: “I checked the merge times”, “I re-ran all 20 checks”, “I compared the two IDL indexes”, and “My advice for today”. “To be fair to `provideContext()`” stayed because the next clause is the useful property of that API, not an announcer. No Lars, Kari, or Jonas in this file.
- Flags (gaps, unsupported claims, likely factual problems). Write "None" if none. The still-in-flux note still lists `outputSchema` (#254) as an open pull request that would change the API. Appendix A, and Chapter 15’s Table 15.1, say #254 merged on 2 November 2026. Left as written. Migration dates and listings were not edited.
