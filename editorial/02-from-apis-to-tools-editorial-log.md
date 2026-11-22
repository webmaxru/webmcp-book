# Editorial log: Chapter 2, From APIs to Tools: A Short History

Manuscript: `manuscript/02-from-apis-to-tools.md`. Old text (15 October 2026): 5,476 words by `wc -w`. New text: 5,555 words. Same voice materials as Chapter 1 (his voice profile, the Book 2 voice report, both skills and slop-patterns.md, the Book 2 introduction and log, the his recent article).

## Pass 1: voice draft (personal-author-voice)

- **Author presence.** "I" appears where it is verified fact or his judgment: the best-practices page "which I co-author" (the page's byline lists Maxim Salnikov, see the author facts and the validation notes), "when I checked in November 2026" for the OpenAPI version. Everything else is tutorial "let's/we" and reader "you". No invented anecdotes.
- **Rhythm and devices.** "Let's slow down and see…", "Please remember that name", "feel free to skim", "And no compiler will tell you.", parenthetical asides instead of semicolons, a few short sentences for checkpoints ("That worked in papers.").
- **Structure** kept: it is a history chapter and the order is chronological; the three "what the history teaches" lessons are three real lessons, kept as they are.

## Pass 2: substantive edit (professional-writing-editor)

- **Point:** the tool (name + description for a model + JSON Schema) is the stable unit; the envelope changed with every generation; all previous envelopes are server-side; WebMCP keeps the tool and moves it into the tab. Every section serves it.
- **Fidelity fix from validation:** the compare page sentence about "live session data, cookies, and DOM elements" no longer exists (page rewritten 27 October 2026). Replaced with the current wording and the page's new title, plus its sentence "WebMCP is not an extension or a replacement of MCP", which supports the "Why not just run MCP in the browser?" section.
- Added one bridging sentence to Chapter 3 ("Chapter 3 shows how much its wire format changed in a single revision"), which is true (the 2026-07-28 revision removed the handshake and sessions) and makes the "actively evolving" argument concrete.
- **Slop sweep:** no "landscape/robust/seamless/delve"; no announcement sentences; semicolons in prose: zero (four in the old text were split or turned into "and"/parentheses).

## Pass 3: voice recheck and fidelity check

- Kept unchanged: all dates, names and numbers (2000, Swagger/SmartBear, OpenAPI 3.2.1 of 10 September 2026, JSON Schema 2020-12, ReAct October 2022, Toolformer February 2023, function calling June 2023 and its quotes, Structured Outputs August 2024 with 100 % vs < 40 %, plug-ins 23 March 2023 with partners, GPTs November 2023, MCP 25 November 2024, AAIF 9 December 2025 with founders and projects, A2A 9 April 2025 / 23 June 2025 / 1.0.0 / August 2026, repository created 5 August 2025), Table 2.1, Figures 2.1–2.2.
- Corrected: compare-page quote and footnote (see above); footnotes ch02-4, ch02-16, ch02-22, ch02-25, ch02-26, ch02-28, ch02-29 carry November 2026 re-check notes, ch02-16 now names the page's authors.
- Removed: the obsolete compare-page sentence only.

## Pass: serious technical prose (22 November 2026)

Register override: professional developer book. Blog scaffolding and named fictional people reduced. Protected spans unchanged.

- Point: a tool is a name, a description for a model, and a JSON Schema. The envelope around that core kept changing, and until WebMCP every envelope stayed on the server.
- What changed (voice/register), with one before/after pair if you changed the opening:
  - The opening Trailhead history was left as it stood. The skim sentence was the register change.
  - Before: “If you have built with function calling or MCP before, feel free to skim. If you haven’t, this is the shortest path to understanding why WebMCP looks the way it does.”
  - After: “If you have built with function calling or MCP before, much of it will be familiar. If you haven’t, the chapter explains why WebMCP looks the way it does.”
  - Also removed “Please remember that name.”, “Let’s slow down and see what actually happens”, and “so let’s name them now”. The claims those sentences introduced stayed.
- Generalized: none. No Lars, Kari, or Jonas in this chapter.
- Kept on purpose: “when I checked in November 2026” and “which I co-author”. All dates, names, percentages, Table 2.1, Figures 2.1 and 2.2, footnotes, the epigraph, and the H1. “And no compiler will tell you.” and “That worked in papers.” stay as limits.
- Flags (gaps, unsupported claims, likely factual problems). Write "None" if none.
  - None.
