# Tools, Not Clicks: Building Agent-Ready Websites with WebMCP

*Working title.* A book about WebMCP, the proposed web standard that lets websites hand AI agents real tools.

AI agents already browse on our behalf, but most of them still work like a tourist with a phrasebook: they take screenshots, guess which button does what, and break the moment a layout changes. WebMCP is the web platform’s proposed answer. A page declares what it can do as named, described, schema-typed tools, and the browser’s agent calls them directly, inside the user’s live, logged-in session, with the human watching and in control. This book explains why that matters, how WebMCP relates to Anthropic’s Model Context Protocol (MCP), and how to use the API to make a real product agent-ready without rebuilding it. It covers registering tools, wiring them into React and Angular, testing them with evals, and hardening them against prompt injection and over-reach. It also gives an honest map of a standard still being argued over, with Google and Microsoft shipping trials, Mozilla neutral, and WebKit opposed, so readers can build now and still be ready for whatever WebMCP becomes.

## Status

| Part | Ch. | Title | Status |
|---|---|---|---|
| | | [Book outline](outline/outline.md) ([PDF](outline/WebMCP_Book_Outline.pdf)) | Done |
| I | 1 | The Agentic Web Arrives | Not started |
| I | 2 | From APIs to Tools: A Short History | Not started |
| I | 3 | MCP in Practice | Not started |
| I | 4 | [Enter WebMCP](chapters/04-enter-webmcp/WebMCP_Ch04_Enter_WebMCP.md) | Drafted |
| II | 5 | [Registering Tools with <code>document.modelContext</code>](chapters/05-registering-tools/WebMCP_Ch05_Registering_Tools.md) | Drafted |
| II | 6 | Annotations, Lifecycle and Errors | Not started |
| II | 7 | Frames, Origins and Page-Embedded Agents | Not started |
| II | 8 | The Declarative API: Forms as Tools | Not started |
| III | 9 | Your First WebMCP App, End to End | Not started |
| III | 10 | WebMCP in Frameworks | Not started |
| III | 11 | Designing Tools Agents Can Actually Use | Not started |
| IV | 12 | Threat Models for Tool-Exposing Pages | Not started |
| IV | 13 | Privacy, Consent and the Human in the Loop | Not started |
| V | 14 | Testing, Debugging and Evals | Not started |
| V | 15 | Browser Support and the Standards Road | Not started |
| VI | 16 | Product and Business Implications | Not started |
| VI | 17 | The Road Ahead | Not started |

Chapter text is Markdown (GitHub-flavoured, with footnotes). Each chapter's figures live in its own `images/` folder and are linked with relative paths.

## Code

The runnable demos built for the book live in a separate repository: [vibeprogrammer/webmcp-book-demos](https://github.com/vibeprogrammer/webmcp-book-demos). It starts with **Fjord Table** (`fjord-table/`), the restaurant-booking site from chapters 4 and 5, whose tool code is copied from the chapter listings.

## Layout

```
outline/                     outline.md and the original PDF
chapters/
  04-enter-webmcp/           WebMCP_Ch04_Enter_WebMCP.md + images/
  05-registering-tools/      WebMCP_Ch05_Registering_Tools.md + images/
```

## A note on dates

WebMCP is a draft from the W3C Web Machine Learning Community Group, not a standard. API details in these drafts were checked against the 13 October 2026 draft and Chrome's documentation on 14 October 2026; each chapter flags what is still in flux.
