#!/usr/bin/env python3
"""Fix glosses for common radicals to be more descriptive."""
import json

# Load semantic graph
with open('web-app/static/game_data/hanzi_semantic_graph.json', 'r') as f:
    graph = json.load(f)

# Fixes for common radicals - more descriptive names
RADICAL_FIXES = {
    '宀': 'roof',
    '亻': 'person (side)',
    '辶': 'walk',
    '氵': 'water (drops)',
    '扌': 'hand (side)',
    '忄': 'heart (side)',
    '艹': 'grass (top)',
    '讠': 'speech (simp)',
    '耂': 'old (top)',
    '覀': 'west (cover)',
    '刂': 'knife (side)',
    '阝': 'mound/city',
    '冫': 'ice',
    '纟': 'silk (simp)',
    '钅': 'metal (simp)',
    '饣': 'food (simp)',
    '犭': 'dog (side)',
    '礻': 'spirit',
    '衤': 'clothing (side)',
    '灬': 'fire (bottom)',
}

changes = []

def fix_node(node):
    char = node.get('char', '')
    if char in RADICAL_FIXES:
        old = node.get('keyword', '')
        new = RADICAL_FIXES[char]
        if old != new:
            node['keyword'] = new
            changes.append((char, old, new))
    for child in node.get('children', []):
        fix_node(child)

fix_node(graph)

print(f'Fixed {len(changes)} radical glosses:')
for char, old, new in changes:
    print(f'  {char}: "{old}" -> "{new}"')

# Save
with open('web-app/static/game_data/hanzi_semantic_graph.json', 'w') as f:
    json.dump(graph, f, ensure_ascii=False, indent=2)
print('Saved!')

# Rebuild component glosses
with open('web-app/static/game_data/component_glosses.json', 'r') as f:
    glosses = json.load(f)

for char, new_gloss in RADICAL_FIXES.items():
    glosses[char] = new_gloss

with open('web-app/static/game_data/component_glosses.json', 'w') as f:
    json.dump(glosses, f, ensure_ascii=False, indent=2)
print('Updated component_glosses.json')

