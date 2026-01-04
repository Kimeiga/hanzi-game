#!/usr/bin/env python3
"""Check Joyo kanji coverage in semantic graph."""

import json

with open('web-app/static/game_data/joyo_kanji.json', 'r') as f:
    joyo = json.load(f)
with open('web-app/static/game_data/hanzi_semantic_graph.json', 'r') as f:
    graph = json.load(f)

def get_all_chars(node):
    chars = set()
    if 'char' in node:
        chars.add(node['char'])
    if 'children' in node:
        for child in node['children']:
            chars.update(get_all_chars(child))
    return chars

graph_chars = get_all_chars(graph)
in_graph = [k for k in joyo if k in graph_chars]
not_in_graph = [k for k in joyo if k not in graph_chars]

print(f'Joyo kanji coverage: {len(in_graph)}/{len(joyo)} ({100*len(in_graph)/len(joyo):.1f}%)')
if not_in_graph:
    print(f'Still missing: {not_in_graph}')
else:
    print('All Joyo kanji are in the semantic graph!')

