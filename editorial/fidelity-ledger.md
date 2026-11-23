# Fidelity ledger

Serious-technical-prose pass, 22 November 2026. Per-chapter records are in `editorial/fidelity/`. This file is the book-level reconciliation.

## Contract

Reader: professional web developers, and in Parts I, IV and VI the technical leads who sit with them. Register: a technical book. The author’s instruction overrides the voice profile where they conflict: fewer first-person anecdotes, named personal stories, casual asides and blog checkpoints. Authorial “I” stays for a measurement, a re-check, co-authorship, or a recommendation marked as the author’s rather than a rule of the specification.

Protected spans were required to stay byte-identical: fenced code (including IDL), figure lines, pipe tables, and footnote definitions. Epigraphs, listing paths and listing numbers were not retitled except where a title named Lars or repeated the false “Listing 4.1 again” claim. No facts, sources or numbers were invented. Where a claim looked wrong, it is flagged below and left, unless the claim was the inaccurate “same code” sentence the demos check named.

## Method

Before any edit, fences, tables, figures and footnote definitions in every `manuscript/*.md` file were hashed. After editing:

- Those hashes still match, file by file.
- Every curly quotation that is contiguous in `HEAD` (and does not run across a code fence) is still contiguous in the edited file. The result of that check was zero missing quotations.
- `python3 tools/lint_manuscript.py` is the manuscript check recorded with the commit.

A looser extractor that deletes fences and then looks for quotation marks reports “missing quotes” in Chapters 3, 5, 7 and 12 and in Appendix A. The same strings are missing from `HEAD`. Each one is prose joined across a fence. They are not dropped quotations.

Part files (`part-1.md` through `part-6.md`) are a single heading each. They were read and left unchanged.

`about-the-author.md` was read. It was already third person. No biographical fact was removed.

## Coverage

| File | Edited | Named people generalized |
| --- | --- | --- |
| `part-1.md` … `part-6.md` | Reviewed, unchanged | — |
| `01-the-agentic-web-arrives.md` | Yes | Lars → a customer |
| `02-from-apis-to-tools.md` | Yes | — |
| `03-mcp-in-practice.md` | Yes | Lars → a customer |
| `04-enter-webmcp.md` | Yes | Ingrid → a guest |
| `05-registering-tools.md` | Yes | a one-off Ingrid → the guest; Listing 4.1 claim corrected in prose |
| `06-annotations-lifecycle-errors.md` | Yes | — |
| `07-frames-origins-agents.md` | Yes | — |
| `08-declarative-api.md` | Yes | — |
| `09-first-webmcp-app.md` | Yes | — |
| `10-webmcp-in-frameworks.md` | Yes | — |
| `11-designing-tools.md` | Yes | — |
| `12-threat-models.md` | Yes | — |
| `13-privacy-consent-human-in-the-loop.md` | Yes | — |
| `14-testing-debugging-evals.md` | Yes | — |
| `15-browser-support-and-standards.md` | Yes | — |
| `16-product-and-business-implications.md` | Yes | Kari → the product lead; Jonas → the front-end lead |
| `17-the-road-ahead.md` | Yes | Kari, Jonas, and the closing Lars |
| `appendix-a-api-reference.md` | Yes | — |
| `appendix-b-glossary.md` | Yes | B.2 entries for Kari and Lars removed |
| `appendix-c-resources.md` | Yes | — |
| `appendix-d-migration.md` | Yes | — |
| `about-the-author.md` | Reviewed, unchanged | — |

Running examples that are products, not characters, stay named: Trailhead, Fjord Table, Supportly, Ledgerly, Test Agent.

## What the register change did

Blog openers (“Let’s”, “In simple words”, “Feel free”, “Please look”, “Bottomline”, smileys, taste-based autobiography) were removed where they only announced a claim that the next sentence already made. Instructional “you” stays. “I” stays for tests, re-checks, co-authorship and advice the text already marks as the author’s.

Two judgments were narrowed rather than restated as fact:

- “I hear this comparison in almost every planning conversation” is now “Planning discussions about agents often start from an SEO analogy.” The rate “almost every” is no longer claimed.
- “I bet this is the most common real-world WebMCP bug” is now “This is an easy WebMCP bug to ship.” The demonstration in that paragraph is unchanged. “Most common” is no longer claimed.

## Flags for the author

These were not “fixed” by changing code, inventing a number, or rewriting a footnote.

1. **Listing 4.1 is not a contiguous excerpt of the runnable file.** Chapter 5 said Listing 5.1 was Listing 4.1 plus numbered markers. Listing 5.1 also adds `outputSchema`. The prose and the Listing 5.1 title now say so. The fenced code in both chapters was not edited. Reported from the demos check in webmaxru/webmcp-book-demos PR 5. Either the prose relationship or the printed listing still needs a decision if Listing 4.1 should match the file.

2. **Listing 17.1’s `outputSchema` does not cover Listing 17.2’s error.** The printed schema requires `products`. Listing 17.2 returns `{ status: 'error', code: 'INVALID_ARGUMENT', message }` and passes the catalog schema through, so that error would not validate. The prose next to Listing 17.1 now says that. The fences were not edited. The demos check says the runnable file uses a schema that covers both branches. The book does not describe that file’s schema.

3. **`outputSchema` / pull request #254 is both merged and still open.** Chapter 15’s table and a later paragraph, and `[^ch15-output-schema]`, say #254 merged on 2 November 2026. Footnote `[^ch15-17]` still lists #254 among the pull requests “all open on 2 November 2026”. Footnote definitions were not edited. Chapter 5’s opening still says the 27 October 2026 IDL matches the 15 October IDL and that later changes are prose, not the API, while Listing 5.2 and the chapter’s own flux note include `outputSchema` from the 2 November merge. Left as written.

4. **“Seventeen days separate the two checks”** (15 October 2026 and 2 November 2026) in Chapter 15. The date difference is eighteen days. The sentence was not changed.

5. **Chapter 11** still says “The most common way to end up with too many tools is to wrap your API”, which is stronger than the Anthropic line it sits next to (“the error they see most”). Left as written.

6. **`VALIDATION.md`** still describes Lars, Kari and Jonas as the book’s fictional example. It is a record of an earlier validation pass and was not rewritten. The manuscript no longer uses those names, except `guest: 'Ingrid Hansen'` inside a Chapter 8 code listing, which was left byte-identical.

7. **Chapter 6** still quotes the specification’s “an specific invocation.” The grammar is the source’s. Left as written.
