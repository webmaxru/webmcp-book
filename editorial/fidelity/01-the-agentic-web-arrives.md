# Fidelity check: Chapter 1, The Agentic Web Arrives

Checked 22 November 2026 against `python3 /tmp/check_fidelity.py manuscript/01-the-agentic-web-arrives.md`. Result: OK. Hashes matched the baseline.

## Protected spans

- Fences: 0 (this chapter has no code).
- Figures: 3. Figure 1.1, Figure 1.2, and Figure 1.3 lines were not edited.
- Tables: 2. Table 1.1 and Table 1.2, including separator rows and the italic captions, were not edited.
- Footnotes: 17 (`[^ch01-1]` through `[^ch01-17]`). Definitions were not edited.
- Quotes: 82, all still present per the checker.
- Also left byte-identical: the H1, the epigraph and its attribution, and `{sample: true}`.

## Numbers, dates, and quotations confirmed still present

Confirmed by search after the edit, not only by the checker:

- The shopping request, quoted in full: “Find me a two-person tent under 4,000 kroner that’s in stock, compare the two best-rated ones, and put the better one in my cart.”
- Jotunheimen, Trailhead, “Moss”, 20 per cent off, “Another screenshot.”
- September 2025 (Gemini in Chrome), October 2025 (Atlas), July 2025 (Operator folded into ChatGPT agent), Claude in Chrome research preview for 1,000 users, available on paid plans by December 2025.
- Anthropic red team: 123 prompt-injection test cases, 29 attack scenarios, 23.6% attack success rate, 11.2 per cent, 35.7 per cent to zero.
- WebArena 14.41 per cent and 78.24 per cent. Computer-Using Agent 58.1 per cent on WebArena and 87 per cent on WebVoyager.
- Screenshots “roughly 1,000–1,800 input tokens each.”
- Spec dated 27 October 2026. “When I re-checked” the implementation-status page on 2 November 2026. Origin trials in Chrome from version 149 and Edge from version 150.
- Tool names `search_products`, `compare_products`, `add_to_cart`, `get_cart`, `checkout`, `search_availability`, `book_table`. Projects Fjord Table, Trailhead, Supportly, Ledgerly, Test Agent. Repository `webmaxru/webmcp-book-demos`.
- “I can search products by query, category, maximum price and stock status…” through “I can show you the cart.”

Not in this chapter before or after the edit, so nothing here to preserve: Fjellheim 2 Tent, 3,499 NOK, order TH-100231, Posten, Saturday, the laptop, the tab.

## Generalized

Lars is now “a customer” / “the customer”. The tea errand is gone. “Probably.” is now “The outcome is still uncertain.” The heading is “A worked example: shopping by actuation”. The service-worker train memory is now the bad-connection analogy, without the author’s biography. “the strongest argument of all” was not restated as fact. “trusting mine” is now a check of the figures printed in the chapter.

## Flags

None in the chapter. VALIDATION.md still describes Lars as an established fictional example. It was not edited.
