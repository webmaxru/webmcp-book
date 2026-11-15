# Changelog

All notable changes to *Tools, Not Clicks: Building Agent-Ready Websites with WebMCP* are recorded here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow [Semantic Versioning](https://semver.org/) as read for a book (see [RELEASING.md](RELEASING.md)).

Each version is a Git tag `vX.Y.Z`. Its GitHub Release carries the PDF, the EPUB and the HTML edition built from that tag. The web edition shows this file as its release history.

## [Unreleased]

### Changed

- Update Chapters 5, 9, 11, 14, 15 and 17 and Appendix A for WebMCP `outputSchema` (PR #254, merged 2 November 2026). Clarify that the member is optional, the native mismatch behavior remains unresolved in issue #92, and agent harnesses should validate before model delivery. Synchronize Chapter 9 and Chapter 17 listings with the companion demo repository.
- Preserve Chromium 156 test observations and state that the supplied Chrome build 159.0.8140.0 was not tested by this repository.

## [2.1.0] - 2026-11-04

New material from reader feedback. Thanks to Francesco Marinoni Moretto (Agentic Standards Map) for reading the book closely and for the question behind the new section.

### Added

- Chapter 16: a new section, “WebMCP and protocol checkout (UCP)”. The same Shopify storefronts that deploy WebMCP also publish a Universal Commerce Protocol profile at `/.well-known/ucp` (fetched on three stores on 4 November 2026). The section covers how the two channels relate (on Shopify, Checkout WebMCP implements the UCP checkout capability in the page), which one an agent should use (Shopify’s guidance, and the silence of both specifications), whether Chapter 13’s human-in-the-loop guarantees carry over (UCP requires a trusted UI or signed AP2 mandates, and Shopify’s in-page tools require the buyer’s confirmation) and which record a dispute relies on (open, with the Article 8(2) question linked to the existing citation). New notes ch16-29 to ch16-32 and a new summary bullet.
- Chapter 13: one sentence pointing from “What a trusted click proves” to the new section.
- VALIDATION.md: Chapter 16 rows 21–29 and Chapter 13 row 38, each with its source and the date it was read.

### Changed

- Chapters 16 and 17: the commenter cited on the Consumer Rights Directive (Article 8(2)) is named as Francesco Marinoni Moretto (GitHub: frmoretto), at his request, in the text and in notes ch16-26 and ch17-35. VALIDATION.md Chapter 16 row 13 and the Chapter 16 editorial log record the change.

## [2.0.2] - 2026-11-02

### Fixed

- The copyright and licence lines across the book's repositories name the author, Maxim Salnikov, and every repository link points to github.com/webmaxru.
- The demos repository's licence reads "Copyright (c) 2026 Maxim Salnikov".

## [2.0.1] - 2026-11-02

### Fixed

- Links to the book's repositories now point to their new home under github.com/webmaxru (the old addresses redirect). The demos repository is public.
- Appendix C's note on link checks says which repository is private.
- The Leanpub page is https://leanpub.com/webmcp.
- The release history no longer links to the private repository's release pages.

## [2.0.0] - 2026-11-02

The second edition. Every chapter, listing and figure was checked against the Chrome WebMCP documentation, the WebMCP specification (Draft Community Group Report of 27 October 2026) and the webmachinelearning/webmcp repository as of 2 November 2026, then rewritten. The code was tested in Chromium 156.0.8078.4. The API the first edition teaches (`document.modelContext.registerTool()`, input schemas, `execute`, `AbortSignal` unregistration, annotations, the declarative form attributes) is unchanged. What changed is the guidance around it, the standards status and the ecosystem. See VALIDATION.md for every finding and its source.

### Changed

- The full text rewritten in the author's voice. Each chapter has an editorial log in `editorial/` and a validation table in `VALIDATION.md`.
- Chapter 1–3: Chrome's comparison page is now "When to use WebMCP and MCP" (27 October) and the quotes follow it. Chapter 3's demo runs on the current MCP SDK 2.4.0 and Inspector 2.13.0, and `requestUserInteraction` is shown next to the open `requestUserInput()` proposal (#204).
- Chapter 4: the spec has four editors and is dated 27 October. Table 4.1 follows the rewritten comparison page. New section on the standards status in November 2026: the W3C TAG's early comment of 26 October and the proposed charter deliverable "Site Capabilities for Agents".
- Chapter 5: checked against the 27 October draft (the API definitions are identical). The open result-serialization question (#361) is covered, and the advice to always return an object stays.
- Chapter 6: Chrome's 30 October best practices (commit points, register tools all at once, wait for the UI, bind approval to the exact plan, idempotency) and the new §6.2 text on untrusted annotations.
- Chapter 7 and 12: the same-origin section of the spec (§6.3.4, "Interaction with the Same-Origin Policy", merged 27 October) replaces the old "still a TODO" note, with the two-sided opt-in it defines.
- Chapter 8: the explainer's `toolcanceled` event is now `toolcancel`, and the TAG comment on the declarative API is covered.
- Chapter 9: the first app keeps one `AbortController` and unregisters every tool if one registration fails, as Chrome's "register tools all at once" rule recommends.
- Chapter 10: Chrome's imperative-API page moved to `use-webmcp-tool` for React and added Vue (16 October). New "React: two hooks" section with Table 10.2, and a short Vue section.
- Chapter 11 and 13: Chrome's new guidance on trust boundaries, stale workflow state and recomputing a plan on confirmation.
- Chapter 14: Chrome's evals page, the Example Agentic Chrome Extension, chrome-devtools-mcp 1.12.0 and the time-travel and version-pinning tests from the build-tools page.
- Chapter 15: browser and standards status as of 2 November 2026 (Chrome 156 Stable, Chrome 157 on 3 November, the origin trial, TPAC 2026, the permissions-policy discussion in #236).
- Chapter 16 and 17: rebuilt on the rewritten comparison page and Chrome's 30 October guidance, with the late-October standards signals.
- Appendices A–D: the API reference cites the 27 October draft and lists the open pull requests, the glossary adds `use-webmcp-tool` and "two-sided opt-in", the resources point to the new web edition, and the migration log runs to 2 November.
- About the Author: co-author of two Chrome WebMCP documentation pages, member of the W3C Web Machine Learning Community Group, maintainer of the `webmcp` agent skill and of agentprose.
- All 38 figures redrawn as SVG diagrams in the new palette.

### Added

- A new visual theme derived from the author's APM book (apm.isainative.dev) for the web edition, the PDF and the EPUB.
- PDF (7 × 9.25 in, for Leanpub and KDP) and EPUB 3 editions built from the same manuscript as the web edition.
- A release flow: tagged versions, GitHub Releases with the PDF, EPUB and HTML edition, and this release history.
- Hosting on Azure Static Web Apps with Bicep templates and a one-command deploy (`infra/deploy.sh`), and a guide for the custom domain webmcp.salnikov.no.
- The Leanpub sample is marked in the manuscript with `{sample: true}` (Part I, Chapter 1, Chapter 5 and About the Author).

### Removed

- The GitHub Pages site and its generator. The manuscript is now kept apart from the styling: `manuscript/` is a clean, Leanpub-ready Markdown manuscript, `theme/` holds the look and `tools/` the build.

## [1.0.0] - 2026-10-15

The first edition, as published on the web edition on GitHub Pages: 17 chapters in six parts and Appendices A–D, written against Chromium 156 with the `WebMCPTesting` feature and the WebMCP draft of 15 October 2026. This version was never tagged in Git; it is recorded here as the baseline for 2.0.0.
