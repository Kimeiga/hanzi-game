#!/usr/bin/env python3
"""Build a component glosses lookup file from the semantic graph."""
import json

# Load semantic graph
with open('web-app/static/game_data/hanzi_semantic_graph.json', 'r') as f:
    graph = json.load(f)

# Collect all char -> gloss mappings
component_glosses = {}

def collect(node):
    char = node.get('char', '')
    keyword = node.get('keyword', '')
    if char and keyword:
        component_glosses[char] = keyword
    for child in node.get('children', []):
        collect(child)

collect(graph)

# Save
output_file = 'web-app/static/game_data/component_glosses.json'
with open(output_file, 'w') as f:
    json.dump(component_glosses, f, ensure_ascii=False, indent=2)

print(f'Saved {len(component_glosses)} component glosses to {output_file}')

