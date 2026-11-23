# Fidelity note — Chapter 15

Reviewed 22 November 2026 after the serious-technical-prose pass. Checker: `OK 15-browser-support-and-standards.md fences=5 tables=2 figures=2 footnotes=37 quotes=186`.

## Protected spans

Counted in the file and confirmed against the checker (hashes match the baseline, so these spans are byte-identical to HEAD):

- Fences: 5. Listing 15.1 (HTML and HTTP), Listing 15.2, Listing 15.3, Listing 15.4.
- Figures: 2. Figure 15.1 and Figure 15.2, including captions.
- Tables: 2. Table 15.1 and the npm package table. Caption lines above the tables were not table rows and were not edited.
- Footnotes: 37. `[^ch15-1]` through `[^ch15-35]`, plus `[^ch15-output-schema]` and `[^ch15-output-validation]`. Definitions were not edited.
- Epigraph left as printed, including “Please note that Community Groups do not create W3C standards.”
- H1 not renamed. No heading in this chapter was on the allowed rename list.

## Numbers, dates, and quotes confirmed still present

Checked in the edited file: 15 October 2026, 2 November 2026, “Seventeen days”, Draft Community Group Report 27 October 2026, Chrome 149 / 156 / 157 (3 November) / 162 (2 February 2027), Edge 150 and 30 March 2027, 9 June 2026, 28 September 2026, 20 October 2026, 26 October 2026 TAG comment, 13 October and 29 October charter dates, about 10 November 2026, Chromium 156.0.8078.4 and stable 156.0.8078.80, build 159.0.8140.0, 5–10 times the tokens and 4–5 times slower, about 9 extensions, millions of storefronts, package 6.0.3 and `use-webmcp-tool` 0.3.0, “Site Capabilities for Agents”, `position: neutral`, `position: oppose`, “Missing: Multi-stakeholder support”, “is not a resolution comment”, “The WPT assertions are wrong, and so is Chrome”. The checker still finds all 186 baseline quote strings. I did not re-read every one of those 186 by hand.

## Generalized

“I wouldn’t be surprised if the name changed on the way to a standard” is now “The name may change on the way to a standard.” The hedge stays. A rename is not stated as a fact. No “almost every” or “most common” claim was in this chapter.

## Flags

`outputSchema` / #254 is merged in Table 15.1 and in the 2 November prose, and still called an open pull request in the charter-consequences paragraph and in the chapter summary. Left as written.

“Seventeen days” between the 15 October 2026 check and the 2 November 2026 check was kept. Those two dates are eighteen days apart on the calendar. Not corrected.
