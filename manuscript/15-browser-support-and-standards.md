# Chapter 15: Browser Support and the Standards Road

> *“Please note that Community Groups do not create W3C standards.”*
>
> — W3C, Community and Business Groups FAQ[^ch15-1]

## Two answers to one question

Every web team asks the same question before adopting a new API, and the Trailhead team is no exception: *which browsers support it?* There are two honest answers to it — and they are quite different.

The engineering answer fits in one sentence. Chromium-based browsers run WebMCP behind origin trials, so Chrome and Edge expose `document.modelContext` on any page that carries a valid trial token, and every other engine doesn’t expose it at all. Chapter 5 showed the feature check for that, and this chapter grows it into a small module that tells you exactly which surface you are standing on.

The standards answer takes the rest of the chapter. WebMCP is a Community Group draft, and its four editors work for Microsoft and Google.[^ch15-2] Mozilla recorded a neutral position, Apple’s WebKit team an opposed one.[^ch15-3][^ch15-4] The W3C Technical Architecture Group (TAG) has been reviewing it since June, keeps the label “Missing: Multi-stakeholder support” on it, and on 26 October 2026 shared its “current thinking” in a comment that, in its own bold words, “is not a resolution comment”.[^ch15-5] An attempt to move the specification into an existing W3C Working Group ran into a threatened formal objection over the summer and was closed on 13 October. Its replacement, a new Agentic Web Working Group, is a draft charter in refinement, and since 29 October that draft no longer lists “WebMCP” as its deliverable at all. It lists “Site Capabilities for Agents”, with WebMCP as the initial input.[^ch15-6][^ch15-7][^ch15-8]

Chapter 4 sketched this picture in one table. This chapter covers how to read each signal (a spec’s status line, a chromestatus entry, an origin trial page, a standards-position label, a TAG review, a charter draft), what each party has actually said, who consumes WebMCP today, and what the possible routes from Community Group to standard mean for a team that ships tools now. At the end there is a script that re-checks all of it for you, because every fact in the following pages has a date on it.

The first edition of this chapter was checked on 15 October 2026. For this edition I re-checked every statement on 2 November 2026, and that is the date the text below speaks from. Seventeen days separate the two checks.

## Reading the signals

Web standards news arrives through a handful of documents, each with its own vocabulary. Before the vendor-by-vendor account, it helps to know what each document can and cannot tell you.

*The specification’s status line.* The top of the WebMCP draft reads “Draft Community Group Report, 23 November 2026”, and the status section says plainly that it “is not a W3C Standard nor is it on the W3C Standards Track.”[^ch15-2] The date changes whenever the editors publish, which during 2026 meant every few days. The 2 November snapshot in Listing 15.4 still shows the 27 October date that page had then. A *Community Group* is an open forum anyone can join for free, and the W3C’s own FAQ asks members not to call its output “standards work” or “draft standards”. CG reports exist to make a later move to a Working Group easier: the contributor licence agreement is designed so that patent commitments carry over.[^ch15-1]

*The commit history.* The status line tells you *that* the draft changed. The repository tells you *what* changed. For WebMCP, the history of `webmachinelearning/webmcp` is the most precise record there is of when an API was renamed, added or removed, and it is the source of every date in Table 15.1.[^ch15-9]

*chromestatus.* Each Chromium feature has an entry with its owners, the blink-dev “intent” threads and its trial stages with milestone numbers. It also has a “browser signals” block for other engines and a standards-maturity field.[^ch15-10] Read the stages and milestones as authoritative, because Chromium engineers maintain them. Read the signals block with care: on 2 November 2026 it still said “No signal” for both Firefox and Safari, months after both had published positions, and the entry was last edited on 28 September.[^ch15-10] The lesson is bigger than WebMCP. A status page is only as current as its last edit, so go to the primary record whenever one exists.

*Origin trial pages.* Chrome and Edge each have a registration page per trial, with the trial’s description, its expiry and its terms.[^ch15-11][^ch15-12]

*Standards positions.* Mozilla and WebKit both run public GitHub repositories where anyone can ask for an engine’s view of a proposal. The outcome is a label (`position: neutral`, `position: oppose` and so on), and the discussion in the issue is where the reasons live.[^ch15-3][^ch15-4]

*TAG design reviews.* The TAG reviews proposals for architectural fit. Its labels track progress (“Progress: in progress”), the review type, the focus areas still pending and, sometimes, a missing prerequisite.[^ch15-5] Labels change rarely — the comments are where the thinking shows up first, as the 26 October comment proved.

*Charter drafts.* When the W3C considers a new Working Group, the draft charter lives in the `w3c/charter-drafts` repository and the process around it in an issue of `w3c/strategy`, whose labels say which phase the charter is in (“In Charter Refinement”, then Advisory Committee review).[^ch15-7] For WebMCP’s future this has become the most important document of all.

Figure 15.1 puts the main events from all these sources on one timeline.

![Figure 15.1 — Fifteen months on the standards road: spec changes, browser milestones, positions, reviews and W3C process events from the first explainer commit in August 2025 to this edition in November 2026, plus the two trial end dates in 2027.](images/figure-15-1.png)

## Chrome and Edge: two origin trials

### Timelines

WebMCP came to Chromium in stages. chromestatus records a developer trial (the API behind a flag, for local testing) starting in Chrome 146, then an origin trial from Chrome 149 through Chrome 156.[^ch15-10] Google announced the trial on 9 June 2026 with the words “In Chrome 149, you can sign up for the WebMCP origin trial.”[^ch15-13] On 28 September 2026 the trial was extended through Chrome 162, and the reason chromestatus gives is unusually candid: “OT feedback has suggested improvements to the API, which we are implementing. The OT extension would enable us to get data on those improvements as well as to continue getting data on the rest of the feature.”[^ch15-10] Nothing in that entry changed between the first edition and this one.

The release train did move, though. When I wrote the first edition, Chrome 156 was a beta. It reached the stable channel on 20 October 2026, Chrome 157 follows on 3 November, and Chrome 162, the last milestone of the extended trial, is scheduled for the stable channel on 2 February 2027.[^ch15-14] So the trial that sounded open-ended in milestones now has a rough calendar date — early 2027.

Microsoft runs its own trial. The project’s implementation-status page says it is live in Edge 150, and the Edge registration page gives a trial expiration date of 30 March 2027.[^ch15-15][^ch15-12] The two trials are measured differently: Chrome counts in milestones, Edge in calendar dates.

For local development no token is needed. Chrome’s documentation tells you to enable `chrome://flags/#enable-webmcp-testing` and relaunch, and that flag corresponds to the `WebMCPTesting` feature this book’s demos pass to Chromium on the command line.[^ch15-16]

### Tokens

An origin trial lets a site use an experimental feature on its own origin, for real users, without those users touching any flags. You register your origin, receive a token and serve that token with every page that should get the feature. Chrome’s origin-trial documentation lists three ways to deliver it: a `<meta http-equiv="origin-trial">` tag in the `<head>`, an `Origin-Trial` HTTP response header, or a meta tag injected from script.[^ch15-11] Edge’s trial page offers the same meta-tag and header options, and its registration is separate from Chrome’s.[^ch15-12]

All listings in this chapter live in the folder `chapters/15-browser-support-and-standards` of the book’s demos repository, and the file paths below are relative to it.

**Listing 15.1** `origin-trial-head.html` and `origin-trial.headers.txt` — enabling both trials on a page

```html
<!-- In the <head> of every page that should run with WebMCP enabled. -->
<!-- One token per trial; Chrome and Edge register separately. -->
<meta http-equiv="origin-trial" content="CHROME_TRIAL_TOKEN">
<meta http-equiv="origin-trial" content="EDGE_TRIAL_TOKEN">
```

The header form of the same thing, for a server or CDN configuration:

```http
Origin-Trial: CHROME_TRIAL_TOKEN
Origin-Trial: EDGE_TRIAL_TOKEN
```

A page can carry several tokens, and Chrome ignores tokens that are invalid or expired.[^ch15-11] That makes Listing 15.1 safe to serve to every browser: each one picks the token it recognises.

Three details of the token model matter in practice.

- *Third-party tokens.* Both trials accept them. chromestatus records third-party support for the Chrome trial, and the Edge trial record has `supportsThirdParty` set to `true`.[^ch15-10][^ch15-12] A third-party token lets a provider of embedded content (Supportly’s Helpdesk Widget from Chapter 7, for example) enable the feature from its own script on every customer site. Chrome’s documentation adds a caution: a third-party token works only when injected by an external script, not in a meta tag, inline script or header.[^ch15-11]
- *Extensions mean renewal.* When a trial is extended, Chrome emails registrants, and each origin has to renew and deploy a new token.[^ch15-11] If you shipped a Chrome 149 token and expect it to work through Chrome 162, check the registration console now.
- *Measurement.* The trial measures adoption with a Chromium use counter named `kModelContextRegisterTool`.[^ch15-10] Google’s stated goal for the experiment is “understanding the API ergonomics for agentic workflows across various verticals such as web commerce and productivity”, along with “metrics for tool usage and latency.”[^ch15-10]

### What can change during a trial

Origin trials exist to change an API. Chrome’s announcement calls trials “time-limited programs that offer early access to experimental platform features”, with the goal of “informing future iterations of the API.”[^ch15-13] The extension reason quoted above says the same about WebMCP specifically. Table 15.1 shows what that meant in 2026: each row is a change to the specification that could break code written against an earlier draft.

**Table 15.1 — Breaking or behaviour-changing spec changes in 2026, from the commit history[^ch15-9]**

| Date | Change | Pull request |
|---|---|---|
| 5 Mar 2026 | `provideContext()` and `clearContext()` removed | #132 |
| 27 May 2026 | `modelContext` getter moved from `Navigator` to `Document` | #184 |
| 8 Jun 2026 | `registerTool()` returns a promise | #200 |
| 21 Jul 2026 | `annotations` moved into a separate object | #225 |
| 17 Aug 2026 | `executeTool()` takes an object instead of a JSON string | #246 |
| 30 Sep 2026 | Origin-keyed agent cluster requirement removed | #330 |
| 8 Oct 2026 | Declarative (HTML forms) API removed from the spec “for now” | #338 |
| 8 Oct 2026 | `UnknownError` replaced with specific `DOMException` types | #339 |
| 2 Nov 2026 | Optional `outputSchema` added to `ModelContextTool` and `RegisteredTool` (now `Tool`) | #254 |
| 19 Nov 2026 | `RegisteredTool` replaced by the `Tool` interface. `window` becomes `source` | #348 |

Between 15 October and 2 November, five more commits landed on the specification, and not one of them touched the IDL. Two fixed edge cases in registration and unregistration (#345 and #347, the second one making `registerTool()` reject with `InvalidStateError` if a tool with the same name appears while the input schema is being serialized). One added Samuel Dallstream of Microsoft as the fourth editor (#352). And two rewrote security prose: a section on risks shared by the whole agent ecosystem (#334), and a proper section on cross-origin exposure with “two-sided opt-in” (#326), which replaced the unfinished placeholder the first edition of this book had to point at.[^ch15-9][^ch15-17] For almost three weeks the surface you program against stood still.

It won’t stand still forever. PR #254, which adds optional `outputSchema` to `ModelContextTool` and what is now `Tool`, merged on 2 November 2026. PR #348, which replaces `RegisteredTool` with `Tool` and renames `window` to `source`, merged on 19 November 2026. Chrome exposes that object starting in 160.0.8173.0 (Appendix E). Two API proposals that would still change the IDL remain open: `requestUserInput()` with interactive, form and URL modes (#204), and an `openWorldHint` annotation (#355). Both were open on 23 November 2026. Pull request #375, a generic-calling explainer, was also open that day and is not an IDL change (Appendix F).[^ch15-17][^ch15-output-schema] The task-supplied Chrome build `159.0.8140.0` supports `outputSchema`. This book’s Playwright tests still run Chromium 156 and do not verify Chrome 159 or 160. The current spec exposes the schema but leaves native mismatch rejection unresolved in issue #92. Harnesses should validate before passing results to a model.[^ch15-output-validation] An earlier reading of this chapter treated a 15 October Chromium landing as the `Tool` interface shipping in Chrome 158. That build number was ahead of the merged specification. The specification change is #348, and the Chrome version that carries it is 160.0.8173.0, not 158.[^ch15-35]

The browser and the draft also don’t always move together. Chrome’s WebMCP overview page, last updated on 7 October 2026, still says “There are two APIs you can use” and describes the declarative one, which the spec removed the next day.[^ch15-16][^ch15-9] Chapter 8 covers what the trial still ships, and Appendix D walks through migrating code written before the May move.

> **Still in flux:** *Error types.* Pull request #339 replaced `UnknownError` with specific exception types on 8 October 2026.[^ch15-9] Chromium 156 still rejects with `UnknownError` when a tool throws or when you call a tool that was unregistered (I re-ran those cases on 2 November 2026), so code that branches on `err.name` should accept both for now. Chromium itself has already caught up on its main branch: a change that makes `executeTool()` reject with the specific types landed on 16 October, after the Chrome 157 branch point, so Chrome 158 (in beta as of 2 November) should be the first release with it. I could not test that build here.[^ch15-35] *Result serialization.* The spec says a tool that returns the string `"hi"` resolves `executeTool()` to the JSON string `'"hi"'`, while Chromium returns the bare string. In issue #361, François Beaufort of Google, who wrote the pull request behind that part of the spec, answered on 26 October that “The WPT assertions are wrong, and so is Chrome”, and proposed that `undefined` should map to `null` instead of rejecting.[^ch15-18] Expect Chromium to change here. *The declarative API.* It is in Chrome’s trial and documentation, and out of the spec.[^ch15-16][^ch15-9] *Which improvements the extension tests.* chromestatus says the extension exists to gather data on improvements suggested by trial feedback, but doesn’t list them.[^ch15-10]

### Detecting what you are running on

With two trials, a flag, a moved attribute and a policy that can switch the whole API off, a single `'modelContext' in document` check answers only part of the question. Listing 15.2 is a small module that answers all of it and registers tools only where that is safe.

**Listing 15.2** `webmcp-support.js` — feature detection across WebMCP builds

```js
// webmcp-support.js: detect WebMCP without assuming which build you are on.
export function detectWebMCP(win = globalThis) {
  const doc = win.document;
  const mc = doc && 'modelContext' in doc ? doc.modelContext : null;
  const policy = doc?.permissionsPolicy ?? doc?.featurePolicy;
  const knowsTools = !!policy && policy.features().includes('tools');
  return {
    available: !!mc && typeof mc.registerTool === 'function',
    secureContext: !!win.isSecureContext,
    methods: mc
      ? ['registerTool', 'getTools', 'executeTool'].filter((m) => typeof mc[m] === 'function')
      : [],
    events: mc
      ? ['toolchange', 'toolactivated', 'toolcancel'].filter((e) => `on${e}` in mc)
      : [],
    // true or false when the browser knows the "tools" policy; null when it doesn't.
    policyAllows: knowsTools ? policy.allowsFeature('tools') : null,
    // A pre-May-2026 build exposed navigator.modelContext; see Appendix D.
    legacyNavigator: 'modelContext' in (win.navigator ?? {}),
  };
}

// Register tools only where the platform supports them; the page works either way.
export async function registerIfSupported(tools, { signal } = {}, win = globalThis) {
  const support = detectWebMCP(win);
  const registered = [];
  if (!support.available || support.policyAllows === false) return { registered, support };
  for (const tool of tools) {
    try {
      await win.document.modelContext.registerTool(tool, { signal });
      registered.push(tool.name);
    } catch (err) {
      console.warn(`WebMCP: "${tool.name}" was not registered (${err.name}: ${err.message})`);
    }
  }
  return { registered, support };
}
```

Each field maps to something in the draft. `modelContext` is a `[SecureContext]` attribute on `Document`, so it exists only on HTTPS pages and on localhost. The `ModelContext` interface declares the three methods and the three event handler attributes the module looks for. Access is gated by a policy-controlled feature named `"tools"`, whose default allowlist is `'self'`.[^ch15-19] And the spec recommends sending `Permissions-Policy: tools=()` from pages that should never register tools, so a page can find the API present and still be forbidden to use it.[^ch15-20]

The book’s demos repository runs Listing 15.2 in Chromium 156.0.8078.4 (the build Playwright caches, a little older than the current stable 156.0.8078.80) in three configurations. I re-ran all of them on 2 November 2026 with the same results as in October. With `--enable-features=WebMCPTesting`, the module reports all three methods, all three events and `policyAllows: true`, and the Trailhead `search_products` tool registers and shows up in `getTools()`. With the same flag plus a `Permissions-Policy: tools=()` header, the API is still present but `policyAllows` is `false`, and calling `registerTool()` anyway is rejected with a `NotAllowedError` whose message reads “Access to the feature “tools” is disallowed by permissions policy.” Without the flag, `document.modelContext` doesn’t exist, the policy doesn’t list a `"tools"` feature, and the page carries on without tools. In all three cases the page itself works, which is the whole point.

Two caveats. First, the module asks `document.permissionsPolicy` and falls back to `document.featurePolicy`, which is the object Chromium 156 answered on in these tests. Neither is available in every engine, so a `null` result means “unknown”, not “allowed”. Second, a polyfill (more on those later in this chapter) defines `document.modelContext` on purpose, and the module will report it as available. For your registration code that is the correct answer. It tells you nothing about which agent, if any, will call the tools.

## Firefox and WebKit, in their own words

Chapter 4 summarised both positions in a paragraph each. They deserve more than that. They are the clearest statements anyone outside Google and Microsoft has made about what WebMCP is for, and each one points to a different future for the API.

### Mozilla: neutral, and renegotiating

Dominic Farolino, one of the spec’s editors, asked Mozilla for a position on 28 May 2026. His request framed WebMCP as serving two use cases: built-in browser agents acting on a site, and in-page agents, “possibly in cross-origin iframes”, calling tools that another origin explicitly exposed.[^ch15-3] Mozilla’s reviewer, Benjamin VanderSloot, replied on 1 June, and his assessment reads like a checklist of what a browser vendor weighs.

He starts with the benefit. The API gives websites a way to declare dedicated “lanes” for automated interaction, and “with honest participants, the benefit is twofold”: agents get a clear signal of what actions are available, and developers no longer have to design one interface that serves both humans and automation.[^ch15-3] Then the risk: “in an adversarial setting there is a risk that sites will provide tools that do not match the experience of a user on the page,” whether to “tar pit automated browsers, provide prompt injection that is invisible to typical users, collect user data from the inputs of the tools, or otherwise manipulate a user’s browsing ‘agent’.” And a fair qualification: “it is not clear to what extent they are exacerbated by this API or if they are inherent to LLMs consuming content from and driving a browser.”[^ch15-3]

Two further points carry practical weight for you. The first is the name. “The name is misleading,” he writes, because developers “(reasonably) assume the MCP spec is involved in any way. There is no MCP here.” He suggests names like “Website Tool API” or “Agent Capability API”.[^ch15-3] Keep that in mind, because in October the TAG asked the same question (more on that below). The second is openness. “As of now, use of this mechanism is restricted to browser developer’s own products and in-page agents,” and opening it up means “adding WebExtension and WebDriver BiDi integrations.”[^ch15-3] In other words, an independent agent shipped as a browser extension has no standard way to call your tools today.

His conclusion: WebMCP “introduces a potentially valuable abstraction” but “opens a surface whose real-world dynamics leave too many open questions to wholeheartedly endorse,” so he proposed neutral, with a willingness “to come back to revisit it once there is more evidence of how it will be used by sites.” The label `position: neutral` was applied on 5 August 2026.[^ch15-3]

The story didn’t end there. Mozilla had filed a meta bug in February, “[meta] Implement a prototype WebMCP API”, and it is still open.[^ch15-21] In August, Jake Archibald opened issue #236 in the WebMCP repository, asking whether the feature should be repositioned “as a general way to call functions in other environments”: windows, workers and other origins, with exposure to “the browser” (and through it to WebDriver or an LLM) as just one more target.[^ch15-22] Back in the positions thread, Farolino asked whether Mozilla’s support depended on dropping the declarative API. Archibald answered that the declarative form “sounds like a reasonable idea” but shouldn’t come “instead of an imperative way to call functions between environments”. Martin Thomson added that #236 “is pretty significant here. As is naming. But this position is not really based on the declarative variant.”[^ch15-3]

The editors have been working through #236 ever since. They sketched handles such as `tool.call(…)` that could be passed across `postMessage()`, and on 22 September Johann Hofmann summarised the security requirements for that model, starting with the rule that cross-origin exposure “must be opt in on the side of the tool providing origin.”[^ch15-22] On 9 October Farolino told the TAG that the editors were “working closely with Mozilla” on these changes “to gain their support”, and asked the TAG to wait for “Mozilla’s refreshed standards position.”[^ch15-5] The issue was on the table at TPAC in Dublin (26–30 October). In a follow-up on 30 October, VanderSloot pointed out that a generic communication tool would need a different meaning for the permissions policy (“allowed to be rolled up into in my tool list” instead of “allowed to register a tool”), and Hofmann concluded: “I think we need to add a second permissions policy”, one for tools exposed to native agents and one for generic tools.[^ch15-22] Archibald disagreed. In his view it is mostly a naming change, and on the morning of 2 November he wrote that “we just need a single policy for the external tools to be exposed at the top level.”[^ch15-22] So the permissions policy is in play, and its final shape is not decided.

As of 2 November 2026, the refreshed position has not been posted, and the Mozilla issue hasn’t changed since August.[^ch15-3] So Mozilla’s neutral is not a resting state. It is a negotiation, and its likely price is an API that looks less like “tools for AI” and more like a general cross-origin function-call mechanism, with agents as one consumer among several. If that happens, the `"tools"` policy you send today may get a sibling.

### WebKit: opposed, and proposing a different process

WebKit’s position, posted on 3 June 2026 and labelled `position: oppose` on 11 June, rests on five arguments.[^ch15-4] Chapter 4 quoted the first two: tool descriptions move the brittleness “from the DOM into the tool descriptions”, and an agent acting for a user “is, in effect, assistive technology” that a site should not single out. The other three are just as important.

- *Unexamined risks.* WebKit calls WebMCP “a new cross-origin invocation path” whose interaction with the platform’s isolation model (COOP, COEP, site isolation) is unexamined, with “no consent or reversibility model for consequential actions”. It warns that a site could over-parameterise a tool so that a helpful agent fills it in from personal data “the user never gave that site”, a pipeline the comment links to cross-site tracking.[^ch15-4]
- *Not really MCP.* Because the spec “does not prescribe the format in which tools are exposed”, WebKit reads WebMCP as a general mechanism for a page to register typed, callable functions, which “belongs with the platform’s existing messaging and capability mechanisms (`postMessage` and similar), not a parallel one.”[^ch15-4] It is the same observation that led Mozilla to #236, with the opposite conclusion.
- *The wrong venue.* “The Machine Learning CG/WG venue is wrong for the work.” The gaps WebMCP identifies, WebKit argues, are in HTML and accessibility semantics, which belong to WHATWG and to the W3C’s ARIA and Accessible Platform Architectures groups.[^ch15-4]

The issue’s labels record the same objections as concerns about API design, duplication, internationalisation, portability, privacy, security, use cases and venue.[^ch15-4]

When Farolino asked follow-up questions, Marcos Cáceres replied on 17 June that WebKit would not answer them point by point, because each question assumed the rest of the approach was sound. Instead, WebKit set out “invariants that put users in control” (“an agent acting on a user’s behalf is assistive technology”, sites should not be told that a user relies on an agent, and the result “must not privilege those who have one”), followed by a seven-step path: set WebMCP aside, stand up “a new community group for agent-assisted user agents”, define the problem with “no solutions and no engineering, just use cases”, hold a W3C workshop (perhaps around TPAC 2026, it suggested), and only then route solutions to HTML, ARIA or elsewhere.[^ch15-4] The WebKit issue has been closed and quiet since that exchange in June.

For an adopter, the practical reading is simple. No WebKit implementation is coming for the API in its current form. Safari’s entry on the implementation-status page links to the position and to nothing else.[^ch15-15] And WebKit’s argument is not about details a few pull requests could fix. It questions whether a separate tool layer should exist at all.

## The TAG review

The TAG’s early review of the Community Group work was filed on 11 June 2026. Marcos Cáceres suggested expediting it, since a proposal to add WebMCP to a Working Group charter was already on the table, and W3C staff agreed.[^ch15-5] On 10 July the TAG labelled it “Progress: in progress” and set six focus areas as pending: API design, web architecture, security, privacy, accessibility and internationalisation. It also added the label that sums up the politics: “Missing: Multi-stakeholder support.”[^ch15-5] All of those labels were still in place on 2 November 2026.

The public thread shows where the argument settled during the summer. After a TAG breakout meeting in August, Farolino reported that the question that “keeps coming up over and over” was why WebMCP is shaped as an explicit capability layer rather than “more HTML semantics”. He asked that any negative resolution on those grounds come with evidence that semantics would be a sufficient alternative.[^ch15-5] Two adopters weighed in. Yoav Weiss, writing “as someone deploying WebMCP (under an Origin Trial in various Chromium browsers) to a large number of storefronts”, listed the Shopify storefront tools in use (browsing collections, managing orders, searching the catalogue, showing product variants, searching store policies) and said he didn’t “see a feasible declarative alternative to the imperative tools that agents can call.”[^ch15-5] A second commenter cited his company’s public benchmark, which reports UI actuation using about 5–10 times the tokens and cost per task, and running 4–5 times slower, than WebMCP. That figure is the vendor’s own claim, and I have not reproduced it.[^ch15-5] TAG members asked people not to read too much into draft notes, and Marcos Cáceres reminded participants that notes shared privately “do not represent the consensus of the TAG in any way, shape, or form.”[^ch15-5]

On 6 October the TAG said the review was “taking a bit longer than usual”, and on 9 October the editors asked it to hold its position until Mozilla’s refreshed position and TPAC.[^ch15-5]

### The early comment of 26 October

Then, on 26 October, the first day of TPAC, Christian Liebel posted the TAG’s “current thinking”. He opens with a very clear disclaimer: “**This is not a resolution comment, and it does not replace the review that we will continue working on.**” The review stays open, and the TAG says it will take Mozilla’s updated position and the TPAC discussions into account.[^ch15-5]

It is still the most detailed statement the TAG has made so far.

- *A Finding on agentic browsing.* Because WebMCP is linked to agentic browsing, which “has web architecture implications of its own (security, privacy, identity delegation)”, the TAG plans to publish a Finding on agentic browsing in general.
- *What WebMCP is good for.* Agentic browsing “can be slow, brittle, and consume excessive tokens”, and WebMCP addresses that “by providing a dynamic list of tools, bridging the gap between the unstructured, natural-language, non-deterministic world of LLMs and the structured, programmatic, deterministic world of web applications.”
- *A web for agents.* The TAG is concerned that WebMCP “creates an agent-only description of a page’s functionality that might be unreachable by human users or screen readers”, with the unintended consequence of a “web for agents” that humans can no longer use through the usual input methods.
- *Declarative first.* Some members worry that WebMCP removes the incentive to build semantically rich, accessible sites, and “ask to fully work out the declarative version before shipping the imperative one.”
- *Brittleness and language.* Success still depends on the model, the schema and the descriptions, and a small local model has to understand the language the descriptions are written in. Imperative tools “only carry the page’s overall language and direction information”, while declarative ones carry their own node’s language and direction.
- *JSON Schema.* Some members note that this would be (like the Prompt API) the first time a web platform API uses JSON Schema, and that the W3C has no existing relationship with the organisation that develops it.
- *The name.* “Is there time to rename the proposal to something like ‘Tools’?”

The TAG adds that it “hasn’t reached consensus on how each of these points affects WebMCP’s impact on the web’s architecture”, and closes with “while we see the value of WebMCP, we believe the points above will need more consideration as this proposal evolves.”[^ch15-5]

Two of those points matter most for a team shipping tools today. The first is the declarative one. If that view wins, the declarative API (removed from the spec in October, still in Chrome’s trial) moves back to the front of the queue, and forms you annotate today are a better long-term bet than they looked a month ago. Chapter 8 is worth a second read with that in mind. The second is the name. Mozilla asked for a rename in June, the TAG asks for one now, and the Agentic Web charter already calls the deliverable something else. The name may change on the way to a standard. Code that keeps every `document.modelContext` call in one module, as Listing 15.2 and Chapter 5’s helper do, will survive a rename with a one-file change.

> **Still in flux:** *The TAG’s conclusion.* There is no resolution yet. The early comment of 26 October 2026 is explicitly not one, and the review continues.[^ch15-5] *Mozilla’s position.* It is being renegotiated around issue #236, and a change could affect the TAG’s “Missing: Multi-stakeholder support” label.[^ch15-22][^ch15-5] *WebKit’s position.* It is `oppose`, and the issue is closed.[^ch15-4]

## Who consumes WebMCP today

Exposing tools is only half of the system. Something has to call them. The project’s implementation-status page is the only list of consumers in one place, and it is the project’s own claim, not each vendor’s.[^ch15-15] The page hasn’t changed since mid-October, and on 2 November 2026 it lists:

- *Chrome:* the origin trial, live from Chrome 149. The trial describes itself as letting websites “register tools for use by agents hosted by the site or in Chrome.”[^ch15-15][^ch15-10]
- *Edge:* the origin trial, live in Edge 150.[^ch15-15]
- *Brave:* “Experimental support is added to Leo AI chat.”[^ch15-15] The Brave issue behind it was closed on 7 July 2026, then reopened twice, most recently on 7 October, and it is still open on 2 November. On 1 October a Brave engineer wrote that the feature is “flagged on in Nightly at the moment”. The issue’s test plan turns on `brave://flags/#enable-webmcp-testing` and expects a “tools pill” in Leo’s sidebar when a page offers tools.[^ch15-23]
- *ChatGPT Desktop:* “WebMCP is supported in ChatGPT Desktop.”[^ch15-15] OpenAI’s earlier agentic browser, ChatGPT Atlas, is gone. OpenAI announced its retirement on 9 July 2026, alongside a desktop app with its own built-in browser, and its help centre says that “ChatGPT Atlas has been retired and no longer receives updates.”[^ch15-24]
- *Meta Ray-Ban Display:* support for web apps is announced but not available yet. It will let Meta AI on the glasses call tools registered with `document.modelContext.registerTool()`. It is off by default and enabled per device.[^ch15-15]
- *Firefox and Safari:* links to their positions, plus Mozilla’s Bugzilla meta bug.[^ch15-15]

Then there are extensions. chromestatus notes that the Chrome Web Store “features about 9 different extensions with WebMCP on their title and 4* or more ratings”.[^ch15-10] MCP-B’s Rook is one such agent extension.[^ch15-25] Mozilla’s point still applies: there is no standard extension or WebDriver API for calling page tools yet, so each of these depends on Chromium-specific plumbing.[^ch15-3] That gap is now written into the draft Agentic Web charter, which says the group’s specifications may include extensions to WebDriver and WebDriver BiDi “to let automation clients, including agents that drive a browser through WebDriver BiDi, use those features, subject to the same permission and consent requirements as other agents.”[^ch15-8]

On the other side of the wire, the site side, the biggest public number comes from Shopify. On 26 October, in the charter discussion, Ilya Grigorik wrote that “Shopify deploys WebMCP across millions of storefronts”, and asked the charter to cover “attribution of agent-originated interaction to the page it acts on”.[^ch15-7] That is a deployment claim by the deployer, and I have no independent count to put next to it.

For planning, my order of confidence is: Chromium browsers with the trial (you can verify that today with a token), Brave behind a flag, then vendors whose support is stated only on the status page. Test against what you can run, and treat the rest as upside.

## Community libraries

Long before the browsers, the community had built WebMCP-shaped libraries. Chapter 4 described MCP-B’s role in the API’s history, and its packages are still the most widely used way to try WebMCP outside a Chromium trial. All three main packages were at version 6.0.3 on 2 November 2026, published on 14 October, under the MIT licence. There has been no release since.[^ch15-26]

| Package | Description (from the npm registry) |
|---|---|
| `@mcp-b/global` | “W3C Web Model Context Protocol (WebMCP) API polyfill. Let AI agents like Claude, ChatGPT, and Gemini interact with your website via document.modelCont[ext]...” |
| `@mcp-b/webmcp-polyfill` | “Vendored upstream WebMCP polyfill plus temporary declarative tools” |
| `usewebmcp` | “Standalone React hooks for strict core WebMCP tool registration with document.modelContext” |
| `use-webmcp-tool` | “React hook for registering WebMCP tools (document.modelContext) with lifecycle-managed registration and MCP result normalization.” |

The last row is new in this edition. On 16 October, Chrome’s Imperative API page switched its React recommendation from `usewebmcp` to `use-webmcp-tool`, a package from GoogleChromeLabs (version 0.3.0, Apache-2.0 licence), and added a Vue option, the `useWebMCP` composable in `@vueuse/core`.[^ch15-27][^ch15-28] Chapter 10 covers the framework options in detail.

The MCP-B documentation site registers a live tool with `document.modelContext.registerTool()` on its own home page and suggests calling it through “the Rook extension or Chrome’s native WebMCP support.”[^ch15-25] The packages live in the `WebMCP-org/npm-packages` repository, which describes them as “Transport layers, React hooks, and browser tools for the Model Context Protocol”.[^ch15-29]

Three cautions apply to any library that tracks a moving draft.

1. *A polyfill is a second implementation with its own schedule.* When the spec dropped the declarative API on 8 October, the polyfill kept “temporary declarative tools”.[^ch15-9][^ch15-26] That is a reasonable choice for users, but it means the polyfill and the draft can disagree.
2. *Version numbers move as fast as the spec, and recommendations move too.* All three MCP-B packages were republished on 14 October 2026, and two days later Chrome’s documentation pointed React developers somewhere else. Pin exact versions, and read the changelog before you upgrade.
3. *A polyfill cannot create consumers.* It gives your page a `document.modelContext` to register on. Calls still need an agent that knows how to reach it, such as a matching extension. The detection code in Listing 15.2 can’t tell native support from a polyfill, and for registration purposes it doesn’t need to.

## From Community Group to Working Group

### What a Working Group would change

The W3C’s rule is short: “Community Groups are for incubation. The Recommendation Track is for standardization.” A technology that gains traction in a CG normally moves to a Working Group (WG) to become a standard, and the CG agreements are written so that participants’ patent commitments carry over.[^ch15-1] For adopters, three things change when a WG takes over a specification.

- *Patent commitments.* The W3C designed its CG agreements for “continuity of IPR commitments” when a Working Group adopts a CG specification, so the move itself is meant to be smooth.[^ch15-1] A WG brings the W3C Patent Policy with it, and the draft charter discussed below has a Patent Policy section.[^ch15-8]
- *Horizontal review.* The draft Agentic Web WG charter requires review for accessibility, internationalisation, privacy and security, and by the TAG, “during each major standards-track document transition”.[^ch15-8]
- *Interoperability as a bar.* To advance beyond Candidate Recommendation, the draft charter expects “at least two independent interoperable implementations of every feature defined in the specification, where interoperability can be verified by passing open test suites.”[^ch15-8] The WebMCP draft already links a test suite on wpt.fyi from its header.[^ch15-2] Today, every implementation of WebMCP is built on Chromium.

That last point is the political core of this chapter — and the least discussed one. Two Chromium-based browsers are not two independent implementations, and the two engines that are independent of Chromium are neutral and opposed. A Working Group would not make WebMCP a standard by itself. It would set a bar that, as of November 2026, nobody has a plan to meet.

### What happened in 2026

The question of a WG came up within a day of the positions being requested. On 28 May 2026, the WebKit engineer who would post WebKit’s position a week later opened issue #192, noting that “Community Groups do not create W3C standards” and asking whether WebMCP should move to the WG.[^ch15-30] W3C staff supported an early rechartering of the Web Machine Learning WG to take it in, and on 9 June a pull request proposed adding WebMCP to that group’s charter “as a tentative deliverable.”[^ch15-6][^ch15-30] The WebML WG is chartered until 30 April 2027.[^ch15-31]

That route ran into trouble almost immediately. WebKit’s position, published the same month, called the machine-learning venue wrong for the work.[^ch15-4] On 18 June the author of #192 clarified that they had proposed discussing the move, not supporting it: “We think WebML WG is the incorrect working group, but WebMCP should be part of some working group.”[^ch15-30] On 13 August the WG recorded a resolution that it “has reviewed the charter proposal and approves the direction. WebKit position duly noted.” Marcos Cáceres replied that it was “baffling how you can record a resolution when a member of the working group has objected,” and Apple disputed the minutes the next day.[^ch15-30] The same day, on the charter pull request, Cáceres recorded “that Apple is opposed to this going working group. Expect a formal objection if this is merged.” He added: “We’d be open to discussing a different venue at the W3C and doing this properly from first principles (i.e., some new agentic web CG/WG).”[^ch15-6]

A formal objection is more than a strong comment. Under the W3C Process, Formal Objections “receive formal consideration and a formal response”, and if the Team cannot resolve one through investigation and mediation, it goes to the W3C Council.[^ch15-32] Any charter that names WebMCP and draws an objection from Apple faces that procedure.

On 28 September W3C staff changed course. The “latest thinking,” wrote Philippe le Hégaret, the W3C’s Chartering Facilitator,[^ch15-33] on the charter pull request, “is to have a working group dedicated to develop specifications that facilitate web pages and applications to be leveraged by LLMs and AI agents,” while the WebML WG would “stay focused on developing APIs for enabling efficient machine learning inference in the browser.”[^ch15-6] The same day a charter proposal for an Agentic Web Working Group appeared, stated to “replace the previous thinking”, and on 13 October the WebML pull request was closed.[^ch15-7][^ch15-6]

### The Agentic Web Working Group charter

The draft charter’s mission is “to develop specifications that facilitate web pages and applications to be leveraged by LLMs and AI agents.” Its scope covers how sites describe their capabilities and context to agents, agent identity and delegation, transparency about agent interactions, “expressing permissions, policies, and constraints on agent actions”, “attribution of agent-originated interaction to the page it acts on”, measuring the performance and outcomes of agent interactions, testing support such as WebDriver extensions, a threat model, and guidance for web authors. It explicitly leaves out model APIs, cryptographic authentication primitives, crawler controls, agent-to-server communications, content provenance and bot detection.[^ch15-8]

The biggest change since the first edition is in the deliverables. Until 29 October, the one named normative deliverable was WebMCP itself. On that day a pull request by Yoav Weiss was merged that “generalizes the WebMCP deliverable to cover the problem space”.[^ch15-34] The normative deliverable is now called *Site Capabilities for Agents*. It “defines how web pages and applications can describe the functionality they offer, and relevant context, in a structured form that agents acting on behalf of users can discover and use reliably”, it covers “both imperative descriptions, provided through script, and declarative ones, provided through markup”, and it names, among other things, tools with “input and output schemas”, hints such as whether an action is “read-only, consequential, or requires explicit user acknowledgement”, “skills scoped to the page”, agents in the browser, in extensions, in the page and in cross-origin frames, and “keeping users informed and in control”. Its last line reads: “The initial input for this deliverable is the WebMCP specification.”[^ch15-8]

The same pull request added tentative deliverables for *Agent Identity*, *Agent Delegation* and *Agent Interaction Measurement* (APIs that let sites measure “the timing and status of invocations of site capabilities”), a non-normative document on *Interaction Modes*, and kept the *Agentic Web Threat Model* as a Group Note.[^ch15-8][^ch15-34]

If the charter is approved as drafted, the Working Group would not be standardising “WebMCP” but a broader thing that starts from WebMCP. Output schemas, skills and user acknowledgement are in its scope although none of them is in the current spec (output schemas are an open pull request). Read together with the TAG’s rename question and its push for the declarative form, the direction is quite consistent: the core idea of named, described, schema-typed tools looks safe, while the name, the exact shape and the balance between imperative and declarative are open.

It is still very much a draft. On 2 November 2026 the chairs, dates and team contact were template placeholders, and the deliverables section still carried both template options for whether the group intends to stop at Candidate Recommendation or go on to Recommendation.[^ch15-8] The W3C announced the start of charter refinement on 1 October and estimated that it “will last until approximately 10 November 2026.”[^ch15-33] The Process Document requires that phase to last at least 28 days, and an Advisory Committee review follows it.[^ch15-32] The strategy issue lists the TAG review, the accessibility considerations and a threat model among its “known or potential areas of concern”.[^ch15-7]

During TPAC week the strategy issue collected support and wishes. Shopify asked for attribution of agent-originated interaction. Others asked for WebDriver BiDi and headless use, agent identification and browser-mediated payments. Comments from Google and Microsoft participants welcomed the generalised deliverables, and one from Google asked the group to coordinate with OAuth and other identity work instead of duplicating it.[^ch15-7] Apple had not commented on the strategy issue as of 2 November 2026. Whether WebKit would accept this group as the “new agentic web CG/WG” Apple said it was open to, and WebMCP as the initial input rather than a proposal to set aside, is not on the public record. Farolino’s answer to WebKit’s call for a new group, back in August, was: “I have no objection to moving WebMCP exactly as-is to such a WG.”[^ch15-30]

### The paths, and what each means for you

Figure 15.2 lays out the routes as they look on 2 November 2026.

![Figure 15.2 — From Community Group draft to standard: the WebML WG route (closed in October 2026), the Agentic Web WG route (charter in refinement, WebMCP as initial input to “Site Capabilities for Agents”) and continued incubation, with what each means for your code.](images/figure-15-2.png)

- *The Agentic Web WG charters with this scope.* The work moves to the Recommendation Track with patent commitments and horizontal review, under a broader deliverable that starts from WebMCP. Expect a stream of changes from TAG and accessibility review (the declarative form, language and direction, perhaps the name), and expect the interoperability bar to keep the result at Candidate Recommendation or below until a second engine implements it. For your code, nothing changes on charter day. Changes come later, through review.
- *The charter is delayed, or WebMCP is taken out of it.* WebMCP stays a CG report. Chromium-based browsers can keep running trials or ship it, but it would remain a Chromium-only feature with no standards-track commitments.
- *The API is reshaped before either happens.* If #236 succeeds, the core becomes a general cross-environment function-call mechanism, agents become one consumer, and a second permissions policy may appear.[^ch15-22] Mozilla might move off neutral, while WebKit’s objection to a separate agent-facing layer would remain.[^ch15-3][^ch15-4] Your tools would survive as functions with names, descriptions and schemas, but registration and invocation code would change.

None of these paths changes the advice from Chapter 4. Build tools as thin wrappers over logic your interface already uses, feature-detect at run time, and treat WebMCP as a progressive enhancement. Then following a breaking change costs you a few lines in one module.

> **Still in flux:** *Charter refinement.* It is expected to end around 10 November 2026, and extensions are announced on the strategy issue.[^ch15-33][^ch15-7] *Apple’s response to the new charter.* Apple threatened a formal objection to the WebML route. Its view of the Agentic Web WG draft is not on the public record as of 2 November 2026.[^ch15-6][^ch15-7] *Recommendation or not.* The draft charter has not yet chosen whether the group will aim for full Recommendation.[^ch15-8]

## Keeping this chapter current yourself

Every fact in this chapter has a date on it, and several will have changed by the time you read this. The responsible way to rely on any of them is to re-check them on a schedule. Listing 15.3 does that for you. It reads eight primary sources, extracts one status from each, saves a snapshot and reports what changed since the last run.

**Listing 15.3** `standards-watch.mjs` — a standards watcher

```js
// standards-watch.mjs: snapshot WebMCP's standards status and report what changed.
// Usage: node standards-watch.mjs [snapshots/last.json]
import { readFile, writeFile } from 'node:fs/promises';

const SOURCES = {
  spec: 'https://webmachinelearning.github.io/webmcp/',
  commits: 'https://github.com/webmachinelearning/webmcp/commits/main.atom',
  chromestatus: 'https://chromestatus.com/api/v0/features/5117755740913664',
  edgeTrial: 'https://developer.microsoft.com/en-us/microsoft-edge/origin-trials/trials/0b76fe60-b266-458e-a285-04e375c0c31a',
  mozilla: 'https://github.com/mozilla/standards-positions/issues/1412',
  webkit: 'https://github.com/WebKit/standards-positions/issues/670',
  tag: 'https://github.com/w3ctag/design-reviews/issues/1238',
  charter: 'https://github.com/w3c/strategy/issues/576',
};

export const parse = {
  spec: (html) => html.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ')
    .match(/(Draft Community Group Report|Final Community Group Report|Working Draft|Editor['’]s Draft)\s*,?\s*(\d{1,2} \w+ \d{4})/)
    ?.slice(1, 3).join(', ') ?? null,
  commits: (xml) => {
    const entry = xml.match(/<entry>[\s\S]*?<\/entry>/)?.[0] ?? '';
    const title = entry.match(/<title>\s*([\s\S]*?)\s*<\/title>/)?.[1]?.replace(/&#39;/g, "'");
    const updated = entry.match(/<updated>([^<]+)<\/updated>/)?.[1];
    return title ? `${updated} ${title}` : null;
  },
  chromestatus: (text) => {
    const feature = JSON.parse(text.replace(/^\)\]\}'\s*/, ''));
    const trial = feature.stages.find((s) => s.stage_type === 150); // origin trial stage
    if (!trial) return null;
    const lasts = [trial.desktop_last, ...trial.extensions.map((e) => e.desktop_last)];
    return { trialFrom: trial.desktop_first, trialThrough: Math.max(...lasts.filter(Boolean)) };
  },
  edgeTrial: (html) => html.match(/Trial Expiration Date<\/strong>\s*<p>([^<]+)<\/p>/)?.[1] ?? null,
  // Current labels only: the issue's "labels" block, not label events in its timeline.
  labels: (prefixes) => (html) => {
    const block = html.match(/"labels":\{"pageInfo":[\s\S]*?\]\}/)?.[0] ?? '';
    return [...block.matchAll(/"name":"([^"]+)"/g)].map((m) => m[1])
      .filter((name) => prefixes.some((p) => name.startsWith(p))).sort();
  },
};
const PARSERS = {
  spec: parse.spec, commits: parse.commits, chromestatus: parse.chromestatus,
  edgeTrial: parse.edgeTrial,
  mozilla: parse.labels(['position:']), webkit: parse.labels(['position:']),
  tag: parse.labels(['Progress:', 'Missing:', 'Resolution:']),
  charter: parse.labels(['In Charter', 'AC review', 'Council']),
};

async function fetchText(url) {
  const res = await fetch(url, {
    headers: { 'user-agent': 'webmcp-standards-watch/1.0' },
    signal: AbortSignal.timeout(30_000),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.text();
}

export async function snapshot() {
  const entries = await Promise.all(Object.entries(SOURCES).map(async ([key, url]) => {
    try { return [key, PARSERS[key](await fetchText(url))]; }
    catch (err) { return [key, { error: err.message }]; }
  }));
  return { checkedAt: new Date().toISOString(), ...Object.fromEntries(entries) };
}

export function diff(before, after) {
  return Object.keys(SOURCES)
    .filter((k) => JSON.stringify(before?.[k]) !== JSON.stringify(after[k]))
    .map((k) => ({ source: k, before: before?.[k] ?? null, after: after[k] }));
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const file = process.argv[2] ?? 'snapshots/last.json';
  const before = await readFile(file, 'utf8').then(JSON.parse).catch(() => null);
  const after = await snapshot();
  const changes = diff(before, after);
  console.log(JSON.stringify(after, null, 2));
  for (const c of changes) console.log(`CHANGED ${c.source}: ${JSON.stringify(c.before)} -> ${JSON.stringify(c.after)}`);
  await writeFile(file, JSON.stringify(after, null, 2) + '\n');
  process.exitCode = before && changes.length ? 2 : 0;
}
```

A few design choices are worth explaining. The script reads GitHub issue pages instead of the GitHub REST API, because unauthenticated API calls are rate-limited, and a weekly job shared by a team hits that limit quickly. It takes only the issue’s current labels block, not the label events in the timeline, so a label that was added and later removed doesn’t show up as current. The test suite has a case for exactly that, built on the TAG’s since-removed “Progress: untriaged” label. Each source fails independently: a page that times out becomes an `{ error }` entry instead of a crash. And the exit code is `2` when something changed, so a CI job can open an issue or send a message.

The eighth source, `charter`, is new in this edition. It reads the labels of the W3C strategy issue for the Agentic Web WG, so you learn when the charter leaves refinement, goes to the Advisory Committee or ends up in front of the Council.

Here is the snapshot it produced while I re-checked this chapter:

**Listing 15.4** `snapshots/2026-11-02.json` — the watcher’s snapshot on 2 November 2026

```json
{
  "checkedAt": "2026-11-02T09:00:12.857Z",
  "spec": "Draft Community Group Report, 27 October 2026",
  "commits": "2026-10-27T11:41:32Z Document cross-origin tool exposure and two-sided opt-in in Section 6…",
  "chromestatus": {
    "trialFrom": 149,
    "trialThrough": 162
  },
  "edgeTrial": "March 30, 2027",
  "mozilla": [
    "position: neutral"
  ],
  "webkit": [
    "position: oppose"
  ],
  "tag": [
    "Missing: Multi-stakeholder support",
    "Progress: in progress"
  ],
  "charter": [
    "In Charter Refinement"
  ]
}
```

(The “…” at the end of the commit title is GitHub’s: its Atom feed shortens long titles.)

Compare it with the first edition’s snapshot from 15 October, which is still in the repository as `snapshots/2026-10-15.json`, and you get a useful lesson. Only two fields changed: the spec date and the newest commit. Everything else, from the trial range to the three sets of labels, is the same. And yet these were the busiest two weeks the standards road has seen so far — the TAG’s early comment, TPAC, the second-permissions-policy idea, the charter’s new deliverable. None of that changed a single label.

Labels record verdicts, not conversations. The watcher is good at telling you *that* something was decided. It is useless for telling you what is being discussed. So run it weekly, and once a month read the threads it points to: the TAG review, #236, the strategy issue and the newest commits. The fields that matter most for planning are `chromestatus.trialThrough` (renew your tokens before it passes), `edgeTrial`, `charter`, and any change to the `mozilla`, `webkit` and `tag` labels. A spec date change on its own is routine, so read the commit titles it points to.

## What this means for your product

- *Plan for Chromium only, and design for everyone.* Today’s reachable audience for WebMCP is users of Chromium-based browsers on sites that carry trial tokens, plus agents that consume tools through Chromium. Your site must work fully without tools in every other browser, and progressive enhancement gives you that for free.
- *Put the trial on someone’s calendar.* Chrome’s trial runs through Chrome 162 (scheduled for stable on 2 February 2027), Edge’s through 30 March 2027, and an extension means new tokens. Assign an owner for registration, renewal and the token in your deployment configuration.
- *Budget for churn, and for a rename.* Table 15.1 lists ten behaviour-changing spec changes in 2026. Two open pull requests would still change the IDL: `requestUserInput()` (#204) and `openWorldHint` (#355). Pull request #375 is an explainer, not an IDL change (Appendix F). The name itself is now questioned by Mozilla, the TAG and the draft charter. Keep WebMCP code in one module, pin library versions, and run the Chapter 14 tests against each new Chromium release.
- *Don’t neglect the declarative API.* The TAG comment and the charter both treat declarative descriptions as first-class. Annotated forms (Chapter 8) are cheap to add next to imperative tools and are the part most aligned with where the review is pushing.
- *Treat standards politics as a risk, not a verdict.* Neutral can become positive if the API is reshaped, and a Working Group would add review and stability. Opposition from WebKit means no Safari support for this design. Neither changes whether well-designed tools help your users in browsers that have them.
- *Feed the process.* Google’s trial asks for feedback on the API shape, and the review threads show that deployment data carries weight: Shopify’s storefront tools were cited in the TAG review and again in the charter discussion.[^ch15-13][^ch15-5][^ch15-7] Real usage from your product is the most persuasive input you can give.

## Chapter summary

- WebMCP is a Draft Community Group Report (23 November 2026, four editors from Microsoft and Google) of the W3C Web Machine Learning CG. It is not a W3C standard and not on the Standards Track. Community Groups incubate, and only a Working Group can standardise.
- Chrome’s origin trial runs from Chrome 149, originally through 156 and since 28 September 2026 extended through 162 (stable on 2 February 2027). Edge’s trial runs in Edge 150 until 30 March 2027. Both accept third-party tokens. Tokens go in a meta tag, an HTTP header or, for third parties, an external script, and an extension means renewing them. Chrome 156, the build this book tests against, has been stable since 20 October 2026.
- Trials exist to change APIs. In 2026 the spec removed `provideContext()`, moved `modelContext` to `Document`, made `registerTool()` return a promise, removed the declarative API and changed its error types. From 15 October to 2 November the IDL did not change. On 2 November #254 added optional `outputSchema`, and on 19 November #348 replaced `RegisteredTool` with `Tool`. `requestUserInput()` (#204) and `openWorldHint` (#355) were still open on 23 November 2026. Chromium is expected to change how it serializes string and `undefined` results.
- Feature detection should cover the secure context, the methods and events, the `"tools"` permissions policy and the old `navigator` surface. In Chromium 156, a page under `Permissions-Policy: tools=()` still sees the API, but calls are rejected with `NotAllowedError`.
- Mozilla is neutral: tools are useful “lanes”, but adversarial sites, a misleading name and a closed set of consumers leave “too many open questions”. It is renegotiating around a more general cross-environment function-call API (#236), where the post-TPAC discussion is about the permissions policy (a second one, or a renamed single one). The refreshed position is not published yet.
- WebKit is opposed: agents are assistive technology and should not be singled out, the tool layer duplicates HTML and ARIA, the risks are unexamined and the venue is wrong. It proposes starting over in a new group, from use cases.
- The TAG review, open since June 2026, is labelled “Missing: Multi-stakeholder support”. Its early, non-resolution comment of 26 October 2026 plans a Finding on agentic browsing, raises a “web for agents” risk, asks some to finish the declarative version first, flags JSON Schema and language handling, and asks about renaming the proposal to something like “Tools”.
- Consumers listed today: the Chrome and Edge trials, Brave Leo (experimental), ChatGPT Desktop (per the project’s status page, while ChatGPT Atlas was retired) and Meta Ray-Ban Display (announced, not yet available), plus Chromium extensions. Community packages (`@mcp-b/global`, `@mcp-b/webmcp-polyfill`, `usewebmcp`, all at 6.0.3) track the draft on their own schedule, and Chrome’s docs now point React developers to `use-webmcp-tool`.
- A move into the WebML Working Group was dropped after Apple warned of a formal objection. The draft Agentic Web Working Group charter, in refinement until about 10 November 2026, now has “Site Capabilities for Agents” as its normative deliverable, with WebMCP as the initial input, plus tentative work on agent identity, delegation and measurement. Standardisation would still require two independent interoperable implementations.
- Re-check status on a schedule. Listing 15.3 snapshots eight primary sources and flags changes, but labels record verdicts, not conversations, so read the threads too.

Chapter 16 turns from the platform to the business: which journeys to expose first, how to keep the agent a guest on your site, and how to measure what agent-driven traffic is worth.

## Notes

[^ch15-1]: W3C, “Community and Business Groups: Frequently Asked Questions”, including “Are Community and Business Group reports W3C standards?”. <https://www.w3.org/community/about/faq/>
[^ch15-2]: WebMCP specification, Draft Community Group Report, 23 November 2026, header (four editors: Brandon Walderman and Samuel Dallstream of Microsoft, Khushal Sagar and Dominic Farolino of Google), test suite link and “Status of this document” (retrieved 23 November 2026). The same header read 27 October 2026 when Listing 15.4 was taken. <https://webmachinelearning.github.io/webmcp/>
[^ch15-3]: mozilla/standards-positions issue #1412, “WebMCP”: request (28 May 2026), Benjamin VanderSloot’s assessment (1 June 2026, GitHub account `bvandersloot-mozilla`, which GitHub links to commits authored as Benjamin VanderSloot (bvandersloot@mozilla.com)), label “position: neutral” (5 August 2026) and the exchange of 24–26 August 2026. The issue was closed, with no activity after 26 August 2026, when re-checked on 2 November 2026. <https://github.com/mozilla/standards-positions/issues/1412>
[^ch15-4]: WebKit/standards-positions issue #670, “WebMCP”: WebKit’s position comment (3 June 2026), label “position: oppose” (11 June 2026), concern and topic labels, and the follow-up of 17 June 2026 (no activity after 17 June 2026 when re-checked on 2 November 2026). <https://github.com/WebKit/standards-positions/issues/670>
[^ch15-5]: w3ctag/design-reviews issue #1238, “Incubation: WebMCP”: filed 11 June 2026, labels applied 10 July 2026 (unchanged on 2 November 2026), comments of 6, 18, 19 and 20 August and 6 and 9 October 2026, and Christian Liebel’s early, non-resolution comment of 26 October 2026. <https://github.com/w3ctag/design-reviews/issues/1238> and <https://github.com/w3ctag/design-reviews/issues/1238#issuecomment-6410471845>
[^ch15-6]: w3c/charter-drafts pull request #829, “[wg/webmachinelearning] Adds WebMCP in scope” (opened 9 June 2026, Apple’s comment of 13 August 2026, closed 13 October 2026). <https://github.com/w3c/charter-drafts/pull/829>
[^ch15-7]: w3c/strategy issue #576, “[wg/agenticweb] Agentic Web Group Charter” (opened 28 September 2026, label “In Charter Refinement” since 1 October 2026), including the comments of 26–29 October 2026 (Ilya Grigorik on Shopify and attribution, 26 October). Thirteen comments, none from an Apple participant, when re-checked on 2 November 2026. <https://github.com/w3c/strategy/issues/576>
[^ch15-8]: W3C, “Agentic Web Working Group Charter” (DRAFT, retrieved 2 November 2026), including Mission, Scope, Out of Scope, Deliverables (“Site Capabilities for Agents”, the tentative deliverables and “Agentic Web Threat Model”), Success Criteria and Patent Policy. <https://w3c.github.io/charter-drafts/2026/agenticweb-wg.html>
[^ch15-9]: Commit history of webmachinelearning/webmcp, branch `main`, read on 15 October and again on 2 November 2026. The commits named in Table 15.1 are fe84c67 (#132, 5 March 2026), c7b5c70 (#184, 27 May 2026), ec37ec4 (#200, 8 June 2026), d29b8d7 (#225, 21 July 2026), a724ab1 (#246, 17 August 2026), d61d0e6 (#330, 30 September 2026), 14ae813 (#338, 8 October 2026) and b206dae (#339, 8 October 2026). Commits after the first edition: 1636b33 (#345), 3279798 (#347, committed 14 October 2026 at 21:00 UTC−3, which is 15 October in UTC), cb3d169 (#352, 20 October), 51ed756 (#334, 20 October) and 6838130 (#326, 27 October 2026). <https://github.com/webmachinelearning/webmcp/commits/main>
[^ch15-10]: chromestatus.com, “WebMCP” (feature 5117755740913664), read through its JSON API on 15 October and 2 November 2026: origin-trial stage (Chrome 149 to 156, third-party support, use counter `kModelContextRegisterTool`), extension stage created 28 September 2026 (through Chrome 162, with the stated reason), developer-trial stage (Chrome 146), standards maturity “Incubation” and browser signals. Entry last updated 28 September 2026. <https://chromestatus.com/feature/5117755740913664>
[^ch15-11]: Chrome for Developers, “Get started with origin trials” (last updated 7 November 2024, retrieved November 2026): tokens in a meta tag, an HTTP header or script, third-party tokens, multiple tokens per page, renewal when a trial is extended, “Chrome ignores invalid or expired tokens.” <https://developer.chrome.com/docs/web-platform/origin-trials>
[^ch15-12]: Microsoft Edge Origin Trials, “WebMCP” trial page: description, “Trial Expiration Date: March 30, 2027” (unchanged on 2 November 2026), registration, and the trial record (`supportsThirdParty: true`, `edgeOnly: false`). <https://developer.microsoft.com/en-us/microsoft-edge/origin-trials/trials/0b76fe60-b266-458e-a285-04e375c0c31a>
[^ch15-13]: Chrome for Developers, “Join the WebMCP origin trial” (Alexandra Klepper, published 9 June 2026). <https://developer.chrome.com/blog/ai-webmcp-origin-trial>
[^ch15-14]: Chromium Dash, release schedule and current releases, read on 2 November 2026: Chrome 156 stable on 20 October 2026 (Stable channel 156.0.8078.80), Chrome 157 stable on 3 November 2026, Chrome 162 stable on 2 February 2027. <https://chromiumdash.appspot.com/schedule>
[^ch15-15]: webmachinelearning/webmcp, “Browser and Agent Implementation Status” (implementation-status.md), unchanged between 15 October and 2 November 2026. <https://github.com/webmachinelearning/webmcp/blob/main/implementation-status.md>
[^ch15-16]: Chrome for Developers, “WebMCP” (published 18 May 2026, updated 7 October 2026, retrieved November 2026): “Get started”, “Local WebMCP” and “Use WebMCP APIs”. <https://developer.chrome.com/docs/ai/webmcp>
[^ch15-17]: webmachinelearning/webmcp pull requests #347 “Handle re-registration during input serialization” (merged 15 October 2026 UTC), #352 (fourth editor, merged 20 October 2026), #334 “Discuss general agent ecosystem risks and link to agent security guidance” (merged 20 October 2026), #326 “Document cross-origin tool exposure and two-sided opt-in in Section 6.3.4” (merged 27 October 2026), #254 “Add `outputSchema` to `ModelContextTool` and `RegisteredTool`” (merged 2 November 2026) and #348 “Introduce the `Tool` interface” (merged 19 November 2026). Still open on 23 November 2026, and not part of #348: #204 “Replace requestUserInteraction with requestUserInput” and #355 “Clarify annotation defaults and add openWorldHint”. <https://github.com/webmachinelearning/webmcp/pulls>
[^ch15-18]: webmachinelearning/webmcp issue #361 (opened 23 October 2026) on result serialization in Chrome and in the web-platform-tests, with François Beaufort’s reply of 26 October 2026. <https://github.com/webmachinelearning/webmcp/issues/361>
[^ch15-19]: WebMCP specification, Draft Community Group Report, 27 October 2026, §4.1 (the `[SecureContext]` `modelContext` attribute on `Document`), §4.2 (`ModelContext` IDL) and §4.4 “Permissions policy integration”. <https://webmachinelearning.github.io/webmcp/#api>
[^ch15-20]: WebMCP specification, Draft Community Group Report, 27 October 2026, §6.4.1 “Disabling WebMCP with Permissions Policy” (the `Permissions-Policy: tools=()` mitigation). <https://webmachinelearning.github.io/webmcp/>
[^ch15-21]: Bugzilla bug 2018306, “[meta] Implement a prototype WebMCP API” (Core :: Machine Learning: General, filed 20 February 2026, status NEW on 2 November 2026), read through the Bugzilla REST API. <https://bugzilla.mozilla.org/show_bug.cgi?id=2018306>
[^ch15-22]: webmachinelearning/webmcp issue #236, “Reposition feature as a generic communication tool?” (opened 3 August 2026 by Jake Archibald), including comments of 26–27 August and 22–24 September 2026, and the post-TPAC exchange of 30 October to 2 November 2026 between Benjamin VanderSloot, Johann Hofmann and Jake Archibald on a second permissions policy (Archibald’s comment of 2 November 2026, 10:10 UTC, was the latest when re-checked). <https://github.com/webmachinelearning/webmcp/issues/236>
[^ch15-23]: brave/brave-browser issue #55232, “[AI Chat]: Add support for the WebMCP protocol to Leo” (opened 5 May 2026, closed 7 July 2026, reopened 27 August, closed 1 October, reopened 7 October, open on 2 November 2026), including its test plan and the comment of 1 October 2026. Event dates read through the GitHub REST API. <https://github.com/brave/brave-browser/issues/55232>
[^ch15-24]: OpenAI Help Center, “ChatGPT Atlas retirement”, read on 15 October 2026 (the page refuses direct automated requests, so it was read through a text-rendering proxy): “ChatGPT Atlas has been retired and no longer receives updates.” Michael Kan, “OpenAI to Retire ChatGPT Atlas Browser Less Than a Year After Launch”, PCMag, 9 July 2026, for the announcement and the targeted deprecation date of 9 August 2026. <https://help.openai.com/en/articles/20001371-chatgpt-atlas-retirement> and <https://www.pcmag.com/news/openai-to-retire-chatgpt-atlas-browser-less-than-a-year-after-launch>
[^ch15-25]: MCP-B, “WebMCP documentation and developer tools” (docs.mcp-b.ai home page, with its live `registerTool()` example and the Rook extension). <https://docs.mcp-b.ai>
[^ch15-26]: npm registry records for `@mcp-b/global`, `@mcp-b/webmcp-polyfill` and `usewebmcp` (each at version 6.0.3 on 2 November 2026, published 14 October 2026, MIT licence, package descriptions as quoted). <https://registry.npmjs.org/@mcp-b/global>, <https://registry.npmjs.org/@mcp-b/webmcp-polyfill>, <https://registry.npmjs.org/usewebmcp>
[^ch15-27]: Chrome for Developers, “Imperative API” (published 18 May 2026, updated 16 October 2026, retrieved November 2026), framework section: React support “using the use-webmcp-tool package” and Vue support “using the @vueuse/core package”. <https://developer.chrome.com/docs/ai/webmcp/imperative-api>
[^ch15-28]: npm registry record for `use-webmcp-tool` (version 0.3.0, published 11 September 2026, Apache-2.0 licence, repository GoogleChromeLabs/use-webmcp-tool, description as quoted). <https://registry.npmjs.org/use-webmcp-tool>
[^ch15-29]: WebMCP-org/npm-packages repository, “NPM packages for MCP-B: Transport layers, React hooks, and browser tools for the Model Context Protocol”. <https://github.com/WebMCP-org/npm-packages>
[^ch15-30]: webmachinelearning/webmcp issue #192, “Transitioning WebMCP to the working group” (opened 28 May 2026), including the comments of 18 June and 13–14 August 2026. <https://github.com/webmachinelearning/webmcp/issues/192>
[^ch15-31]: W3C, “Web Machine Learning Working Group” group page (charter until 30 April 2027). <https://www.w3.org/groups/wg/webmachinelearning/>
[^ch15-32]: W3C Process Document, 18 August 2025: §4 charter development (refinement of at least 28 days), §5.6 Formal Objections and the W3C Council. <https://www.w3.org/policies/process/>
[^ch15-33]: Xueyuan Jia (W3C), “Start of refinement for a draft Agentic Web Working Group charter”, public-new-work mailing list, 1 October 2026. <https://lists.w3.org/Archives/Public/public-new-work/2026Oct/0002.html>
[^ch15-34]: w3c/charter-drafts pull request #901, which generalizes the WebMCP deliverable and adds identity, delegation, measurement and interaction modes (Yoav Weiss, opened 27 October 2026, merged 29 October 2026). <https://github.com/w3c/charter-drafts/pull/901>
[^ch15-35]: Chromium changes 8546218, “[WebMCP] Reject executeTool() with granular DOMExceptions” (landed 16 October 2026, Cr-Commit-Position #1720407), and 8510757, “[3/N] WebMCP: Introduce the `Tool` interface object” (landed 15 October 2026, #1719188), both exported to web-platform-tests. Chrome 157 branched at #1717349 and Chrome 158 at #1727472 (Chromium Dash, read 2 November 2026). <https://chromium-review.googlesource.com/c/chromium/src/+/8546218>, <https://chromium-review.googlesource.com/c/chromium/src/+/8510757>

[^ch15-output-schema]: webmachinelearning/webmcp pull request #254, merged 2 November 2026. <https://github.com/webmachinelearning/webmcp/pull/254>
[^ch15-output-validation]: webmachinelearning/webmcp issue #92, open on 15 November 2026. The current discussion includes proposals for host-side error behavior but no normative change requiring `executeTool()` to reject output mismatches. <https://github.com/webmachinelearning/webmcp/issues/92>
