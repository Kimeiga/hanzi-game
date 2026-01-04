#!/usr/bin/env python3
"""Analyze which components need glosses for character equations."""
import json

# Load all the data
with open('web-app/static/game_data/char_to_decomposition.json', 'r') as f:
    decomp = json.load(f)

with open('web-app/static/game_data/allowed_components.json', 'r') as f:
    allowed = json.load(f)

with open('web-app/static/game_data/hanzi_semantic_graph.json', 'r') as f:
    graph = json.load(f)

# Build a dict of all chars with glosses in the semantic graph
chars_with_glosses = {}
def collect_glosses(node):
    char = node.get('char', '')
    kw = node.get('keyword', '')
    if char and kw:
        chars_with_glosses[char] = kw
    if 'children' in node:
        for child in node['children']:
            collect_glosses(child)

collect_glosses(graph)

print(f'Total allowed components (leaf components from HSK): {len(allowed)}')
print(f'Total chars with glosses in semantic graph: {len(chars_with_glosses)}')

# Check which allowed components have glosses
with_gloss = []
without_gloss = []

for comp in allowed:
    if comp in chars_with_glosses:
        with_gloss.append((comp, chars_with_glosses[comp]))
    else:
        without_gloss.append(comp)

print(f'\nComponents WITH glosses: {len(with_gloss)}')
print(f'Components WITHOUT glosses: {len(without_gloss)}')

# Categorize components without glosses
entity_refs = []
unicode_chars = []

for comp in without_gloss:
    if comp.startswith('&'):
        entity_refs.append(comp)
    else:
        unicode_chars.append(comp)

print(f'\n=== Breakdown of components needing glosses ===')
print(f'Entity references (like &CDP-855B;): {len(entity_refs)}')
print(f'Unicode characters: {len(unicode_chars)}')

# Further categorize Unicode chars
ascii_chars = []  # A-Z, 0-9, etc
cjk_radicals = []  # U+2E80-2EFF range (CJK Radicals Supplement)
cjk_strokes = []  # U+31C0-31EF range (CJK Strokes)
extended_cjk = []  # SIP characters (U+20000+)
other_cjk = []

for comp in unicode_chars:
    if len(comp) != 1:
        other_cjk.append(comp)
        continue
    cp = ord(comp)
    if cp < 0x100:  # ASCII/Latin-1
        ascii_chars.append(comp)
    elif 0x2E80 <= cp <= 0x2EFF:  # CJK Radicals Supplement
        cjk_radicals.append(comp)
    elif 0x31C0 <= cp <= 0x31EF:  # CJK Strokes
        cjk_strokes.append(comp)
    elif cp >= 0x20000:  # SIP (Extension B+)
        extended_cjk.append(comp)
    else:
        other_cjk.append(comp)

print(f'\n=== Categorized Unicode chars needing glosses ===')
print(f'ASCII/Latin (A-Z, 0-9, etc): {len(ascii_chars)}')
print(f'CJK Radicals Supplement (⺀-⻿): {len(cjk_radicals)}')
print(f'CJK Strokes (㇀-㇯): {len(cjk_strokes)}')
print(f'Extended CJK (U+20000+): {len(extended_cjk)}')
print(f'Other CJK: {len(other_cjk)}')

print(f'\n=== CJK Radicals needing glosses ({len(cjk_radicals)}): ===')
for comp in sorted(cjk_radicals, key=ord):
    cp = ord(comp)
    print(f'  {comp} (U+{cp:04X})')

print(f'\n=== Extended CJK needing glosses ({len(extended_cjk)}): ===')
for comp in sorted(extended_cjk, key=ord)[:40]:
    cp = ord(comp)
    print(f'  {comp} (U+{cp:04X})')
if len(extended_cjk) > 40:
    print(f'  ... and {len(extended_cjk) - 40} more')

print(f'\n=== Entity references needing glosses ({len(entity_refs)}): ===')
for comp in sorted(entity_refs)[:20]:
    print(f'  {comp}')
if len(entity_refs) > 20:
    print(f'  ... and {len(entity_refs) - 20} more')

