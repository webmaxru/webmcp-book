# Chapter 11: Designing Tools Agents Can Actually Use

> *“More tools don’t always lead to better outcomes.”*
>
> — Anthropic, “Writing effective tools for agents — with agents”[^ch11-1]

## The reader who can’t ask questions

Every tool you register has two readers. The first one is the browser. It checks the name, stores the schema as a string and calls `execute` when it’s told to (Chapter 5). The second one is a language model that has never seen your site before. It’s in the middle of someone else’s errand, and it will decide in a fraction of a second whether your tool is the one it needs. The browser reads your definition literally. The model reads it the way a new colleague reads a note left on their desk: whatever the note doesn’t say, they guess.

Everything the model knows about a tool comes from four places. The name and the description are read before any call. The input schema tells it what to send. The result, including any error, tells it what happened and what to do next. Nothing else reaches it. Not your code, not your intentions, not the comment above the function. The specification describes the description member as “a natural language description of the tool’s functionality” that “helps agents understand when and how to use the tool,”[^ch11-2] and that’s about all the help the platform gives. Making the text good is your job.

Chapters 5 and 6 gave Trailhead and Fjord Table working tools and a set of rules that were enough to get started. Chapter 10 left a sharper question: Trailhead’s tools work, but are they the *right* tools? This chapter treats tool design as product design. It decides how many tools to offer and how coarse to make them, names and describes them within a character budget, writes schemas that leave little room for misreading, words results and errors so that the model does the right thing next, and keeps all that agent-facing text in step with the interface people see.

This chapter uses two projects. Trailhead gets a redesigned catalogue and cart. The Helpdesk Widget from Chapter 7, which Supportly embeds in Ledgerly, gets its three tools rewritten from the model’s side. Every rule comes with a check you can run. The demos folder for this chapter has a small lint for tool definitions and a validator that reads the same schema the agent sees, and its test suite runs every tool in Chromium 156 with WebMCP enabled.[^ch11-3]

## Tool strategy and budget

### Every tool costs something before it is called

A tool that is never called still costs the agent something. The explainer is blunt about it: “Every registered tool (its name, description, and input schema) consumes tokens in the model prompt, adds to inference latency, and increases the potential for tool confusion or hallucination.” It warns that “dozens or hundreds” of tools can “severely degrade agent performance or lead agent browsers to drop tools or fail to process them.”[^ch11-4] Chrome’s best-practices guide says the same thing more gently. There is no maximum, but “each tool takes up part of the context window and adds to the time for completion,” and “the more tools you provide and the more the tools have overlap, the harder it is for the agent to pick correctly.”[^ch11-5]

“Drop tools or fail to process them” isn’t a hypothetical anymore. In September 2026 a developer posted a data point to the Community Group from jjhub, a code-review app whose page registered one tool per operation, 126 in total. Descriptions were short (a median of 94 characters) and every schema was a flat object. ChatGPT’s browser answered with “WebMCP is disabled for this page because the site’s WebMCP configuration exceeds supported limits.” Zero tools, no exception, nothing the page could observe. Chrome showed no error and handed the agent the same flat list of 126. The team rewrote registration to keep at most 20 tools registered at any time.[^ch11-25] The limit exists, it differs between agents, and your page won’t be told when it hits it.

Nobody has published a number for WebMCP. The closest figure I found comes from a different platform. OpenAI’s function-calling guide suggests aiming “for fewer than 20 functions available at the start of a turn at any one time,” and calls that “just a soft suggestion.”[^ch11-6] Use it as a sanity check, and don’t chase it. Keep in mind that your page isn’t the only thing in the agent’s context, either. The agent may have tools from other tabs, its own built-in tools and tools from MCP servers, and your page’s tools compete with all of them.

You can measure your own share. The lint in Listing 11.1, later in this chapter, has a `measureTools()` function that adds up the characters of each definition as `getTools()` returns it. Characters aren’t tokens, because every model tokenizes differently, but they are a stable proxy you can track in CI. Trailhead’s three catalogue and cart tools in this chapter come to 1,798 characters, and the widget’s three come to 1,850 (*measured in Chromium 156*).[^ch11-3]

### Start from tasks, not endpoints

The most common way to end up with too many tools is to wrap your API. Trailhead’s backend has endpoints for listing products, getting one product, getting a price, getting stock, filtering by category, adding a cart line, updating a cart line and so on. Exposing each one as a tool feels thorough. Anthropic’s engineering team describes it as the error they see most: “tools that merely wrap existing software functionality or API endpoints—whether or not the tools are appropriate for agents.”[^ch11-1] Their fix is to design for the task. Instead of `list_users`, `list_events` and `create_event`, offer a single `schedule_event` that “finds availability and schedules an event.”[^ch11-1] OpenAI’s guide makes the same point from the other side: “Combine functions that are always called in sequence.”[^ch11-6] And jjhub above is exactly this story. Its 126 tools mirrored its MCP server one to one.

Chrome’s guide on building tools, which André Cipriani Bandarra and I wrote, starts from the same place and turns it into a short framework.[^ch11-24] Define the user goal first: what is the ideal outcome, what context is required, what are the boundaries (“what the agent should not do or what actions are restricted”) and which goals to prioritize. Then define the initial state, the “starting line” of where the person is in your product and what the agent already knows. Then role-play the conversation between the person and the agent, step by step, and write down which tool each step needs. A gap in the role-play is a missing tool. A tool that no step needs is one you can drop.

Figure 11.1 shows the result for Trailhead. On the left are the backend operations. On the right are the five tools the store actually registers. The mapping isn’t one to one. `search_products` absorbs three filter endpoints as optional parameters. `compare_products` replaces “get one product” called four times. `add_to_cart` covers both “add a line” and “increase a quantity,” because a person never thinks of those as different things.

![Figure 11.1 — From endpoints to tasks. Eleven backend operations become five Trailhead tools. Filters become parameters, repeated lookups become one comparison, and operations that are always chained become one call.](images/figure-11-1.png)

The role-play doesn’t need anything fancy. Write down what a person actually comes to do and what they would say to a shop assistant. Table 11.1 does that for Trailhead.

**Table 11.1 — Trailhead’s user tasks and the tools that serve them**

| What the person says | Tool | Why this shape |
|---|---|---|
| “Find me a light two-person tent under 4,000 kroner.” | `search_products` | One search with optional filters, not one tool per filter |
| “Which of these two is lighter?” | `compare_products` | One call returns every attribute for 2–4 products |
| “Put the boots in my basket, size 42.” | `add_to_cart` | Adding and increasing are the same act for a person |
| “What’s in my cart?” | `get_cart` | Read-only, so it can run without asking |
| “Go ahead and order it.” | `checkout` | Separate because it has consequences (Chapter 6) |

### Coarse or fine?

“Fewer tools” isn’t a rule to apply blindly. Chrome asks that “each tool should consist of a single function” and warns against overlap,[^ch11-5] and the explainer asks that “each tool should represent a single, well-defined function.”[^ch11-4] How do you reconcile “consolidate” with “single function”? Ask where a person would see one decision.

Three tests work well in practice:

- **Merge what is always chained.** If the agent will call A and then B every time, make one tool. A search that needs a separate “apply filter” call is two tools pretending to be one.
- **Split where consequences differ.** Annotations belong to the whole tool (Chapter 6). A tool that both reads and buys can’t be `readOnlyHint`, so the agent has to treat every call as risky. `get_cart` and `checkout` stay separate for that reason, even though both are about the cart.
- **Split where the person would want to be asked.** If one branch of a tool needs confirmation and another doesn’t, the agent can’t tell from the definition which call it’s about to make. Make two tools.

The Helpdesk Widget passes all three tests with three tools. Searching articles reads. Opening a ticket writes, and the person confirms it in the widget. Checking a ticket reads text written by people. Folding “search, and if nothing helps, open a ticket” into one tool would save a call and lose the confirmation boundary.

Chrome’s best-practices page adds a counterweight: “Trust the agent to complete the task.” Instead of writing rigid instructions, “assume the agent is able to understand what is required to complete the task, rather than expecting the agent to manage an exact flow of steps.”[^ch11-5] In other words, a tool set is a vocabulary. You give the agent good verbs, and it composes them.

### Collections, skills and other ways to scale

What should an application with a hundred tools do? WebMCP has no answer yet, but the question is very much alive in the Community Group. Issue #255, “Tool collections: coarse-grained grouping with progressive disclosure,” opened on 22 August 2026, observes that “a moderately complex app can easily surface 100+ tools” and that `getTools()` “hands the agent one flat list.” It proposes groups that an agent could read first and drill into later.[^ch11-7] The jjhub data point landed in that thread, together with what the team did about it: a core set of about eight tools, three loader tools (`list_tool_groups`, `load_tool_group` and `search_tools`), automatic loading of the group that matches the current view, and least-recently-used unloading so that the budget of 20 is never exceeded.[^ch11-25] On 20 October Kenneth Rohde Christiansen added feedback from the harness side. His team loads tools lazily in its own agent frontend, and he favours “hints on tools that feed whatever search a harness already has, not an explicit grouping API.”[^ch11-25]

Issue #161, opened on 3 April 2026, proposes “skills”: a `registerSkill()` call that bundles tool names with workflow instructions and context, because “Tools can tell agents what a site can do, but Skills tell agents how to do it well.”[^ch11-8] Issue #167 proposed lazy schemas, a `disabled` flag and an `updateTool()` method, and it’s closed now.[^ch11-9] The explainer sums up where things stand: “WebMCP does not currently define an in-place `updateTool()` method, lazy schemas, or disabled and grouped tool states.”[^ch11-4]

> **Still in flux:** Neither tool collections (#255) nor skills (#161) is in the 27 October 2026 draft, and both issues are open.[^ch11-7][^ch11-8] Until something lands, the tools you have for scaling are the ones Chapter 10 used: register by page state, keep the default set small and remove tools that don’t apply. jjhub’s loader tools show how far you can get with plain `registerTool()` and an `AbortSignal`. The skills strawman’s sample instructions include lines such as “Always mention 30-day return policy before checkout.” Chapter 12 treats exactly that kind of text, an instruction to the agent placed in tool metadata, as a risk. Whatever form grouping takes, expect agents to read it with the same suspicion they bring to descriptions.

## Naming, descriptions and character budgets

### Names that sort themselves out

Chapter 5 covered what the browser accepts in a name: 1 to 128 ASCII letters, digits, underscores, hyphens and full stops. What agents handle well is narrower. Chrome recommends verbs “that describe exactly what happens” and separating execution from initiation: `create-event` is “a tool for immediate event creation,” while `start-event-creation-process` “redirects the user to a form to create the event.”[^ch11-5] Its security guide recommends keeping names to about 30 characters.[^ch11-10]

Two more habits pay off once a tab has tools from more than one source. First, keep one naming style per site. Trailhead and Supportly both use `snake_case` with a verb and an object: `search_products`, `add_to_cart`, `search_articles`, `get_ticket_status`. Second, put the object in the name, even when it seems obvious. Ledgerly’s page can hold Ledgerly’s own tools and Supportly’s widget tools at the same time (Chapter 7). A bare `search` from each would leave the agent guessing. Anthropic reports that grouping related tools under shared prefixes or suffixes helps agents “select the right tools at the right time,” and that the choice between prefixes and suffixes had “non-trivial effects” in their evaluations, varying by model.[^ch11-1] `search_articles` and `search_products` are distinguishable without any extra machinery.

Parameter names deserve the same care. Anthropic’s example is to name a parameter `user_id` rather than `user`.[^ch11-1] The widget uses `ticketId`, not `id` or `ticket`. An agent that reads `ticketId` with the example `SUP-1042` in its description doesn’t have to guess whether to send a number, a URL or a ticket object.

### What a description has to say

The description is read every time the agent considers your tool, so every sentence has to earn its place. Use a four-part template and drop any part that the name already makes obvious:

1. **What it does, as a verb and an object.** “Search Supportly’s help articles…”
2. **When it’s the right tool**, especially compared with its neighbours. “…for how-to answers about Ledgerly.”
3. **What comes back**, in enough detail that the agent knows what it can do with the result. “Returns up to 5 articles, best match first, each with title, link and a short excerpt.”
4. **Side effects and who confirms them**, stated as facts. “The user reviews and sends it in the help widget.”

Chrome’s guide asks for the same core. A clear description “should describe what the tool does and when to use it,” and you should “rely on positive language and preferences instead of negative language, such as limitations.” Its example puts “This tool can create a calendar event, scheduled for a specific date and time” against “Don’t use this tool for weather.”[^ch11-5] The reason is practical. A prohibition names a task the tool doesn’t do, which puts that task in the model’s mind. And it never ends, because there is always another thing the tool doesn’t do.

Anthropic suggests imagining how you “would describe your tool to a new hire on your team,” and making explicit the context you would otherwise bring implicitly: “specialized query formats, definitions of niche terminology, relationships between underlying resources.”[^ch11-1] OpenAI calls the same idea “the intern test”: “Can an intern/human correctly use the function given nothing but what you gave the model?”[^ch11-6] For a web page, the implicit context is usually the product’s vocabulary. Ledgerly users say “export”, Supportly calls a ticket’s state `waiting_on_user`, and Trailhead writes prices in NOK. Put that vocabulary in the description.

Three things don’t belong in a description:

- **Live state.** “The cart has 3 items” is wrong as soon as someone adds a fourth, and agents may cache the definition. Chapter 10 moved that kind of information into results and read-only tools.
- **Instructions to the agent about its own behaviour.** “Always call this tool first” or “Prefer this tool over other searches” is steering, not description. Chapter 12 explains why a careful agent should read it as an injection attempt, which makes it counterproductive as well as rude.
- **Vague verbs for consequential acts.** The specification’s own warning example is a tool named `finalizeCart` described as “Finalizes the current shopping cart,” which actually places an order. An agent that thinks the user wants to view a final cart calls it, “and it actually triggers a purchase.”[^ch11-11] The draft lists “poorly written descriptions, outdated documentation, or inherent imprecision in natural language” and “side effects not mentioned in the description” as forms of accidental misalignment.[^ch11-11] If a tool spends money, sends a message or deletes something, its description says so in the first sentence.

### Parameter descriptions

Every parameter needs a description, and the most useful ones are short and concrete. A good parameter description says what the value means, gives its format or unit, shows one realistic example and, where it matters, says where the value comes from. Trailhead’s two versions of `sku`:

- Chapter 6: “Product SKU from search_products.”
- This chapter: “SKU from search_products. Footwear SKUs end in the EU size, e.g. TH-BOOT-FJELL-42.”

The second one adds the single piece of local knowledge the agent couldn’t have guessed. As you’ll see in a moment, the same sentence also appears in the error the agent receives when it gets the SKU wrong. Written once, used twice.

### Character budgets, enforced by a test

Chrome’s security guide recommends 500 characters per tool description, 150 per parameter description, 30 per tool or parameter name and 1,500 per tool output. It notes that “there is some variation across agents” and that the figures may change or move into the specification.[^ch11-10] The draft itself limits only the name, to 128 characters. Its security section suggests restricting other lengths because shorter text “helps shrink the possible universe of attacks,” and says that “further work is needed to evaluate the right size limits for titles, names, and other inputs,” pointing to issue #73.[^ch11-12] That issue, opened on 30 January 2026 and still open, also mentions quality: “there is also a cutoff at which long elaborate prompts tend to confuse models more than help them.”[^ch11-13]

Budgets that live in a style guide get forgotten. Budgets that live in a test don’t. Listing 11.1 is a small lint that runs over `getTools()` output in the demos’ test suite. It checks the budgets, the naming style, that the description says what the tool returns and that every parameter is described. It also checks three habits from this section: no steering words, no prohibitions as framing, and no empty or numeric enum values.

**Listing 11.1** `shared/tool-lint.js` — Measuring and linting agent-facing text

```js
// Measures and lints the agent-facing text of tools, as getTools() returns them.
// A development check for tests and CI; nothing here runs in production.

// Chrome's recommended budgets (guidance, not enforced by the browser).
export const BUDGET = { name: 30, description: 500, paramName: 30, paramDescription: 150 };

// Phrases that instruct the agent instead of describing the tool (Chapter 12).
const STEERING = /\b(always|never|you must|ignore|instead of any other|prefer this tool)\b/i;
const PROHIBITION = /(^|\.\s+)(do not|don't|never) /i;

// What a tool costs the agent before anyone calls it: the characters of the
// definition it reads. Characters, not tokens; tokenizers differ by model.
export function measureTools(tools) {
  const rows = tools.map((t) => ({
    name: t.name,
    chars: JSON.stringify({ name: t.name, description: t.description, inputSchema: t.inputSchema }).length,
  }));
  return { rows, total: rows.reduce((sum, r) => sum + r.chars, 0) };
}

export function lintTool(tool) {
  const problems = [];
  const add = (where, rule, detail) => problems.push({ tool: tool.name, where, rule, detail });

  if (tool.name.length > BUDGET.name) add('name', 'budget', `${tool.name.length} characters`);
  if (!/^[a-z]+(_[a-z]+)+$/.test(tool.name)) add('name', 'verb_object', 'use snake_case verb_object');

  const d = tool.description ?? '';
  if (d.length > BUDGET.description) add('description', 'budget', `${d.length} characters`);
  if (!/\breturns?\b/i.test(d)) add('description', 'says_what_it_returns', 'say what comes back');
  if (STEERING.test(d)) add('description', 'no_steering', d.match(STEERING)[0]);
  if (PROHIBITION.test(d)) add('description', 'positive_framing', 'state what it does, not what not to do');

  const schema = typeof tool.inputSchema === 'string' ? JSON.parse(tool.inputSchema) : tool.inputSchema;
  for (const [name, p] of Object.entries(schema?.properties ?? {})) {
    const where = `inputSchema.${name}`;
    if (name.length > BUDGET.paramName) add(where, 'budget', `${name.length} characters`);
    if (!p.description) add(where, 'described', 'every parameter needs a description');
    else if (p.description.length > BUDGET.paramDescription) add(where, 'budget', `${p.description.length} characters`);
    const values = p.enum ?? p.oneOf?.map((o) => o.const) ?? [];
    if (values.includes('')) add(where, 'no_empty_enum', 'make the parameter optional instead');
    if (values.some((v) => /^\d+$/.test(String(v)))) add(where, 'readable_enum', 'use words, not IDs');
  }
  return problems;
}
```

A lint like this can’t tell whether a description is *good*. It catches the mechanical mistakes, so that review time goes on the words. It’s also deliberately conservative. “Must” in a description isn’t always steering, and you may decide to allow it. That’s fine, as long as every exception is a decision someone made rather than an accident.

Running it over the earlier versions of the tools in this book is instructive. Table 11.2 shows what it found in the definitions from Chapters 6 and 7.

**Table 11.2 — Lint findings for the earlier tool definitions**

| Tool (source) | Findings |
|---|---|
| `search_products` (Listing 6.2) | `category` has no description |
| `add_to_cart` (Listing 6.7) | `quantity` has no description |
| `search_articles` (Listing 7.3) | `query` has no description |
| `create_ticket` (Listing 7.3) | `subject`, `body` and `priority` have no descriptions |
| `get_ticket_status` (Listing 7.3) | Description doesn’t say what it returns in those words, and `ticketId` has no description |

Source: `tests/run-tests.mjs` in the demos folder, run on 2 November 2026.[^ch11-3]

None of these is a bug in the sense Chapters 6 and 7 cared about. The tools worked, and the tests passed. They are exactly the gaps a model fills with guesses, though. An undescribed `priority` enum invites the agent to choose `high` for anything that sounds unpleasant. The next section shows how to say what each value means.

## Schemas that reduce ambiguity

### The schema is advice, so make it precise advice

Chapter 5 established that the browser doesn’t validate arguments against `inputSchema`. It stores “the stringified representation of the inputSchema,” makes it available to the agent, and passes whatever object comes back to `execute`.[^ch11-14] That makes the schema a piece of writing aimed at the model, not a contract. It can still be very precise writing. JSON Schema has keywords that close off whole classes of misreading, and the ones that matter most for tools are few.

**Enums with words.** The `enum` keyword “is used to restrict a value to a fixed set of values.”[^ch11-15] Use values a person would say: `'tents'`, not `3`. Chrome and the explainer both make the point with shipping: `shipping="Express"` instead of `shipping_id=1`.[^ch11-5][^ch11-4] Listing 11.1 flags numeric enum values for that reason.

**No empty option.** In Chapter 8 we noticed that a declarative form’s “No preference” option becomes the value `""` in the schema, and a hand-written tool would make the parameter optional instead. That’s the rule: absence is expressed by leaving a parameter out, never by a magic value. The lint flags `""` in any enum.

**Optional parameters say what happens when they are omitted.** “Only search one category. Omit to search all of them.” “`true` hides products that are out of stock. Default false.” The agent shouldn’t have to infer a default.

**Required means “can’t work without it.”** Not “usually useful”, and not “we’d like to know”. Over-requiring forces the agent to invent values. The specification’s privacy section adds a sharper reason to keep the list short. In its over-parameterization scenario, a dress-search tool adds optional parameters for age, pregnancy and location, and because “agents are designed to be helpful,” they fill them in from personal context, creating “a personalization-to-fingerprinting pipeline.”[^ch11-16] OpenAI’s guide has the everyday version: “Don’t make the model fill arguments you already know.”[^ch11-6] Supportly already knows who is signed in to the widget, so `create_ticket` asks for the problem and nothing about the person.

**Raw input over computed input.** Chrome’s newer guidance asks you to “accept raw user input” and to avoid “asking the agent to perform math or transform the input strings.” Its example: if a user says “11:00 to 15:00,” the tool should take that as a string instead of asking the model to calculate the minutes in between.[^ch11-5] Your code is better at arithmetic than the model is, and it doesn’t get tired.

**Arrays with bounds.** `compare_products` takes `skus` with `minItems: 2`, `maxItems: 4` and `uniqueItems: true`. The bounds say in schema terms what the description says in words, and they survive registration intact. `getTools()` in Chromium returned them unchanged (*observed*).[^ch11-3]

**Structure that prevents impossible states.** OpenAI’s example is `toggle_light(on: bool, off: bool)`, which “allows for invalid calls.”[^ch11-6] One `state` enum with `'on'` and `'off'` can’t be both.

### Enums that explain themselves: `oneOf` with titles

A bare enum tells the agent which strings are allowed. It doesn’t say what they mean. For many parameters the meaning is obvious (`'tents'`). For others it isn’t, and the difference matters. The widget’s `priority` is the clearest case. To a model, `high` and `normal` are adjectives. To Supportly’s support team they are promises: a high-priority ticket gets a reply within four hours and pulls someone off other work.

JSON Schema can say both things. `oneOf` means the value “must be valid against exactly one of the given subschemas,”[^ch11-17] and a subschema can be a single `const` value, which “is used to restrict a value to a single value.”[^ch11-18] Each subschema can also carry a `title`, which JSON Schema describes as preferably short text about the data.[^ch11-19] Put together, a list of `{ const, title }` pairs is an enum in which every value has its own explanation. Chapter 8 shows that Chrome’s declarative implementation generates a similar structure for a `<select>`, an `anyOf` list that pairs each option value with its visible text as a `title`. That isn’t an accident. The visible label is exactly what a person reads to choose.

Listing 11.2 defines the widget’s priorities once, in a module that both the widget’s form and its tools import. That second fact turns out to matter as much as the first, and this chapter returns to it later.

**Listing 11.2** `helpdesk/copy.js` — One source for the widget’s words

```js
// Supportly widget: every word that people and agents see, in one place.
// The form (widget-form.js) and the tools (widget-tools.js) both import it.
export const LIMITS = { query: 200, subject: 120, body: 4000 };

export const PRIORITIES = [
  { const: 'low', title: 'Low: a question; nothing is blocked. Reply within 2 business days.' },
  { const: 'normal', title: 'Normal: something is broken, with a workaround. Reply within 1 business day.' },
  { const: 'high', title: 'High: the user or their team cannot work. Reply within 4 hours.' },
];

export const COPY = {
  searchArticles: { title: 'Search help articles' },
  createTicket: { title: 'Open a support ticket', send: 'Send ticket', cancel: 'Cancel' },
  getTicketStatus: { title: 'Check a support ticket' },
  fields: {
    subject: 'Subject',
    body: 'What happened?',
    priority: 'How urgent is it?',
  },
};
```

The titles describe each level in terms the agent can match against what the user said (“nothing is blocked”, “cannot work”). They also state the consequence (“Reply within 4 hours”), so that the agent can tell the user what to expect. Chromium 156 passed the `oneOf` array through registration unchanged, and `getTools()` returned all three `{ const, title }` pairs exactly as written (*observed*).[^ch11-3]

There is a cost. The widget’s `create_ticket` definition grew from 415 characters in Chapter 7 to 1,014 in this chapter, and most of the growth is the three titles and the parameter descriptions (*measured*).[^ch11-3] It’s still well inside Chrome’s budgets, because the budgets apply to individual descriptions rather than whole schemas. But it’s real context the agent pays for on every turn. Spend it where a wrong choice is expensive. `priority` qualifies. Trailhead’s `category` doesn’t, because its values say what they are.

Chrome’s best-practices page has a related lesson about a select field for honorifics. A model “may make the wrong choice,” and the page advises against “adding narrow rules to patch this issue.” Make the field optional and let the agent ask the user instead.[^ch11-5] A `oneOf` list with good titles is for values the agent can choose correctly from the conversation. A value only the person knows is a question, and a later section shows how a result can ask it.

> **Still in flux:** Which JSON Schema, and does the agent see `title`? The draft cites JSON Schema without naming a dialect or subset. On 5 March 2026 the Community Group resolved that the browser should be responsible for schema validation and that the spec should “codify a subset”. Pull request #289, which implemented that, was closed unmerged on 1 October 2026, and issue #92 is still open.[^ch11-20] The discussion didn’t stop there. On 16 October a repository collaborator argued in #92 for making both `inputSchema` and `outputSchema` required, so that “a loose object schema” becomes “an explicit choice”, and on 30 October Johann Hofmann replied with “Full support from security for requiring and validating these schemas in the spec.”[^ch11-20] MCP’s tools specification defaults to the 2020-12 dialect when no `$schema` is present.[^ch11-21] `oneOf`, `const` and `title` are all core keywords, and Chromium preserves them. Whether a particular agent shows subschema titles to its model is up to the agent, because to the browser the schema is a string. If you depend on the titles, test with the agents you care about (Chapter 14 covers evals). And write every tool with a schema today. If #92 goes the way the thread is leaning, a schema will stop being optional.

### One schema, two jobs: validate with the schema you published

“Validate strictly in code, loosely in schema” is Chrome’s rule,[^ch11-5] and Chapter 6 followed it with hand-written checks in every `execute`. That works, but it creates a drift risk. The schema says `maximum: 10`, the code checks `> 12`, and nobody notices until an agent is told one thing and refused for another.

Listing 11.3 removes the duplication. `checkArgs()` validates the arguments against the same schema object the tool registered, using only the core keywords this book recommends. It returns a Chapter 6 style failure whose message names the field and repeats that field’s own description.

**Listing 11.3** `shared/validate.js` — Validating against the published schema

```js
import { fail } from './results.js';

// Checks arguments against the same schema the agent was given, using only the
// core keywords this book recommends. Returns null when the arguments are valid,
// otherwise a fail() result that names the field and says what valid looks like.
export function checkArgs(schema, args) {
  if (args === null || typeof args !== 'object' || Array.isArray(args)) {
    return fail('INVALID_INPUT', 'Send the arguments as one JSON object.');
  }
  const props = schema.properties ?? {};
  for (const key of schema.required ?? []) {
    if (args[key] === undefined || args[key] === '') {
      return fail('MISSING_ARGUMENT', `Provide "${key}". ${props[key]?.description ?? ''}`.trim(),
        { field: key });
    }
  }
  for (const [key, value] of Object.entries(args)) {
    if (!(key in props)) {
      return fail('UNKNOWN_ARGUMENT',
        `"${key}" is not a parameter of this tool. Parameters: ${Object.keys(props).join(', ')}.`,
        { field: key });
    }
    const problem = check(props[key], value);
    if (problem) {
      return fail('INVALID_ARGUMENT', `"${key}" ${problem} ${props[key].description ?? ''}`.trim(),
        { field: key });
    }
  }
  return null;
}

// enum, or oneOf made of { const, title } pairs (see Listing 11.4).
const allowedValues = (p) =>
  p.enum ?? (p.oneOf?.every((o) => 'const' in o) ? p.oneOf.map((o) => o.const) : null);

function check(p, v) {
  const values = allowedValues(p);
  if (values && !values.includes(v)) {
    return `must be one of ${values.map((x) => JSON.stringify(x)).join(', ')}.`;
  }
  if (p.type === 'string') {
    if (typeof v !== 'string') return 'must be a string.';
    if (p.maxLength !== undefined && v.length > p.maxLength) {
      return `is ${v.length} characters; the limit is ${p.maxLength}.`;
    }
    if (p.pattern && !new RegExp(p.pattern).test(v)) return 'is not in the expected format.';
  }
  if (p.type === 'number' || p.type === 'integer') {
    if (typeof v !== 'number' || !Number.isFinite(v)) return 'must be a number.';
    if (p.type === 'integer' && !Number.isInteger(v)) return 'must be a whole number.';
    if (p.minimum !== undefined && v < p.minimum) return `must be at least ${p.minimum}.`;
    if (p.maximum !== undefined && v > p.maximum) return `must be at most ${p.maximum}.`;
  }
  if (p.type === 'boolean' && typeof v !== 'boolean') return 'must be true or false.';
  if (p.type === 'array') {
    if (!Array.isArray(v)) return 'must be a list.';
    if (p.minItems !== undefined && v.length < p.minItems) return `needs at least ${p.minItems} items.`;
    if (p.maxItems !== undefined && v.length > p.maxItems) return `takes at most ${p.maxItems} items.`;
    if (p.uniqueItems && new Set(v).size !== v.length) return 'must not repeat an item.';
    for (const item of v) {
      const problem = p.items && check(p.items, item);
      if (problem) return `has an item that ${problem}`;
    }
  }
  return null;
}
```

The trick is in the last argument of each message: `props[key].description`. Every parameter description already says what a valid value looks like (“Highest price in NOK, e.g. 2500.”), so the error can quote it. When an agent sent `maxPrice: '2500'` as a string, Chromium returned this to the caller (*observed*):[^ch11-3]

```json
{
  "status": "error",
  "code": "INVALID_ARGUMENT",
  "message": "\"maxPrice\" must be a number. Highest price in NOK, e.g. 2500.",
  "field": "maxPrice"
}
```

This isn’t a full JSON Schema validator, and it isn’t meant to be one. It doesn’t resolve `$ref`, it ignores keywords it doesn’t know and it stops at the first problem. If your schemas need more, use a real validator library. For tools written the way this chapter recommends, flat objects with a handful of described properties, forty lines are enough. And they guarantee that what you tell the agent and what you enforce are the same thing.

The validator is only the first line of defence. Chrome’s guide on building tools is explicit that strict schemas help the agent pick the right tool, while “the application code must enforce trust boundaries”: authorization, exact identifiers, known subjects and sequence safety. “Enforcement belongs in your application logic, beyond readOnlyHint or untrustedContentHint.”[^ch11-24] `checkArgs()` answers “is this argument well formed?”. Whether this account may open a ticket, or whether that ticket belongs to this account, is still your service’s question, and the widget answers it later in this chapter.

## Returning useful results and errors

### Declare the result shape, then validate it in the harness

`outputSchema` is an optional JSON Schema for a tool’s return value. PR #254 added it to `ModelContextTool` and `RegisteredTool`. Since PR #348 the exposed object is `Tool`, and a tool registered without a schema reports `outputSchema` as `null`. An in-page agent can read it through `getTools()`.[^ch11-output-schema] The schema describes the result the tool promises; the current spec does not require native `executeTool()` to reject a mismatch. Issue #92 remains open on validation ownership and error semantics.[^ch11-output-validation]

Validate every result against its declared schema before the result enters the model’s next prompt. If it fails, give the model a concise error with a schema path or safe reason, and omit the malformed result from both transcript and error text. A result can contain untrusted page content, so quoting the bad value inside the error would send it to the model by another route. If a tool has no `outputSchema`, preserve the optional case rather than inventing an object wrapper for plain text. The Test Agent in Chapter 9 demonstrates this boundary; WebMCP Extension PR #98 is another host-side example.[^ch11-output-extension]

### Results: high signal, the right identifiers, and an honest count

A result has two jobs. It answers the question, and it gives the agent what it needs for the next step. Anthropic recommends returning “only high signal information,” avoiding “low-level technical identifiers” such as `uuid` or `mime_type`. It observes that agents “grapple with natural language names, terms, or identifiers significantly more successfully than they do with cryptic identifiers.”[^ch11-1] That doesn’t mean dropping identifiers. It means keeping the ones the next tool needs, next to a name a person would recognize. Trailhead’s search returns `sku` (which `compare_products` and `add_to_cart` take) and `name` (which the agent says to the user). It leaves out internal product IDs, warehouse codes and image URLs.

Results also need a size limit. Chrome’s budget is 1,500 characters per tool output.[^ch11-10] Anthropic recommends “pagination, range selection, filtering, and/or truncation with sensible default parameter values” for responses that could get large, and adds: “If you choose to truncate responses, be sure to steer agents with helpful instructions.”[^ch11-1] A list cut at ten items without saying so is a quiet lie. The agent will tell the user “here are the tents” when it has seen a tenth of them.

Listing 11.4 applies all this to Trailhead’s two read-only catalogue tools.

**Listing 11.4** `trailhead/catalog-tools.js` — Catalogue tools that return what the next step needs

```js
import { catalog } from './store.js';
import { checkArgs } from '../shared/validate.js';
import { fail } from '../shared/results.js';

const LIMIT = 10;

const searchSchema = {
  type: 'object',
  properties: {
    query: { type: 'string', maxLength: 100,
      description: 'What the user wants, in their words, e.g. "light 2 person tent".' },
    category: { type: 'string', enum: ['tents', 'sleeping-bags', 'backpacks', 'footwear', 'clothing'],
      description: 'Only search one category. Omit to search all of them.' },
    maxPrice: { type: 'number', minimum: 0, description: 'Highest price in NOK, e.g. 2500.' },
    inStockOnly: { type: 'boolean', description: 'true hides products that are out of stock. Default false.' },
  },
  required: ['query'],
};

const compareSchema = {
  type: 'object',
  properties: {
    skus: { type: 'array', items: { type: 'string' }, minItems: 2, maxItems: 4, uniqueItems: true,
      description: '2 to 4 different SKUs from search_products, e.g. ["TH-TENT-2P", "TH-TENT-3P"].' },
  },
  required: ['skus'],
};

export async function registerCatalogTools(signal) {
  await document.modelContext.registerTool({
    name: 'search_products',
    title: 'Search products',
    description:
      'Search the Trailhead outdoor-gear catalogue. Returns up to 10 products, best match ' +
      'first, each with SKU, name, price in NOK, rating and whether it is in stock, plus the ' +
      'total number of matches. Does not change the cart.',
    inputSchema: searchSchema,
    annotations: { readOnlyHint: true },
    async execute(args) {
      const invalid = checkArgs(searchSchema, args);
      if (invalid) return invalid;
      const matches = catalog.search(args);
      const result = {
        products: matches.slice(0, LIMIT).map((p) => ({                // ①
          sku: p.sku, name: p.name, price: { amount: p.price, currency: 'NOK' },
          rating: p.rating, inStock: p.stock > 0,
        })),
        total: matches.length,
      };
      if (matches.length > LIMIT) {                                    // ②
        result.note = `Showing ${LIMIT} of ${matches.length}. Add category or maxPrice to narrow the search.`;
      } else if (matches.length === 0) {
        result.note = 'No products matched. Try fewer or more general words.';
      }
      return result;
    },
  }, { signal });

  await document.modelContext.registerTool({
    name: 'compare_products',
    title: 'Compare products',
    description:
      'Compare 2 to 4 products side by side. Returns one row per attribute (price in NOK, ' +
      'rating, stock, weight in grams and the specs of that category) with each product\'s value.',
    inputSchema: compareSchema,
    annotations: { readOnlyHint: true },
    async execute(args) {
      const invalid = checkArgs(compareSchema, args);
      if (invalid) return invalid;
      const unknownSkus = args.skus.filter((sku) => !catalog.get(sku));
      if (unknownSkus.length) {                                        // ③
        return fail('UNKNOWN_SKU',
          `No product has SKU ${unknownSkus.join(', ')}. Use search_products to find SKUs.`,
          { unknownSkus });
      }
      const products = args.skus.map((sku) => catalog.get(sku));
      const row = (attribute, value) =>
        ({ attribute, values: Object.fromEntries(products.map((p) => [p.sku, value(p)])) });
      const specKeys = [...new Set(products.flatMap((p) => Object.keys(p.specs)))];
      return {
        products: products.map((p) => ({ sku: p.sku, name: p.name })),
        rows: [
          row('price (NOK)', (p) => p.price),
          row('rating', (p) => p.rating),
          row('in stock', (p) => p.stock > 0),
          ...specKeys.map((k) => row(k, (p) => p.specs[k] ?? null)),     // ④
        ],
      };
    },
  }, { signal });
}
```

① Each product carries exactly the fields Trailhead’s canonical result shape defines: SKU, name, price with its currency, rating and a boolean for stock. The stock *count* stays private. The agent doesn’t need it, and competitors don’t either.

② When there are more matches than fit, the result says how many, how many it’s showing and which parameters would narrow the search. A broad search for “tent” in the demo matched 16 products. The result listed 10, said `"Showing 10 of 16. Add category or maxPrice to narrow the search."`, and came to 1,312 characters, inside the 1,500 budget (*observed in Chromium 156*).[^ch11-3] An empty result isn’t an error either. It returns an empty list and a note suggesting broader words.

③ An unknown SKU is a failure the agent can fix. The message says which SKU and which tool will find the right one, and it lists the bad SKUs in a field a program can read.

④ The comparison returns rows of attributes with one value per SKU. An agent can turn that shape into a sentence or a table without guessing which number belongs to which product.

> **Still in flux:** `outputSchema`. WebMCP results are strings: whatever your `execute` returns is serialized and handed to the caller (Chapter 5). There is no way yet to tell the agent the shape of a result in advance. Issue #9, “Introduce `outputSchema`,” has been open since 12 August 2025. Pull request #254, which adds `outputSchema` to the tool dictionary, was opened on 21 August 2026, was last updated on 26 October 2026 and is still open.[^ch11-22] MCP already has the feature. A tool may declare an `outputSchema` and return `structuredContent` that conforms to it.[^ch11-21] Until WebMCP decides, describe the result in the description (“Returns up to 10 products … each with SKU, name, price in NOK…”) and keep result shapes stable.

### Errors the model can act on

Chapter 6 set the convention. Tool-level failures are results, not exceptions, shaped `{ status: 'error', code, message }`, with a stable code for programs and a sentence for the model. The specification allows exactly this. Its error table “only tracks the list of platform-defined failures,” and “tool execution failures defined by tool authors can also be reported to the tool caller in the response JSON string.”[^ch11-23] MCP takes the same position. Its tools specification says that tool execution errors “contain actionable feedback that language models can use to self-correct and retry with adjusted parameters,” that they are reported in results with `isError: true`, and that clients “SHOULD provide tool execution errors to language models to enable self-correction.”[^ch11-21] Chrome’s guide on building tools puts it in one line: the response “should act as a guide rather than a dead end.”[^ch11-24]

The wording of every `message` follows these rules:

1. **Name the thing that was wrong.** `"quantity" must be a whole number.` beats `Invalid input.` If more than one argument could be at fault, say which.
2. **Show what right looks like, with an example from the real data.** “Ticket ID as the user sees it, e.g. SUP-1042.” Anthropic contrasts “opaque error codes or tracebacks” with messages that “clearly communicate specific and actionable improvements.”[^ch11-1]
3. **Point to the next step, by tool name if there is one.** “Use search_products to find SKUs.”
4. **Say who should act if it isn’t the agent.** “Ask the user which size.” “Tell the user they can open another after 23:57 (UTC).”
5. **Leave out internals.** No stack traces, no database errors, no class names. The platform already strips your thrown exceptions to a name (Chapter 6), so don’t smuggle them back in through the message.
6. **Keep the code stable and the message free.** Programs and tests branch on `code`. The message can be reworded whenever evals show that a better phrasing works.

The build-tools guide has a set of examples that line up with these rules nicely.[^ch11-24] A wrong state or missing prerequisite (“No flight search results found. Search for flights first.”), an invalid parameter (“Invalid date format. Provide the date in YYYY-MM-DD format.”), an unexpected empty answer from a backend (“No flights found matching your criteria. Try adjusting your search parameters.”) and a business rule (“Order 123 has already shipped. Redirect the user to the returns policy.”). Every one of them names the problem and the next step in the same breath. The best-practices page adds one more for a specific case: “If a tool is rate limited, return a meaningful error or advise the user to manually take on the task.”[^ch11-5]

### Refusals are not failures

Rule 4 hides an important distinction. Some failures are the agent’s to fix: a malformed date, an unknown SKU, a missing argument. The agent should simply try again with better input. Other outcomes aren’t failures of the call at all. The arguments were fine, but a rule says no: a purchase limit, a sold-out item, a rate limit, an account that isn’t allowed to do this. Retrying with different arguments won’t help. In most cases the agent *shouldn’t* even try, because the obvious workaround changes what the person asked for. An agent told “only 2 per customer” that silently adds 2 instead of 3 has made a decision that belonged to the user.

If both outcomes come back as `status: 'error'`, the agent has to work out from the prose which kind it got. It’s better to say so in the status. Listing 11.5 puts Chapter 6’s `fail()` and three siblings in one module, giving four non-success statuses that each answer the question “who acts next?” The earlier chapters’ tools already return these shapes, and this section explains the reasoning.

**Listing 11.5** `shared/results.js` — Four ways a call can fall short

```js
// Result shapes shared by every tool on the page: Chapter 6's fail(), plus
// three siblings. `status` is what the agent reads first; it says who acts next.

// The agent can fix this itself: other arguments, or another tool first.
export const fail = (code, message, details = {}) =>
  ({ status: 'error', code, message, ...details });

// A rule says no. Other arguments won't help; the user has to decide.
export const refuse = (code, message, details = {}) =>
  ({ status: 'refused', code, message, ...details });

// Only the user knows the answer. Ask them, then call again.
export const needsInput = (missing, message, details = {}) =>
  ({ status: 'needs_input', code: 'MISSING_INFORMATION', missing, message, ...details });

// The user said no in the page's own UI. Don't retry unless they ask.
export const cancelledByUser = (message) =>
  ({ status: 'cancelled_by_user', message });
```

Table 11.3 sums up the vocabulary. Chapter 7’s widget returns `cancelled_by_user`, and Chapter 13 returns a `needs_input` result for a missing size. This listing gives them one home.

**Table 11.3 — Result statuses and who acts next**

| `status` | Meaning | Who acts next | Retry? |
|---|---|---|---|
| a domain word (`added`, `created`), or none | It worked | The agent, with the result | — |
| `error` | The call was wrong in a way the agent can fix | The agent: new arguments, or another tool first | Yes, after fixing |
| `needs_input` | Only the user knows something the call needs | The user answers, then the agent calls again | Yes, with the answer |
| `refused` | A rule says no, and other arguments won’t help | The user decides what to do | Not without the user |
| `cancelled_by_user` | The person declined in the page’s own UI | Nobody, unless the user asks again | No |

Figure 11.2 shows the same thing as the decision an agent faces after each call.

![Figure 11.2 — Who acts next. Each status tells the agent whether to continue, fix its call, ask the user, or stop.](images/figure-11-2.png)

Reserving `status` for the outcome has a consequence for result design: don’t use the same field name for domain data. A ticket’s state returned as `status: 'open'` could be mistaken for an outcome by an agent applying Table 11.3. That’s why Chapter 7’s `get_ticket_status` and this chapter’s both return it as `ticketState`.

`needs_input` is the answer to what the build-tools guide calls variance. A person may say “I need to go to NYC next week,” and the guide asks for tools “flexible enough” for the agent “to ask for missing parameters (“Which day next week?”), instead of making assumptions which may lead to failure.”[^ch11-24] The status makes that question explicit, so the agent doesn’t have to infer it from a sentence.

Listing 11.6 applies the vocabulary to Trailhead’s `add_to_cart`.

**Listing 11.6** `trailhead/cart-tools.js` — `add_to_cart` that tells the agent who decides

```js
import { cart, catalog } from './store.js';
import { checkArgs } from '../shared/validate.js';
import { fail, refuse, needsInput } from '../shared/results.js';

const addSchema = {
  type: 'object',
  properties: {
    sku: { type: 'string',
      description: 'SKU from search_products. Footwear SKUs end in the EU size, e.g. TH-BOOT-FJELL-42.' },
    quantity: { type: 'integer', minimum: 1, maximum: 10, description: 'How many to add, 1 to 10.' },
  },
  required: ['sku', 'quantity'],
};

export async function registerCartTools(signal) {
  await document.modelContext.registerTool({
    name: 'add_to_cart',
    title: 'Add to cart',
    description:
      'Add 1 to 10 units of one product to the cart, by SKU. Adding a SKU that is already ' +
      'in the cart increases its quantity. Returns the cart line and the cart total in NOK.',
    inputSchema: addSchema,
    async execute(args) {
      const invalid = checkArgs(addSchema, args);
      if (invalid) return invalid;                                       // ①
      const { sku, quantity } = args;

      const sizes = catalog.sizesOf(sku);
      if (sizes) {                                                       // ②
        return needsInput(['size'],
          `This product comes in EU sizes ${sizes.join(', ')}. Ask the user which size, then ` +
          `call add_to_cart again with the sized SKU, e.g. ${sku}-${sizes[0]}.`,
          { sizes });
      }

      const product = catalog.get(sku);
      if (!product) {
        return fail('UNKNOWN_SKU', `No product has SKU "${sku}". Use search_products to find SKUs.`);
      }

      const inCart = cart.quantityOf(sku);
      if (product.limitPerCustomer && inCart + quantity > product.limitPerCustomer) {
        return refuse('PURCHASE_LIMIT',                                  // ③
          `${product.name} is limited to ${product.limitPerCustomer} per customer and the cart ` +
          `has ${inCart}. Ask the user before adding a smaller quantity.`,
          { limit: product.limitPerCustomer, inCart });
      }
      if (product.stock < inCart + quantity) {
        return refuse('OUT_OF_STOCK',
          `Only ${product.stock} of ${product.name} in stock and the cart has ${inCart}. ` +
          'Ask the user before adding a smaller quantity.',
          { available: product.stock, inCart });
      }

      const line = cart.add(sku, quantity);
      return { status: 'added', line, total: { amount: cart.total(), currency: 'NOK' } };
    },
  }, { signal });
}
```

① Malformed arguments are the agent’s to fix, and Listing 11.3 produces the message.

② The boots come in sizes, and the SKU without a size names the product family, not something you can buy. The agent can’t know the user’s shoe size, so this is `needs_input`, not `error`. The result lists the sizes and shows what a sized SKU looks like, so that after one question to the user the next call succeeds. In Chromium 156 the result was `{"status":"needs_input","code":"MISSING_INFORMATION","missing":["size"],…}` with the sizes 40 to 45 (*observed*).[^ch11-3]

③ The limited-edition jacket allows two per customer. A request for three is `refused`, and the message says what the agent should do instead of “fixing” it: ask the user. The sold-out tent takes the same path, and so does Chapter 6’s `OUT_OF_STOCK`, a business-rule refusal (“only three left”) that uses `status: 'refused'` for exactly this reason.

The line between `error` and `refused` is a judgment call at the edges. A practical test: *would a good human assistant make this change without checking with the person?* Reformatting a date, yes. Picking a shoe size, buying fewer jackets or waiting an hour to open a ticket, no.

### The same request, twice

There is one more refusal worth designing for, and it has nothing to do with the arguments being wrong. Agents retry. A call times out, the agent isn’t sure whether it went through, and it sends the same call again. People do the same thing when they press a submit button twice. For a read-only tool that’s harmless. For a tool that creates something, it’s a second ticket, a second booking or a second order.

The build-tools guide calls this a duplication conflict and suggests an idempotency key: “use the exact order details to ensure a single request wasn’t sent repeatedly by mistake,” and if it was, “reject it.”[^ch11-24] For the widget, the exact details are the subject, the body and the priority. If an identical ticket was opened in the past hour, `create_ticket` doesn’t open the form again. It returns `refused` with the code `DUPLICATE_TICKET` and the ID of the ticket that already exists, so the agent can tell the person where their request went. The status is chosen on purpose. The arguments were perfectly valid, and changing them to get around the check would be the worst possible fix. You’ll see the check in the widget’s code in Listing 11.8.

## Keeping agent-facing text in step with the UI

### Two descriptions of one product

A WebMCP page describes itself twice. Once to people, in labels, buttons, help text and validation messages. And once to agents, in names, titles, descriptions, schemas and results. Left alone, the two drift apart. Someone renames the “Urgent” priority to “High” in the form and forgets the tool. A designer raises the subject limit to 150 characters, and the schema still says 120. Support changes its response times, and the descriptions still promise the old ones.

Drift hurts in both directions. An agent that uses words the page doesn’t show confuses the person watching (“I’ve set priority to urgent”, and there is no urgent). A page whose tool accepts what its form rejects lets the agent do things a person can’t, which Chapter 13 identifies as a parity and accessibility problem. The explainer asks for synchronized state because “AI agents and human users collaborate in the same browser session,”[^ch11-4] and Chrome asks you to “update the interface state after functions are completed,” because agents “may rely on the interface to plan next steps.”[^ch11-5] Shared words are the static half of the same idea.

Since 30 October 2026 Chrome’s best-practices page says it as an architectural rule, too: “Share the application service.” Keep “the visible user interface (UI), WebMCP tools, and testing environments in sync by sharing a single application service for validation, permissions, and side effects.”[^ch11-5] Chapter 10 did that for Trailhead’s logic. This section does it for the widget’s words, with three practices.

**One source for the words.** Listing 11.2 already put the widget’s titles, priority labels and limits in one module. The form and the tools both import it, so the agent’s `title` for `create_ticket` is the label on the button a person presses, and the `title` of each priority is the text of each option in the form. The specification says the tool’s `title` is used by the browser “to reference the tool in the user interface” and recommends that it be localized to the user’s language,[^ch11-2] so a shared string is also the natural home for its translations.

**Build the human UI from the same data.** Listing 11.7 renders the widget’s ticket form from that module, and its `confirmTicket()` shows the agent’s draft in the same form a person would fill in by hand.

**Listing 11.7** `helpdesk/widget-form.js` — The person’s form, built from the same copy

```js
import { COPY, PRIORITIES, LIMITS } from './copy.js';

// The person's ticket form, built from the same copy as the agent's tool.
export function renderTicketForm(root) {
  root.innerHTML = `
    <button type="button" id="new-ticket">${COPY.createTicket.title}</button>
    <form id="ticket-form" hidden>
      <h2>${COPY.createTicket.title}</h2>
      <label>${COPY.fields.subject}
        <input name="subject" maxlength="${LIMITS.subject}" required></label>
      <label>${COPY.fields.body}
        <textarea name="body" maxlength="${LIMITS.body}" required></textarea></label>
      <label>${COPY.fields.priority}
        <select name="priority">${PRIORITIES.map((p) =>
          `<option value="${p.const}">${p.title}</option>`).join('')}</select></label>
      <button value="send">${COPY.createTicket.send}</button>
      <button value="cancel" formnovalidate>${COPY.createTicket.cancel}</button>
    </form>`;
}

// Shows the agent's draft in the form and waits for the person to send or cancel.
export function confirmTicket(draft, signal) {
  const form = document.getElementById('ticket-form');
  for (const [field, value] of Object.entries(draft)) form.elements[field].value = value;
  form.hidden = false;
  return new Promise((resolve) => {
    const done = (sent) => { form.hidden = true; form.onsubmit = null; resolve(sent); };
    form.onsubmit = (event) => {
      event.preventDefault();
      done(event.submitter?.value === 'send');
    };
    signal.addEventListener('abort', () => done(false), { once: true });
  });
}
```

**Test the parity.** The demo’s tests load the widget, read the button label, the form heading, the `<option>` elements and the `maxlength` attributes from the DOM, and compare them with what `getTools()` returns. In Chromium 156 the tool title, the button label and the form heading were the same string. The three options matched the three `{ const, title }` pairs exactly, and both `maxlength` values matched the schema’s `maxLength` (*observed*).[^ch11-3] If someone edits one side, the test fails.

### Changing the words

Shared words don’t solve one more thing: agents read your definition when they see it, not every time they call. The explainer’s guidance is explicit. A tool’s implementation can change freely, but “a tool’s name, description, and input schema are loaded into the model’s context statically,” so changing them means unregistering and registering again, which fires `toolchange`.[^ch11-4] For a shared copy module that only changes on deploy, a page reload does that for you. For copy that changes while the page is open (a feature flag, a language switch), re-register the affected tools, as Chapter 10 did for view-scoped tools.

The explainer also asks that `execute` “still validate current inputs, authorization, and preconditions before running,” because state can change between the moment the model read the schema and the moment it calls.[^ch11-4] Listing 11.3 helps here too. Validation reads the schema at call time, so the two can’t disagree. Chrome’s newer guidance takes the same thought one step further for consequential tools. “Reject calls made against stale workflow state,” and when the person confirms, “recompute the current state and reject stale work.”[^ch11-5] The widget’s rate limit and duplicate check are read at call time for exactly that reason, and Chapter 10’s checkout compares the cart before and after the person confirms.

## The Helpdesk Widget, redesigned

Listing 11.8 brings the chapter together for the widget. Compare it with Listing 7.3. The registration mechanics, `exposedTo` and the confirmation in the widget’s own frame are unchanged. What changed is everything the agent reads, plus one check the first version didn’t have.

**Listing 11.8** `helpdesk/widget-tools.js` — The widget’s tools, written for the model

```js
// Supportly help widget: the three tools, redesigned (compare Listing 7.3).
import { helpdesk } from './helpdesk-api.js';
import { confirmTicket } from './widget-form.js';
import { COPY, LIMITS, PRIORITIES } from './copy.js';
import { checkArgs } from '../shared/validate.js';
import { fail, refuse, cancelledByUser } from '../shared/results.js';

const searchSchema = {
  type: 'object',
  properties: {
    query: { type: 'string', maxLength: LIMITS.query,
      description: 'The user\'s question or the error text they see, e.g. "export invoices to CSV".' },
  },
  required: ['query'],
};

const ticketSchema = {
  type: 'object',
  properties: {
    subject: { type: 'string', maxLength: LIMITS.subject,
      description: 'One-line summary, e.g. "CSV export fails for March invoices".' },
    body: { type: 'string', maxLength: LIMITS.body,
      description: 'What happened, what the user expected, and the steps that led to it.' },
    priority: { type: 'string', oneOf: PRIORITIES,                      // ①
      description: 'How urgent the problem is for the user.' },
  },
  required: ['subject', 'body', 'priority'],
};

const statusSchema = {
  type: 'object',
  properties: {
    ticketId: { type: 'string', pattern: '^SUP-[0-9]+$',
      description: 'Ticket ID as the user sees it, e.g. SUP-1042.' },
  },
  required: ['ticketId'],
};

export async function registerWidgetTools({ signal, exposedTo = [] }) {
  const mc = document.modelContext;
  const options = { signal, exposedTo };

  await mc.registerTool({
    name: 'search_articles',
    title: COPY.searchArticles.title,
    description:
      'Search Supportly\'s help articles for how-to answers about Ledgerly. Returns up to ' +
      '5 articles, best match first, each with title, link and a short excerpt.',
    inputSchema: searchSchema,
    annotations: { readOnlyHint: true },
    async execute(args) {
      const invalid = checkArgs(searchSchema, args);
      if (invalid) return invalid;
      const articles = await helpdesk.search(args.query, 5);
      if (articles.length === 0) {
        return { articles, note: 'No articles matched. Try the exact words of the error message.' };
      }
      return { articles };
    },
  }, options);

  await mc.registerTool({
    name: 'create_ticket',
    title: COPY.createTicket.title,                                       // ②
    description:
      'Open a support ticket with Supportly\'s team about a problem with Ledgerly. The user ' +
      'reviews and sends it in the help widget; their account and contact details are added ' +
      'automatically. Returns the ticket ID, e.g. SUP-1042, and when to expect a reply.',
    inputSchema: ticketSchema,                                            // ③
    annotations: { consequentialHint: true },
    async execute(args, { signal }) {
      const invalid = checkArgs(ticketSchema, args);
      if (invalid) return invalid;
      const duplicate = await helpdesk.findDuplicate(args);
      if (duplicate) {                                                    // ④
        return refuse('DUPLICATE_TICKET',
          `An identical ticket, ${duplicate.id}, was opened at ${duplicate.openedAt} (UTC). ` +
          'Give the user that ticket ID instead of opening a second one.',
          { ticketId: duplicate.id });
      }
      const quota = await helpdesk.ticketQuota();
      if (quota.remaining === 0) {                                        // ⑤
        return refuse('TICKET_LIMIT',
          `This account has opened ${quota.used} tickets in the past hour, the most allowed. ` +
          `Tell the user they can open another after ${quota.resetsAt} (UTC).`,
          { resetsAt: quota.resetsAt });
      }
      const sent = await confirmTicket(args, signal);
      if (!sent) return cancelledByUser('The user closed the ticket form without sending it.');
      const ticket = await helpdesk.createTicket(args);
      return { status: 'created', ticketId: ticket.id, expectedReply: ticket.expectedReply };
    },
  }, options);

  await mc.registerTool({
    name: 'get_ticket_status',
    title: COPY.getTicketStatus.title,
    description:
      'Get the state of one of the user\'s Supportly tickets by its ID. Returns the ticket ' +
      'state (open, waiting_on_user or resolved), when it last changed, and the latest reply, ' +
      'quoted as its author wrote it.',
    inputSchema: statusSchema,
    annotations: { readOnlyHint: true, untrustedContentHint: true },
    async execute(args) {
      const invalid = checkArgs(statusSchema, args);
      if (invalid) return invalid;
      const ticket = await helpdesk.getTicket(args.ticketId);
      if (!ticket) {                                                      // ⑥
        return fail('TICKET_NOT_FOUND',
          `No ticket ${args.ticketId} on this account. Check the ID with the user; it is in ` +
          'the confirmation email.');
      }
      return {
        ticketId: ticket.id,
        ticketState: ticket.state,                                        // ⑦
        updated: ticket.updated,
        latestReply: ticket.latestReply,
      };
    },
  }, options);
}
```

① `priority` uses the `oneOf` list from Listing 11.2, so the agent reads what each level promises. When an agent sent `priority: 'urgent'`, the call returned `"\"priority\" must be one of \"low\", \"normal\", \"high\". How urgent the problem is for the user."` (*observed*).[^ch11-3]

② The tool’s title comes from the same copy as the widget’s button.

③ The schema asks only for the problem. The description says that account and contact details “are added automatically,” which tells the agent not to go looking for them, without a prohibition.

④ The duplicate check. The same subject, body and priority within an hour count as the same request. The call returns `status: 'refused'`, `code: 'DUPLICATE_TICKET'` and the existing `ticketId`, and the form never opens. In the tests, sending the first ticket’s content again returned `SUP-1044`, the ID of the ticket created a moment earlier, and the form stayed hidden (*observed*).[^ch11-3]

⑤ A rate limit is a refusal too, checked *before* the form opens, so the person isn’t asked to review a ticket that can’t be sent. After three tickets in an hour the fourth call returned `status: 'refused'`, `code: 'TICKET_LIMIT'`, with the time the limit resets, and the form stayed hidden (*observed*).[^ch11-3] The duplicate check runs first on purpose. A person who resends a ticket they already opened should hear where it is, not that they are out of tickets.

⑥ A ticket that belongs to another Supportly customer gets exactly the same answer as one that doesn’t exist. Saying “that ticket belongs to someone else” would confirm that it exists, which is information the caller has no right to. The tests compare the two messages and find them identical apart from the ID.

⑦ The ticket’s own state is `ticketState`, so `status` stays free for outcomes (Table 11.3). The reply is returned as written, in its own field, under `untrustedContentHint` (Chapters 6 and 12).

Figure 11.3 compares what the agent reads before any call, for the earlier and current versions of the five tools that appear in both.

![Figure 11.3 — Characters the agent reads per tool definition, earlier versions (Listings 6.2, 6.7 and 7.3) and this chapter’s, measured with measureTools() in Chromium 156. Every definition grew, and most of the growth is parameter descriptions and priority titles.](images/figure-11-3.png)

Every tool got longer, and the widget roughly doubled, from 955 to 1,850 characters. That is the honest trade-off of this chapter. Good design isn’t about making definitions as short as possible. It’s about making every character a decision. The additions are parameter descriptions with examples, one sentence about what each tool returns and three priority titles. All five definitions still fit Chrome’s budgets, and the lint found nothing in any of them (*observed*).[^ch11-3] The duplicate check didn’t add a single character. It lives in the result, where the agent reads it only when it matters.

What the lint can’t tell you is whether a real model now picks the right tool and fills it in correctly more often. Inspection can’t answer that, evaluation can. Chrome’s guide recommends evaluation-driven development, with code-based checks for rule-based outputs such as character limits and LLM-as-a-judge for the rest,[^ch11-5] and Anthropic’s article reports that “even small refinements to tool descriptions can yield dramatic improvements.”[^ch11-1] Chapter 14 builds that eval loop for Trailhead and the widget.

## Trailhead and the widget so far

The demos folder `chapters/11-designing-tools/` has every listing in this chapter as a file, byte for byte. A few files that the book doesn’t print fill the gaps: Trailhead’s in-memory catalogue and cart, Supportly’s in-memory help centre (with the hourly limit and the duplicate check behind it), the two demo pages, the metadata of the earlier tool versions used for Table 11.2 and Figure 11.3, and the dev-only `document.modelContext` mock from Chapter 6.

`npm test` runs 101 checks. There are syntax checks for all 16 scripts, ten unit tests of the validator, the lint and the result helpers in Node, and 37 behavioural checks that run twice, once against the mock and once in Chromium 156.0.8078.4 with `--enable-features=WebMCPTesting`, plus one check that WebMCP is available there. All 101 passed on 2 November 2026.[^ch11-3] A separate script, `npm run check-listings`, confirms that the eight listings in this chapter match the files byte for byte. The widget runs on a single origin here. Chapter 7’s folder runs it across two origins inside Ledgerly.

## Chapter summary

- A tool has two readers. The browser checks its syntax, and the model decides from the name, description, schema and results alone. Tool design is writing for a reader who can’t ask questions.
- Every registered tool costs context before it’s called, and agents handle too many tools differently, sometimes by turning WebMCP off for the page. Design from user goals and a role-played conversation instead of from endpoints. Merge steps that are always chained, split where consequences differ or where the person would want to be asked. Measure your definitions and track the number.
- Tool collections (#255) and skills (#161) are open proposals, not part of the 27 October 2026 draft. Today’s tools for scale are page-state registration, a small default set and, if you need it, loader tools you build yourself.
- Name tools as verb and object, in one style per site, with the object in the name. Describe what the tool does, when to use it, what it returns and what it changes, in positive terms. Keep live state and instructions to the agent out of descriptions, and put consequential side effects in the first sentence.
- Chrome’s budgets (500 characters per description, 150 per parameter description, 30 per name, 1,500 per output) are guidance. Enforce them with a lint in your tests rather than a style guide.
- Use enums with words, no empty options, required only for what the tool can’t work without, raw input instead of computed input, bounded arrays, and `oneOf` lists of `{ const, title }` where the meaning of a value matters. Don’t ask for what the page already knows. Always publish a schema, because #92 is leaning towards making it required.
- Validate against the schema you published, and reuse each parameter’s description in its error message. Enforce authorization and ownership in your application code, beyond any schema or annotation.
- Return high-signal results with the identifiers the next tool needs, say when a list is truncated and keep outputs under budget. `outputSchema` is still an open question in WebMCP.
- Word errors to name the problem, show a valid example, point to the next step and say who should act. Distinguish `error` (the agent can fix it), `needs_input` (ask the user), `refused` (a rule says no, and the user decides) and `cancelled_by_user` (stop). Refuse a duplicate of something you already created, and point to the original.
- Keep agent-facing text in step with the UI by sharing one source of words, building the form from it and testing the parity in a real browser. Re-register when agent-facing metadata changes, and check state again at call time and at confirmation.

## Notes

[^ch11-1]: Anthropic, “Writing effective tools for agents — with agents” (Engineering at Anthropic, published 11 September 2025), sections “Choosing the right tools for agents”, “Namespacing your tools”, “Returning meaningful context from your tools”, “Optimizing tool responses for token efficiency” and “Prompt-engineering your tool descriptions”. <https://www.anthropic.com/engineering/writing-tools-for-agents>
[^ch11-2]: WebMCP specification, Draft Community Group Report, 27 October 2026, §4.2.1 the `ModelContextTool` dictionary: `title` (“used by the user agent to reference the tool in the user interface. It is recommended that this string be localized to the user’s language”) and `description` (“A natural language description of the tool’s functionality. This helps agents understand when and how to use the tool.”). <https://webmachinelearning.github.io/webmcp/#dictdef-modelcontexttool>
[^ch11-3]: Tested by the author on 2 November 2026 in Chromium 156.0.8078.4 (Playwright 1.64.1’s Chromium build, launched with `--enable-features=WebMCPTesting`) and against the dev-only mock, 101 of 101 checks passed. The first edition’s run of 14 October 2026 measured the same character counts. Test suite and raw results: `chapters/11-designing-tools/tests/run-tests.mjs` and `tests/results/observations.json` in the book’s demos repository. <https://github.com/webmaxru/webmcp-book-demos/tree/main/chapters/11-designing-tools>
[^ch11-4]: WebMCP explainer (README), “Best Practices”: “Tool Strategy and Budget”, “Keeping agent-facing parts of a tool definition updated”, “Minimize Cognitive Computing for the Model” and “Reliability and Error Handling”, read 2 November 2026. <https://github.com/webmachinelearning/webmcp#best-practices>
[^ch11-5]: Chrome for Developers, “WebMCP best practices” by Alexandra Klepper, Maxim Salnikov and François Beaufort (published 18 May 2026, last updated 30 October 2026), sections “Create a tool strategy” (“Trust the agent to complete the task”), “Use clear language and semantic code”, “Minimize cognitive computing” (“Accept raw user input”), “Prioritize reliability”, “Enforce architectural constraints” (“Share the application service”, “Stale workflow state”, “Recompute on confirmation”) and “Eval testing and debugging” (including the honorifics example). <https://developer.chrome.com/docs/ai/webmcp/best-practices>
[^ch11-6]: OpenAI API documentation, “Function calling”, best-practices section (“Pass the intern test”, “Use enums and object structure to prevent invalid states”, “Don’t make the model fill arguments you already know”, “Combine functions that are always called in sequence”, “Aim for fewer than 20 functions available at the start of a turn”), read 14 October 2026 (not re-read for this edition). <https://platform.openai.com/docs/guides/function-calling>
[^ch11-7]: webmachinelearning/webmcp issue #255, “Tool collections: coarse-grained grouping with progressive disclosure” (opened 22 August 2026, open on 2 November 2026). <https://github.com/webmachinelearning/webmcp/issues/255>
[^ch11-8]: webmachinelearning/webmcp issue #161, “Proposal: Skills — workflow-level context for tool composition” (opened 3 April 2026, open on 2 November 2026), section “Strawman API”. <https://github.com/webmachinelearning/webmcp/issues/161>
[^ch11-9]: webmachinelearning/webmcp issue #167, “Proposal: Dynamic Tool Definitions in WebMCP” (opened 17 April 2026, closed). <https://github.com/webmachinelearning/webmcp/issues/167>
[^ch11-10]: Chrome for Developers, “WebMCP tool security” (published 9 June 2026, last updated 1 September 2026), section “Set character budgets”. <https://developer.chrome.com/docs/ai/webmcp/secure-tools>
[^ch11-11]: WebMCP specification, Draft Community Group Report, 27 October 2026, §6.3.2 “Misrepresentation of Intent”: §6.3.2.2 “Misalignment Types” and §6.3.2.3 “Scenario: Ambiguous Finalization”. <https://webmachinelearning.github.io/webmcp/#security-privacy>
[^ch11-12]: WebMCP specification, Draft Community Group Report, 27 October 2026, §6.4.2 “Restricting maximum input lengths”. <https://webmachinelearning.github.io/webmcp/#security-privacy>
[^ch11-13]: webmachinelearning/webmcp issue #73, “Consider restricting maximum input lengths” (opened 30 January 2026, open on 2 November 2026). <https://github.com/webmachinelearning/webmcp/issues/73>
[^ch11-14]: WebMCP specification, Draft Community Group Report, 27 October 2026, §3 “Supporting concepts” (a tool definition’s *input schema* is “the stringified representation of the inputSchema passed to registerTool()”) and §4.2 the `registerTool()` and `executeTool()` steps. <https://webmachinelearning.github.io/webmcp/#dom-modelcontext-registertool>
[^ch11-15]: JSON Schema, “Understanding JSON Schema”, “Enumerated values”. <https://json-schema.org/understanding-json-schema/reference/enum>
[^ch11-16]: WebMCP specification, Draft Community Group Report, 27 October 2026, §6.3.3 “Privacy Leakage Through Over-Parameterization” (§6.3.3.1 and the `search-dresses` example in §6.3.3.2). <https://webmachinelearning.github.io/webmcp/#security-privacy>
[^ch11-17]: JSON Schema, “Understanding JSON Schema”, “Schema Composition” (`allOf`, `anyOf`, `oneOf`, `not`). <https://json-schema.org/understanding-json-schema/reference/combining>
[^ch11-18]: JSON Schema, “Understanding JSON Schema”, “Constant values”. <https://json-schema.org/understanding-json-schema/reference/const>
[^ch11-19]: JSON Schema, “Understanding JSON Schema”, “Annotations” (“A ‘title’ will preferably be short, whereas a ‘description’ will provide a more lengthy explanation”). <https://json-schema.org/understanding-json-schema/reference/annotations>
[^ch11-20]: webmachinelearning/webmcp issue #92, “Who owns the validation layer?” (opened 17 February 2026, open on 2 November 2026), including the resolution recorded on 5 March 2026 and the comments of 16 October 2026 (sjdallst2) and 30 October 2026 (Johann Hofmann). Pull request #289, “Input validation (Fixes #92)”, was closed unmerged by its author on 1 October 2026. <https://github.com/webmachinelearning/webmcp/issues/92>
[^ch11-21]: Model Context Protocol specification, revision 2026-07-28, “Server Features: Tools”, sections “Tool” (`outputSchema` defaults to the 2020-12 dialect), “Structured Content”, “Output Schema” and “Error Handling” (“Tool Execution Errors contain actionable feedback…” and “Clients SHOULD provide tool execution errors to language models to enable self-correction”). <https://modelcontextprotocol.io/specification/2026-07-28/server/tools>
[^ch11-22]: webmachinelearning/webmcp issue #9, “Introduce `outputSchema` (was: Should output also have a schema?)” (opened 12 August 2025), and pull request #254, “Add `outputSchema` to `ModelContextTool` and `RegisteredTool`” by François Beaufort (merged 2 November 2026). The exposed object is now `Tool` (pull request #348, Appendix E). <https://github.com/webmachinelearning/webmcp/pull/254>
[^ch11-23]: WebMCP specification, Draft Community Group Report, 27 October 2026, §3 the tool execution error table and the note beneath it. <https://webmachinelearning.github.io/webmcp/#tool-execution-error>
[^ch11-24]: Chrome for Developers, “Build your user’s agentic workflows with WebMCP tools” by André Cipriani Bandarra and Maxim Salnikov (published 26 August 2026, last updated 30 October 2026), sections “Define the user goal”, “Define the initial state”, “Role-play the conversation”, “Address variance”, “Enforce trust boundaries” and “Fail gracefully and enable recovery” (including “Duplication conflict”). <https://developer.chrome.com/docs/ai/webmcp/build-tools>
[^ch11-25]: webmachinelearning/webmcp issue #255, comments by johnhenry (15 September 2026, the jjhub data point: 126 tools, the ChatGPT browser message quoted in the text, and the move to a budget of 20 registered tools with loader tools) and by Kenneth Rohde Christiansen (20 October 2026, feedback from the harness side). <https://github.com/webmachinelearning/webmcp/issues/255>

[^ch11-output-schema]: webmachinelearning/webmcp pull request #254, merged 2 November 2026. <https://github.com/webmachinelearning/webmcp/pull/254>
[^ch11-output-validation]: webmachinelearning/webmcp issue #92, open on 15 November 2026; the November discussion has not changed the spec’s execution algorithm. <https://github.com/webmachinelearning/webmcp/issues/92>
[^ch11-output-extension]: GoogleChromeLabs/webmcp-extension pull request #98, host-side validation before model delivery, open on 15 November 2026. <https://github.com/GoogleChromeLabs/webmcp-extension/pull/98>
