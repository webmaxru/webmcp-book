from pathlib import Path
import re

path = Path('.github/scripts/apply-output-schema-update.py')
source = path.read_text(encoding='utf-8')

old_heading = '## Layer 4: evaluations against real models'
new_heading = '## Layer 4: evals'
if old_heading in source:
    source = source.replace(old_heading, new_heading, 1)
elif new_heading not in source:
    raise SystemExit('Chapter 14 Layer 4 heading anchor not found')

duplicate_label = "'Chapter 5 output subsection old start'"
label_position = source.find(duplicate_label)
if label_position >= 0:
    start = source.rfind('edit(p,', 0, label_position)
    end = source.find('updates[p] = read(p).rstrip() + """', label_position)
    if start < 0 or end < 0:
        raise SystemExit('Could not remove duplicate obsolete Chapter 5 edit')
    source = source[:start] + source[end:]

summary_label = "'Chapter 17 summary output schema'"
label_position = source.find(summary_label)
if label_position >= 0:
    start = source.rfind('edit(p,', 0, label_position)
    caption_position = source.find('**Listing 17.1**', label_position)
    end = source.rfind('edit(p,', label_position, caption_position)
    if start < 0 or caption_position < 0 or end <= start:
        raise SystemExit('Could not locate Chapter 17 summary edit boundaries')
    replacement = '\n'.join([
        'summary = read(p)',
        'summary, count = re.subn(',
        '    r"(?m)^ *- Output schemas are resolved.*$",',
        '    "  - PR #254 added optional `outputSchema` to the spec on 2 November. Issue #92 remains open on validation behavior. Chromium 156 still drops the member from `getTools()`; agent harnesses should validate declared results before returning them to a model.",',
        '    summary,',
        '    count=1,',
        ')',
        'if count != 1:',
        "    raise RuntimeError('Chapter 17 outputSchema summary line not found')",
        'updates[p] = summary',
        '',
    ])
    source = source[:start] + replacement + source[end:]
elif 'Chapter 17 outputSchema summary line not found' not in source:
    raise SystemExit('Chapter 17 summary edit was not found')

checklist_label = "'Chapter 17 checklist adapter'"
label_position = source.find(checklist_label)
if label_position >= 0:
    start = source.rfind('edit(p,', 0, label_position)
    line_end = source.find('\n', label_position)
    if start < 0 or line_end < 0:
        raise SystemExit('Could not locate Chapter 17 checklist edit boundaries')
    replacement = """chapter17 = read(p)
chapter17, count = re.subn(
    r"(?m)^[ \\t]*2\\.[ \\t]+\\*\\*Put the API shape in one file\\.\\*\\*.*$",
    "  2. **Put the API shape in one file.** Only the adapter calls `document.modelContext` (Listing 17.2). When continuation support or a new exposure keyword arrives, or the API moves again (Appendix D covers the last move), one file changes. The adapter already passes `outputSchema` through.",
    chapter17,
    count=1,
)
if count == 0 and "The adapter already passes `outputSchema` through." not in chapter17:
    candidates = [line for line in chapter17.splitlines() if "Put the API shape in one file." in line]
    raise SystemExit('Chapter 17 checklist adapter line not found: ' + repr(candidates[:2]))
updates[p] = chapter17
"""
    source = source[:start] + replacement.rstrip('\n') + source[line_end:]
elif 'Chapter 17 checklist adapter line not found' not in source:
    raise SystemExit('Chapter 17 checklist edit was not found')

# Replace the brittle Appendix A IDL adjacent-line replacements with dictionary-scoped edits.
appendix_marker = '# Appendix A: mirror the current IDL'
appendix_position = source.find(appendix_marker)
if appendix_position < 0:
    raise SystemExit('Appendix A IDL updater section not found')
idl_start = source.find('  idl = read(p)', appendix_position)
idl_end = source.find('  edit(p,', idl_start)
if idl_start < 0 or idl_end < 0:
    raise SystemExit('Could not locate Appendix A IDL updater boundaries')
idl_replacement = '''  idl = read(p)
  def add_output_schema(text: str, dictionary: str) -> str:
      start = text.find(f'dictionary {dictionary} {{')
      if start < 0:
          raise RuntimeError(f'Appendix A {dictionary} IDL dictionary not found')
      end = text.find('\\n};', start)
      if end < 0:
          raise RuntimeError(f'Appendix A {dictionary} IDL dictionary end not found')
      block = text[start:end]
      if re.search(r'(?m)^[ \\t]*object outputSchema;', block):
          return text
      match = re.search(r'(?m)^([ \\t]*)object inputSchema;[ \\t]*$', block)
      if match is None:
          raise RuntimeError(f'Appendix A {dictionary} IDL inputSchema not found')
      insert_at = start + match.end()
      return text[:insert_at] + '\\n' + match.group(1) + 'object outputSchema;' + text[insert_at:]

  idl = add_output_schema(idl, 'ModelContextTool')
  idl = add_output_schema(idl, 'RegisteredTool')
  updates[p] = idl

'''
source = source[:idl_start] + idl_replacement + source[idl_end:]

path.write_text(source, encoding='utf-8')
print('Repaired Chapter 14, Chapter 17, and Appendix A manuscript updater anchors')
