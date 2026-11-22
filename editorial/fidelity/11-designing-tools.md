# Fidelity check: Chapter 11, Designing Tools Agents Can Actually Use

Date: 22 November 2026. Register pass only. Compared with `python3 /tmp/check_fidelity.py manuscript/11-designing-tools.md`.

## Protected spans

Checker: `OK 11-designing-tools.md fences=9 tables=3 figures=3 footnotes=28 quotes=221`.

Counted in the file after editing: 9 fenced blocks (18 fence lines), 3 figure lines (`![Figure 11.1`, `![Figure 11.2`, `![Figure 11.3`), 3 tables (11.1, 11.2, 11.3), 28 footnote definitions (`[^ch11-1]` through `[^ch11-25]`, plus `[^ch11-output-schema]`, `[^ch11-output-validation]`, and `[^ch11-output-extension]`). Listing labels and paths were not edited. The H1 was not edited. No callout was added or removed.

One edit was reverted. Changing “In Chapter 8 we noticed that a declarative form’s “No preference”” made the checker report a missing quote. That span runs from a backtick through the opening quote before “No preference”. The original wording was restored. The checker then printed OK.

## Numbers, dates, and quotes confirmed still present

Counts and dates read in the prose and notes and found unchanged: jjhub’s 126 tools, median description 94 characters, a budget of 20, OpenAI’s “fewer than 20”, Trailhead’s 1,798 characters and the widget’s 1,850, `create_ticket` growing from 415 to 1,014 characters, the widget from 955 to 1,850, Chrome budgets of 500 / 150 / 30 / 1,500, 101 checks passed on 2 November 2026 in Chromium 156.0.8078.4, issue #255 opened 22 August 2026, issue #161 opened 3 April 2026, the 5 March 2026 resolution, PR #289 closed 1 October 2026, #92 comments of 16 October and 30 October, issue #9 open since 12 August 2025, PR #254 opened 21 August 2026 and last updated 26 October 2026.

Quotes read and found unchanged, including: the epigraph “More tools don’t always lead to better outcomes.”, the ChatGPT sentence “WebMCP is disabled for this page because the site’s WebMCP configuration exceeds supported limits.”, “for fewer than 20 functions available at the start of a turn at any one time”, “just a soft suggestion.”, Anthropic’s “tools that merely wrap existing software functionality or API endpoints—whether or not the tools are appropriate for agents.”, “finds availability and schedules an event.”, “Combine functions that are always called in sequence.”, “what the agent should not do or what actions are restricted”, “Trust the agent to complete the task.”, “a moderately complex app can easily surface 100+ tools”, “Tools can tell agents what a site can do, but Skills tell agents how to do it well.”, “Always mention 30-day return policy before checkout.”, “the intern test”, “and it actually triggers a purchase.”, “must be valid against exactly one of the given subschemas”, “may make the wrong choice”, “Validate strictly in code, loosely in schema”, “Don’t make the model fill arguments you already know.”, “I need to go to NYC next week”, “Which day next week?”, and “use the exact order details to ensure a single request wasn’t sent repeatedly by mistake”.

## Generalized

Shared-exploration “we” (“left us”, “we’ll decide”, “we’ll work”, “we saw”, “we followed”, “we’ll come back”, “Here we do it”) was rewritten as “this chapter”, “Chapter 6”, “Chapter 8 shows”, or “this section”. “I use a four-part template” and “the rules I apply” became instructions. The four parts and the six message rules were not changed. “The test I use” became “A practical test”. The previous sentence still calls the `error` / `refused` line a judgment call, and the question in italics is unchanged. No “almost every” or “most common” claim was created. “The most common way to end up with too many tools is to wrap your API” was already in the chapter and was left as written.

## Flags

`outputSchema` is described two ways. Left unchanged.

- “Declare the result shape, then validate it in the harness” says PR #254 added `outputSchema` to `ModelContextTool` and `RegisteredTool`. Note `[^ch11-output-schema]` says that pull request was merged 2 November 2026.
- The *Still in flux* note on `outputSchema` says there is no way yet to tell the agent the shape of a result in advance, and that PR #254 was last updated on 26 October 2026 and is still open. Note `[^ch11-22]` says the pull request was open on 2 November 2026.

Those two accounts disagree about whether the pull request had landed and whether a tool can declare its result shape. Not corrected.

“The most common way to end up with too many tools is to wrap your API” was already in the chapter and was left as written. The next sentences cite Anthropic’s “the error they see most” and the jjhub case. That support is narrower than a claim about the most common WebMCP design.
