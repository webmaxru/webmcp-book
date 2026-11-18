from pathlib import Path
import json
import subprocess

root = Path('.')
appendix = root / 'manuscript/appendix-c-resources.md'
text = appendix.read_text(encoding='utf-8')
old = 'Every URL here was fetched again on 2 November 2026 for this edition, and each one answered with a working page, with two kinds of exception you should know about.'
new = 'The resources in the second edition were fetched again on 2 November 2026, with two kinds of exception you should know about. The polyfill entry in Section C.7 was checked on 18 November 2026.'
assert text.count(old) == 1
text = text.replace(old, new, 1)
anchor = '## C.7 Community projects and framework guides\n\n'
assert text.count(anchor) == 1
addition = '''- **W3C WebMCP polyfill** (`@w3c/webmcp-polyfill`). Want to build and test tools before a browser exposes the native API? This open-source JavaScript package gives a page `document.modelContext` so you can register tools, discover them and call them. It is useful both for web developers exposing app features and for people building in-page agents or extensions that can reach the page's tools. You can also use it to try the draft before giving feedback.\n  <https://www.npmjs.com/package/@w3c/webmcp-polyfill>\n  <https://github.com/w3c-oss/webmcp-polyfill>\n\n  Install the package and load its automatic entry point before registering tools:\n\n  ```bash\n  npm install @w3c/webmcp-polyfill\n  ```\n\n  ```js\n  import "@w3c/webmcp-polyfill/auto";\n  ```\n\n  The package follows the WebMCP draft, ships TypeScript definitions based on `webmcp-types` and has no runtime JavaScript dependencies. Version 0.1.1 targets `webmcp-types` 0.1.10. It installs only in a secure context (HTTPS or localhost) and does not replace a native `document.modelContext`.\n\n  There are boundaries to keep in mind. The polyfill does not provide a browser agent, and its documentation says that talking to an actual browser agent needs browser support. Declarative forms are not implemented, and the project's testing notes list differences from the draft. WebMCP is still a Community Group draft, not a W3C Standard, so expect both the API and the package to change. Check the testing notes before depending on a particular behaviour. *Chapters 9, 14 and 15.*\n  <https://github.com/w3c-oss/webmcp-polyfill/blob/main/TESTING.md>\n\n'''
text = text.replace(anchor, anchor + addition, 1)
appendix.write_text(text, encoding='utf-8')
meta = root / 'tools/book.json'
metadata = json.loads(meta.read_text(encoding='utf-8'))
assert metadata['version'] == '2.1.0'
metadata['version'] = '2.2.0'
meta.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
changelog = root / 'CHANGELOG.md'
text = changelog.read_text(encoding='utf-8')
old = '## [Unreleased]\n\n### Changed\n'
new = '## [Unreleased]\n\n## [2.2.0] - 2026-11-18\n\n### Added\n\n- Appendix C: the W3C WebMCP polyfill, including installation, intended audiences, TypeScript definitions and the limits of polyfill and browser-agent support.\n\n### Changed\n'
assert text.count(old) == 1
changelog.write_text(text.replace(old, new, 1), encoding='utf-8')
log = root / 'editorial/appendix-c-resources-editorial-log.md'
with log.open('a', encoding='utf-8') as f:
    f.write('\n## 18 November 2026 — WebMCP polyfill\n- Added the W3C polyfill to C.7 in the book\'s author voice, with the install command, automatic entry point, intended audiences, secure-context and native-API boundaries, and links to the package and its testing notes.\n- Checked the package documentation and the Community Group draft on 18 November 2026. Version 0.1.1 targets webmcp-types 0.1.10. No new browser behaviour was observed for this addition.\n')
validation = root / 'VALIDATION.md'
text = validation.read_text(encoding='utf-8')
anchor = '## Sources\n'
assert text.count(anchor) == 1
addition = '''## Appendix C follow-up: W3C WebMCP polyfill (18 November 2026)\n\nThe npm package README for `@w3c/webmcp-polyfill` 0.1.1 was read on 18 November 2026. It documents installation and the `auto` entry point, registration, discovery and execution, types targeting `webmcp-types` 0.1.10, no runtime JavaScript dependencies, the secure-context requirement, and the native-API and browser-agent boundaries. It says declarative forms are not implemented and points to its testing notes for differences from the draft. The specification identifies itself as a Draft Community Group Report. No package or browser behaviour was tested for this addition.\n\nSources: <https://www.npmjs.com/package/@w3c/webmcp-polyfill>, <https://github.com/w3c-oss/webmcp-polyfill/blob/main/TESTING.md>, <https://webmachinelearning.github.io/webmcp/>.\n\n'''
validation.write_text(text.replace(anchor, addition + anchor, 1), encoding='utf-8')
subprocess.run(['python3', 'tools/wordcount.py', '--update'], check=True)
assert '"version": "2.2.0"' in meta.read_text(encoding='utf-8')
assert text.count(anchor) == 1
(root / '.github/workflows/prepare-webmcp-polyfill-release.yml').unlink()
Path(__file__).unlink()
