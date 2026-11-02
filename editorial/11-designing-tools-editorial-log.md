# Editorial log: Chapter 11, "Designing Tools Agents Can Actually Use" (second edition)

Manuscript: `manuscript/11-designing-tools.md`
Figures: `figures/src/figure-11-1.svg`, `figure-11-2.svg`, `figure-11-3.svg` (hand-written SVG, APM palette, rendered with `figures/render.py`)
Demos: `chapters/11-designing-tools/` (101/101 checks, mock and Chromium 156.0.8078.4 WebMCPTesting, 2 November 2026, 8/8 listings match)
Validation: VALIDATION.md (45 rows)
Length: 10435 words before, 12185 words after (`wc -w`, code included). Growth comes from new sourced material: Chrome's build-tools guide (user goal, role-play, variance, trust boundaries, graceful failure, duplication conflict), Chrome's 30 October best-practices additions (trust the agent, raw input, honorifics, shared service, stale state), the jjhub data point in #255, the #92 comments and the duplicate-ticket check.

Material read before writing: his voice profile, the Book 2 voice report, `.agents/skills/personal-author-voice/SKILL.md`, `.agents/skills/professional-writing-editor/SKILL.md` with `references/slop-patterns.md`, Book 2 `manuscript/00-introduction.md`, Book 2 `editorial/01-audit-the-agent-environment-editorial-log.md`, his recent article, the validation notes, the house style.

## Pass 1: voice draft

- Register: technical walkthrough. "We" for the work done together on Trailhead and the widget ("We'll work on two projects", "In Chapter 6 we followed it"), "let's" before listings and comparisons ("Let's have a look at the numbered comments.", "Let's compare Trailhead's two versions of `sku`"). First person singular only for authorial choices and facts: "The closest figure I found", "I use a four-part template", "The test I use", "the rules I apply to every message", "In Chapter 6 I promised", and "Chrome's guide on building tools, which André Cipriani Bandarra and I wrote" (byline verified on the page, the author facts / the validation notes).
- His markers, used where they fit and not as decoration: "Please note" (four times, each before a consequence the reader should not miss), "of course" (once), rhetorical questions answered at once ("How do you reconcile…? Ask where…"), short checkpoint sentences ("Say so.", "Written once, used twice."). No "Bottomline" here, because the summary list already closes the chapter.
- Contractions as in his articles (it's, doesn't, you'll). No exclamation marks, no emoji.

## Pass 2: substantive edit (professional-writing-editor)

- Structure kept: the chapter's six H2 sections still follow the order a tool is read (strategy, names, schemas, results, UI parity, the widget). Two additions found a natural home instead of new top-level sections: the build-tools framework inside "Start from tasks, not endpoints", and "The same request, twice" as the last H3 of the results section, right before Listing 11.8 uses it.
- Cut reflexive "X, not Y" contrasts from 18 to 12. The ones kept carry an argument (tasks vs endpoints, writing vs contract, results vs exceptions).
- No triads for rhythm: lists of three exist only where there are three things (three tests, three practices, three things that don't belong).
- Removed every prose semicolon, including in the notes ("opened …; open on …" became "opened …, open on …").
- Clean-manuscript conversions: listing labels to `**Listing 11.N** \`path\` — title`, the three Still-in-flux boxes to `> **Still in flux:** …` on one line.

## Pass 3: voice recheck and fidelity check

Every quote was re-read on its source page on 2 November 2026 except the OpenAI guide (script-rendered page, marked in the validation file and in note 6). Three Chrome quotes were tightened to the exact current wording. The "evaluation-driven development" phrase lost its quote marks because the page shows it as a key term, not a sentence.

Corrections: spec date 15 → 27 October 2026 (notes 2, 11, 12, 14, 16, 23 and two in-text mentions), issue status dates to 2 November, test totals 99 → 101, Listing 11.8 callouts renumbered, Figure 11.3 caption.

Additions (all sourced, see validation rows 4, 8, 10, 23, 25, 26, 28, 33, 35, 37, 38, 40): jjhub/ChatGPT limit data point and Kenneth Rohde Christiansen's harness feedback (#255), the #92 comments of 16 and 30 October, the build-tools framework, trust the agent, raw input, honorifics, trust boundaries, graceful-failure examples, variance, duplication conflict with a working demo, shared application service, stale workflow state.

Removals: none of the first edition's technical content.
