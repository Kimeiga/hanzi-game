#!/usr/bin/env python3
"""Fix final duplicate keywords."""
import json

with open('web-app/static/game_data/hanzi_semantic_graph.json', 'r') as f:
    graph = json.load(f)

changes = []

def find_and_update(node, char, new_keyword):
    if 'char' in node and node['char'] == char:
        old_kw = node.get('keyword', '')
        node['keyword'] = new_keyword
        changes.append((char, old_kw, new_keyword))
        return True
    if 'children' in node:
        for child in node['children']:
            if find_and_update(child, char, new_keyword):
                return True
    return False

fixes = [
    ('諦', 'resign (trad/jp)'),
    ('捨', 'discard'),
    ('夕', 'dusk'),
    ('晩', 'evening'),
    ('徴', 'levy (trad/jp)'),
    ('賦', 'tribute (trad/jp)'),
    ('霊', 'soul (trad/jp)'),
    ('気', 'spirit (jp)'),
]

for char, new_kw in fixes:
    find_and_update(graph, char, new_kw)

print(f'Applied {len(changes)} changes:')
for char, old, new in changes:
    print(f'  {char}: "{old}" -> "{new}"')

with open('web-app/static/game_data/hanzi_semantic_graph.json', 'w') as f:
    json.dump(graph, f, ensure_ascii=False, indent=2)
print('Saved!')

