#!/usr/bin/env python3
"""Find JLPT kanji with potentially wrong semantic categories."""

import json

with open('web-app/static/game_data/jlpt_kanji.json', 'r') as f:
    jlpt = json.load(f)
with open('web-app/static/game_data/kanji_details.json', 'r') as f:
    details = json.load(f)
with open('web-app/static/game_data/hanzi_semantic_graph.json', 'r') as f:
    graph = json.load(f)

char_info = {}
def walk(node, path=[]):
    if 'char' in node:
        char_info[node['char']] = {'keyword': node.get('keyword', '?'), 'path': ' > '.join(path)}
    if 'children' in node:
        for c in node['children']:
            walk(c, path + [c['name']] if 'name' in c else path)
walk(graph)

# Find kanji with potentially wrong categories
issues = []
for level in ['N5', 'N4', 'N3', 'N2', 'N1']:
    for k in jlpt[level]:
        info = char_info.get(k, {})
        d = details.get(k, {})
        kw = info.get('keyword', '?')
        path = info.get('path', '')
        jp = d.get('meaning', '')
        
        # Actions that are in wrong categories
        action_words = ['go', 'come', 'enter', 'exit', 'eat', 'write', 'read', 'speak', 'hear', 'see', 
                        'walk', 'run', 'stand', 'sit', 'buy', 'sell', 'make', 'use', 'put', 'take']
        
        if any(w in jp.lower().split() for w in action_words) and 'Actions' not in path:
            issues.append((k, kw, jp, path, level, 'Should be Action'))

print(f'Found {len(issues)} potential action mismatches')
for k, kw, jp, path, level, issue in issues[:40]:
    print(f'{level} {k}  {kw:15s}  {jp:20s}  {path[:45]}')

