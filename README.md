# Tools, Not Clicks: Building Agent-Ready Websites with WebMCP

[![Deploy book to GitHub Pages](https://github.com/vibeprogrammer/webmcp-book/actions/workflows/deploy-pages.yml/badge.svg)](https://github.com/vibeprogrammer/webmcp-book/actions/workflows/deploy-pages.yml)
[![Read online](https://img.shields.io/badge/read-free%20online-2ea44f)](https://vibeprogrammer.github.io/webmcp-book/)

A practical book on WebMCP, the proposed web standard that lets a website give AI agents real, typed tools instead of making them click through the page.

**[Read it free online →](https://vibeprogrammer.github.io/webmcp-book/)**

<!-- Leanpub ebook: add the link (and a buy badge, if wanted) here once the book is published on Leanpub. -->

## Table of contents

- [About the book](#about-the-book)
- [Status](#status)
- [Contents](#contents)
- [Code and demos](#code-and-demos)
- [Build the web edition locally](#build-the-web-edition-locally)
- [Errata and feedback](#errata-and-feedback)
- [Author](#author)
- [Copyright and license](#copyright-and-license)

## About the book

AI agents already browse on our behalf, but most of them still work from screenshots: they guess which button does what, and they break when the layout changes. WebMCP is the web platform's proposed answer. A page declares what it can do as named, described, schema-typed tools on `document.modelContext`, and the browser's agent calls them directly, inside the user's own session, with the user watching and in control.

**Who it's for**

- Front-end and full-stack web developers who build production apps in JavaScript or TypeScript (plain, React, Angular or similar) and want a hands-on path from a first tool to production.
- Product managers, tech leads and engineering managers who need to decide whether, where and when to invest in agent-readiness. Part VI and the chapter openers work without the code.

**What you'll learn**

- Why agents need tools rather than clicks, and how WebMCP relates to the Model Context Protocol (MCP).
- How to register tools with `document.modelContext`: schemas, annotations, lifecycle, errors, frames and origins, and the declarative form API.
- How to build an agent-ready app end to end, wire WebMCP into React and Angular, and design tools that models actually use well.
- How to threat-model tool-exposing pages and keep a human in the loop for consent and privacy.
- How to test, debug and evaluate tools, follow browser support and the standards process, and judge the product and business impact.

## Status

**Complete.** All 17 chapters and Appendices A–D are written. The whole book was technically reviewed on 15 October 2026:

- Every claim was checked against sources read that day.
- Spec references are dated to the WebMCP [Draft Community Group Report](https://webmachinelearning.github.io/webmcp/) of 15 October 2026 from the W3C Web Machine Learning Community Group.
- Every code listing was re-run in Chromium 156 with `--enable-features=WebMCPTesting` and against a `document.modelContext` mock. All demo tests pass.

WebMCP is still a Community Group draft, not a W3C standard, and it changes between browser releases. Each chapter marks what is still in flux in **Still in flux** callouts.

## Contents

| Part | Chapter | Read online | Source |
|:---:|---|:---:|:---:|
| **I** | 1. The Agentic Web Arrives | [Web](https://vibeprogrammer.github.io/webmcp-book/chapters/01-the-agentic-web-arrives.html) | [Markdown](chapters/01-the-agentic-web-arrives/WebMCP_Ch01_The_Agentic_Web_Arrives.md) |
|  | 2. From APIs to Tools: A Short History | [Web](https://vibeprogrammer.github.io/webmcp-book/chapters/02-from-apis-to-tools.html) | [Markdown](chapters/02-from-apis-to-tools/WebMCP_Ch02_From_APIs_to_Tools.md) |
|  | 3. MCP in Practice | [Web](https://vibeprogrammer.github.io/webmcp-book/chapters/03-mcp-in-practice.html) | [Markdown](chapters/03-mcp-in-practice/WebMCP_Ch03_MCP_in_Practice.md) |
|  | 4. Enter WebMCP | [Web](https://vibeprogrammer.github.io/webmcp-book/chapters/04-enter-webmcp.html) | [Markdown](chapters/04-enter-webmcp/WebMCP_Ch04_Enter_WebMCP.md) |
| **II** | 5. Registering Tools with `document.modelContext` | [Web](https://vibeprogrammer.github.io/webmcp-book/chapters/05-registering-tools.html) | [Markdown](chapters/05-registering-tools/WebMCP_Ch05_Registering_Tools.md) |
|  | 6. Annotations, Lifecycle and Errors | [Web](https://vibeprogrammer.github.io/webmcp-book/chapters/06-annotations-lifecycle-errors.html) | [Markdown](chapters/06-annotations-lifecycle-errors/WebMCP_Ch06_Annotations_Lifecycle_Errors.md) |
|  | 7. Frames, Origins and Page-Embedded Agents | [Web](https://vibeprogrammer.github.io/webmcp-book/chapters/07-frames-origins-agents.html) | [Markdown](chapters/07-frames-origins-agents/WebMCP_Ch07_Frames_Origins_Agents.md) |
|  | 8. The Declarative API: Forms as Tools | [Web](https://vibeprogrammer.github.io/webmcp-book/chapters/08-declarative-api.html) | [Markdown](chapters/08-declarative-api/WebMCP_Ch08_Declarative_API.md) |
| **III** | 9. Your First WebMCP App, End to End | [Web](https://vibeprogrammer.github.io/webmcp-book/chapters/09-first-webmcp-app.html) | [Markdown](chapters/09-first-webmcp-app/WebMCP_Ch09_First_WebMCP_App.md) |
|  | 10. WebMCP in Frameworks | [Web](https://vibeprogrammer.github.io/webmcp-book/chapters/10-webmcp-in-frameworks.html) | [Markdown](chapters/10-webmcp-in-frameworks/WebMCP_Ch10_WebMCP_in_Frameworks.md) |
|  | 11. Designing Tools Agents Can Actually Use | [Web](https://vibeprogrammer.github.io/webmcp-book/chapters/11-designing-tools.html) | [Markdown](chapters/11-designing-tools/WebMCP_Ch11_Designing_Tools.md) |
| **IV** | 12. Threat Models for Tool-Exposing Pages | [Web](https://vibeprogrammer.github.io/webmcp-book/chapters/12-threat-models.html) | [Markdown](chapters/12-threat-models/WebMCP_Ch12_Threat_Models.md) |
|  | 13. Privacy, Consent and the Human in the Loop | [Web](https://vibeprogrammer.github.io/webmcp-book/chapters/13-privacy-consent-human-in-the-loop.html) | [Markdown](chapters/13-privacy-consent-human-in-the-loop/WebMCP_Ch13_Privacy_Consent_Human_in_the_Loop.md) |
| **V** | 14. Testing, Debugging and Evals | [Web](https://vibeprogrammer.github.io/webmcp-book/chapters/14-testing-debugging-evals.html) | [Markdown](chapters/14-testing-debugging-evals/WebMCP_Ch14_Testing_Debugging_Evals.md) |
|  | 15. Browser Support and the Standards Road | [Web](https://vibeprogrammer.github.io/webmcp-book/chapters/15-browser-support-and-standards.html) | [Markdown](chapters/15-browser-support-and-standards/WebMCP_Ch15_Browser_Support_and_Standards.md) |
| **VI** | 16. Product and Business Implications | [Web](https://vibeprogrammer.github.io/webmcp-book/chapters/16-product-and-business-implications.html) | [Markdown](chapters/16-product-and-business-implications/WebMCP_Ch16_Product_and_Business_Implications.md) |
|  | 17. The Road Ahead | [Web](https://vibeprogrammer.github.io/webmcp-book/chapters/17-the-road-ahead.html) | [Markdown](chapters/17-the-road-ahead/WebMCP_Ch17_The_Road_Ahead.md) |

| Appendix | Read online | Source |
|---|:---:|:---:|
| A. API Quick Reference (IDL, Attributes, Events, Errors) | [Web](https://vibeprogrammer.github.io/webmcp-book/appendices/a-api-reference.html) | [Markdown](appendices/a-api-reference/WebMCP_AppA_API_Reference.md) |
| B. Glossary | [Web](https://vibeprogrammer.github.io/webmcp-book/appendices/b-glossary.html) | [Markdown](appendices/b-glossary/WebMCP_AppB_Glossary.md) |
| C. Resources and Further Reading | [Web](https://vibeprogrammer.github.io/webmcp-book/appendices/c-resources.html) | [Markdown](appendices/c-resources/WebMCP_AppC_Resources.md) |
| D. Migration Notes: `navigator.modelContext` and `provideContext()` to `document.modelContext` | [Web](https://vibeprogrammer.github.io/webmcp-book/appendices/d-migration.html) | [Markdown](appendices/d-migration/WebMCP_AppD_Migration.md) |

Also in this repository: the original [book outline](outline/outline.md) ([PDF](outline/WebMCP_Book_Outline.pdf)).

The chapters are GitHub-flavoured Markdown with footnotes. Each chapter's figures live in an `images/` folder next to its Markdown file.

## Code and demos

Every listing in the book is runnable code in the companion repository, **[vibeprogrammer/webmcp-book-demos](https://github.com/vibeprogrammer/webmcp-book-demos)**. It has one folder per chapter (plus Fjord Table, the restaurant-booking site that runs through the book), each with its own tests against Chromium's WebMCP and a mock. See its README for requirements and a quick start.

## Build the web edition locally

The web edition is generated from the Markdown by [`site/generate.py`](site/generate.py). You need Python 3 (CI uses Python 3.12).

```bash
python -m pip install -r site/requirements.txt
python site/generate.py                    # writes site/_site/ (git-ignored)
python -m http.server -d site/_site 8000   # then open http://localhost:8000
```

Every push to `main` that touches `chapters/`, `appendices/`, `outline/` or `site/` runs [`.github/workflows/deploy-pages.yml`](.github/workflows/deploy-pages.yml), which builds the site and publishes it to GitHub Pages. [`site/README.md`](site/README.md) explains how the build works.

## Errata and feedback

Found a mistake, a broken link or code that no longer works in a newer browser? Please [open an issue](https://github.com/vibeprogrammer/webmcp-book/issues/new). Include the chapter and section (or listing number), what you expected, and your browser and version. Problems with the runnable code belong in the [demos repository's issues](https://github.com/vibeprogrammer/webmcp-book-demos/issues).

## Author

**Maxim Salnikov** is a developer advocate, conference speaker and community organizer based in Oslo.

- LinkedIn: [linkedin.com/in/webmax](https://www.linkedin.com/in/webmax/)
- GitHub: [@webmaxru](https://github.com/webmaxru)
- Newsletter: [isainative.substack.com](https://isainative.substack.com/)

## Copyright and license

© 2026 Maxim Salnikov. Free to read online; all rights reserved.

The code in the companion [webmcp-book-demos](https://github.com/vibeprogrammer/webmcp-book-demos) repository is available under the [MIT License](https://github.com/vibeprogrammer/webmcp-book-demos/blob/main/LICENSE).
