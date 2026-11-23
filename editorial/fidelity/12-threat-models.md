# Fidelity check: Chapter 12, Threat Models for Tool-Exposing Pages

Date: 22 November 2026. Register pass only. Compared with `python3 /tmp/check_fidelity.py manuscript/12-threat-models.md` and with the same command against `HEAD`.

## Protected spans

Checker on the edited file:

`FAIL 12-threat-models.md` — `missing quotes: 1`, the span that begins `` `.[^ch12-35] The new spec text adds the consequence for frames ``.

The same command against `HEAD:manuscript/12-threat-models.md` prints that same single missing quote. The span is the prose between two `allow="tools"` ASCII quotes, and Listing 12.4’s fence sits in the middle. The quote string is present after the fences are removed (85 of 85). It is not a contiguous substring of the raw file (84 of 85). The fence was not edited.

Hash-matched to the baseline after editing: fences 7, tables 1, figures 2, footnotes 45.

Counted in the file: 7 fenced blocks (listings 12.1 through 12.7), 1 table (Table 12.1, including its separator row), 2 figure lines (`![Figure 12.1`, `![Figure 12.2`), 45 footnote definitions (`[^ch12-1]` through `[^ch12-41]` and `[^ch12-43]` through `[^ch12-46]`; `[^ch12-42]` is unused, as the earlier log said). Listing labels and paths were not edited. The H1 was not edited. No callout was added or removed. The epigraph was not edited.

Two edits were reverted because they sat inside other baseline quote spans bounded by `allow="tools"`: “we can now quote the spec instead of the browser… Here we look at them as security controls”, and “We’ll follow the unresolved elicitation design”.

## Numbers, dates, and quotes confirmed still present

Read in the prose and confirmed unchanged: Draft Community Group Report **27 October 2026**, the 15 October draft, Chromium 156.0.8078.4, twenty-six tests, tool-name limit 128, issue #73, pull request #265, Chrome budgets 30 / 150 / 500 / 1,500, the “export” search returning three of fourteen matches in 1,088 characters with the community answer clipped to 300, the 50,000-character `query` and undeclared `accountEmail` against `maxLength: 200` and `additionalProperties: false`, pull request #334 merged 20 October 2026, pull request #326 merged 27 October 2026, issue #313 still open on 2 November 2026, and `NotAllowedError` when `allow="tools"` is removed.

Quotes read and found unchanged, including the epigraph “While some models have layers that address prompt injection, it’s impossible to guarantee safety inside of a large language model (LLM). Models are probabilistic in nature.”, “cannot define precise mitigation strategies that agents or user agents must provide”, “requires heightened security handling”, “Enforcement belongs in your application logic, beyond readOnlyHint or untrustedContentHint.”, and “ignore your previous instructions”.

## Generalized

“I bet this is the most common real-world WebMCP bug you will ship” became “This is an easy WebMCP bug to ship.” The words “most common” are not in that sentence. The Chromium demonstration that follows is unchanged.

“I’m sure” was deleted from “You will not write that tool.” The steering examples in the next sentence are unchanged.

## Flags

The checker’s one failure matches `HEAD` and is the fence-crossing span described above. Not repaired by editing the listing.

The old “most common” bet is now only “an easy WebMCP bug to ship”, with the 50,000-character query and the undeclared field as the evidence in the same paragraph.
