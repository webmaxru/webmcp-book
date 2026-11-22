{sample: false}
# Chapter 2: From APIs to Tools: A Short History

> *“Every new data source requires its own custom implementation, making truly connected systems difficult to scale.”*
>
> — Anthropic, “Introducing the Model Context Protocol”[^ch02-1]

## One capability, many descriptions

Trailhead, the outdoor-gear store from Chapter 1, has one capability that every agent wants: product search. Give it a query, an optional category, a maximum price in kroner and an “in stock only” flag, and it returns a list of products. Trailhead’s own React front end calls it dozens of times an hour.

Now imagine the requests landing on Trailhead’s engineering team over a few years. In 2023 somebody asks for a ChatGPT plug-in, which means an OpenAPI description and a manifest file. Later that year the plug-in becomes a GPT action. The mobile team wants their in-app assistant to call search through OpenAI’s function calling, and then a second assistant uses Anthropic’s API, which describes the same function in a slightly different envelope. In 2025 someone asks for an MCP server so that desktop assistants can find Trailhead’s products. A partner wants Trailhead’s “gear advisor” agent to be discoverable by other companies’ agents over A2A. And in 2026 the product team asks why the browser’s built-in assistant still clicks through the filter sidebar instead of just searching.

Each request is reasonable. Each one describes the same capability (a name, a sentence about what it does and a schema for its inputs) in a slightly different place. That repetition is the story of this chapter. It explains how the *tool*, a named, described, schema-typed capability that a model can choose to call, became the common unit of agent capability, why the industry kept reinventing the envelope around it, and why the browser tab was the last big place left without one.

There is no code in this chapter, but it introduces the vocabulary the rest of the book relies on. If you have built with function calling or MCP before, much of it will be familiar. If you haven’t, the chapter explains why WebMCP looks the way it does.

## Before tools: APIs for programs

Long before anyone asked a language model to book a table, the web had a well-developed way for one program to use another: the web API. Roy Fielding’s 2000 doctoral dissertation gave the dominant style its name, Representational State Transfer (REST), along with the idea of resources addressed by URLs and manipulated with a small set of HTTP methods.[^ch02-2] By the 2010s almost every serious web product had an HTTP API next to its user interface.

APIs designed for programs come with an assumption that becomes important later in this story. The caller is a developer who reads the documentation once, writes code against it and then runs that code many times. The documentation can be long and the conventions can be subtle, because a human reads it and a compiler enforces the result.

That assumption pushed the industry towards machine-readable API descriptions, so that client code, documentation and tests could be generated instead of written by hand. The one that won is the *OpenAPI Specification*. It started as the Swagger Specification, which SmartBear Software donated to what became the OpenAPI Initiative, an open governance project under the Linux Foundation.[^ch02-3] An OpenAPI document lists an API’s operations, their parameters, request bodies and responses. The latest published version is 3.2.1, dated 10 September 2026 (still the latest when I checked in November 2026).[^ch02-4]

Inside OpenAPI documents, the shapes of request and response bodies are described with *JSON Schema*, a vocabulary for saying what a JSON value must look like: its type, its properties, which of them are required, which strings are allowed. JSON Schema has its own specification, and its current version is called 2020-12.[^ch02-5] JSON Schema is the thread running through every stage of this chapter, and WebMCP’s `inputSchema` is a JSON Schema too.

So by the early 2020s the web already had a common language for describing capabilities to programs. What it didn’t have was a caller that could read a description and decide on its own when to use it.

## Teaching models to use tools

Large language models changed who the caller could be. In October 2022 the ReAct paper showed that a model could interleave “reasoning traces and task-specific actions”, so that the actions let it “interface with external sources” and the reasoning helped it plan and handle exceptions.[^ch02-6] In February 2023 the Toolformer paper showed that models could “teach themselves to use external tools via simple APIs”, deciding “which APIs to call, when to call them, what arguments to pass, and how to best incorporate the results”.[^ch02-7]

Those two sentences describe the loop every agent in this book runs. The model gets a goal and a list of things it can do. It decides whether to do one of them, and with what arguments. Something outside the model performs the action and hands back the result. The model reads the result and decides what to do next.

Research prototypes taught models to emit tool calls in ad hoc text formats that the surrounding program had to parse. That worked in papers. It didn’t work well enough for products, because a model that is almost right about the format produces a call the parser rejects, or (worse) one the parser accepts with the wrong arguments. Products needed a contract: a way for the developer to declare the available tools, and for the model to answer with a call that matches the declaration.

## Function calling: JSON Schema becomes the lingua franca

That contract arrived in model APIs in 2023. In June OpenAI announced that developers could “describe functions” to two new model versions and “have the model intelligently choose to output a JSON object containing arguments to call those functions.”[^ch02-8] The models had been “fine-tuned to both detect when a function needs to be called (depending on the user’s input) and to respond with JSON that adheres to the function signature,” and developers described the functions “via JSON Schema”.[^ch02-8] OpenAI’s examples are a good summary of what tools are for. A request like “Email Anya to see if she wants to get coffee next Friday” becomes a call to `send_email(to: string, body: string)`, and “Who are my top ten customers this month?” becomes an internal API call.[^ch02-8]

The idea spread across the industry because it was simple and because JSON Schema was already familiar. Anthropic’s API defines a tool with a `name`, a `description` and an `input_schema`, and Claude answers with a `tool_use` block that your code executes.[^ch02-9] Google’s Gemini API offers function calling too, with schemas written in “a subset of the OpenAPI schema”.[^ch02-10] Field names differ a little from vendor to vendor. The substance is the same everywhere: a name, a natural-language description and a JSON Schema for the arguments.

Reliability came next. A model that produces JSON “that adheres to the function signature” most of the time still produces broken calls some of the time. In August 2024 OpenAI introduced *Structured Outputs*, which constrains generation so that outputs “reliably adhere to developer-supplied JSON Schemas.” For function calling it is enabled “by setting `strict: true` within your function definition,” and on OpenAI’s own evaluation of complex schema following, the new model scored 100 per cent against less than 40 per cent for the June 2023 model.[^ch02-11] The schema had become more than documentation for the model. It was a hard constraint on its output.

### The round trip, step by step

WebMCP keeps exactly the same shape as a function call. Take Trailhead’s mobile assistant, built on a model API with function calling, and a customer who types “any two-person tents under 4,000 kroner in stock?”

1. *The application declares its tools.* Together with the conversation, it sends the model a list of tool definitions. One of them is `search_products`, with a description (“Search Trailhead’s catalogue by keyword, category, maximum price in NOK and stock status”) and a JSON Schema saying that `query` is a required string, `category` is one of five values, `maxPrice` is a number and `inStockOnly` is a boolean.
1. *The model decides.* It reads the request and the tool descriptions and concludes that this question needs a search. Instead of answering in prose, it returns a structured call: the tool name and a JSON object of arguments, with `query` set to “two-person tent”, `category` to “tents”, `maxPrice` to 4000 and `inStockOnly` to true.
1. *The application acts.* The app’s code (not the model) checks the arguments, calls Trailhead’s search API with them and gets back a list of products.
1. *The result goes back to the model.* The app sends the products to the model as the result of that call.
1. *The model answers, or calls again.* It might summarise three tents for the customer, or call a second tool to compare two of them.

Notice what the model never does: it never touches Trailhead’s systems directly. It only proposes calls. Everything that has an effect happens in code the developer controls, and that’s also where checks, logging and confirmations go. Notice, too, that the model’s choice depends almost entirely on two pieces of text, the tool name and its description, plus the schema. Those three things are the whole interface between the model and the capability.

Three properties of function calling carry straight through to WebMCP:

- *The description is written for a model.* It is not API reference documentation for a developer. In a sentence or two, it has to tell a model when this tool is the right choice and when it isn’t. Chapter 11 is about writing these well.
- *The schema is the contract.* It tells the model which arguments are valid, and it gives the receiving code a way to check them. In WebMCP, as Chapter 5 shows, the browser passes the schema to the agent but does not validate calls against it, so your code still has to.
- *The model chooses, and your code acts.* Function calling never executes anything by itself. The model proposes a call, and the application decides whether and how to run it. That separation is what makes it possible to put a human confirmation step in the middle, and WebMCP relies on it.

Function calling solved the problem of *expressing* a tool call. It didn’t solve the problem of *distributing* tools. In the original design, each application’s developer wrote the tool definitions into their own code. If Trailhead wanted its search to be usable from someone else’s assistant, it needed a way to publish the definition and have that assistant pick it up.

## OpenAPI meets the chatbot: plug-ins and actions

The first big attempt to solve distribution came before function calling was even public in the API. On 23 March 2023 OpenAI announced “experimental support for AI plugins in ChatGPT — tools designed specifically for language models.”[^ch02-12] The design reused the web’s existing description format. To build a plug-in, a developer would “build an API with endpoints you’d like a language model to call,” then “create an OpenAPI specification documenting your API, and a manifest file that links to the OpenAPI spec and includes some plugin-specific metadata.”[^ch02-13] The manifest carried fields such as `name_for_model` and `description_for_model`, separate from the names and descriptions shown to people, and when a user enabled a plug-in, its documentation was “shown to the language model as part of the conversation.”[^ch02-13] OpenTable, Instacart, Wolfram and Zapier were among the launch partners.[^ch02-13]

For anyone who builds websites this was a significant moment, for two reasons. It confirmed that an existing, widely used API description format could be repurposed as a tool description with very little extra work. And it showed the separation of audiences that WebMCP later formalises: a name and a description for the model, and a different presentation for the human.

The plug-in beta didn’t last in that form. In November 2023 OpenAI introduced GPTs, custom versions of ChatGPT, and with them *actions*: developers “can also define custom actions by making one or more APIs available to the GPT. Like plugins, actions allow GPTs to integrate external data or interact with the real-world.”[^ch02-14][^ch02-12] The envelope changed. The idea of an API described for a model stayed.

> **Still in flux:** Product names in this space are recycled freely. In 2026 the word “plugin” is back in ChatGPT, now for packages that bundle skills, connected apps and interactive extensions, and OpenAI’s release notes describe supported plugins using MCP events to trigger automations.[^ch02-15][^ch02-12] These have little in common with the 2023 plug-ins apart from the name. When you read about “plugins”, “actions”, “apps” or “connectors”, check the date and the vendor before assuming you know what is meant.

Plug-ins and actions had one more property that matters for the next section: they were specific to one platform. An OpenAPI document was portable, but the manifest, the review process, the authentication flow and the user experience belonged to ChatGPT. A company that wanted to reach the users of several assistants had to repeat the exercise for each of them.

## The description is the new documentation

Plug-ins made one lesson explicit that function calling had left implicit: an API has two audiences now. The manifest’s `name_for_human` and `description_for_human` were for the person browsing a plug-in store, and `name_for_model` and `description_for_model` were for the model deciding whether to call it.[^ch02-13] Those are different jobs, and they need different writing.

Documentation for developers can be long, because developers read it once and then write code. A tool description is read by a model every time it decides what to do, often next to dozens of other descriptions, and it has a sentence or two to say when this tool is the right one. It is closer to a prompt than to reference documentation. Get it wrong and the model calls the tool when it shouldn’t, doesn’t call it when it should, or fills in the arguments badly. And no compiler will tell you.

The same advice has turned up in every generation of the technology. Chrome’s WebMCP best-practices page, which I co-author, gives the current version of it. “A clear description should describe what the tool does and when to use it,” it says, and it recommends positive language over prohibitions: instead of “Don’t use this tool for weather,” write “This tool can create a calendar event, scheduled for a specific date and time.”[^ch02-16] It also warns against names that hide what a tool does, contrasting a `create-event` tool that creates an event immediately with a `start-event-creation-process` tool that only redirects the user to a form.[^ch02-16]

The point for this chapter is that the description travelled with the tool through every envelope. Function definitions, plug-in manifests, GPT actions, MCP tools and WebMCP tools all carry one, and it does the same job in each of them. A team that learns to write good tool descriptions for one of these formats has learned it for all of them. Chapter 11 is devoted to doing it well for WebMCP.

## Why one integration per platform doesn’t scale

Step back from the vendor names and look at the arithmetic. Suppose there are *N* AI applications that want to use tools, and *M* services that want to offer them. If every pair needs its own integration, someone has to build and maintain up to *N × M* of them. Ten assistants and a thousand services make ten thousand integrations, each with its own manifest format, authentication flow, review process and quirks. Most will never be built. The ones that are built will drift out of date.

A shared protocol changes the sum. If every assistant speaks the protocol as a client and every service speaks it as a server, the work is *N + M*: each side implements the protocol once. Figure 2.1 shows the difference. It’s the same argument that made HTTP, USB and the Language Server Protocol worth standardising, and it’s the argument Anthropic made when it open-sourced the Model Context Protocol on 25 November 2024. “Every new data source requires its own custom implementation,” the announcement said, “making truly connected systems difficult to scale.” MCP was offered as “a universal, open standard for connecting AI systems with data sources, replacing fragmented integrations with a single protocol.”[^ch02-1]

![Figure 2.1 — Why bespoke integrations don’t scale. With one integration per pairing, N AI applications and M services need up to N × M connectors. With a shared protocol, each side implements it once: N + M.](images/figure-2-1.png)

Chapter 3 covers MCP in depth, so here are only the facts this chapter needs. MCP defines hosts (the AI applications), clients (connectors inside a host) and servers (the services that offer capabilities), and they talk to each other with JSON-RPC 2.0 messages.[^ch02-17] Among the things a server can offer are *tools*, and an MCP tool definition will look very familiar by now: a `name`, an optional `title`, a `description` and an `inputSchema`, which is a JSON Schema.[^ch02-18] The current version of the protocol is dated 2026-07-28.[^ch02-17]

What changed with MCP was not the shape of a tool. It was who owned the envelope. Function definitions belonged to whoever wrote the application. Plug-in manifests belonged to one platform. MCP belonged to nobody in particular, and on 9 December 2025 Anthropic made that formal by donating it to the Agentic AI Foundation, a directed fund under the Linux Foundation “co-founded by Anthropic, Block and OpenAI, with support from Google, Microsoft, Amazon Web Services (AWS), Cloudflare, and Bloomberg.”[^ch02-19] The foundation launched with three founding projects: MCP, Block’s goose and OpenAI’s AGENTS.md.[^ch02-20]

For Trailhead, MCP collapses most of the requests from the start of this chapter into one: build an MCP server once, and every assistant that speaks MCP can search the catalogue. Chapter 3 builds exactly that server.

## Agents talking to agents

Tools assume a particular relationship: an agent in charge, calling capabilities that do what they are told and return a result. Not every interaction fits. Sometimes the thing on the other end is itself an agent, with its own model, its own judgment and its own long-running work. A travel agent might hand a hotel search to a hotel chain’s booking agent and wait for it to negotiate dates. Trailhead’s gear advisor might be asked by a hiking app’s agent to recommend a tent, and come back an hour later when the stock arrives.

On 9 April 2025 Google announced the Agent2Agent protocol (A2A) for this case, “with support and contributions from more than 50 technology partners.”[^ch02-21] Google described it as “an open protocol that complements Anthropic’s Model Context Protocol (MCP), which provides helpful tools and context to agents.”[^ch02-21] Its specification describes A2A as “an open standard designed to facilitate communication and interoperability between independent, potentially opaque AI agent systems.”[^ch02-22] *Opaque* is the key word. Where an MCP server exposes individual tools with schemas, an A2A agent exposes itself. It publishes an *Agent Card*, a JSON document describing what it can do and how to reach it, which other agents can fetch from a well-known location such as `/.well-known/agent-card.json`.[^ch02-22][^ch02-21] The calling agent delegates a task, and the remote agent decides how to carry it out.

A2A went the same way to neutral governance as MCP, only faster. The Linux Foundation launched the A2A project on 23 June 2025.[^ch02-23] The specification reached version 1.0.0.[^ch02-22] And in August 2026 A2A was accepted as a Growth Stage project at the same Agentic AI Foundation that hosts MCP.[^ch02-24] The announcement described the division of labour neatly: MCP “serves as the vertical integration layer connecting agents to internal tools and databases,” while A2A “acts as the horizontal protocol enabling peer-to-peer collaboration.”[^ch02-24]

A2A is not the only proposal for agents talking to agents, and this book doesn’t go further into that category. It matters here because of what it shares with everything else in this chapter. A2A connects agents running on servers, over the network, each authenticated in its own way. Like MCP servers, OpenAPI plug-ins and function calls, it assumes the capability lives somewhere an agent can reach without a user’s browser.

> **Still in flux:** Both MCP and A2A now sit under the Agentic AI Foundation, and both keep versioning their specifications: MCP by date (the current version is 2026-07-28) and A2A by number (1.0.0, still the latest released version in November 2026).[^ch02-17][^ch02-22] Membership, project stages and the relationship between the two protocols will probably keep changing. Check the foundation’s and the projects’ own pages for the current picture.

## Where the browser fits

Put the whole history on one line, as in Figure 2.2, and a pattern appears. Every stage moved tools further away from any particular application and closer to a shared, neutral description. And every stage kept tools on the server side.

![Figure 2.2 — From APIs to tools, 2000–2026. Each step kept the same core (a name, a description for the model, a JSON Schema for inputs) and changed who owns the envelope. Every step until WebMCP connects an agent to a server. WebMCP puts tools in the page.](images/figure-2-2.png)

That server-side bias is no accident. It follows from who the callers were: model APIs running in data centres, chat assistants running in the cloud, agents talking to agents over the network. For those callers, the natural home of a capability is an HTTP endpoint.

But Chapter 1 showed where a growing share of agent work actually happens: in the user’s browser, in a tab where the user is already signed in, looking at a page that already holds the state they care about. For that kind of work, every integration in this chapter has the same three weaknesses. The WebMCP explainer groups MCP and OpenAPI together as *backend integrations* and lists them.[^ch02-25]

- *The interface is bypassed.* The agent talks to the service’s backend, and the page the user is looking at doesn’t change. Trailhead’s cart, filled through an MCP server, doesn’t update the cart badge in the user’s open tab until something reloads it.
- *State and authentication have to be duplicated.* The user is signed in to the tab. The backend integration needs its own credentials and its own idea of what the user is doing.
- *There is a second thing to build.* Trailhead’s front end already knows how to search, filter and add to the cart. A backend integration means writing and operating a separate server that does the same things.

Chrome’s documentation puts the contrast in two short sentences. With WebMCP, “Tools run in the page with the user’s session. Instead of your application being a guest within an agent, the agent is a guest on your platform.”[^ch02-26]

That’s the gap WebMCP fills. It keeps everything this chapter has built up (a tool with a name, a description written for a model, a JSON Schema for its inputs, a model that chooses and code that acts) and moves the code into the page. The WebMCP explainer describes pages that use it as “in-page Model Context Protocol (MCP) servers that implement tools exposing client-side logic and DOM interaction rather than server-side APIs.”[^ch02-25] The explainer’s repository was created on 5 August 2025, a little more than eight months after the launch of MCP.[^ch02-27]

### Why not just run MCP in the browser?

If WebMCP is “in-page MCP”, why not simply put an MCP server in the page and let the browser’s agent connect to it as an MCP client? The WebMCP explainer considered exactly that and gives two reasons against it.[^ch02-28] First, “MCP was built primarily for server-to-client and stdio/SSE process communication. It lacks native web concepts like origins, standard browser permissions, DOM integration, and tab-level lifecycle management.” Second, “coupling a web API directly to an actively evolving backend protocol would hinder backward compatibility and platform stability.”[^ch02-28] Web APIs, once shipped, are very hard to change, and MCP has published several dated versions and keeps evolving. Chapter 3 shows how much its wire format changed in a single revision.

So WebMCP takes MCP’s *vocabulary* and leaves its *protocol* behind. In the explainer’s words, it “shares a common vocabulary with MCP (e.g., tools, schemas, parameters), but provides a form-fitting, client-safe solution designed natively for the web platform.”[^ch02-28] The explainer’s list of prior art reads like a summary of this chapter: MCP, the community MCP-B project, which built “browser tab and extension transports for local in-page communication”, OpenAPI, “used in platform-specific extensions like ChatGPT Actions”, and A2A, “focused on connecting distinct autonomous AI agents to one another.”[^ch02-28] Chrome’s own comparison page is just as direct: WebMCP “is not an extension or a replacement of MCP.”[^ch02-26]

Chapter 4 tells the rest of that story, including the other alternatives the editors rejected. For now the important point is continuity. A developer who has written a function definition or an MCP tool will find a WebMCP tool familiar from the first line: the same name, the same kind of description, the same JSON Schema. What’s new is where the `execute` function runs and what it can reach.

### Five approaches side by side

Table 2.1 lines up the approaches.

| | Function calling | OpenAPI plug-ins and actions | MCP | A2A | WebMCP |
|---|---|---|---|---|---|
| What is described | Functions in your own app | An HTTP API | Tools, resources and prompts on a server | A whole agent, via its Agent Card | Tools in a web page |
| Who owns the envelope | Each model vendor | One assistant platform | An open protocol (AAIF) | An open protocol (AAIF) | A W3C Community Group draft |
| Where the code runs | Your application | Your backend | Your server or local process | The remote agent | The user’s tab |
| Uses the user’s live session | Only if your app does | No | No | No | Yes |
| Typical caller | Your own app’s model | One assistant | Any MCP host | Another agent | A browser agent |
| Schema language | JSON Schema (vendor subsets) | OpenAPI / JSON Schema | JSON Schema | Agent Card (JSON) | JSON Schema |

*Table 2.1 — Five ways to give an agent a capability. All but A2A describe tools with a name, a description and a JSON Schema. They differ in who owns the format and where the code runs.*

None of these replaces the others. A store like Trailhead might reasonably use all five: function calling inside its own support chatbot, an MCP server for desktop assistants and back-office agents, an A2A agent card for its gear advisor, and WebMCP tools on its storefront for the browser agents its customers already use. The rest of the book is about the last one, but it borrows freely from the others. The vocabulary of tools comes from function calling, the shape of a tool definition comes from MCP, and the hard-won lessons about descriptions, schemas and confirmation steps apply everywhere.

## What the history teaches

Three lessons from this short history shape the rest of the book.

*The core of a tool is stable, the envelope is not.* A name, a description for a model and a JSON Schema for the inputs have survived every generation since 2023, while the formats wrapped around them (functions, plug-in manifests, actions, MCP tool lists) came and went. In practice this means time spent designing good tools is never wasted. If WebMCP changes shape again before it settles (and Chapter 4 explains why it might), your names, descriptions and schemas will move to the new shape with few changes.

*Distribution is the hard part.* Expressing a tool call turned out to be easy once JSON Schema was in place. Getting the right tools in front of the right agent, with the right authentication, without building one integration per platform, is what took years and several false starts. WebMCP’s answer to distribution is unusual: the tools are discovered by visiting the page, so the page itself is the distribution channel. That has real limits, which Chrome lists honestly (“Clients and browsers must visit a site directly to know if it has callable tools”), and real advantages, which Part III explores.[^ch02-29]

*Someone has to own the decision to act.* From function calling onwards, the model proposes and the code disposes. The question every generation had to answer was whose code, and who gets asked before something irreversible happens. For server-side integrations the answer is usually the assistant platform. For WebMCP it is the site, in its own interface, with the user watching. That shift is the subject of Part IV.

## Chapter summary

- Web APIs, described with OpenAPI and JSON Schema, gave programs a common way to use services long before language models arrived. OpenAPI started as Swagger and is now governed under the Linux Foundation. JSON Schema’s current version is 2020-12.
- Research such as ReAct (2022) and Toolformer (2023) showed that models could decide when to call tools and with what arguments. Products needed a stricter contract than free-text formats.
- Function calling, introduced by OpenAI in June 2023 and adopted across vendors, made the tool a first-class concept: a name, a description written for a model, and a JSON Schema for the arguments. Structured Outputs (August 2024) turned the schema into a hard constraint.
- ChatGPT plug-ins (March 2023) and then GPT actions (November 2023) used OpenAPI to distribute tools to an assistant, but each such integration belonged to one platform.
- One integration per pairing means N × M connectors. MCP, open-sourced by Anthropic in November 2024 and donated to the Linux Foundation’s Agentic AI Foundation in December 2025, reduces that to N + M. Its tools have a name, a description and an `inputSchema`.
- A2A, announced by Google in April 2025 and now also under the Agentic AI Foundation, connects opaque agents to each other through Agent Cards instead of exposing individual tools.
- Every one of these integrations runs on the server side, which bypasses the page, duplicates state and authentication, and means building a second system. WebMCP keeps the tool and moves it into the user’s tab. Chapter 3 now covers MCP properly, because WebMCP borrows its vocabulary.

## Notes

[^ch02-1]: Anthropic, “Introducing the Model Context Protocol” (25 November 2024). <https://www.anthropic.com/news/model-context-protocol>
[^ch02-2]: Roy Thomas Fielding, *Architectural Styles and the Design of Network-based Software Architectures*, doctoral dissertation, University of California, Irvine (2000). <https://ics.uci.edu/~fielding/pubs/dissertation/top.htm>
[^ch02-3]: OpenAPI Initiative, “About”. <https://www.openapis.org/about>
[^ch02-4]: OpenAPI Specification v3.2.1 (10 September 2026), the latest published version when re-checked in November 2026. <https://spec.openapis.org/oas/latest.html>
[^ch02-5]: JSON Schema, “Specification” (current version 2020-12). <https://json-schema.org/specification>
[^ch02-6]: Shunyu Yao et al., “ReAct: Synergizing Reasoning and Acting in Language Models”, arXiv:2210.03629 (v1 6 October 2022), abstract. <https://arxiv.org/abs/2210.03629>
[^ch02-7]: Timo Schick et al., “Toolformer: Language Models Can Teach Themselves to Use Tools”, arXiv:2302.04761 (9 February 2023), abstract. <https://arxiv.org/abs/2302.04761>
[^ch02-8]: OpenAI, “Function calling and other API updates” (June 2023, with an update of 20 July 2023). <https://openai.com/index/function-calling-and-other-api-updates/>
[^ch02-9]: Anthropic, “Tool use with Claude”, Claude API documentation. <https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview>
[^ch02-10]: Google AI for Developers, “Function calling with the Gemini API”, including “Notes and limitations”. <https://ai.google.dev/gemini-api/docs/function-calling>
[^ch02-11]: OpenAI, “Introducing Structured Outputs in the API” (6 August 2024). <https://openai.com/index/introducing-structured-outputs-in-the-api/>
[^ch02-12]: OpenAI Help Center, “ChatGPT — Release Notes”, entries for 23 March 2023 (“Introducing plugins in ChatGPT”), 6 November 2023 (“Introducing GPTs”) and September–October 2026 (plugins). <https://help.openai.com/en/articles/6825453-chatgpt-release-notes>
[^ch02-13]: OpenAI, “ChatGPT plugins” (23 March 2023), as archived by the Internet Archive on 31 December 2023 (the original page did not load when checked). <https://web.archive.org/web/20231231002503/https://openai.com/blog/chatgpt-plugins>
[^ch02-14]: OpenAI, “Introducing GPTs” (6 November 2023). <https://openai.com/index/introducing-gpts/>
[^ch02-15]: OpenAI Help Center, “Plugins in ChatGPT”. <https://help.openai.com/en/articles/20001256>
[^ch02-16]: Chrome for Developers, “WebMCP best practices”, by Alexandra Klepper, Maxim Salnikov and François Beaufort (published 18 May 2026, updated 30 October 2026, retrieved November 2026). <https://developer.chrome.com/docs/ai/webmcp/best-practices>
[^ch02-17]: Model Context Protocol, Specification, version 2026-07-28 (latest), Overview. <https://modelcontextprotocol.io/specification/2026-07-28>
[^ch02-18]: Model Context Protocol, Specification 2026-07-28, “Tools” (server features). <https://modelcontextprotocol.io/specification/2026-07-28/server/tools>
[^ch02-19]: Anthropic, “Donating the Model Context Protocol and establishing the Agentic AI Foundation” (9 December 2025). <https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation>
[^ch02-20]: Agentic AI Foundation, “Linux Foundation Announces the Formation of the Agentic AI Foundation (AAIF), Anchored by New Project Contributions Including Model Context Protocol (MCP), goose and AGENTS.md” (9 December 2025). <https://aaif.io/news/linux-foundation-announces-formation-of-aaif>
[^ch02-21]: Rao Surapaneni et al., “Announcing the Agent2Agent Protocol (A2A)”, Google Developers Blog (9 April 2025). <https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/>
[^ch02-22]: Agent2Agent (A2A) Protocol Specification, latest released version 1.0.0 (re-checked November 2026), §1 Introduction and the Agent Card discovery example. <https://a2a-protocol.org/latest/specification/>
[^ch02-23]: The Linux Foundation, “Linux Foundation Launches the Agent2Agent Protocol Project to Enable Secure, Intelligent Communication Between AI Agents” (23 June 2025). <https://www.linuxfoundation.org/press/linux-foundation-launches-the-agent2agent-protocol-project-to-enable-secure-intelligent-communication-between-ai-agents>
[^ch02-24]: A2A Protocol blog, “A New Chapter for A2A: Joining the Agentic AI Foundation” (27 August 2026). <https://a2a-protocol.org/latest/blog/2026/08/27/a-new-chapter-for-a2a-joining-the-agentic-ai-foundation/>
[^ch02-25]: WebMCP explainer (README), introduction and “Backend Integrations vs. In-browser WebMCP Tools”, webmachinelearning/webmcp (retrieved November 2026). <https://github.com/webmachinelearning/webmcp>
[^ch02-26]: Chrome for Developers, “When to use WebMCP and MCP” (formerly “WebMCP and MCP compared”; published 11 March 2026, updated 27 October 2026), introduction and “Control UI access” (retrieved November 2026). <https://developer.chrome.com/docs/ai/webmcp/compare-mcp>
[^ch02-27]: GitHub REST API, repository metadata for webmachinelearning/webmcp (`created_at`: 2025-08-05T13:10:14Z), read 15 October 2026. <https://api.github.com/repos/webmachinelearning/webmcp>
[^ch02-28]: WebMCP explainer, “Alternatives Considered” and “Prior Art” (retrieved November 2026). <https://github.com/webmachinelearning/webmcp#alternatives-considered>
[^ch02-29]: Chrome for Developers, “WebMCP” (published 18 May 2026, updated 7 October 2026), “Limitations” (retrieved November 2026). <https://developer.chrome.com/docs/ai/webmcp>
