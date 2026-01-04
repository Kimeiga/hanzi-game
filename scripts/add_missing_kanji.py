#!/usr/bin/env python3
"""Add missing kanji to the semantic graph."""

import json

# Load graph
with open('web-app/static/game_data/hanzi_semantic_graph.json', 'r') as f:
    graph = json.load(f)

# Find Society > Government
def find_category(node, target_name, path=[]):
    if node.get('name') == target_name:
        return node, path + [target_name]
    if 'children' in node:
        for child in node['children']:
            if isinstance(child, dict) and 'name' in child:
                result = find_category(child, target_name, path + [node.get('name', '')])
                if result:
                    return result
    return None

result = find_category(graph, 'Government')
if result:
    gov_node, path = result
    print('Found path:', ' > '.join(path))
    
    # Check if 科 already exists
    existing = [c.get('char') for c in gov_node.get('children', []) if isinstance(c, dict)]
    if '科' not in existing:
        # Add 科
        new_entry = {
            'char': '科',
            'keyword': 'department',
            'simp': None,
            'pinyin': 'kē',
            'meaning': 'department, branch of study, section',
            'study_order': None
        }
        
        if 'children' not in gov_node:
            gov_node['children'] = []
        
        gov_node['children'].append(new_entry)
        print('Added 科 to Government')
        
        with open('web-app/static/game_data/hanzi_semantic_graph.json', 'w') as f:
            json.dump(graph, f, ensure_ascii=False, indent=2)
        print('Saved!')
    else:
        print('科 already exists in Government')
else:
    print('Government category not found')

