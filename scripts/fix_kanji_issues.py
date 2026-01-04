#!/usr/bin/env python3
"""Fix kanji glosses and semantic graph issues."""
import json
import re

# Load files
with open('web-app/static/game_data/hanzi_semantic_graph.json', 'r') as f:
    graph = json.load(f)
with open('web-app/static/game_data/kanji_details.json', 'r') as f:
    details = json.load(f)

# Fixes for semantic graph keywords
semantic_fixes = {
    '行': {'keyword': 'go', 'meaning': 'go; walk; travel; move'},
    '気': {'keyword': 'spirit', 'meaning': 'spirit; energy; air; atmosphere'},
    '着': {'keyword': 'arrive', 'meaning': 'arrive; wear; attach'},
    '売': {'keyword': 'sell', 'meaning': 'sell'},
    '坂': {'keyword': 'slope', 'meaning': 'slope; hill'},
    '了': {'keyword': 'finish', 'meaning': 'finish; complete; understand'},
    '戯': {'keyword': 'play', 'meaning': 'play; frolic; drama'},
    '恒': {'keyword': 'constant', 'meaning': 'constant; permanent'},
}

# Fixes for kanji_details meanings
detail_fixes = {
    '校': {'meaning': 'school', 'description': '校 is a Japanese kanji that means school. 校 has 10 strokes, and is the 316th most common kanji in Japanese.'},
    '行': {'meaning': 'go; row'},
    '気': {'meaning': 'spirit; energy; air'},
}

# Apply fixes to semantic graph
def fix_graph(node):
    if 'char' in node and node['char'] in semantic_fixes:
        fix = semantic_fixes[node['char']]
        print(f"Fixing {node['char']}: '{node.get('keyword')}' -> '{fix['keyword']}'")
        node['keyword'] = fix['keyword']
        node['meaning'] = fix['meaning']
    if 'children' in node:
        for child in node['children']:
            fix_graph(child)

fix_graph(graph)

# Apply fixes to kanji_details
for char, fix in detail_fixes.items():
    if char in details:
        for key, val in fix.items():
            old_val = details[char].get(key, '')
            print(f"Fixing {char} {key}: '{old_val}' -> '{val}'")
            details[char][key] = val

# Save updated files
with open('web-app/static/game_data/hanzi_semantic_graph.json', 'w') as f:
    json.dump(graph, f, ensure_ascii=False, indent=2)
print("Saved hanzi_semantic_graph.json")

with open('web-app/static/game_data/kanji_details.json', 'w') as f:
    json.dump(details, f, ensure_ascii=False, indent=2)
print("Saved kanji_details.json")

print("\nFixes complete!")

