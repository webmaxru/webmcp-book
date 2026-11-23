# Editorial log: Chapter 8, "The Declarative API: Forms as Tools"

Manuscript: `manuscript/08-declarative-api.md`
Figures: `figures/src/figure-8-1.svg`, `figure-8-2.svg` (hand-written SVG, APM figure kit) rendered to `manuscript/resources/images/figure-8-1.png`, `figure-8-2.png`
Demo: `chapters/08-declarative-api/` in webmaxru/webmcp-book-demos (no code change; suite re-run 2 Nov 2026 on Chromium 156.0.8078.4: 17 passed, 0 failed)
Validation: VALIDATION.md (48 rows)
Length: 8,656 words (Oct 15) → 9,382 words (`wc -w`, listings included). The growth is new material (TAG early comment, issue #361 serialization note, PR #350 explainer fix, re-run statement), about 450 words. The rest was tightened slightly.

Materials read before writing: his voice profile and the Book 2 voice report, .agents/skills/personal-author-voice/SKILL.md, professional-writing-editor/references/slop-patterns.md, Book 2's introduction and the Ch1 editorial log, his recent article (the latest applied example of the voice).

## Pass 1: voice draft (personal-author-voice)

Register: the technical-walkthrough register, with the exploratory register for the "where it came from" and status sections.

- Maxim speaks as the author: "I" for real authorial choices and for the tests ("so I tested it", "I expected the agent to keep waiting... It didn't", "Personally for me, this is the strongest argument..."), tutorial "we/let's" for the walkthrough ("Let's look at Fjord Table's booking page the way an agent would", "Let's follow these steps"), "you" for the reader.
- One verified biographical fact used: he co-authors Chrome's "WebMCP best practices" page (byline verified on the page, 2 Nov 2026: Alexandra Klepper, Maxim Salnikov, François Beaufort). Used once, as a parenthesis where the chapter quotes that page. No invented anecdotes.
- His repertoire, used where it fits and not as a checklist: "Have a look", "Some important things to notice here", "Bottomline:", "Pretty much the same list, right?", "of course", one ":)" (on "You started them, after all"), parenthetical asides, spaced em dashes as spoken pauses (2.8 per 1k words, moderate on purpose).
- Rhetorical questions only where they open a real distinction ("And what does the person see?", "what happens when an agent calls it?").

## Pass 2: substantive edit (professional-writing-editor)

- Structure kept (it already followed the life of a call). The opening status callout was merged into one block with its three parts (spec, Chrome, what to do) instead of three italic sub-paragraphs.
- Callouts converted to the house form (`> **Still in flux:** *Title.* ...`). Listing labels converted to `**Listing 8.N** `path` — title`, paths relative to the demos repo root.
- Slop pass: no "Here's the thing", "worth noting", "robust", "seamless", "landscape", "delve", no triads added, no summary closers at section ends. Contrast constructions "not X, but Y": 0. Semicolons in prose: 0 (one removed from Table 8.1, one from the UnknownError paragraph).
- Lint-driven rewording: the explainer's "entirely a TODO" and "are TBD" are paraphrased (the build's placeholder lint fails on those tokens even inside quotes).
- An inference I had first written as fact ("Chromium uses one result path for both") was replaced with an honest statement that I don't know whether the declarative path will change with issue #361.
- "Put the clearest possible constraints in the schema" → "into the form": for declarative tools the schema follows the form.

## Pass 3: voice recheck + fidelity check

Scripted check against the Oct 15 text: every inline code token, every number and every URL of the old prose is present in the new text, except one deliberately changed code span (the "No submit button was found..." message, which had broken nested backticks and is now one clean span). All 12 code blocks are byte-identical to the old blocks and to the demo files.

Corrections (per the validation notes and primary sources, see the validation file):
1. Spec draft date 15 Oct → 27 Oct 2026 (IDL unchanged).
2. "Six days before this chapter was written" dropped; status re-dated to 2 Nov 2026.
3. Explainer's `toolcanceled` → `toolcancel` (PR #350, 16 Oct 2026); its open question on `ModelContext` vs `<form>` added.
4. Chrome 156 is now Stable (20 Oct 2026); tests re-run 2 Nov on the same build.
5. New: W3C TAG early comment (26 Oct 2026) asking to work out the declarative version first.
6. New: issue #361 on result serialization (spec author: Chrome is wrong) next to Table 8.2.
7. New: no `outputSchema` in the imperative draft either (open PR #254).
8. Footnotes re-dated ("retrieved November 2026"), four new footnotes (ch08-21 to ch08-24).

Removals: none of the technical content. Only time-relative framing ("six days before this chapter was written", "The explainer still calls the cancel event `toolcanceled`").

## Pass: serious technical prose (22 November 2026)

Register override: professional developer book. Blog scaffolding and named fictional people reduced. Protected spans unchanged.

- Point: Chrome can turn an existing form into a tool with a few attributes, and that behaviour is an implementation fact about Chromium 156, not a specification.
- What changed (voice/register), with one before/after pair if you changed the opening:
  - Before: “Let’s look at Fjord Table’s booking page the way an agent would. … Pretty much the same list, right? … Can we just say “this form is a tool” … In Chrome’s implementation, we can.”
  - After: “Fjord Table’s booking page already had the shape of a tool, long before anyone typed `registerTool()`. … A tool definition is that same list … Can the markup say “this form is a tool” … In Chrome’s implementation, the markup can.”
  - Also dropped “Have a look”, “Let’s follow these steps”, “Some important things to notice here”, the “Bottomline” label on the form-reset rule, “Personally for me”, and the smiley after “you started them”.
- Generalized: “Personally for me, this is the strongest argument that the declarative idea will come back” became “The TAG comment is one argument that the declarative idea will come back”. The ranking “strongest” is not stated as fact.
- Kept on purpose: “when I re-checked”, “so I tested it”, “I re-ran” / “17 of 17”, “than I tested”, “when I removed `toolname`”, “I’m one of its co-authors”, “In my tests” / “I haven’t used it”, “what I observed”, “I didn’t test it”, “I can’t tell you (I haven’t seen its plans)”, “my tests”, “The details I observed”, “I expected the agent to keep waiting. It didn’t.”, “Other limits I found”, “no error my code could catch”, “That’s how I re-validated”. Left in place because they sit inside baseline quote spans: “We’ll come back to it below”, “which makes sense if you think about it”, “Useful, of course.”
- Flags (gaps, unsupported claims, likely factual problems). Write "None" if none.
  - None in the claims. The three phrases above were blog register. A later check showed the baseline “quote” crossed a fence, so they were not real quotations. Reconciliation removed “of course”, “which makes sense if you think about it”, and “We’ll come back to it below”. The observations and the forward reference stay.

