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

# The updater accidentally retained a second obsolete Chapter 5 edit for the
# old output-schema callout. Remove that edit while preserving the citations.
duplicate_label = "'Chapter 5 output subsection old start'"
label_position = source.find(duplicate_label)
if label_position >= 0:
    start = source.rfind('edit(p,', 0, label_position)
    end = source.find('updates[p] = read(p).rstrip() + """', label_position)
    if start < 0 or end < 0:
        raise SystemExit('Could not remove duplicate obsolete Chapter 5 edit')
    source = source[:start] + source[end:]

# Replace the brittle full-sentence summary matcher with a line-level match.
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

path.write_text(source, encoding='utf-8')
print('Repaired the Chapter 14 heading and Chapter 17 summary matcher')
