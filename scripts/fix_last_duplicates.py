#!/usr/bin/env python3
"""Fix the last 2 duplicates."""
import json

with open('web-app/static/game_data/hanzi_semantic_graph.json', 'r') as f:
    graph = json.load(f)

changes = []

def find_and_update(node, char, new_keyword, new_meaning=None):
    if 'char' in node and node['char'] == char:
        old_kw = node.get('keyword', '')
        node['keyword'] = new_keyword
        if new_meaning:
            node['meaning'] = new_meaning
        changes.append((char, old_kw, new_keyword))
        return True
    if 'children' in node:
        for child in node['children']:
            if find_and_update(child, char, new_keyword, new_meaning):
                return True
    return False

# Fix remaining duplicates
fixes = [
    # 'river': ['川', '河']
    # 川 = river/stream (smaller), 河 = river (larger, like Yellow River)
    ('川', 'river', 'river; stream'),  # Keep
    ('河', 'large river', 'river (large); the Yellow River'),
    
    # 'section': ['段', '部']  
    # 段 = step/stage/paragraph, 部 = section/department
    ('段', 'step', 'step; stage; paragraph'),
    ('部', 'section', 'section; department; part'),  # Keep
]

print("Fixing last duplicates...")

for char, new_kw, meaning in fixes:
    find_and_update(graph, char, new_kw, meaning)

print(f"\nApplied {len(changes)} changes:")
for char, old, new in changes:
    print(f"  {char}: '{old}' -> '{new}'")

with open('web-app/static/game_data/hanzi_semantic_graph.json', 'w') as f:
    json.dump(graph, f, ensure_ascii=False, indent=2)
print("\nSaved hanzi_semantic_graph.json")

